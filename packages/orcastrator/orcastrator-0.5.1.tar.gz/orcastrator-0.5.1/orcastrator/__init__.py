import logging

# Create the package-level logger
logger = logging.getLogger("orcastrator")
logger.addHandler(logging.NullHandler())  # Prevent "No handler found" warning

# Version info
__version__ = "0.5.1"
