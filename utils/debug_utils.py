import logging
import os
from typing import Any, Optional
from datetime import datetime
from enum import Enum
from config.settings import LOG_LEVEL

class LogLevel(Enum):
    """
    Enum for log levels used in the application.

    Log Level Hierarchy (from most verbose to least verbose):
    - TRACE (-1): Most detailed debugging info (custom level, rarely used)
    - DEBUG (0): Detailed debugging information, data processing steps, API calls
    - INFO (1): General informational messages, operation status, progress updates
    - WARNING (2): Warning messages for potential issues, missing data, rate limiting
    - ERROR (3): Error messages for exceptions, failures, critical issues
    - CRITICAL (4): Critical system failures that may cause application to stop

    Usage Examples:
    - Development/Debugging: Use DEBUG to see all details including ratio calculations
    - Production: Use INFO or WARNING to reduce console noise
    - Error Monitoring: Use ERROR to see only problems

    Note: The primary log level is configured in config/settings.py LOG_LEVEL setting.
    """
    TRACE = -1      # Most verbose: custom detailed tracing
    DEBUG = 0       # Debug info: calculations, data processing, API calls
    INFO = 1        # General info: status updates, progress, successful operations
    WARNING = 2     # Warnings: potential issues, missing data, rate limits
    ERROR = 3       # Errors: exceptions, failures, critical problems
    CRITICAL = 4    # Critical: system failures, application crashes

class DebugUtils:
    """
    Utility class for debug logging and configuration.

    LOG LEVEL CONFIGURATION:
    ========================

    PRIMARY CONFIGURATION (Permanent):
    ----------------------------------
    Edit config/settings.py and change LOG_LEVEL value:

        LOG_LEVEL = "DEBUG"    # Shows all messages (most verbose)
        LOG_LEVEL = "INFO"     # Shows info, warnings, errors
        LOG_LEVEL = "WARNING"  # Shows warnings and errors only
        LOG_LEVEL = "ERROR"    # Shows errors only
        LOG_LEVEL = "CRITICAL" # Shows critical failures only

    RUNTIME CONFIGURATION (Temporary):
    ----------------------------------
    Use DebugUtils.set_log_level() method:

        from utils.debug_utils import DebugUtils, LogLevel
        DebugUtils.set_log_level(LogLevel.DEBUG)   # Most verbose
        DebugUtils.set_log_level(LogLevel.ERROR)   # Errors only

    TESTING CONFIGURATION:
    ----------------------
    Use DebugUtils.test_logging() to verify current settings:

        DebugUtils.test_logging()  # Shows sample messages at all levels

    LOG OUTPUT LOCATIONS:
    ---------------------
    - Console: Real-time output during application execution
    - File: logs/stock_analyzer_YYYYMMDD.log (persistent storage)
    """

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DebugUtils, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        """Set up the logger with file and console handlers."""
        if DebugUtils._logger is not None:
            return

        # Create logger
        DebugUtils._logger = logging.getLogger('StockAnalyzer')

        # Set log level from settings
        log_level = getattr(logging, LOG_LEVEL.upper(), logging.DEBUG)
        DebugUtils._logger.setLevel(log_level)

        # Prevent duplicate log entries
        DebugUtils._logger.handlers.clear()

        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        # Create file handler
        log_file = os.path.join(logs_dir, f"stock_analyzer_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Add formatter to handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        DebugUtils._logger.addHandler(file_handler)
        DebugUtils._logger.addHandler(console_handler)
        DebugUtils._logger.propagate = False

    @classmethod
    def get_logger(cls):
        """Get the configured logger instance."""
        if cls._instance is None:
            cls()
        return cls._logger

    @classmethod
    def log_api_call(cls, api_name: str, symbol: str = None, attempt: int = 1, total_attempts: int = 1, params: Optional[dict] = None, args: Any = None, kwargs: Any = None) -> None:
        """Log API call details in a standardized format, including arguments."""
        logger = cls.get_logger()
        logger.debug(f"API Call - {api_name} - Symbol: {symbol} - Attempt: {attempt}/{total_attempts} - Args: {args} - Kwargs: {kwargs} - Params: {params}")

    @classmethod
    def log_error(cls, error: Exception, context: Optional[str] = None) -> None:
        """Log error details in a standardized format."""
        try:
            logger = cls.get_logger()
            error_message = f"Error Details: {str(error)}"
            if context:
                error_message = f"Context: {context} - {error_message}"

            logger.error("Error Details: ")
            logger.error(f"Context: {context}")
            logger.error(f"Error Type: {type(error).__name__}")
            logger.error(f"Error Message: {str(error)}")
            logger.error("--------------------------------------------------")

            # Log stack trace
            import traceback
            logger.error("Stack Trace: " + traceback.format_exc())

        except Exception as logging_error:
            print(f"Failed to log error: {logging_error}")
            print(f"Original error: {error}")

    @classmethod
    def info(cls, message: str) -> None:
        """Log info message."""
        logger = cls.get_logger()
        logger.info(message)

    @classmethod
    def debug(cls, message: str) -> None:
        """Log debug message."""
        logger = cls.get_logger()
        logger.debug(message)

    @classmethod
    def warning(cls, message: str) -> None:
        """Log warning message."""
        logger = cls.get_logger()
        logger.warning(message)

    @classmethod
    def error(cls, message: str) -> None:
        """Log error message."""
        logger = cls.get_logger()
        logger.error(message)

    @classmethod
    def log_warning(cls, message: str) -> None:
        """Log warning message."""
        logger = cls.get_logger()
        logger.warning(message)

    @classmethod
    def log_debug(cls, message: str) -> None:
        """Log debug message."""
        logger = cls.get_logger()
        logger.debug(message)

    @classmethod
    def set_log_level(cls, level: LogLevel) -> None:
        """
        Set the minimum log level programmatically (runtime override).

        This method allows you to change the log level at runtime without
        modifying the config/settings.py file. This is useful for:
        - Temporary debugging sessions
        - Testing different log levels
        - Dynamic log level adjustment based on conditions

        Args:
            level (LogLevel): The minimum log level to display

        Example:
            from utils.debug_utils import DebugUtils, LogLevel

            # Show all messages (most verbose)
            DebugUtils.set_log_level(LogLevel.DEBUG)

            # Show only errors
            DebugUtils.set_log_level(LogLevel.ERROR)

        Note: This override is temporary and will be reset when the application restarts.
        For permanent changes, modify LOG_LEVEL in config/settings.py
        """
        # Ensure logger is initialized
        if cls._instance is None:
            cls()

        if cls._logger:
            log_level_mapping = {
                LogLevel.TRACE: logging.DEBUG,  # Map TRACE to DEBUG (closest equivalent)
                LogLevel.DEBUG: logging.DEBUG,
                LogLevel.INFO: logging.INFO,
                LogLevel.WARNING: logging.WARNING,
                LogLevel.ERROR: logging.ERROR,
                LogLevel.CRITICAL: logging.CRITICAL
            }

            python_level = log_level_mapping.get(level, logging.DEBUG)
            cls._logger.setLevel(python_level)
            for handler in cls._logger.handlers:
                handler.setLevel(python_level)

    @classmethod
    def test_logging(cls) -> None:
        """
        Test logging configuration by displaying sample messages at all levels.

        This method helps verify that your logging configuration is working correctly
        and shows which messages will be visible at the current log level.

        Usage:
            from utils.debug_utils import DebugUtils
            DebugUtils.test_logging()
        """
        logger = cls.get_logger()

        print("\n=== LOGGING TEST ===")
        print(f"Current LOG_LEVEL setting: {LOG_LEVEL}")
        print(f"Current logger level: {logger.level} ({logging.getLevelName(logger.level)})")
        print("\nTesting all log levels:")
        print("(You should see messages at or above your configured level)\n")

        # Test all levels
        cls.debug("🔍 DEBUG: This is a debug message - shows detailed info")
        cls.info("ℹ️  INFO: This is an info message - shows general status")
        cls.warning("⚠️  WARNING: This is a warning message - shows potential issues")
        cls.error("❌ ERROR: This is an error message - shows problems")
        logger.critical("🚨 CRITICAL: This is a critical message - shows system failures")

        print("\n=== END LOGGING TEST ===\n")