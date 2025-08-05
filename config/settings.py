"""
Application Settings and Configuration

This module contains all application-wide settings and feature flags.
"""

from typing import Dict, Any
import os
from pathlib import Path

# Feature Flags
ENABLE_AI_FEATURES = True
ENABLE_GOOGLE_DRIVE = False  # Set to True to enable Google Drive integration
ENABLE_TECHNICAL_ANALYSIS = True
ENABLE_FUNDAMENTAL_ANALYSIS = True
ENABLE_PORTFOLIO_ANALYSIS = True

# API Configuration
API_RATE_LIMIT_DELAY = 10  # seconds
API_MAX_RETRIES = 3
API_REQUEST_DELAY = 2  # seconds
API_RATE_LIMIT_COOLDOWN = 120  # seconds

# File Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = DATA_DIR / "exports"
LOG_DIR = BASE_DIR / "logs"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# Logging Settings
# LOG_LEVEL: Controls what messages are displayed in console and saved to log files
# Available values and their meanings:
#   "DEBUG"   - Shows all messages (most verbose): debug info, data processing steps, API calls, etc.
#   "INFO"    - Shows informational messages and above: operation status, progress updates, warnings, errors
#   "WARNING" - Shows warnings and above: potential issues, missing data, rate limiting, errors
#   "ERROR"   - Shows only errors: exceptions, failures, critical issues
#   "CRITICAL" - Shows only critical system failures (rarely used)
# 
# For development/troubleshooting: use "DEBUG" to see all details
# For production: use "INFO" or "WARNING" to reduce noise
# To see only problems: use "ERROR"
LOG_LEVEL = "ERROR"  # Current setting: shows all debug statements and error details
LOG_FILE = LOG_DIR / "app.log"

# Financial Analysis Settings
DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"
DEFAULT_NEWS_LIMIT = 5
DEFAULT_DAYS_BACK = 365

# Export Settings
EXPORT_EXCEL = True
EXPORT_WORD = True
EXPORT_JSON = True

# AI Settings
DEFAULT_AI_MODEL = "gpt-3.5-turbo"
AI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google Drive Settings
GOOGLE_DRIVE_CREDENTIALS_FILE = INPUT_DIR / "Service Account.json"

class Settings:
    """Configuration management for the application."""
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize the application settings."""
        # Create necessary directories
        DATA_DIR.mkdir(exist_ok=True)
        EXPORT_DIR.mkdir(exist_ok=True)
        LOG_DIR.mkdir(exist_ok=True)
        INPUT_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_api_settings(cls) -> Dict[str, Any]:
        """Get API-related settings."""
        return {
            "rate_limit_delay": API_RATE_LIMIT_DELAY,
            "max_retries": API_MAX_RETRIES,
            "request_delay": API_REQUEST_DELAY,
            "rate_limit_cooldown": API_RATE_LIMIT_COOLDOWN
        }
    
    @classmethod
    def get_logging_settings(cls) -> Dict[str, Any]:
        """Get logging-related settings."""
        return {
            "level": LOG_LEVEL,
            "file": LOG_FILE
        }
    
    @classmethod
    def get_feature_flags(cls) -> Dict[str, bool]:
        """Get feature flags."""
        return {
            "ai_features": ENABLE_AI_FEATURES,
            "google_drive": ENABLE_GOOGLE_DRIVE,
            "technical_analysis": ENABLE_TECHNICAL_ANALYSIS,
            "fundamental_analysis": ENABLE_FUNDAMENTAL_ANALYSIS,
            "portfolio_analysis": ENABLE_PORTFOLIO_ANALYSIS
        }
    
    @classmethod
    def get_export_settings(cls) -> Dict[str, Any]:
        """Get export-related settings."""
        return {
            "excel": EXPORT_EXCEL,
            "word": EXPORT_WORD,
            "json": EXPORT_JSON,
            "export_dir": EXPORT_DIR
        }

# Initialize settings on import
Settings.initialize() 