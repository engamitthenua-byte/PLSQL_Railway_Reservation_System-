"""
Test Suite: Database Operations & PL/SQL Components
Tests Stored Procedures, Functions, Triggers, Constraints, and CRUD workflows.
- Passenger Management CRUD (REGISTER_PASSENGER, UPDATE_PASSENGER, DELETE_PASSENGER)
- Train Administration (ADD_TRAIN, UPDATE_TRAIN, Unique Constraints)
- Stored Functions (CALCULATE_FARE, GET_AVAILABLE_SEATS, GET_RESERVATION_STATUS)
- Audit Triggers (TRG_TRAIN_AUDIT, TRG_RESERVATION_AUDIT)
"""

import unittest
import time
import oracledb

from services.passenger_service import (
    register_passenger,
    get_passenger_by_id,
    search_passengers,
    update_passenger,
    delete_passenger,
    get_all_passengers
)
from services.train_service import (
    add_train,
    get_all_trains,
    search_trains_by_keyword,
    update_train,
    get_train_stops,
    get_train_schedule_inventory
)
from database.db_connection import execute_query, call_function


class TestDatabaseOperations(unittest.TestCase):

    def test_01_passenger_crud_lifecycle(self):
        """Tests complete passenger lifecycle: Create, Read, Update, Delete with integrity rules."""
        unique_phone = f"99{int(time.time()) % 100000000:08d}"
        unique_email = f"user_{int(time.time())}@railway.ac.in"

        # 1. CREATE via REGISTER_PASSENGER
        ok, msg, pid = register_passenger(
            full_name="Oracle Test Passenger",
            age=29,
            gender="Female",
            phone_number=unique_phone,
            email=unique_email
        )
        self.assertTrue(ok, f"Registration failed: {msg}")
        self.assertIsNotNone(pid)

        # 2. READ & SEARCH
        p = get_passenger_by_id(pid)
        self.assertIsNotNone(p)
        self.assertEqual(p["full_name"], "Oracle Test Passenger")
        self.assertEqual(p["age"], 29)

        matches = search_passengers("Oracle Test Passenger")
        self.assertTrue(any(m["passenger_id"] == pid for m in matches))

        # 3. UPDATE via UPDATE_PASSENGER
        up_ok, up_msg = update_passenger(
            passenger_id=pid,
            full_name="Oracle Test Passenger Updated",
            age=30,
            gender="Female",
            phone_number=unique_phone,
            email=unique_email
        )
        self.assertTrue(up_ok, f"Update failed: {up_msg}")

        p_after = get_passenger_by_id(pid)
        self.assertEqual(p_after["full_name"], "Oracle Test Passenger Updated")
        self.assertEqual(p_after["age"], 30)

        # 4. DELETE via DELETE_PASSENGER (Allowed because no bookings exist)
        del_ok, del_msg = delete_passenger(pid)
        self.assertTrue(del_ok, f"Delete failed: {del_msg}")
        self.assertIsNone(get_passenger_by_id(pid))

    def test_02_passenger_deletion_prevention_on_historical_reservation(self):
        """Enforces referential integrity: passengers with existing bookings cannot be deleted."""
        # Find a passenger who has existing reservations
        rows = execute_query("SELECT passenger_id FROM RESERVATIONS FETCH FIRST 1 ROWS ONLY")
        if not rows:
            self.skipTest("No existing reservations in DB to test historical passenger retention.")

        booked_passenger_id = rows[0]["passenger_id"]
        del_ok, del_msg = delete_passenger(booked_passenger_id)
        self.assertFalse(del_ok, "Passenger with reservations should not be deleted.")
        self.assertIn("reservation", del_msg.lower())

    def test_03_train_addition_and_duplicate_rejection(self):
        """Tests ADD_TRAIN procedure and duplicate train number constraint."""
        stations = execute_query("SELECT station_id FROM STATIONS FETCH FIRST 2 ROWS ONLY")
        s1 = stations[0]["station_id"]
        s2 = stations[1]["station_id"]

        unique_train_no = f"T{int(time.time()) % 100000:05d}"

        # First insertion should succeed
        ok, msg, tid = add_train(unique_train_no, "Speed Test Express", "Superfast", s1, s2, 700)
        self.assertTrue(ok, f"Adding train failed: {msg}")
        self.assertIsNotNone(tid)

        # Duplicate insertion with identical train number must fail
        dup_ok, dup_msg, _ = add_train(unique_train_no, "Duplicate Train", "Express", s1, s2, 500)
        self.assertFalse(dup_ok)
        self.assertIn("already exists", dup_msg.lower())

    def test_04_train_update_and_audit_trigger(self):
        """Tests UPDATE_TRAIN procedure, status transition, and TRG_TRAIN_AUDIT trigger logging."""
        trains = execute_query("SELECT train_id, train_number, train_name FROM TRAINS FETCH FIRST 1 ROWS ONLY")
        if not trains:
            self.skipTest("No trains found in database.")

        tid = trains[0]["train_id"]
        tname = trains[0]["train_name"]

        # Update train status to MAINTENANCE
        ok, msg = update_train(
            train_id=tid,
            train_name=tname,
            train_type="Rajdhani",
            total_capacity=750,
            status="MAINTENANCE"
        )
        self.assertTrue(ok, f"Train update failed: {msg}")

        # Verify audit log record exists for TRAINS update
        audit_rows = execute_query(
            "SELECT details, operation FROM AUDIT_LOG WHERE table_name = 'TRAINS' AND record_id = :1 ORDER BY log_id DESC FETCH FIRST 1 ROWS ONLY",
            [tid]
        )
        self.assertTrue(len(audit_rows) > 0, "Expected an audit log entry for train modification.")
        self.assertIn("MAINTENANCE", audit_rows[0]["details"])

        # Revert back to ACTIVE
        update_train(tid, tname, "Superfast", 750, "ACTIVE")

    def test_05_stored_functions(self):
        """Tests PL/SQL stored functions CALCULATE_FARE, GET_AVAILABLE_SEATS, and GET_RESERVATION_STATUS."""
        # 1. CALCULATE_FARE
        fare, err = call_function("CALCULATE_FARE", oracledb.NUMBER, [1384.0, "Rajdhani", "3A", 2])
        self.assertIsNone(err)
        self.assertGreater(float(fare or 0.0), 0.0)

        # Fare for 0 passengers should be 0.0
        zero_fare, _ = call_function("CALCULATE_FARE", oracledb.NUMBER, [1000.0, "Superfast", "SL", 0])
        self.assertEqual(float(zero_fare or 0.0), 0.0)

        # 2. GET_AVAILABLE_SEATS
        seats, err = call_function("GET_AVAILABLE_SEATS", oracledb.NUMBER, [1, "SL"])
        self.assertIsNone(err)
        self.assertGreaterEqual(int(seats or 0), 0)

        # 3. GET_RESERVATION_STATUS
        status, err = call_function("GET_RESERVATION_STATUS", oracledb.STRING, ["NON_EXISTENT_PNR_9999"])
        self.assertIsNone(err)
        self.assertEqual(status, "NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
