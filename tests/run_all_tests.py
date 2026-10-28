"""
Master Test Suite Runner for Smart Railway Reservation System.
Executes the full test suite against Oracle Database & PL/SQL components:
- test_database_operations.py
- test_booking.py
- test_cancellation.py
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def run_all_tests() -> bool:
    print("=" * 70)
    print("STARTING TEST SUITE: SMART RAILWAY RESERVATION SYSTEM")
    print("Oracle Database & PL/SQL Component Verification")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Discover and add test modules
    tests_dir = os.path.join(BASE_DIR, "tests")
    suite.addTests(loader.discover(start_dir=tests_dir, pattern="test_*.py"))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Overall Success: {result.wasSuccessful()}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
