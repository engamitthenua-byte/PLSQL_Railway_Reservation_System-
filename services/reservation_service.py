"""
Reservation Service Layer.
Coordinates ticket booking, cancellation, and PNR inquiries.
Encapsulates PL/SQL transaction boundaries and concurrency controls.
"""

from typing import Any, Dict, List, Optional, Tuple
import logging
import oracledb
import config
from database.db_connection import get_db_connection, execute_query, execute_non_query, call_procedure, call_function

logger = logging.getLogger("ReservationService")


def book_ticket(
    passenger_id: int,
    schedule_id: int,
    from_station_id: int,
    to_station_id: int,
    journey_date_str: str,
    seat_class: str,
    passenger_list: List[Dict[str, Any]],
    payment_method: str = "UPI"
) -> Tuple[bool, Optional[str], Optional[int], str]:
    """
    Executes atomic ticket reservation using the PL/SQL stored procedure BOOK_TICKET.
    Prevents overbooking via database row-level locking (SELECT ... FOR UPDATE).

    Args:
        passenger_id: Primary booker ID in PASSENGERS
        schedule_id: Train schedule ID
        from_station_id: Boarding station ID
        to_station_id: Destination station ID
        journey_date_str: Date string 'YYYY-MM-DD'
        seat_class: '1A', '2A', '3A', or 'SL'
        passenger_list: List of dicts: [{'name': '...', 'age': 30, 'gender': 'Male'}]
        payment_method: 'UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Cash'

    Returns:
        (success: bool, pnr: Optional[str], reservation_id: Optional[int], message: str)
    """
    passenger_count = len(passenger_list)
    if passenger_count == 0:
        return False, None, None, "At least one passenger must be specified."

    # 1. Fetch distance and train type to calculate authoritative fare via PL/SQL function
    info_sql = """
        SELECT (s2.distance_from_source_km - s1.distance_from_source_km) AS dist, t.train_type
        FROM TRAIN_SCHEDULES sch
        JOIN TRAINS t ON sch.train_id = t.train_id
        JOIN TRAIN_STOPS s1 ON t.train_id = s1.train_id AND s1.station_id = :1
        JOIN TRAIN_STOPS s2 ON t.train_id = s2.train_id AND s2.station_id = :2
        WHERE sch.schedule_id = :3
    """
    rows = execute_query(info_sql, [from_station_id, to_station_id, schedule_id])
    if not rows:
        return False, None, None, "Cannot find valid train stop route for selected stations and schedule."

    dist = float(rows[0]["dist"])
    train_type = rows[0]["train_type"]

    # Calculate total fare using PL/SQL function CALCULATE_FARE
    calc_fare, _ = call_function("CALCULATE_FARE", oracledb.NUMBER, [dist, train_type, seat_class, passenger_count])
    total_fare = float(calc_fare or 0.0)

    # 2. Call PL/SQL Stored Procedure BOOK_TICKET
    # Parameters:
    #   p_passenger_id, p_schedule_id, p_from_station_id, p_to_station_id,
    #   p_journey_date, p_seat_class, p_passenger_count, p_total_fare, p_payment_method
    # Outputs:
    #   o_reservation_id (NUMBER), o_pnr_number (VARCHAR2), o_status_code (NUMBER), o_message (VARCHAR2)
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                from datetime import datetime
                if isinstance(journey_date_str, str):
                    date_val = datetime.strptime(journey_date_str[:10], "%Y-%m-%d").date()
                else:
                    date_val = journey_date_str

                o_res_id = cursor.var(oracledb.NUMBER)
                o_pnr = cursor.var(oracledb.STRING)
                o_status = cursor.var(oracledb.NUMBER)
                o_msg = cursor.var(oracledb.STRING)

                cursor.callproc(
                    "BOOK_TICKET",
                    [
                        passenger_id,
                        schedule_id,
                        from_station_id,
                        to_station_id,
                        date_val,
                        seat_class,
                        passenger_count,
                        total_fare,
                        payment_method,
                        o_res_id,
                        o_pnr,
                        o_status,
                        o_msg,
                    ]
                )

                status_code = o_status.getvalue()
                msg = o_msg.getvalue()

                if status_code != 0:
                    conn.rollback()
                    return False, None, None, msg

                res_id = int(o_res_id.getvalue())
                pnr = o_pnr.getvalue()

                # 3. Insert individual passenger records into RESERVATION_PASSENGERS
                coach_prefix = {"1A": "H1", "2A": "A1", "3A": "B1", "SL": "S1"}.get(seat_class, "S1")
                for idx, p in enumerate(passenger_list, 1):
                    seat_num = f"{coach_prefix}-{idx + 10}"
                    cursor.execute(
                        """
                        INSERT INTO RESERVATION_PASSENGERS (reservation_id, passenger_name, age, gender, seat_number)
                        VALUES (:1, :2, :3, :4, :5)
                        """,
                        [res_id, p["name"], p["age"], p.get("gender", "Other"), seat_num]
                    )

                conn.commit()
                return True, pnr, res_id, f"Ticket booked successfully! PNR: {pnr}"

            except Exception as e:
                conn.rollback()
                return False, None, None, f"Booking transaction failed: {e}"


def cancel_ticket(pnr_number: str, reason: str = "Passenger Request") -> Tuple[bool, float, float, str]:
    """
    Cancels an existing ticket via PL/SQL stored procedure CANCEL_TICKET.
    Restores seat inventory and updates transaction status atomically.

    Returns:
        (success: bool, refund_amount: float, cancellation_charge: float, message: str)
    """
    # Outputs: o_refund_amount (NUMBER), o_cancellation_charge (NUMBER), o_status_code (NUMBER), o_message (VARCHAR2)
    results, err = call_procedure(
        "CANCEL_TICKET",
        [pnr_number.strip().upper(), reason],
        [oracledb.NUMBER, oracledb.NUMBER, oracledb.NUMBER, oracledb.STRING]
    )

    if err:
        return False, 0.0, 0.0, f"Cancellation procedure failed: {err}"

    refund_amt, cancel_charge, status_code, message = results
    if status_code == 0:
        return True, float(refund_amt or 0.0), float(cancel_charge or 0.0), message
    else:
        return False, 0.0, 0.0, message


def get_reservation_by_pnr(pnr_number: str) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]], str]:
    """
    Retrieves full reservation details and passengers by PNR using
    the PL/SQL stored procedure GET_RESERVATION_DETAILS.
    """
    results, err = call_procedure(
        "GET_RESERVATION_DETAILS",
        [pnr_number.strip().upper()],
        [oracledb.CURSOR, oracledb.CURSOR, oracledb.NUMBER, oracledb.STRING]
    )

    if err:
        return None, [], f"Database error: {err}"

    res_rows, pass_rows, status_code, message = results
    if status_code != 0 or not res_rows:
        return None, [], message

    return res_rows[0], pass_rows, message


def get_all_reservations(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieves all reservations ordered by most recent booking time."""
    sql = """
        SELECT r.reservation_id, r.pnr_number,
               TO_CHAR(r.journey_date, 'YYYY-MM-DD') AS journey_date,
               r.seat_class, r.passenger_count, r.total_fare, r.booking_status,
               TO_CHAR(r.booking_time, 'YYYY-MM-DD HH24:MI') AS booking_time,
               p.full_name AS passenger_name, p.phone_number,
               t.train_number, t.train_name,
               s_from.station_code AS from_code, s_to.station_code AS to_code
        FROM RESERVATIONS r
        JOIN PASSENGERS p ON r.passenger_id = p.passenger_id
        JOIN TRAIN_SCHEDULES sch ON r.schedule_id = sch.schedule_id
        JOIN TRAINS t ON sch.train_id = t.train_id
        JOIN STATIONS s_from ON r.from_station_id = s_from.station_id
        JOIN STATIONS s_to ON r.to_station_id = s_to.station_id
        ORDER BY r.booking_time DESC
        FETCH FIRST :1 ROWS ONLY
    """
    return execute_query(sql, [limit])


def get_suggested_pnrs(status: Optional[str] = "CONFIRMED", limit: int = 100) -> List[str]:
    """
    Retrieves a list of recent PNR numbers from Oracle Database.
    Defaults to returning active (CONFIRMED) reservations sorted newest first.
    Excludes cancelled reservations so users get actionable recommendations.
    """
    try:
        if status:
            sql = """
                SELECT pnr_number
                FROM RESERVATIONS
                WHERE booking_status = :1
                ORDER BY booking_time DESC
                FETCH FIRST :2 ROWS ONLY
            """
            rows = execute_query(sql, [status, limit])
        else:
            sql = """
                SELECT pnr_number
                FROM RESERVATIONS
                ORDER BY booking_time DESC
                FETCH FIRST :1 ROWS ONLY
            """
            rows = execute_query(sql, [limit])

        return [r["pnr_number"] for r in rows if r.get("pnr_number")]
    except Exception as e:
        logger.warning(f"Error fetching PNR suggestions: {e}")
        return []

