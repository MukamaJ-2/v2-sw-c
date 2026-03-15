"""
Centralized logging configuration for the Cafeteria Management System.

Added: Replaces print() for errors with structured logging.
- Timestamps, log levels, and context (extra={}) for debugging
- Output to stderr so it doesn't mix with user-facing print() output
"""
import logging
import sys


def setup_logger(name: str = "cafeteria", level: int = logging.INFO) -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger()
