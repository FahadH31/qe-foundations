"""Unit tests for the new SQL-validation code.  Run from the repo root:
    python -m unittest discover -s tests -t . -v
"""
import sqlite3
import unittest
from pathlib import Path

from qe_foundations.ingestion.sqlite_loader import InvalidValueError, convert_records, load_all
from qe_foundations.validation.sql_checks import overall_status, parse_checks, run_all, run_check

ROOT = Path(__file__).resolve().parents[1]
CHECKS = parse_checks((ROOT / "sql" / "part_e_checks.sql").read_text(encoding="utf-8"))


class TestParseChecks(unittest.TestCase):
    def test_finds_twenty_checks(self):
        self.assertEqual(len(CHECKS), 20)
        self.assertEqual([c.check_id for c in CHECKS][:2], ["E-01", "E-02"])


class TestChecksOnKnownData(unittest.TestCase):
    """Load data/ (dirty) or data/clean into an in-memory database with your loader, then run single checks."""

    def test_dirty_seed_has_two_surplus_duplicate_runs(self):
        conn = sqlite3.connect(":memory:")
        try:
            load_all(conn, ROOT / "data", ROOT / "sql" / "schema.sql")
            e05 = next(c for c in CHECKS if c.check_id == "E-05")
            res = run_check(conn, e05)
            self.assertEqual(res.status, "FAIL")
            self.assertEqual(len(res.violating_ids), 2)
            self.assertEqual(sorted(res.violating_ids), [44, 45])
        finally:
            conn.close()

    def test_clean_data_passes_every_check(self):
        conn = sqlite3.connect(":memory:")
        try:
            load_all(conn, ROOT / "data" / "clean", ROOT / "sql" / "schema.sql")
            results = run_all(conn, CHECKS)
            self.assertEqual(overall_status(results), "PASS")
            for r in results:
                self.assertEqual(r.status, "PASS")
        finally:
            conn.close()

    def test_a_check_can_fail_on_purpose(self):
        conn = sqlite3.connect(":memory:")
        try:
            load_all(conn, ROOT / "data" / "clean", ROOT / "sql" / "schema.sql")
            conn.execute("UPDATE test_runs SET result = 'PASSED' WHERE run_id = 1;")
            conn.commit()
            e14 = next(c for c in CHECKS if c.check_id == "E-14")
            res = run_check(conn, e14)
            self.assertEqual(res.status, "FAIL")
            self.assertIn(1, res.violating_ids)
        finally:
            conn.close()


class TestIngestionContract(unittest.TestCase):
    def test_blank_cells_become_null_and_bad_ids_raise(self):
        records = [
            {"case_id": "1", "title": "Test 1", "module": "login", "priority": "P1", "status": "active", "created_date": ""}
        ]
        tuples = convert_records("test_cases", records)
        self.assertEqual(tuples[0][0], 1)
        self.assertIsNone(tuples[0][5])

        bad_records = [
            {"case_id": "not_an_int", "title": "Test 2", "module": "login", "priority": "P1", "status": "active", "created_date": "2026-01-01"}
        ]
        with self.assertRaises(InvalidValueError):
            convert_records("test_cases", bad_records)


if __name__ == "__main__":
    unittest.main()
