"""
Database connection manager and query executor for Oracle Database.
Provides connection pooling, transaction safety, and helper functions for
executing SQL queries, calling PL/SQL procedures, and invoking functions.
"""

import sys
import logging
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
import oracledb

import config

logging.basicConfig(level=logging.INFO if config.DEBUG else logging.WARNING)
logger = logging.getLogger("RailwayDB")

# Global connection pool reference
_pool: Optional[oracledb.ConnectionPool] = None


def init_pool():
    """Initializes the Oracle connection pool."""
    global _pool
    if _pool is None:
        try:
            _pool = oracledb.create_pool(
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                host=config.DB_HOST,
                port=config.DB_PORT,
                service_name=config.DB_SERVICE,
                min=config.DB_POOL_MIN,
                max=config.DB_POOL_MAX,
                increment=config.DB_POOL_INC,
            )
            logger.info("Oracle Database connection pool initialized.")
        except Exception as e:
            logger.error(f"Failed to create Oracle connection pool: {e}")
            raise


def close_pool():
    """Closes all connections in the pool."""
    global _pool
    if _pool is not None:
        try:
            _pool.close()
            _pool = None
            logger.info("Oracle Database connection pool closed.")
        except Exception as e:
            logger.error(f"Error closing connection pool: {e}")


def test_connection() -> Tuple[bool, str]:
    """Tests connectivity to the Oracle database."""
    try:
        conn = get_raw_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT sys_context('USERENV', 'CON_NAME'), SYSDATE FROM dual")
            row = cursor.fetchone()
            msg = f"Connected to PDB: {row[0]}, Server Time: {row[1]}"
        conn.close()
        return True, msg
    except Exception as e:
        return False, str(e)


def get_raw_connection():
    """Returns a connection from the pool or creates a direct connection."""
    global _pool
    if _pool is None:
        try:
            init_pool()
        except Exception:
            # Fallback to direct standalone connection if pool fails
            return oracledb.connect(
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                host=config.DB_HOST,
                port=config.DB_PORT,
                service_name=config.DB_SERVICE,
            )
    return _pool.acquire()


@contextmanager
def get_db_connection():
    """Context manager for acquiring and releasing a connection."""
    conn = get_raw_connection()
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.warning(f"Error releasing connection: {e}")


def execute_query(sql: str, params: Optional[Any] = None) -> List[Dict[str, Any]]:
    """
    Executes a SELECT query with parameterized inputs and returns
    a list of dictionaries where keys are lowercase column names.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            if not cursor.description:
                return []

            columns = [col[0].lower() for col in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results


def execute_non_query(sql: str, params: Optional[Any] = None) -> int:
    """
    Executes an INSERT, UPDATE, or DELETE statement with parameterized inputs.
    Commits the transaction and returns the number of rows affected.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            rowcount = cursor.rowcount
            conn.commit()
            return rowcount


def call_procedure(proc_name: str, in_params: List[Any], out_types: List[Any]) -> Tuple[List[Any], Optional[str]]:
    """
    Calls a PL/SQL stored procedure with inputs and out parameters.
    
    Args:
        proc_name: Name of stored procedure, e.g. 'REGISTER_PASSENGER'
        in_params: List of input values
        out_types: List of Oracle types for outputs (e.g. oracledb.NUMBER, oracledb.STRING, oracledb.CURSOR)
        
    Returns:
        Tuple of (list_of_output_values, error_message_if_any)
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # Prepare output variables
                out_vars = [cursor.var(t) for t in out_types]
                all_params = list(in_params) + out_vars

                cursor.callproc(proc_name, all_params)

                # Extract output values
                results = []
                for var in out_vars:
                    val = var.getvalue()
                    if isinstance(val, oracledb.Cursor):
                        # Fetch all rows from ref cursor as dicts
                        cols = [c[0].lower() for c in val.description]
                        cursor_rows = [dict(zip(cols, r)) for r in val.fetchall()]
                        results.append(cursor_rows)
                    else:
                        results.append(val)

                return results, None
            except Exception as e:
                conn.rollback()
                return [], str(e)


def call_function(func_name: str, return_type: Any, params: List[Any]) -> Tuple[Any, Optional[str]]:
    """
    Calls a PL/SQL stored function.
    
    Args:
        func_name: Name of stored function, e.g. 'CALCULATE_FARE'
        return_type: Oracle type of returned value (e.g. oracledb.NUMBER, oracledb.STRING)
        params: List of arguments
        
    Returns:
        Tuple of (return_value, error_message_if_any)
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                val = cursor.callfunc(func_name, return_type, params)
                return val, None
            except Exception as e:
                return None, str(e)
