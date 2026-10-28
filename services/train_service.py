"""
Train Service Layer.
Manages train inventory, schedules, stops, and train inquiries via Oracle Database and PL/SQL.
Demonstrates parameterized SQL queries, PL/SQL stored procedures, and check constraints.
"""

from typing import Any, Dict, List, Optional, Tuple
import oracledb
from database.db_connection import execute_query, execute_non_query, call_procedure, call_function


def add_train(
    train_number: str,
    train_name: str,
    train_type: str,
    source_station_id: int,
    dest_station_id: int,
    total_capacity: int = 500
) -> Tuple[bool, str, Optional[int]]:
    """
    Adds a new train via PL/SQL stored procedure ADD_TRAIN.
    """
    results, err = call_procedure(
        "ADD_TRAIN",
        [train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity],
        [oracledb.NUMBER, oracledb.NUMBER, oracledb.STRING]
    )

    if err:
        return False, f"Procedure execution failed: {err}", None

    train_id, status_code, message = results
    if status_code == 0:
        return True, message, int(train_id)
    else:
        return False, message, None


def update_train(
    train_id: int,
    train_name: str,
    train_type: str,
    total_capacity: int,
    status: str
) -> Tuple[bool, str]:
    """
    Updates train information via PL/SQL stored procedure UPDATE_TRAIN.
    """
    results, err = call_procedure(
        "UPDATE_TRAIN",
        [train_id, train_name, train_type, total_capacity, status],
        [oracledb.NUMBER, oracledb.STRING]
    )

    if err:
        return False, f"Procedure execution failed: {err}"

    status_code, message = results
    return status_code == 0, message


def get_all_trains() -> List[Dict[str, Any]]:
    """Retrieves all trains with origin and destination station details."""
    sql = """
        SELECT t.train_id, t.train_number, t.train_name, t.train_type,
               t.total_capacity, t.status,
               s_src.station_code AS source_code, s_src.station_name AS source_name,
               s_dst.station_code AS dest_code, s_dst.station_name AS dest_name
        FROM TRAINS t
        JOIN STATIONS s_src ON t.source_station_id = s_src.station_id
        JOIN STATIONS s_dst ON t.dest_station_id = s_dst.station_id
        ORDER BY t.train_number ASC
    """
    return execute_query(sql)


def search_trains_by_keyword(keyword: str) -> List[Dict[str, Any]]:
    """
    Searches trains by train number, train name, or type using parameterized SQL.
    """
    clean_kw = f"%{keyword.strip().lower()}%"
    sql = """
        SELECT t.train_id, t.train_number, t.train_name, t.train_type,
               t.total_capacity, t.status,
               s_src.station_code AS source_code, s_src.station_name AS source_name,
               s_dst.station_code AS dest_code, s_dst.station_name AS dest_name
        FROM TRAINS t
        JOIN STATIONS s_src ON t.source_station_id = s_src.station_id
        JOIN STATIONS s_dst ON t.dest_station_id = s_dst.station_id
        WHERE LOWER(t.train_number) LIKE :1
           OR LOWER(t.train_name) LIKE :2
           OR LOWER(t.train_type) LIKE :3
        ORDER BY t.train_number ASC
    """
    return execute_query(sql, [clean_kw, clean_kw, clean_kw])


def get_train_by_id(train_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single train by primary key ID."""
    sql = """
        SELECT t.train_id, t.train_number, t.train_name, t.train_type,
               t.total_capacity, t.status,
               s_src.station_code AS source_code, s_src.station_name AS source_name,
               s_dst.station_code AS dest_code, s_dst.station_name AS dest_name
        FROM TRAINS t
        JOIN STATIONS s_src ON t.source_station_id = s_src.station_id
        JOIN STATIONS s_dst ON t.dest_station_id = s_dst.station_id
        WHERE t.train_id = :1
    """
    rows = execute_query(sql, [train_id])
    return rows[0] if rows else None


def get_train_stops(train_id: int) -> List[Dict[str, Any]]:
    """Retrieves all intermediate stops for a train ordered by stop sequence."""
    sql = """
        SELECT ts.stop_id, ts.stop_sequence, ts.arrival_time, ts.departure_time,
               ts.distance_from_source_km, ts.day_offset,
               s.station_id, s.station_code, s.station_name, s.city, s.state
        FROM TRAIN_STOPS ts
        JOIN STATIONS s ON ts.station_id = s.station_id
        WHERE ts.train_id = :1
        ORDER BY ts.stop_sequence ASC
    """
    return execute_query(sql, [train_id])


def get_train_schedule_inventory(train_id: int) -> List[Dict[str, Any]]:
    """
    Retrieves schedules and seat inventory capacity for a specific train.
    """
    sql = """
        SELECT sch.schedule_id,
               TO_CHAR(sch.departure_date, 'YYYY-MM-DD') AS departure_date,
               TO_CHAR(sch.arrival_date, 'YYYY-MM-DD') AS arrival_date,
               sch.base_fare, sch.status AS schedule_status,
               st.seat_class, st.total_seats, st.booked_seats, st.available_seats
        FROM TRAIN_SCHEDULES sch
        JOIN TRAIN_SEATS st ON sch.schedule_id = st.schedule_id
        WHERE sch.train_id = :1
        ORDER BY sch.departure_date DESC, st.seat_class ASC
    """
    return execute_query(sql, [train_id])


def _build_raw_results(
    from_station_id: int,
    to_station_id: int,
    journey_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Internal helper: runs the train-stop join query with an optional date filter."""
    sql = """
        SELECT t.train_id, t.train_number, t.train_name, t.train_type,
               sch.schedule_id,
               TO_CHAR(sch.departure_date, 'YYYY-MM-DD') AS departure_date,
               TO_CHAR(sch.arrival_date, 'YYYY-MM-DD') AS arrival_date,
               sch.base_fare,
               s1.departure_time AS origin_departure_time,
               s1.day_offset AS origin_day_offset,
               s2.arrival_time AS dest_arrival_time,
               s2.day_offset AS dest_day_offset,
               (s2.distance_from_source_km - s1.distance_from_source_km) AS segment_distance_km,
               st_from.station_code AS from_code, st_from.station_name AS from_name,
               st_to.station_code AS to_code, st_to.station_name AS to_name
        FROM TRAINS t
        JOIN TRAIN_STOPS s1 ON t.train_id = s1.train_id AND s1.station_id = :1
        JOIN TRAIN_STOPS s2 ON t.train_id = s2.train_id AND s2.station_id = :2
        JOIN TRAIN_SCHEDULES sch ON t.train_id = sch.train_id
        JOIN STATIONS st_from ON s1.station_id = st_from.station_id
        JOIN STATIONS st_to ON s2.station_id = st_to.station_id
        WHERE s1.stop_sequence < s2.stop_sequence
          AND sch.status = 'SCHEDULED'
          AND t.status = 'ACTIVE'
    """
    params = [from_station_id, to_station_id]

    if journey_date:
        sql += " AND sch.departure_date = TO_DATE(:3, 'YYYY-MM-DD')"
        params.append(journey_date)

    sql += " ORDER BY s1.departure_time ASC"
    return execute_query(sql, params)


def _process_raw_results(raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enriches raw DB rows with duration, seats, and fares calculated via PL/SQL."""
    processed = []
    for r in raw_results:
        # Calculate journey duration in minutes
        dep_parts = [int(p) for p in r["origin_departure_time"].split(":")]
        arr_parts = [int(p) for p in r["dest_arrival_time"].split(":")]
        dep_mins = (dep_parts[0] * 60) + dep_parts[1] + (r["origin_day_offset"] * 1440)
        arr_mins = (arr_parts[0] * 60) + arr_parts[1] + (r["dest_day_offset"] * 1440)
        duration_mins = arr_mins - dep_mins
        if duration_mins < 0:
            duration_mins += 1440

        hours = int(duration_mins // 60)
        mins = int(duration_mins % 60)
        duration_formatted = f"{hours}h {mins:02d}m"

        # Query seat availability for each class from TRAIN_SEATS
        seats_sql = """
            SELECT seat_class, available_seats, total_seats
            FROM TRAIN_SEATS
            WHERE schedule_id = :1
            ORDER BY seat_class
        """
        seat_rows = execute_query(seats_sql, [r["schedule_id"]])
        seat_avail = {sr["seat_class"]: sr["available_seats"] for sr in seat_rows}

        # Calculate estimated fares using PL/SQL function CALCULATE_FARE
        dist = float(r["segment_distance_km"])
        train_type = r["train_type"]
        fare_sl, _ = call_function("CALCULATE_FARE", oracledb.NUMBER, [dist, train_type, "SL", 1])
        fare_3a, _ = call_function("CALCULATE_FARE", oracledb.NUMBER, [dist, train_type, "3A", 1])
        fare_2a, _ = call_function("CALCULATE_FARE", oracledb.NUMBER, [dist, train_type, "2A", 1])
        fare_1a, _ = call_function("CALCULATE_FARE", oracledb.NUMBER, [dist, train_type, "1A", 1])

        r_dict = dict(r)
        r_dict["duration_min"] = duration_mins
        r_dict["duration_formatted"] = duration_formatted
        r_dict["departure_time"] = r["origin_departure_time"]
        r_dict["arrival_time"] = r["dest_arrival_time"]
        r_dict["seat_availability"] = seat_avail
        r_dict["fare_sl"] = float(fare_sl or 0.0)
        r_dict["fare_3a"] = float(fare_3a or 0.0)
        r_dict["fare_2a"] = float(fare_2a or 0.0)
        r_dict["fare_1a"] = float(fare_1a or 0.0)
        r_dict["total_fare"] = r_dict["fare_sl"]
        processed.append(r_dict)
    return processed


def search_trains(
    from_station_id: int,
    to_station_id: int,
    journey_date: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Searches for trains connecting the origin and destination stations.
    Calculates segment distance, journey duration, seat availability, and fares.
    Returns:
        Tuple of (train_results, metadata_dict)
    """
    date_filter_used = bool(journey_date)
    raw_results = _build_raw_results(from_station_id, to_station_id, journey_date)

    fallback_used = False
    if not raw_results and date_filter_used:
        raw_results = _build_raw_results(from_station_id, to_station_id, journey_date=None)
        fallback_used = True

    processed = _process_raw_results(raw_results)
    meta = {
        "count": len(processed),
        "fallback_used": fallback_used
    }
    return processed, meta
