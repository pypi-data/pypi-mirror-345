import logging
import sys  # Import sys for stderr

# Create a logger for the package
# This is the single instance that will be shared
logger = logging.getLogger("orcastrator")

# Add a NullHandler to the logger by default
# This prevents "No handler found" warnings if the library is used
# by an application that doesn't configure logging.
# It's good practice for libraries.
logger.addHandler(logging.NullHandler())
logger.propagate = False


# --- Keep the configuration function ---
def configure_logging(level=logging.INFO, log_file=None, use_console=True):
    """Configure logging for the orcastrator package.

    Removes existing handlers and sets up new ones based on arguments.
    This should typically be called once by the application using the library.

    Args:
        level: The logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Optional path to a log file. If None, no file logging.
        use_console: Whether to log to the console (stderr). Default is True.
    """
    # Set the level on the main logger
    logger.setLevel(level)

    # Remove all existing handlers added by previous calls or defaults
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()  # Close handler to release resources like file handles

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add console handler if requested
    if use_console:
        console_handler = logging.StreamHandler(sys.stderr)  # Explicitly use stderr
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # If no handlers were added (e.g., use_console=False and log_file=None),
    # add back the NullHandler to prevent warnings.
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
