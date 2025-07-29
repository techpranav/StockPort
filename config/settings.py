from typing import Dict, Any
import os
from pathlib import Path
import yfinance as yf

class Settings:
    """Configuration management for the application."""
    
    # API Settings
    API_RATE_LIMIT_DELAY = 10  # seconds
    API_MAX_RETRIES = 3
    API_REQUEST_DELAY = 2  # seconds
    API_RATE_LIMIT_COOLDOWN = 120  # seconds
    
    # File Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    EXPORT_DIR = DATA_DIR / "exports"
    LOG_DIR = BASE_DIR / "logs"
    
    # Logging Settings
    LOG_LEVEL = "ERROR"
    LOG_FILE = LOG_DIR / "app.log"
    
    # Financial Analysis Settings
    DEFAULT_PERIOD = "1y"
    DEFAULT_INTERVAL = "1d"
    DEFAULT_NEWS_LIMIT = 5
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize the application settings."""
        # Create necessary directories
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.EXPORT_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_api_settings(cls) -> Dict[str, Any]:
        """Get API-related settings."""
        return {
            "rate_limit_delay": cls.API_RATE_LIMIT_DELAY,
            "max_retries": cls.API_MAX_RETRIES,
            "request_delay": cls.API_REQUEST_DELAY,
            "rate_limit_cooldown": cls.API_RATE_LIMIT_COOLDOWN
        }
    
    @classmethod
    def get_logging_settings(cls) -> Dict[str, Any]:
        """Get logging-related settings."""
        return {
            "log_level": cls.LOG_LEVEL,
            "log_file": str(cls.LOG_FILE)
        }
    
    @classmethod
    def get_analysis_settings(cls) -> Dict[str, Any]:
        """Get analysis-related settings."""
        return {
            "default_period": cls.DEFAULT_PERIOD,
            "default_interval": cls.DEFAULT_INTERVAL,
            "default_news_limit": cls.DEFAULT_NEWS_LIMIT
        }

    def _fetch_historical_data(self, ticker: yf.Ticker) -> Dict[str, Any]:
        if self._skip_history:
            return None
        # ... rest of the method 