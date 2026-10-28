"""
Station Service Layer.
Manages railway stations using Oracle Database and PL/SQL.
"""

from typing import Any, Dict, List, Optional, Tuple
import oracledb
from database.db_connection import execute_query, execute_non_query, call_procedure


def add_station(
    station_code: str,
    station_name: str,
    city: str,
    state: str
) -> Tuple[bool, str, Optional[int]]:
    """
    Adds a new station via PL/SQL stored procedure ADD_STATION.
    """
    results, err = call_procedure(
        "ADD_STATION",
        [station_code, station_name, city, state],
        [oracledb.NUMBER, oracledb.NUMBER, oracledb.STRING]
    )

    if err:
        return False, f"Procedure call failed: {err}", None

    station_id, status_code, message = results
    if status_code == 0:
        return True, message, int(station_id)
    else:
        return False, message, None


def get_all_stations() -> List[Dict[str, Any]]:
    """Retrieves all stations ordered by station code."""
    sql = """
        SELECT station_id, station_code, station_name, city, state
        FROM STATIONS
        ORDER BY station_code ASC
    """
    return execute_query(sql)


def get_station_by_id(station_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single station by its ID."""
    sql = """
        SELECT station_id, station_code, station_name, city, state
        FROM STATIONS
        WHERE station_id = :1
    """
    rows = execute_query(sql, [station_id])
    return rows[0] if rows else None


def delete_station(station_id: int) -> Tuple[bool, str]:
    """
    Deletes a station if no foreign key dependencies exist.
    """
    # Check if station is in use in TRAIN_STOPS, TRAINS, or ROUTE_CONNECTIONS
    chk_trains = execute_query(
        "SELECT COUNT(*) AS cnt FROM TRAINS WHERE source_station_id = :1 OR dest_station_id = :1",
        [station_id]
    )
    if chk_trains and chk_trains[0]["cnt"] > 0:
        return False, "Cannot delete station: It is configured as a source or destination for active trains."

    chk_stops = execute_query(
        "SELECT COUNT(*) AS cnt FROM TRAIN_STOPS WHERE station_id = :1",
        [station_id]
    )
    if chk_stops and chk_stops[0]["cnt"] > 0:
        return False, "Cannot delete station: It is referenced in train schedules/stops."

    try:
        execute_non_query("DELETE FROM STATIONS WHERE station_id = :1", [station_id])
        return True, "Station deleted successfully."
    except Exception as e:
        return False, f"Failed to delete station: {e}"
