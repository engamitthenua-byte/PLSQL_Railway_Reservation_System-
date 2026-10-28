"""
Passenger Service Layer.
Interfaces between the GUI and Oracle Database for passenger management.
Implements full CRUD operations using PL/SQL stored procedures and parameterized SQL queries.
"""

from typing import Any, Dict, List, Optional, Tuple
import oracledb
from database.db_connection import execute_query, execute_non_query, call_procedure


def register_passenger(
    full_name: str,
    age: int,
    gender: str,
    phone_number: str,
    email: str
) -> Tuple[bool, str, Optional[int]]:
    """
    Registers a new passenger by invoking the PL/SQL stored procedure REGISTER_PASSENGER.
    Returns: (success: bool, message: str, passenger_id: Optional[int])
    """
    results, err = call_procedure(
        "REGISTER_PASSENGER",
        [full_name, age, gender, phone_number, email],
        [oracledb.NUMBER, oracledb.NUMBER, oracledb.STRING]
    )

    if err:
        return False, f"Failed to execute procedure: {err}", None

    passenger_id, status_code, message = results
    if status_code == 0:
        return True, message, int(passenger_id)
    else:
        return False, message, None


def update_passenger(
    passenger_id: int,
    full_name: str,
    age: int,
    gender: str,
    phone_number: str,
    email: str
) -> Tuple[bool, str]:
    """
    Updates passenger details by invoking the PL/SQL stored procedure UPDATE_PASSENGER.
    Returns: (success: bool, message: str)
    """
    results, err = call_procedure(
        "UPDATE_PASSENGER",
        [passenger_id, full_name, age, gender, phone_number, email],
        [oracledb.NUMBER, oracledb.STRING]
    )

    if err:
        return False, f"Failed to execute procedure: {err}"

    status_code, message = results
    return status_code == 0, message


def delete_passenger(passenger_id: int) -> Tuple[bool, str]:
    """
    Deletes a passenger by invoking the PL/SQL stored procedure DELETE_PASSENGER.
    Enforces referential integrity: prevents deletion if the passenger has reservation history.
    Returns: (success: bool, message: str)
    """
    results, err = call_procedure(
        "DELETE_PASSENGER",
        [passenger_id],
        [oracledb.NUMBER, oracledb.STRING]
    )

    if err:
        return False, f"Failed to execute procedure: {err}"

    status_code, message = results
    return status_code == 0, message


def get_all_passengers() -> List[Dict[str, Any]]:
    """Retrieves all registered passengers."""
    sql = """
        SELECT passenger_id, full_name, age, gender, phone_number, email,
               TO_CHAR(registration_date, 'YYYY-MM-DD HH24:MI') AS reg_date
        FROM PASSENGERS
        ORDER BY passenger_id DESC
    """
    return execute_query(sql)


def get_passenger_by_id(passenger_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single passenger record by ID."""
    sql = """
        SELECT passenger_id, full_name, age, gender, phone_number, email,
               TO_CHAR(registration_date, 'YYYY-MM-DD') AS reg_date
        FROM PASSENGERS
        WHERE passenger_id = :1
    """
    rows = execute_query(sql, [passenger_id])
    return rows[0] if rows else None


def search_passengers(keyword: str) -> List[Dict[str, Any]]:
    """Searches passengers by ID, name, phone, or email using parameterized SQL."""
    cleaned = f"%{keyword.strip().lower()}%"
    sql = """
        SELECT passenger_id, full_name, age, gender, phone_number, email,
               TO_CHAR(registration_date, 'YYYY-MM-DD') AS reg_date
        FROM PASSENGERS
        WHERE LOWER(full_name) LIKE :1
           OR LOWER(phone_number) LIKE :2
           OR LOWER(email) LIKE :3
           OR TO_CHAR(passenger_id) = :4
        ORDER BY passenger_id DESC
    """
    return execute_query(sql, [cleaned, cleaned, cleaned, keyword.strip()])


def get_passenger_history(passenger_id: int) -> List[Dict[str, Any]]:
    """Retrieves all past reservations made by a passenger."""
    sql = """
        SELECT r.reservation_id, r.pnr_number, r.journey_date, r.seat_class,
               r.passenger_count, r.total_fare, r.booking_status,
               t.train_number, t.train_name,
               sf.station_code AS from_code, st.station_code AS to_code
        FROM RESERVATIONS r
        JOIN TRAIN_SCHEDULES sch ON r.schedule_id = sch.schedule_id
        JOIN TRAINS t ON sch.train_id = t.train_id
        JOIN STATIONS sf ON r.from_station_id = sf.station_id
        JOIN STATIONS st ON r.to_station_id = st.station_id
        WHERE r.passenger_id = :1
        ORDER BY r.booking_time DESC
    """
    return execute_query(sql, [passenger_id])
