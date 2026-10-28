"""
Test Suite: Ticket Cancellation Workflow & Inventory Restoration
Tests the PL/SQL stored procedure CANCEL_TICKET, seat inventory restoration,
atomic transaction consistency, fee calculation, and audit log generation.
"""

import unittest
import oracledb

from services.reservation_service import book_ticket, cancel_ticket, get_reservation_by_pnr
from database.db_connection import execute_query, call_function


class TestTicketCancellation(unittest.TestCase):

    def test_01_cancellation_and_inventory_restoration(self):
        """
        Tests complete cancellation cycle:
        1. Book a ticket for 1 passenger
        2. Record seat inventory before cancellation
        3. Call CANCEL_TICKET procedure
        4. Verify seat inventory is restored in TRAIN_SEATS
        5. Verify status is CANCELLED and refund calculated
        6. Verify audit log entry in CANCELLATIONS
        """
        schedule_id = 1
        seat_class = "3A"

        # 1. Book a ticket to cancel
        ok, pnr, res_id, msg = book_ticket(
            passenger_id=1,
            schedule_id=schedule_id,
            from_station_id=2,
            to_station_id=1,
            journey_date_str="2026-10-25",
            seat_class=seat_class,
            passenger_list=[{"name": "Cancel Test Subject", "age": 35, "gender": "Male"}],
            payment_method="UPI"
        )
        self.assertTrue(ok, f"Pre-booking failed: {msg}")

        # Check inventory right after booking
        avail_after_booking = call_function("GET_AVAILABLE_SEATS", oracledb.NUMBER, [schedule_id, seat_class])[0]

        # 2. Cancel the ticket
        can_ok, refund, fee, can_msg = cancel_ticket(pnr, reason="Unit test cancellation scenario")
        self.assertTrue(can_ok, f"Cancellation failed: {can_msg}")
        self.assertGreater(fee, 0.0, "Cancellation fee must be greater than zero.")
        self.assertGreaterEqual(refund, 0.0, "Refund amount must be non-negative.")

        # 3. Verify seat inventory is restored (+1 seat)
        avail_after_cancel = call_function("GET_AVAILABLE_SEATS", oracledb.NUMBER, [schedule_id, seat_class])[0]
        self.assertEqual(avail_after_cancel, avail_after_booking + 1)

        # 4. Verify reservation status in Oracle DB
        res_info, _, _ = get_reservation_by_pnr(pnr)
        self.assertIsNotNone(res_info)
        self.assertEqual(res_info["booking_status"], "CANCELLED")

        # 5. Verify audit log entry created
        audit_rows = execute_query(
            "SELECT details FROM AUDIT_LOG WHERE table_name = 'CANCELLATIONS' AND operation = 'INSERT' ORDER BY log_id DESC FETCH FIRST 1 ROWS ONLY"
        )
        self.assertTrue(len(audit_rows) > 0)
        self.assertIn("Ticket Cancelled", audit_rows[0]["details"])

    def test_02_repeated_cancellation_prevention(self):
        """Verifies that an already cancelled ticket cannot be cancelled again (idempotency check)."""
        # Create and cancel a ticket
        ok, pnr, res_id, _ = book_ticket(
            passenger_id=1,
            schedule_id=1,
            from_station_id=2,
            to_station_id=1,
            journey_date_str="2026-10-25",
            seat_class="SL",
            passenger_list=[{"name": "Repeated Cancel Subject", "age": 40, "gender": "Female"}],
            payment_method="Cash"
        )
        self.assertTrue(ok)

        # First cancellation succeeds
        can1_ok, _, _, _ = cancel_ticket(pnr, reason="First cancel")
        self.assertTrue(can1_ok)

        # Second cancellation must be rejected by CANCEL_TICKET
        can2_ok, _, _, can2_msg = cancel_ticket(pnr, reason="Second cancel attempt")
        self.assertFalse(can2_ok)
        self.assertIn("already cancelled", can2_msg.lower())

    def test_03_non_existent_pnr_rejection(self):
        """Verifies that attempting to cancel an unknown PNR is cleanly rejected."""
        fake_pnr = "PNR_FAKE_999999"
        ok, refund, fee, msg = cancel_ticket(fake_pnr, reason="Fraudulent test")
        self.assertFalse(ok)
        self.assertIn("no reservation found", msg.lower())


if __name__ == "__main__":
    unittest.main()
