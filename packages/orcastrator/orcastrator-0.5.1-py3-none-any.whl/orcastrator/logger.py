import logging
import sys
from pathlib import Path
from typing import Optional, Union


def setup_logger(
    log_file: Optional[Union[str, Path]] = None,
    level: int = logging.INFO,
    console_level: int = logging.WARNING,
) -> logging.Logger:
    """
    Configure a logger with file and console handlers.

    Args:
        log_file: Path to the log file. If None, no file logging is set up.
        level: Logging level for the file handler.
        console_level: Logging level for the console handler.

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("orcastrator")
    logger.setLevel(logging.DEBUG)  # Capture all levels
    logger.propagate = False  # Don't propagate to the root logger

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (for warnings and errors by default)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path, mode="a")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Get a module-level logger
logger = logging.getLogger("orcastrator")
