import os
import tempfile
import unittest

from qe_foundations.ingestion.exceptions import (
    SourceNotFoundError,
    UnsupportedFormatError,
)
from qe_foundations.ingestion.loader import load_test_cases


class TestIngestion(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_load_valid_csv(self):
        path = os.path.join(self.tmp.name, "valid.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("id,title,status,duration\n")
            f.write("T1,Login test,pass,1.2\n")
            f.write("T2,Search test,fail,0.8\n")

        report = load_test_cases(path)
        self.assertEqual(len(report.valid), 2)
        self.assertEqual(len(report.rejected), 0)

    def test_load_csv_with_bad_row(self):
        path = os.path.join(self.tmp.name, "bad_row.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("id,title,status,duration\n")
            f.write("T1,Good test,pass,1.0\n")
            f.write("T2,Bad status,invalid_status,1.5\n")

        report = load_test_cases(path)
        self.assertEqual(len(report.valid), 1)
        self.assertEqual(len(report.rejected), 1)

    def test_missing_file_raises_error(self):
        missing_path = os.path.join(self.tmp.name, "missing.csv")
        with self.assertRaises(SourceNotFoundError):
            load_test_cases(missing_path)

    def test_unsupported_format_raises_error(self):
        txt_path = os.path.join(self.tmp.name, "test.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("hello")
        with self.assertRaises(UnsupportedFormatError):
            load_test_cases(txt_path)

    def test_bad_row_logs_warning(self):
        path = os.path.join(self.tmp.name, "warning.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("id,title,status,duration\n")
            f.write("T1,Negative time,pass,-2.0\n")

        with self.assertLogs("qe_foundations.ingestion", level="WARNING"):
            load_test_cases(path)


if __name__ == "__main__":
    unittest.main()
