import logging
import sys


def setup_logging(level="INFO", logfile=None):
    """Configure and return the package logger for qe_foundations."""
    logger = logging.getLogger("qe_foundations")
    logger.setLevel(logging.DEBUG)

    # if already configured, do not add a duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if logfile:
        file_handler = logging.FileHandler(logfile, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
