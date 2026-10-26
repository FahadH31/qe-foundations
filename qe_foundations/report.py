"""python -m qe_foundations.report   (Part F: the Week 2 integration command)

Ingest the seed data into SQLite, run the SQL validation suite, log the results and print a PASS/FAIL data-quality summary.

Exit codes:  0 = every check passed   1 = at least one check failed   2 = the data could not be ingested (or the SQL failed)
"""
import argparse
import logging
import sqlite3
import sys
from pathlib import Path

from qe_foundations.ingestion.sqlite_loader import IngestionError, load_all
from qe_foundations.validation.sql_checks import overall_status, parse_checks, run_all

log = logging.getLogger("qe_foundations.report")


def build_parser():
    """[given] The command-line interface."""
    parser = argparse.ArgumentParser(prog="python -m qe_foundations.report",
                                     description="Ingest test data and print a data-quality report.")
    parser.add_argument("--data", default="data", help="folder with builds.csv, test_cases.csv, test_runs.json, defects.json")
    parser.add_argument("--db", default=":memory:", help="SQLite database file (default: in memory)")
    parser.add_argument("--checks", default="sql/part_e_checks.sql", help="file with the @CHECK queries")
    parser.add_argument("--schema", default="sql/schema.sql", help="CREATE TABLE script")
    parser.add_argument("--log-file", default="logs/report.log", help="where to write the log")
    parser.add_argument("--show", action="store_true", help="also print the offending ids of failed checks")
    return parser


def format_report(results, show=False):
    """Return the report as a list of text lines."""
    lines = []
    failed_checks = 0
    total_violations = 0
    total_checks = len(results)

    for r in results:
        status_tag = f"[{r.status}]"
        line = f"{status_tag} {r.check_id:<4} {r.category:<20} {len(r.violating_ids):>2} violation(s)  {r.description}"
        lines.append(line)
        if r.status == "FAIL":
            failed_checks += 1
            total_violations += len(r.violating_ids)
            if show and r.violating_ids:
                lines.append(f"       Offending IDs: {', '.join(str(i) for i in r.violating_ids)}")

    lines.append("")
    if failed_checks > 0:
        summary = f"DATA QUALITY: FAIL ({failed_checks} of {total_checks} checks failed, {total_violations} violating row(s))"
    else:
        summary = f"DATA QUALITY: PASS ({total_checks} of {total_checks} checks passed)"
    lines.append(summary)
    return lines


def main(argv=None):
    """Return the exit code (the __main__ block passes it to sys.exit)."""
    parser = build_parser()
    args = parser.parse_args(argv)

    log_path = Path(args.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(args.log_file, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    root_log = logging.getLogger()
    root_log.setLevel(logging.INFO)
    root_log.handlers = [handler]

    log.info("report started")
    conn = None
    try:
        conn = sqlite3.connect(args.db)
        loaded = load_all(conn, args.data, args.schema)

        checks_text = Path(args.checks).read_text(encoding="utf-8")
        checks = parse_checks(checks_text)
        results = run_all(conn, checks)

        counts_str = ", ".join(f"{t}={c}" for t, c in loaded.items())
        print(f"Loaded: {counts_str}")
        report_lines = format_report(results, show=args.show)
        for line in report_lines:
            print(line)

        status = overall_status(results)
        log.info("report finished: %s", status)
        return 0 if status == "PASS" else 1

    except IngestionError as e:
        log.error("Ingestion failed: %s", e)
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except (sqlite3.Error, OSError) as e:
        log.error("Execution error: %s", e)
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    finally:
        if conn:
            conn.close()
        handler.close()
        root_log.removeHandler(handler)


if __name__ == "__main__":
    sys.exit(main())
