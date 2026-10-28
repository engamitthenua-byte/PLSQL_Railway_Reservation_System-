"""
Database Setup Script for Oracle Database
Executes schema.sql, procedures.sql, functions.sql, triggers.sql, and sample_data.sql.
"""

import os
import re
import sys
import oracledb
from dotenv import load_dotenv

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_USER = os.getenv("DB_USER", "railway_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "1521"))
DB_SERVICE = os.getenv("DB_SERVICE", "FREEPDB1")


def get_connection():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        service_name=DB_SERVICE,
    )


def split_sql_script(content: str):
    """
    Carefully splits Oracle SQL files containing standard DDL/DML and PL/SQL blocks.
    Slash ('/') indicates the execution boundary for PL/SQL blocks.
    Semicolons (';') terminate individual DDL/DML statements.
    """
    statements = []
    content = content.replace('\r\n', '\n')
    
    # Split content on lines that are just '/'
    chunks = re.split(r'^[ \t]*/[ \t]*$', content, flags=re.MULTILINE)
    
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        
        # Check if this chunk is a PL/SQL block
        # (starts with DECLARE, BEGIN, or CREATE [OR REPLACE] PROCEDURE/FUNCTION/TRIGGER)
        chunk_no_comments = re.sub(r'--.*$', '', chunk, flags=re.MULTILINE).strip()
        upper_chunk = chunk_no_comments.upper()
        
        is_plsql = bool(re.match(r'^(DECLARE|BEGIN|CREATE\s+(OR\s+REPLACE\s+)?(PROCEDURE|FUNCTION|TRIGGER|PACKAGE))', upper_chunk))
        
        if is_plsql:
            # Execute as a single PL/SQL block
            clean_stmt = chunk_no_comments.rstrip()
            if not clean_stmt.endswith(';'):
                clean_stmt += ';'
            statements.append(clean_stmt)
        else:
            # Chunk consists of standard DDL/DML statements separated by semicolons
            # Split by ';' while ignoring comments
            raw_stmts = chunk.split(';')
            for raw_stmt in raw_stmts:
                # Remove line comments
                lines = [l for l in raw_stmt.split('\n') if not l.strip().startswith('--')]
                clean_stmt = '\n'.join(lines).strip()
                if clean_stmt:
                    statements.append(clean_stmt)
                    
    return statements


def execute_sql_file(cursor, file_path: str):
    print(f"\n---> Executing: {os.path.basename(file_path)}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    statements = split_sql_script(content)
    success_count = 0
    error_count = 0

    for idx, stmt in enumerate(statements, 1):
        try:
            cursor.execute(stmt)
            success_count += 1
        except Exception as e:
            # Print brief summary of error
            preview = stmt[:70].replace('\n', ' ')
            print(f"  [WARN/ERROR] Statement {idx} failed: {e}")
            print(f"       Statement was: {preview}...")
            error_count += 1

    print(f"  Result: {success_count} succeeded, {error_count} failed/skipped.")
    return error_count == 0


def run_setup():
    print("=" * 70)
    print("SMART RAILWAY RESERVATION SYSTEM")
    print("Oracle Database & PL/SQL Initialization")
    print(f"Connecting to: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_SERVICE}")
    print("=" * 70)

    try:
        conn = get_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        print(" Connected to Oracle Database successfully!")
    except Exception as e:
        print(f" Connection failed: {e}")
        return False

    db_dir = os.path.dirname(os.path.abspath(__file__))
    sql_files = [
        os.path.join(db_dir, "schema.sql"),
        os.path.join(db_dir, "procedures.sql"),
        os.path.join(db_dir, "functions.sql"),
        os.path.join(db_dir, "triggers.sql"),
        os.path.join(db_dir, "sample_data.sql"),
    ]

    for sql_file in sql_files:
        if os.path.exists(sql_file):
            execute_sql_file(cursor, sql_file)
        else:
            print(f" File not found: {sql_file}")

    # Verify tables and records
    print("\n" + "=" * 70)
    print("DATABASE VERIFICATION SUMMARY")
    print("=" * 70)
    tables = [
        "STATIONS", "PASSENGERS", "TRAINS", "TRAIN_STOPS",
        "TRAIN_SCHEDULES", "TRAIN_SEATS", "RESERVATIONS",
        "RESERVATION_PASSENGERS", "BOOKING_TRANSACTIONS",
        "CANCELLATIONS", "ROUTE_CONNECTIONS", "AUDIT_LOG"
    ]

    for tbl in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            count = cursor.fetchone()[0]
            print(f"  [OK] Table {tbl.ljust(25)}: {count} records")
        except Exception as e:
            print(f"  [ERROR] Table {tbl.ljust(22)}: Error - {e}")

    cursor.close()
    conn.close()
    print("\nDatabase initialization complete!")
    return True


if __name__ == "__main__":
    run_setup()
