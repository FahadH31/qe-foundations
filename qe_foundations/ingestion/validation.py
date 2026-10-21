"""qe_foundations/ingestion/validation.py  -  TASK 5 (about 25 min)

validate_record() decides whether ONE raw record is acceptable.

IMPORTANT: this is VALIDATION OF EXTERNAL DATA. Raise exceptions here.
Do NOT use `assert` in this file (assertions can be switched off with `python -O`).
See README Task 5 for the exact rules.
"""

import math
from .exceptions import InvalidValueError, MissingFieldError

REQUIRED_FIELDS = ("id", "title", "status", "duration")
VALID_STATUSES = ("pass", "fail", "blocked")


def validate_record(row, raw):
    """Turn one raw record into a clean dict, or raise a RecordValidationError.

    row : 1-based record number in the file (used in error messages)
    raw : whatever the reader produced for that record (usually a dict)

    Returns {"id": str, "title": str, "status": str, "duration": float}.
    """
    # Check 1
    if not isinstance(raw, dict):
        raise InvalidValueError(row, "record", raw, "an object with the test fields")
    
    # Check 2
    for name in REQUIRED_FIELDS:
        value = raw.get(name)
        if value is None or str(value).strip() == "":
            raise MissingFieldError(row, name)

    # Check 3
    status = str(raw["status"]).strip().lower()
    if status not in VALID_STATUSES:
        raise InvalidValueError(row, "status", raw["status"], "A valid status (pass/fail/blocked)")
    
    # Check 4
    raw_duration = raw["duration"]
    # check for boolean
    if str(raw_duration).strip().upper() == "TRUE" or str(raw_duration).strip().upper() == "FALSE":
        raise InvalidValueError(row, "duration", raw["duration"], "Duration value cannot be boolean.")
    # try convert to float
    try:
        duration = float(raw_duration)
    except (ValueError, TypeError) as error:
        raise InvalidValueError(row, "duration", raw["duration"], error) from error
    if duration < 0 or not math.isfinite(duration):     # check all of negative, infinite, nan
        raise InvalidValueError(row, "duration", raw["duration"], "Duration value cannot be negative, infinite, or NaN.")

    return {                                                                                                                                                                 
        "id": str(raw["id"]).strip(),                                                                                                                                        
        "title": str(raw["title"]).strip(),                                                                                                                                  
        "status": status,                                                                                                                                                    
        "duration": duration,                                                                                                                                                
    }   
