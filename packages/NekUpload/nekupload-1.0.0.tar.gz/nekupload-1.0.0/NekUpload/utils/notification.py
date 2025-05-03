import logging
import warnings

def warn_with_logging(message: str):
    logging.warning(message)  # Log the warning
    warnings.warn(message, DeprecationWarning, stacklevel=3)  # Emit a DeprecationWarning
