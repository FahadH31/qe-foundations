"""Load the four Release Tracker data files into SQLite.   (Part F - Tuesday ingestion meets Friday SQL)

Files in data/:   builds.csv   test_cases.csv   test_runs.json   defects.json
(builds.csv was saved from Excel: it starts with a byte-order mark.)

THE CONTRACT:
  1. Only STRUCTURAL problems stop the load -> raise IngestionError subclasses.
  2. DIRTY DATA is loaded as it is (orphans, NULLs, bad values, etc.).
  3. CSV '' and JSON null both become SQL NULL. Integer columns become int.
  4. Foreign keys stay OFF during load.
  5. Calling load_all twice on the same connection drops + recreates tables first.
"""
import csv
import json
import logging
import sqlite3
from pathlib import Path

log = logging.getLogger(__name__)

class IngestionError(Exception):
    """Base class for ingestion errors."""
    pass

class SourceNotFoundError(IngestionError):
    pass

class MalformedSourceError(IngestionError):
    pass

class MissingColumnsError(IngestionError):
    pass

class InvalidValueError(IngestionError):
    pass

class DuplicateIdError(IngestionError):
    pass

# table -> (file name, columns in table order, columns that must be integers)
SOURCES = {
    "builds": ("builds.csv",
               ["build_id", "build_name", "release", "built_date", "reported_total", "reported_passed", "reported_failed"],
               ["build_id", "reported_total", "reported_passed", "reported_failed"]),
    "test_cases": ("test_cases.csv",
                   ["case_id", "title", "module", "priority", "status", "created_date"],
                   ["case_id"]),
    "test_runs": ("test_runs.json",
                  ["run_id", "build_id", "case_id", "tester", "run_date", "result", "duration_sec"],
                  ["run_id", "build_id", "case_id", "duration_sec"]),
    "defects": ("defects.json",
                ["defect_id", "run_id", "case_id", "title", "severity", "status", "opened_date", "closed_date"],
                ["defect_id", "run_id", "case_id"]),
}
LOAD_ORDER = ["builds", "test_cases", "test_runs", "defects"]
PRIMARY_KEY = {"builds": "build_id", "test_cases": "case_id", "test_runs": "run_id", "defects": "defect_id"}


def convert_records(table, records):
    """Turn a list of raw records (dicts) into a list of tuples in table-column order."""
    cols = SOURCES[table][1]
    int_cols = set(SOURCES[table][2])
    pk_col = PRIMARY_KEY[table]
    seen_pks = set()
    out = []

    for rec in records:
        for col in cols:
            if col not in rec:
                raise MissingColumnsError(f"Missing column '{col}' in {table}")

        pk_val = rec.get(pk_col)
        if pk_val is None or pk_val == "":
            raise InvalidValueError(f"Empty primary key in {table}")

        try:
            pk_val_int = int(pk_val)
        except (ValueError, TypeError):
            raise InvalidValueError(f"Primary key '{pk_val}' in {table} is not an integer")

        if pk_val_int in seen_pks:
            raise DuplicateIdError(f"Duplicate primary key {pk_val_int} in {table}")
        seen_pks.add(pk_val_int)

        row_vals = []
        for col in cols:
            val = rec[col]
            if val is None or val == "":
                row_vals.append(None)
            elif col in int_cols:
                try:
                    row_vals.append(int(val))
                except (ValueError, TypeError):
                    raise InvalidValueError(f"Column '{col}' expected integer, got '{val}'")
            else:
                row_vals.append(val)
        out.append(tuple(row_vals))

    return out


def create_schema(conn, schema_path):
    """DROP TABLE IF EXISTS for the four tables, then execute schema.sql."""
    conn.execute("PRAGMA foreign_keys = OFF;")
    for table in reversed(LOAD_ORDER):
        conn.execute(f"DROP TABLE IF EXISTS {table};")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def load_all(conn, data_dir, schema_path):
    """Create the tables and load all four files. Return {table: count}."""
    create_schema(conn, schema_path)
    data_dir = Path(data_dir)
    loaded = {}

    for table in LOAD_ORDER:
        filename, cols, _ = SOURCES[table]
        filepath = data_dir / filename
        if not filepath.is_file():
            raise SourceNotFoundError(f"Source file not found: {filepath}")

        if filename.endswith(".csv"):
            try:
                with open(filepath, "r", encoding="utf-8-sig") as f:
                    records = list(csv.DictReader(f))
            except Exception as e:
                raise MalformedSourceError(f"Cannot read CSV {filename}: {e}")
        elif filename.endswith(".json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    records = json.load(f)
            except Exception as e:
                raise MalformedSourceError(f"Cannot parse JSON {filename}: {e}")
        else:
            raise IngestionError(f"Unsupported extension for {filename}")

        tuples = convert_records(table, records)
        placeholders = ", ".join("?" for _ in cols)
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders});"
        conn.executemany(sql, tuples)
        conn.commit()
        loaded[table] = len(tuples)
        log.info("Loaded %d rows into %s", len(tuples), table)

    return loaded
