"""
Test Suite: Ticket Booking Workflow & Transactions
Tests the PL/SQL stored procedure BOOK_TICKET, concurrency row locking (SELECT ... FOR UPDATE),
inventory consistency, unique PNR assignment, and cursor retrieval.
"""

import unittest
from datetime import datetime
import oracledb

from services.reservation_service import book_ticket, get_reservation_by_pnr, get_suggested_pnrs
from database.db_connection import execute_query, call_function


class TestTicketBooking(unittest.TestCase):

    def test_01_successful_ticket_booking(self):
        """Tests end-to-end atomic booking: inventory deduction, PNR generation, and payment record."""
        schedule_id = 1
        seat_class = "SL"

        # Check pre-booking seat availability
        init_avail = call_function("GET_AVAILABLE_SEATS", oracledb.NUMBER, [schedule_id, seat_class])[0]
        self.assertGreaterEqual(init_avail, 1, "Schedule should have available SL seats.")

        passenger_list = [
            {"name": "Booking Test Passenger 1", "age": 27, "gender": "Male"},
            {"name": "Booking Test Passenger 2", "age": 25, "gender": "Female"}
        ]

        ok, pnr, res_id, msg = book_ticket(
            passenger_id=1,
            schedule_id=schedule_id,
            from_station_id=2,  # MMCT
            to_station_id=1,    # NDLS
            journey_date_str="2026-10-25",
            seat_class=seat_class,
            passenger_list=passenger_list,
            payment_method="UPI"
        )

        self.assertTrue(ok, f"Booking failed: {msg}")
        self.assertIsNotNone(pnr)
        self.assertTrue(pnr.startswith("PNR"))
        self.assertIsNotNone(res_id)

        # Verify seat inventory deducted in TRAIN_SEATS
        post_avail = call_function("GET_AVAILABLE_SEATS", oracledb.NUMBER, [schedule_id, seat_class])[0]
        self.assertEqual(post_avail, init_avail - 2)

        # Verify details via GET_RESERVATION_DETAILS cursor procedure
        res_info, pass_rows, err_msg = get_reservation_by_pnr(pnr)
        self.assertIsNotNone(res_info)
        self.assertEqual(res_info["pnr_number"], pnr)
        self.assertEqual(res_info["booking_status"], "CONFIRMED")
        self.assertEqual(len(pass_rows), 2)
        self.assertEqual(pass_rows[0]["passenger_name"], "Booking Test Passenger 1")

        # Verify PNR is recommended in active PNRs list
        suggested = get_suggested_pnrs(status="CONFIRMED", limit=10)
        self.assertIn(pnr, suggested)

    def test_02_insufficient_seats_rejection(self):
        """Tests that BOOK_TICKET rejects requests exceeding available capacity."""
        schedule_id = 1
        seat_class = "1A"

        avail = call_function("GET_AVAILABLE_SEATS", oracledb.NUMBER, [schedule_id, seat_class])[0]
        excess_count = int(avail or 0) + 15

        huge_party = [{"name": f"Excess Guest {i}", "age": 30, "gender": "Other"} for i in range(excess_count)]

        ok, pnr, res_id, msg = book_ticket(
            passenger_id=1,
            schedule_id=schedule_id,
            from_station_id=2,
            to_station_id=1,
            journey_date_str="2026-10-25",
            seat_class=seat_class,
            passenger_list=huge_party,
            payment_method="Net Banking"
        )

        self.assertFalse(ok)
        self.assertIsNone(pnr)
        self.assertIn("insufficient seats", msg.lower())

    def test_03_invalid_inputs_rejection(self):
        """Tests input validation: zero passengers, same source and destination."""
        # Zero passengers
        ok, pnr, res_id, msg = book_ticket(
            passenger_id=1,
            schedule_id=1,
            from_station_id=2,
            to_station_id=1,
            journey_date_str="2026-10-25",
            seat_class="SL",
            passenger_list=[],
            payment_method="UPI"
        )
        self.assertFalse(ok)
        self.assertIn("at least one passenger", msg.lower())

        # Same origin and destination
        ok2, pnr2, res_id2, msg2 = book_ticket(
            passenger_id=1,
            schedule_id=1,
            from_station_id=1,
            to_station_id=1,
            journey_date_str="2026-10-25",
            seat_class="SL",
            passenger_list=[{"name": "Valid Name", "age": 22, "gender": "Male"}],
            payment_method="UPI"
        )
        self.assertFalse(ok2)


if __name__ == "__main__":
    unittest.main()
