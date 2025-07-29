import logging
import os
from typing import Any, Optional
from datetime import datetime
from enum import Enum

class LogLevel(Enum):
    """Enum for log levels."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

class DebugUtils:
    """Utility class for debug logging and configuration."""
    
    _instance = None
    _logger = None
    _debug_mode = False  # Set default to True for development
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DebugUtils, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Setup the logger with debug configuration."""
        try:
            if self._logger is None:
                # Remove any existing handlers
                logging.getLogger('StockAnalyzer').handlers = []
                
                self._logger = logging.getLogger('StockAnalyzer')
                self._logger.setLevel(logging.DEBUG)  # Set default level to DEBUG
                
                # Create logs directory if it doesn't exist
                os.makedirs('logs', exist_ok=True)
                
                # Create file handler
                log_file = f'logs/stock_analyzer_{datetime.now().strftime("%Y%m%d")}.log'
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)  # Set file handler to DEBUG
                
                # Create console handler
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)  # Set console handler to DEBUG
                
                # Create formatter
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(formatter)
                console_handler.setFormatter(formatter)
                
                # Add handlers to logger
                self._logger.addHandler(file_handler)
                self._logger.addHandler(console_handler)
                
                # Prevent propagation to root logger
                self._logger.propagate = False
                
                # Log successful initialization
                self._logger.debug("Logger initialized successfully")
        except Exception as e:
            print(f"Error initializing logger: {str(e)}")
            # Create a basic logger as fallback
            self._logger = logging.getLogger('StockAnalyzer')
            self._logger.setLevel(logging.DEBUG)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            self._logger.addHandler(console_handler)
            self._logger.propagate = False
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get the logger instance."""
        if cls._instance is None:
            cls()
        if cls._logger is None:
            # Create a basic logger as fallback
            cls._logger = logging.getLogger('StockAnalyzer')
            cls._logger.setLevel(logging.DEBUG)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            cls._logger.addHandler(console_handler)
            cls._logger.propagate = False
        return cls._logger
    
    @classmethod
    def log_api_call(cls, api_name: str, symbol: str = None, attempt: int = 1, total_attempts: int = 1, params: Optional[dict] = None) -> None:
        """Log API call details in a standardized format."""
        if cls._debug_mode:
            logger = cls.get_logger()
            logger.debug(f"API Call - {api_name} - Symbol: {symbol} - Attempt: {attempt}/{total_attempts} - Params: {params}")
    
    @classmethod
    def log_error(cls, error: Exception, context: Optional[str] = None) -> None:
        """Log error details in a standardized format."""
        try:
            logger = cls.get_logger()
            if context:
                logger.error(f"{context}: {str(error)}", exc_info=True)
            else:
                logger.error(str(error), exc_info=True)
        except Exception as e:
            print(f"Error logging failed: {str(e)}")
            print(f"Original error: {str(error)}")
    
    @classmethod
    def log_info(cls, message: str) -> None:
        """Log info message."""
        logger = cls.get_logger()
        logger.info(message)
    
    @classmethod
    def log_warning(cls, message: str) -> None:
        """Log warning message."""
        logger = cls.get_logger()
        logger.warning(message)
    
    @classmethod
    def log_debug(cls, message: str) -> None:
        """Log debug message."""
        if cls._debug_mode:
            logger = cls.get_logger()
            logger.debug(message)
    
    @classmethod
    def set_debug_mode(cls, enabled: bool) -> None:
        """Enable or disable debug mode."""
        cls._debug_mode = enabled
        if cls._instance and cls._logger:
            level = logging.DEBUG if enabled else logging.INFO
            cls._logger.setLevel(level)
            for handler in cls._logger.handlers:
                handler.setLevel(level)
    
    @classmethod
    def is_debug_mode(cls) -> bool:
        """Check if debug mode is enabled."""
        return cls._debug_mode
    
    @classmethod
    def log_api_call(cls, api_name: str, symbol: str = None, attempt: int = 1, total_attempts: int = 1, params: Optional[dict] = None) -> None:
        """Log API call details in a standardized format.
        
        Args:
            api_name: Name of the API being called
            symbol: Stock symbol being queried (optional)
            attempt: Current attempt number (optional)
            total_attempts: Total number of attempts allowed (optional)
            params: Additional parameters for the API call (optional)
        """
        if cls._debug_mode:
            logger = cls.get_logger()
            
            # Log basic API call info
            logger.debug(f"\nAPI Call Details:")
            logger.debug(f"API: {api_name}")
            
            # Log symbol if provided
            if symbol:
                logger.debug(f"Symbol: {symbol}")
            
            # Log attempt info if provided
            if attempt and total_attempts:
                logger.debug(f"Attempt: {attempt}/{total_attempts}")
            
            # Log timestamp
            logger.debug(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Log parameters if provided
            if params:
                logger.debug(f"Parameters: {params}")
            
            logger.debug("-" * 50)
    
    @classmethod
    def log_error(cls, error: Exception, context: Optional[str] = None) -> None:
        """Log error details in a standardized format.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
        """
        try:
            # Ensure logger is initialized
            if cls._instance is None:
                cls()
            
            logger = cls.get_logger()
            
            # Log error details
            logger.error("\nError Details:")
            if context:
                logger.error(f"Context: {context}")
            logger.error(f"Error Type: {type(error).__name__}")
            logger.error(f"Error Message: {str(error)}")
            logger.error("-" * 50)
            
            # Log full stack trace
            logger.error("Stack Trace:", exc_info=True)
        except Exception as e:
            # Fallback to basic error printing if logger fails
            print(f"\nError Details:")
            if context:
                print(f"Context: {context}")
            print(f"Error Type: {type(error).__name__}")
            print(f"Error Message: {str(error)}")
            print("-" * 50)
            print(f"Logger Error: {str(e)}")
    
    @classmethod
    def log_info(cls, message: str) -> None:
        """Log info message."""
        logger = cls.get_logger()
        logger.info(message)
    
    @classmethod
    def log_warning(cls, message: str) -> None:
        """Log warning message."""
        logger = cls.get_logger()
        logger.warning(message)
    
    @classmethod
    def log_debug(cls, message: str) -> None:
        """Log debug message."""
        if cls._debug_mode:
            logger = cls.get_logger()
            logger.debug(message)
    
    @classmethod
    def set_log_level(cls, level: LogLevel) -> None:
        """Set the minimum log level.
        
        Args:
            level: Minimum log level to display
        """
        if cls._instance and cls._logger:
            cls._logger.setLevel(level.value)
            for handler in cls._logger.handlers:
                handler.setLevel(level.value)
    
    @classmethod
    def set_log_file(cls, file_path: Optional[str] = None) -> None:
        """Set the log file path for debug output.
        
        Args:
            file_path: Path to the log file. If None, logging to file is disabled.
        """
        if cls._instance and cls._logger:
            if file_path:
                cls._logger.info(f"Debug output will be written to: {file_path}")
            else:
                cls._logger.info("Debug output will not be written to any file")
    
    @classmethod
    def _log(cls, level: LogLevel, *args: Any, **kwargs: Any) -> None:
        """Internal logging method.
        
        Args:
            level: Log level of the message
            *args: Arguments to print
            **kwargs: Keyword arguments to print
        """
        try:
            # Ensure logger is initialized
            if cls._instance is None:
                cls()
                
            if not cls._debug_mode:
                return
                
            # Format the message with timestamp and level
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"[{timestamp}] [{level.name}] {' '.join(str(arg) for arg in args)}"
            
            # Print to console
            print(message, **kwargs)
            
            # Write to log file if enabled
            if cls._logger and cls._logger.handlers:
                for handler in cls._logger.handlers:
                    if handler.level <= level.value:
                        handler.emit(logging.LogRecord(
                            'StockAnalyzer',
                            level.value,
                            None,
                            None,
                            message,
                            None,
                            None
                        ))
        except Exception as e:
            # Fallback to basic printing if logger fails
            print(f"Logger Error: {str(e)}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
    
    @classmethod
    def debug(cls, *args: Any, **kwargs: Any) -> None:
        """Log debug level message."""
        cls._log(LogLevel.DEBUG, *args, **kwargs)
    
    @classmethod
    def info(cls, *args: Any, **kwargs: Any) -> None:
        """Log info level message."""
        cls._log(LogLevel.INFO, *args, **kwargs)
    
    @classmethod
    def warning(cls, *args: Any, **kwargs: Any) -> None:
        """Log warning level message."""
        cls._log(LogLevel.WARNING, *args, **kwargs)
    
    @classmethod
    def error(cls, *args: Any, **kwargs: Any) -> None:
        """Log error level message."""
        cls._log(LogLevel.ERROR, *args, **kwargs)
    
    @classmethod
    def critical(cls, *args: Any, **kwargs: Any) -> None:
        """Log critical level message."""
        cls._log(LogLevel.CRITICAL, *args, **kwargs) 

    @classmethod
    def log_api_call_count(cls, count: int) -> None:
        """Log the total number of API calls made."""
        logger = cls.get_logger()
        logger.debug(f"Total API calls made: {count}") 