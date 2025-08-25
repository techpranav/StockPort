"""
Unified Application Configuration

This is the single source of truth for all application settings and feature flags.
All other modules should import from this file only.
"""

import os
from pathlib import Path
from typing import Dict, Any

# ============================================================================
# ENVIRONMENT DETECTION
# ============================================================================

def is_cloud_environment() -> bool:
    """Check if running in a cloud environment."""
    return (
        "STREAMLIT_SERVER_RUNNING" in os.environ or
        "STREAMLIT_CLOUD" in os.environ or
        "STREAMLIT_SHARING" in os.environ or
        os.path.exists("/app/.streamlit/")
    )

# ============================================================================
# FEATURE FLAGS (Single place to enable/disable features)
# ============================================================================

# Core Features
ENABLE_AI_FEATURES = True
ENABLE_GOOGLE_DRIVE = True
ENABLE_TECHNICAL_ANALYSIS = True
ENABLE_FUNDAMENTAL_ANALYSIS = True
ENABLE_PORTFOLIO_ANALYSIS = True

# Export Features
ENABLE_EXCEL_EXPORT = True
ENABLE_WORD_EXPORT = True
ENABLE_CSV_EXPORT = True
ENABLE_JSON_EXPORT = True

# Cloud-specific Features
ENABLE_USER_SETTINGS = True
ENABLE_SESSION_PERSISTENCE = True
ENABLE_CLOUD_GOOGLE_DRIVE = True
ENABLE_CACHING = True
ENABLE_BATCH_DOWNLOADS = True
SHOW_ANALYSIS_PROGRESS = True

# ============================================================================
# PATHS AND DIRECTORIES
# ============================================================================

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = DATA_DIR / "exports"
LOG_DIR = BASE_DIR / "logs"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = BASE_DIR / "reports"

# Credentials directory
CREDENTIALS_DIR = BASE_DIR / "config" / "credentials"

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Rate limiting and delays
API_RATE_LIMIT_DELAY = 10  # seconds
API_MAX_RETRIES = 3
API_REQUEST_DELAY = 2  # seconds
API_RATE_LIMIT_COOLDOWN = 120  # seconds
API_DELAY_SECONDS = 0.1  # Cloud-specific delay

# AI Configuration
DEFAULT_AI_MODEL = "gpt-3.5-turbo"
AI_API_KEY = os.getenv("OPENAI_API_KEY")

# ============================================================================
# GOOGLE DRIVE CONFIGURATION
# ============================================================================

# Google Drive settings
GOOGLE_DRIVE_USE_SERVICE_ACCOUNT = os.getenv("GOOGLE_DRIVE_USE_SERVICE_ACCOUNT", "false").lower() == "true"
GOOGLE_DRIVE_SCOPES = os.getenv("GOOGLE_DRIVE_SCOPES", "https://www.googleapis.com/auth/drive.file")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")  # optional default upload folder

# OAuth client secret JSON (for User OAuth)
GOOGLE_DRIVE_CREDENTIALS_FILE = Path(
    os.getenv("GOOGLE_DRIVE_CREDENTIALS_FILE", str(CREDENTIALS_DIR / "client_secret.json"))
)

# Service Account JSON (for headless mode)
GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS", str(CREDENTIALS_DIR / "service_account.json")
)

# ============================================================================
# ANALYSIS SETTINGS
# ============================================================================

# Financial Analysis Settings
DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"
DEFAULT_NEWS_LIMIT = 5
DEFAULT_DAYS_BACK = 365
MAX_HISTORY_DAYS = 1825  # 5 years

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

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
LOG_LEVEL = "INFO" if is_cloud_environment() else "ERROR"
LOG_FILE = LOG_DIR / "app.log"

# ============================================================================
# CLOUD-SPECIFIC SETTINGS
# ============================================================================

# Security (Cloud)
ALLOW_FILE_UPLOADS = True
MAX_FILE_SIZE_MB = 10
ALLOWED_FILE_TYPES = [".txt", ".csv"]

# Performance (Cloud)
CACHE_TTL_HOURS = 24
MAX_CONCURRENT_ANALYSES = 5

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

class AppConfig:
    """Unified configuration management for the application."""
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize the application settings and create necessary directories."""
        # Create necessary directories
        for directory in [DATA_DIR, EXPORT_DIR, LOG_DIR, INPUT_DIR, OUTPUT_DIR, REPORTS_DIR]:
            directory.mkdir(exist_ok=True)
    
    @classmethod
    def get_api_settings(cls) -> Dict[str, Any]:
        """Get API-related settings."""
        return {
            "rate_limit_delay": API_RATE_LIMIT_DELAY,
            "max_retries": API_MAX_RETRIES,
            "request_delay": API_REQUEST_DELAY,
            "rate_limit_cooldown": API_RATE_LIMIT_COOLDOWN,
            "delay_seconds": API_DELAY_SECONDS
        }
    
    @classmethod
    def get_google_drive_config(cls) -> Dict[str, Any]:
        """Get Google Drive configuration for current environment."""
        if is_cloud_environment():
            return {
                "enabled": ENABLE_GOOGLE_DRIVE,
                "use_service_account": False,  # Always OAuth for cloud
                "scopes": GOOGLE_DRIVE_SCOPES,
                "credentials_file": None,  # Set per user
                "folder_id": None,  # Set per user
                "setup_method": "oauth"  # Always OAuth for cloud
            }
        else:
            # Local environment - use file-based config
            return {
                "enabled": ENABLE_GOOGLE_DRIVE,
                "use_service_account": GOOGLE_DRIVE_USE_SERVICE_ACCOUNT,
                "scopes": GOOGLE_DRIVE_SCOPES,
                "credentials_file": str(GOOGLE_DRIVE_CREDENTIALS_FILE),
                "folder_id": GOOGLE_DRIVE_FOLDER_ID,
                "setup_method": "service_account" if GOOGLE_DRIVE_USE_SERVICE_ACCOUNT else "oauth"
            }
    
    @classmethod
    def get_feature_flags(cls) -> Dict[str, Any]:
        """Get all feature flags."""
        return {
            "ai_features": ENABLE_AI_FEATURES,
            "google_drive": ENABLE_GOOGLE_DRIVE,
            "technical_analysis": ENABLE_TECHNICAL_ANALYSIS,
            "fundamental_analysis": ENABLE_FUNDAMENTAL_ANALYSIS,
            "portfolio_analysis": ENABLE_PORTFOLIO_ANALYSIS,
            "excel_export": ENABLE_EXCEL_EXPORT,
            "word_export": ENABLE_WORD_EXPORT,
            "csv_export": ENABLE_CSV_EXPORT,
            "json_export": ENABLE_JSON_EXPORT
        }
    
    @classmethod
    def get_export_settings(cls) -> Dict[str, Any]:
        """Get export-related settings."""
        return {
            "excel": ENABLE_EXCEL_EXPORT,
            "word": ENABLE_WORD_EXPORT,
            "csv": ENABLE_CSV_EXPORT,
            "json": ENABLE_JSON_EXPORT,
            "output_dir": str(OUTPUT_DIR),
            "reports_dir": str(REPORTS_DIR)
        }
    
    @classmethod
    def get_analysis_settings(cls) -> Dict[str, Any]:
        """Get analysis-related settings."""
        return {
            "default_period": DEFAULT_PERIOD,
            "default_interval": DEFAULT_INTERVAL,
            "default_news_limit": DEFAULT_NEWS_LIMIT,
            "default_days_back": DEFAULT_DAYS_BACK,
            "max_history_days": MAX_HISTORY_DAYS,
            "technical_analysis": ENABLE_TECHNICAL_ANALYSIS,
            "fundamental_analysis": ENABLE_FUNDAMENTAL_ANALYSIS,
            "portfolio_analysis": ENABLE_PORTFOLIO_ANALYSIS
        }

# ============================================================================
# LEGACY COMPATIBILITY (for existing imports)
# ============================================================================

# These constants are kept for backward compatibility
# New code should use AppConfig.get_*() methods instead

# Feature flags (legacy)
ENABLE_AI_FEATURES = ENABLE_AI_FEATURES
ENABLE_GOOGLE_DRIVE = ENABLE_GOOGLE_DRIVE
ENABLE_TECHNICAL_ANALYSIS = ENABLE_TECHNICAL_ANALYSIS
ENABLE_FUNDAMENTAL_ANALYSIS = ENABLE_FUNDAMENTAL_ANALYSIS
ENABLE_PORTFOLIO_ANALYSIS = ENABLE_PORTFOLIO_ANALYSIS

# Export flags (legacy)
EXPORT_EXCEL = ENABLE_EXCEL_EXPORT
EXPORT_WORD = ENABLE_WORD_EXPORT
EXPORT_JSON = ENABLE_JSON_EXPORT

# Paths (legacy)
BASE_DIR = BASE_DIR
DATA_DIR = DATA_DIR
EXPORT_DIR = EXPORT_DIR
LOG_DIR = LOG_DIR
INPUT_DIR = INPUT_DIR
OUTPUT_DIR = OUTPUT_DIR
