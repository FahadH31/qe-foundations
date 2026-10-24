# Testing and Logging

## Running Tests
Run all unit tests from the root directory using:
```
python -m unittest discover -s tests
```

## Logging
Logging is initialized using setup_logging(level="INFO", logfile=None) in qe_foundations/utils/logging_setup.py
- By default, INFO and higher messages are sent to console standard output.
- When logfile is provided, DEBUG level and higher messages are written to that log file.
