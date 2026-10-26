"""Run the SQL data-quality checks stored in sql/part_e_checks.sql.   (Part F - Thursday validation + Friday joins)

The file format (one block per check):
    -- @CHECK E-05 | uniqueness | One run per (build, case) ... | returns test_runs.run_id
    SELECT ... ;          <- returns the VIOLATING rows, first column = primary key. Zero rows = PASS.
"""
import logging
import re
import sqlite3
from collections import namedtuple

log = logging.getLogger(__name__)

Check = namedtuple("Check", "check_id category description returns sql")
CheckResult = namedtuple("CheckResult", "check_id category description returns violating_ids status")

_TAG = re.compile(r"^--\s*@CHECK\s+(.*)$")


def parse_checks(text):
    """[given] Parse the check-file text into a list of Check tuples (comment lines inside a block are ignored)."""
    checks, header, sql_lines = [], None, []
    for line in text.splitlines():
        match = _TAG.match(line.strip())
        if match:
            header, sql_lines = [p.strip() for p in match.group(1).split("|")], []
            continue
        if header is None or line.strip().startswith("--"):
            continue
        sql_lines.append(line)
        sql = "\n".join(sql_lines).strip()
        if sql.endswith(";") and sqlite3.complete_statement(sql):
            checks.append(Check(header[0], header[1], header[2],
                                header[3].replace("returns", "").strip() if len(header) > 3 else "", sql))
            header, sql_lines = None, []
    return checks


def run_check(conn, check):
    """Execute ONE check and return a CheckResult."""
    rows = conn.execute(check.sql).fetchall()
    violating_ids = [r[0] for r in rows]
    status = "PASS" if len(violating_ids) == 0 else "FAIL"
    return CheckResult(check.check_id, check.category, check.description, check.returns, violating_ids, status)


def run_all(conn, checks):
    """Run every check and return the list of CheckResult (same order as the file)."""
    results = []
    for check in checks:
        res = run_check(conn, check)
        results.append(res)
        if res.status == "PASS":
            log.info("[%s] %s: 0 violations", res.check_id, res.description)
        else:
            log.warning("[%s] %s: %d violation(s) (ids: %s)", res.check_id, res.description, len(res.violating_ids), res.violating_ids)
    return results


def overall_status(results):
    """Return "FAIL" if any result has status "FAIL", else "PASS"."""
    return "FAIL" if any(r.status == "FAIL" for r in results) else "PASS"
