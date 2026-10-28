"""
Reporting and Analytics Service Layer.
Generates administrative summaries, revenue reports, occupancy metrics,
and invokes PL/SQL reporting procedures.
"""

from typing import Any, Dict, List, Optional
import oracledb
from database.db_connection import execute_query, call_procedure


def get_dashboard_summary() -> Dict[str, Any]:
    """
    Retrieves live aggregate metrics from Oracle Database for the main dashboard.
    """
    # 1. Total counts
    counts_sql = """
        SELECT
            (SELECT COUNT(*) FROM PASSENGERS) AS total_passengers,
            (SELECT COUNT(*) FROM TRAINS) AS total_trains,
            (SELECT COUNT(*) FROM STATIONS) AS total_stations,
            (SELECT COUNT(*) FROM RESERVATIONS) AS total_reservations,
            (SELECT COUNT(*) FROM RESERVATIONS WHERE booking_status = 'CONFIRMED') AS confirmed_reservations,
            (SELECT COUNT(*) FROM RESERVATIONS WHERE booking_status = 'CANCELLED') AS cancelled_reservations,
            (SELECT NVL(SUM(total_fare), 0) FROM RESERVATIONS WHERE booking_status = 'CONFIRMED') AS net_fare_revenue,
            (SELECT NVL(SUM(cancellation_charge), 0) FROM CANCELLATIONS) AS cancellation_fees,
            (SELECT NVL(SUM(available_seats), 0) FROM TRAIN_SEATS) AS total_seats_available,
            (SELECT NVL(SUM(booked_seats), 0) FROM TRAIN_SEATS) AS total_seats_booked
        FROM dual
    """
    row = execute_query(counts_sql)[0]

    # 2. Recent booking activity
    recent_sql = """
        SELECT r.pnr_number, p.full_name AS passenger_name, t.train_number,
               s_from.station_code AS from_code, s_to.station_code AS to_code,
               r.seat_class, r.passenger_count, r.total_fare, r.booking_status,
               TO_CHAR(r.booking_time, 'YYYY-MM-DD HH24:MI') AS booking_time
        FROM RESERVATIONS r
        JOIN PASSENGERS p ON r.passenger_id = p.passenger_id
        JOIN TRAIN_SCHEDULES sch ON r.schedule_id = sch.schedule_id
        JOIN TRAINS t ON sch.train_id = t.train_id
        JOIN STATIONS s_from ON r.from_station_id = s_from.station_id
        JOIN STATIONS s_to ON r.to_station_id = s_to.station_id
        ORDER BY r.booking_time DESC
        FETCH FIRST 5 ROWS ONLY
    """
    recent_bookings = execute_query(recent_sql)

    total_rev = float(row["net_fare_revenue"]) + float(row["cancellation_fees"])

    return {
        "total_passengers": int(row["total_passengers"]),
        "total_trains": int(row["total_trains"]),
        "total_stations": int(row["total_stations"]),
        "total_reservations": int(row["total_reservations"]),
        "confirmed_reservations": int(row["confirmed_reservations"]),
        "cancelled_reservations": int(row["cancelled_reservations"]),
        "total_revenue": round(total_rev, 2),
        "total_seats_available": int(row["total_seats_available"]),
        "total_seats_booked": int(row["total_seats_booked"]),
        "recent_activity": recent_bookings,
    }


def get_train_performance_report() -> List[Dict[str, Any]]:
    """
    Invokes the PL/SQL stored procedure GENERATE_BOOKING_REPORT to retrieve
    train-wise reservations, passenger loads, and financial yields via ref cursor.
    """
    results, err = call_procedure(
        "GENERATE_BOOKING_REPORT",
        [None, None],  # from_date, to_date (None for all time)
        [oracledb.CURSOR]
    )

    if err or not results:
        # Fallback SQL query if ref cursor invocation encounters issues
        fallback_sql = """
            SELECT t.train_number, t.train_name,
                   COUNT(r.reservation_id) AS total_reservations,
                   SUM(CASE WHEN r.booking_status = 'CONFIRMED' THEN r.passenger_count ELSE 0 END) AS confirmed_passengers,
                   SUM(CASE WHEN r.booking_status = 'CANCELLED' THEN r.passenger_count ELSE 0 END) AS cancelled_passengers,
                   NVL(SUM(CASE WHEN r.booking_status = 'CONFIRMED' THEN r.total_fare ELSE 0 END), 0) AS gross_revenue,
                   NVL(SUM(c.cancellation_charge), 0) AS cancellation_fees_retained,
                   NVL(SUM(CASE WHEN r.booking_status = 'CONFIRMED' THEN r.total_fare ELSE 0 END), 0) +
                   NVL(SUM(c.cancellation_charge), 0) AS net_revenue
            FROM TRAINS t
            LEFT JOIN TRAIN_SCHEDULES sch ON t.train_id = sch.train_id
            LEFT JOIN RESERVATIONS r ON sch.schedule_id = r.schedule_id
            LEFT JOIN CANCELLATIONS c ON r.reservation_id = c.reservation_id
            GROUP BY t.train_number, t.train_name
            ORDER BY net_revenue DESC
        """
        return execute_query(fallback_sql)

    return results[0]


def get_seat_occupancy_by_class() -> List[Dict[str, Any]]:
    """
    Retrieves aggregated seat occupancy percentages broken down by travel class (1A, 2A, 3A, SL).
    """
    sql = """
        SELECT seat_class,
               SUM(total_seats) AS total_seats,
               SUM(booked_seats) AS booked_seats,
               SUM(available_seats) AS available_seats,
               ROUND((SUM(booked_seats) * 100.0) / NULLIF(SUM(total_seats), 0), 1) AS occupancy_pct
        FROM TRAIN_SEATS
        GROUP BY seat_class
        ORDER BY seat_class ASC
    """
    return execute_query(sql)


def get_cancellations_report() -> List[Dict[str, Any]]:
    """Retrieves all cancellation records with refund and audit information."""
    sql = """
        SELECT c.cancellation_id, c.cancellation_ref,
               TO_CHAR(c.cancellation_time, 'YYYY-MM-DD HH24:MI') AS cancel_time,
               c.refund_amount, c.cancellation_charge, c.reason,
               r.pnr_number, r.journey_date, r.seat_class, r.passenger_count,
               p.full_name AS passenger_name, t.train_number
        FROM CANCELLATIONS c
        JOIN RESERVATIONS r ON c.reservation_id = r.reservation_id
        JOIN PASSENGERS p ON r.passenger_id = p.passenger_id
        JOIN TRAIN_SCHEDULES sch ON r.schedule_id = sch.schedule_id
        JOIN TRAINS t ON sch.train_id = t.train_id
        ORDER BY c.cancellation_time DESC
    """
    return execute_query(sql)
