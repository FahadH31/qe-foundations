"""qe_foundations/ingestion/loader.py  -  TASK 6 (about 30 min)

Ties everything together:
    file -> reader (format) -> validate_record (rules) -> IngestionReport

Error POLICY (the heart of the milestone):
    SourceError            -> the whole file is unusable -> let it propagate (raise)
    RecordValidationError  -> one record is bad          -> COLLECT it and carry on

Already done for you: the IngestionReport and BatchResult classes' constructors
and the READERS lookup table. You write the TODOs.
"""

import csv
from pathlib import Path

from .contexts import LoadSession
from .exceptions import (
    DuplicateIdError,
    RecordValidationError,
    SourceError,
    SourceNotFoundError,
    UnsupportedFormatError,
)
from .readers import read_csv_records, read_json_records, read_xml_records
from .validation import validate_record

# Which reader handles which file extension (always compare lower-case suffixes).
READERS = {
    ".csv": read_csv_records,
    ".json": read_json_records,
    ".xml": read_xml_records,
}


class IngestionReport:
    """Result of loading ONE file: the valid records AND every rejected one."""

    def __init__(self, source, rows_seen=0):
        self.source = source
        self.rows_seen = rows_seen
        self.valid = []       # clean dicts returned by validate_record
        self.rejected = []    # RecordValidationError instances

    def summary(self):
        return f"{self.source}: {self.rows_seen} rows seen, {len(self.valid)} valid, {len(self.rejected)} rejected"

    def rejected_rows(self):
        """TODO (6A): the rejected records as plain dicts, ordered by row number.

        Each dict has exactly the keys: "source", "row", "field", "reason"
        ("reason" is the text of the exception, str(error)).
        """
        # need to convert self.rejected (list of RecordValidationError instances) into a list of regular dictionaries.
        dicts_list = []

        for record in self.rejected:
            dicts_list.append(dict(
                source = self.source,
                row = record.row,
                field = record.field,
                reason = str(record)
            ))

        return sorted(dicts_list, key = lambda dicts: dicts["row"])

    def check_invariants(self):
        assert len(self.valid) + len(self.rejected) == self.rows_seen, "Number of seen records does not equal number of valid + rejected records."

        values = [d["id"] for d in self.valid if "id" in d]     # collect list of IDs from the dictionaries in self.valid, if "id" exists in that dict.
        assert len(values) == len(set(values)), "Duplicate values are present in list of valid records."    # set removes duplicates

        type_flag = True
        for item in self.rejected:
            if not isinstance(item, RecordValidationError):
                type_flag = False
        
        assert type_flag, "An object in rejected[] is not of type RecordValidationError"

class BatchResult:
    """Result of loading a whole folder."""

    def __init__(self):
        self.reports = []           # IngestionReport, one per file that could be read
        self.failed_sources = []    # SourceError instances, one per unusable file

    def totals(self):
        """TODO (6D): return a dict with exactly these keys:

            "files_ok", "files_failed", "valid", "rejected"
        """

        total_valid_rows = 0
        total_rejected_rows = 0 
        for report in self.reports:
            total_valid_rows += len(report.valid)
            total_rejected_rows += len(report.rejected) 

        return dict(
            files_ok = len(self.reports),
            files_failed = len(self.failed_sources),
            valid = total_valid_rows,
            rejected = total_rejected_rows
        ) 

def load_test_cases(path):
    """Load one CSV/JSON/XML file into an IngestionReport (TODO 6C).

    * Wrap the whole job in `with LoadSession(path):`
    * unknown extension -> raise UnsupportedFormatError
    * SourceError subclasses from the readers must propagate unchanged
    * rows are numbered from 1 (the header line of a CSV does not count) 
    * bad records are COLLECTED in report.rejected, good ones go to report.valid
    * a repeated id -> DuplicateIdError for the LATER occurrence (the first one stays valid)
    * call report.check_invariants() before returning
    """
    with LoadSession(path):
        # Check if file extention is valid
        file_ext = Path(path).suffix.lower()
        if file_ext not in READERS:
            raise UnsupportedFormatError(path, file_ext)

        # If yes then call the appropriate reader
        reader = READERS[file_ext]
        raw_records = reader(path)

        # create a report
        report = IngestionReport(Path(path).name, rows_seen = len(raw_records))
        seen_ids = set()

        # loop length of records. 'i+1' is used as the row number
        for i in range(len(raw_records)):
            try:
                clean_record = validate_record(i+1, raw_records[i])   # returns a clean dict from the raw record 
                if clean_record["id"] in seen_ids:                    # handle duplicate IDs
                    report.rejected.append(DuplicateIdError(i+1, clean_record["id"]))     # if a failed row, append to the rejected list of this report 
                else:
                    seen_ids.add(clean_record["id"])    # add to set to fill out list of IDs
                    report.valid.append(clean_record)   # if succeeded, add to the valid list of this report
            except RecordValidationError as error:
                report.rejected.append(error)
        
        report.check_invariants()

        return report

def load_directory(folder):
    """Load every file directly inside `folder` (TODO 6D).

    * sorted by file name; sub-folders are skipped
    * a bad FILE never stops the batch: collect its SourceError in failed_sources
    * a folder that does not exist (or is not a folder) -> raise SourceNotFoundError(folder)
    """
    folder = Path(folder)

    if not folder.is_dir():                 # if folder does not exist as an actual folder
        raise SourceNotFoundError(folder)

    files = [f for f in folder.iterdir() if f.is_file()]  # stores list of files in this directory only if it is actually a file
    files = sorted(files, key=lambda f:f.name)      # updated to sort by filename

    batch = BatchResult()
    for file in files:
        try:
            report = load_test_cases(file)      # returns an ingestionreport
            batch.reports.append(report)        # append that report to batch's list of reports
        except SourceError as error:            # if source error then append it to the batch's failed_sources list of reports
            batch.failed_sources.append(error)
    
    return batch


def write_rejected_csv(report, out_path):
    """Write report.rejected_rows() to a CSV file (TODO 6E) and return the Path.

    Header exactly: source,row,field,reason     (use csv.DictWriter)
    Create the parent folder if needed. Open the file with newline="".
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, mode = "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, ["source", "row", "field", "reason"])
        writer.writeheader()                        # guarantee header is written even if nothing in report.rejected
        writer.writerows(report.rejected_rows())     # using the method written earlier, under IngestionReport class
    
    return out_path