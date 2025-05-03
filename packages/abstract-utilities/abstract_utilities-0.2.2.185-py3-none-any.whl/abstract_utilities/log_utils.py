import logging
import os
from .path_utils import mkdirs
from logging.handlers import RotatingFileHandler
from .abstract_classes import SingletonMeta
# from abstract_utilities import get_logFile  # Potential conflict - consider removing or renaming


        
class AbstractLogManager(metaclass=SingletonMeta):
    def __init__(self):
        # Create a logger; use __name__ to have a module-specific logger if desired.
        self.logger = logging.getLogger("AbstractLogManager")
        self.logger.setLevel(logging.DEBUG)  # Set to lowest level to let handlers filter as needed.

        # Create a console handler with a default level.
        self.console_handler = logging.StreamHandler()
        # Default level: show warnings and above.
        self.console_handler.setLevel(logging.WARNING)

        # Formatter for the logs.
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.console_handler.setFormatter(formatter)

        # If there are no handlers already attached, add our console handler.
        if not self.logger.hasHandlers():
            self.logger.addHandler(self.console_handler)

    def set_debug(self, enabled: bool) -> None:
        """
        Enable or disable DEBUG level messages.
        When enabled, the console handler will output DEBUG messages and above.
        When disabled, it falls back to INFO or WARNING (adjust as needed).
        """
        if enabled:
            self.console_handler.setLevel(logging.DEBUG)
            self.logger.debug("DEBUG logging enabled.")
        else:
            # For example, disable DEBUG by raising the level to INFO.
            self.console_handler.setLevel(logging.INFO)
            self.logger.info("DEBUG logging disabled; INFO level active.")

    def set_info(self, enabled: bool) -> None:
        """
        Enable or disable INFO level messages.
        When enabled, INFO and above are shown; when disabled, only WARNING and above.
        """
        if enabled:
            # Lower the handler level to INFO if currently higher.
            self.console_handler.setLevel(logging.INFO)
            self.logger.info("INFO logging enabled.")
        else:
            self.console_handler.setLevel(logging.WARNING)
            self.logger.warning("INFO logging disabled; only WARNING and above will be shown.")

    def set_warning(self, enabled: bool) -> None:
        """
        Enable or disable WARNING level messages.
        When disabled, only ERROR and CRITICAL messages are shown.
        """
        if enabled:
            # WARNING messages enabled means handler level is WARNING.
            self.console_handler.setLevel(logging.WARNING)
            self.logger.warning("WARNING logging enabled.")
        else:
            self.console_handler.setLevel(logging.ERROR)
            self.logger.error("WARNING logging disabled; only ERROR and CRITICAL messages will be shown.")

    def get_logger(self) -> logging.Logger:
        """Return the configured logger instance."""
        return self.logger

def get_logFile(bpName: str=None, maxBytes: int = 100000, backupCount: int = 3) -> logging.Logger:
    """Return a logger that writes messages at INFO level or above to a rotating file."""
    # Create logs directory if it doesn't exist
    bpName = bpName or 'default'
    log_dir = mkdirs('logs')
    log_path = os.path.join(log_dir, f'{bpName}.log')

    # Create or get the named logger
    logger = logging.getLogger(bpName)
    logger.setLevel(logging.INFO)

    # Check if logger already has a handler to avoid duplicate logs on multiple calls.
    if not logger.handlers:
        # Configure the rotating file handler
        log_handler = RotatingFileHandler(log_path, maxBytes=maxBytes, backupCount=backupCount)
        log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        
        # (Optional) Also add a console handler if desired:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger



def get_logger_callable(logger, level='info'):
    """
    Determine the logging callable from a logger or logger method.
    
    Args:
        logger: Logger object, logger method (e.g., logger.info), or None.
        default_level (str): Logging level to use if logger is a Logger object (e.g., 'info', 'error').
    
    Returns:
        callable: Function to call for logging (e.g., logger.info or logger).
        None: If logger is None or invalid.
    """
    if logger is None:
        return None
    elif isinstance(logger, logging.Logger):
        # Logger object, return the specified method (e.g., logger.info)
        return getattr(logger, level.lower(), None)
    elif callable(logger) and hasattr(logger, '__self__') and isinstance(logger.__self__, logging.Logger):
        # Bound method (e.g., logger.info)
        return logger
    else:
        # Invalid logger, treat as None
        return None
    
def print_or_log(message, logger=True, level='info'):
    """
    Print or log a message based on the logger provided.
    
    Args:
        message (str): Message to print or log.
        logger: Logger object, logger method (e.g., logger.info), or None.
        level (str): Logging level if logger is a Logger object (e.g., 'info', 'error').
    """
    if logger == True:
        logger =get_logFile('default')
    log_callable = get_logger_callable(logger, level=level)
    if log_callable:
        log_callable(message)
    else:
        print(message)
