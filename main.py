"""
Smart Railway Reservation System
A Python Tkinter Application Using Oracle Database and PL/SQL

Demonstrates core Oracle Database and PL/SQL concepts:
- Relational schema design, primary keys, foreign keys, check constraints
- Stored Procedures, Functions, and Database Triggers
- Implicit and Explicit Cursors (SYS_REFCURSOR)
- Concurrency control with SELECT ... FOR UPDATE
- ACID transactions with explicit rollback and commit
- Audit logging and data integrity protection

Technology Stack:
- Python 3.11+
- Tkinter & ttk GUI
- Oracle Database 23c/23ai/19c/21c
- oracledb Python Driver
- Matplotlib for data visualization

Entry Point: Launches the Desktop Graphical Interface.
"""

import sys
import argparse
from database.db_connection import test_connection, init_pool, close_pool
import config


def parse_args():
    parser = argparse.ArgumentParser(description=config.APP_TITLE)
    parser.add_argument("--setup-db", action="store_true", help="Re-runs database setup and inserts sample data")
    parser.add_argument("--run-tests", action="store_true", help="Executes the full test suite and exits")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.setup_db:
        from database.setup_database import run_setup
        print("Running database initialization...")
        run_setup()
        return

    if args.run_tests:
        from tests.run_all_tests import run_all_tests
        print("Executing automated test suite...")
        success = run_all_tests()
        sys.exit(0 if success else 1)

    print("=" * 75)
    print(f" {config.APP_TITLE}")
    print(f" {config.APP_SUBTITLE}")
    print(f" Version: {config.APP_VERSION}")
    print("=" * 75)

    # Pre-test Oracle Database connectivity
    print(f"Connecting to Oracle Database at {config.DB_HOST}:{config.DB_PORT}/{config.DB_SERVICE} as '{config.DB_USER}'...")
    connected, status_msg = test_connection()
    if connected:
        print(f" [OK] {status_msg}")
        try:
            init_pool()
        except Exception as e:
            print(f" [WARN] Connection pool warning: {e}")
    else:
        print(f" [WARN] Oracle Database connection failed: {status_msg}")
        print(" Please ensure Oracle Database is running and configuration in .env is correct.")

    print("\nLaunching Desktop Tkinter Graphical User Interface...")

    from gui.main_window import MainWindow

    try:
        app = MainWindow()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    finally:
        close_pool()
        print("Database resources released cleanly.")


if __name__ == "__main__":
    main()
