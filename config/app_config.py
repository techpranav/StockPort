"""
Unified Application Configuration

This is the single source of truth for all application settings and feature flags.
All other modules should import from this file only.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment variables

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
ENABLE_AI_FEATURES = False
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

# Authentication and Licensing Features
# Default enabled via config, overridable by env
ENABLE_AUTHENTICATION = os.getenv("ENABLE_AUTHENTICATION", "true").lower() == "true"
ENABLE_STRIPE_PAYMENTS = os.getenv("ENABLE_STRIPE_PAYMENTS", "false").lower() == "true"
ENABLE_SOCIAL_LOGIN = os.getenv("ENABLE_SOCIAL_LOGIN", "true").lower() == "true"
ENABLE_ADMIN_PANEL = os.getenv("ENABLE_ADMIN_PANEL", "false").lower() == "true"

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
    
    @classmethod
    def get_auth_settings(cls) -> Dict[str, Any]:
        """Get authentication and licensing settings."""
        return {
            "enabled": ENABLE_AUTHENTICATION,
            "stripe_enabled": ENABLE_STRIPE_PAYMENTS,
            "social_login_enabled": ENABLE_SOCIAL_LOGIN,
            "admin_panel_enabled": ENABLE_ADMIN_PANEL,
            "database_path": str(AUTH_DATABASE_PATH),
            "session_timeout_hours": SESSION_TIMEOUT_HOURS,
            "session_secret_key": SESSION_SECRET_KEY,
            "remember_me_days": REMEMBER_ME_DAYS,
            "stripe_secret_key": STRIPE_SECRET_KEY,
            "stripe_publishable_key": STRIPE_PUBLISHABLE_KEY,
            "stripe_webhook_secret": STRIPE_WEBHOOK_SECRET,
            "license_plans": LICENSE_PLANS,
            "google_oauth_client_id": GOOGLE_OAUTH_CLIENT_ID,
            "google_oauth_client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
            "google_oauth_redirect_uri": GOOGLE_OAUTH_REDIRECT_URI,
            "microsoft_oauth_client_id": MICROSOFT_OAUTH_CLIENT_ID,
            "microsoft_oauth_client_secret": MICROSOFT_OAUTH_CLIENT_SECRET,
            "microsoft_oauth_redirect_uri": MICROSOFT_OAUTH_REDIRECT_URI,
            "microsoft_oauth_tenant_id": MICROSOFT_OAUTH_TENANT_ID,
            "csrf_secret_key": CSRF_SECRET_KEY,
            "rate_limit_requests": RATE_LIMIT_REQUESTS,
            "rate_limit_window": RATE_LIMIT_WINDOW
        }

# ============================================================================
# AUTHENTICATION AND LICENSING CONFIGURATION
# ============================================================================

# Database
AUTH_DATABASE_PATH = BASE_DIR / "data" / "auth.db"

# Session Configuration
SESSION_TIMEOUT_HOURS = 24
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "your-secret-key-change-in-production")
REMEMBER_ME_DAYS = int(os.getenv("REMEMBER_ME_DAYS", "30"))

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Razorpay Configuration (India)
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

# PayPal Configuration (Global)
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")  # sandbox or live

# Payment Gateway Selection
PAYMENT_GATEWAY = os.getenv("PAYMENT_GATEWAY", "auto")  # auto, razorpay, stripe, paypal

# License Plans
LICENSE_PLANS = {
    "basic_monthly": {
        "name": "Basic Monthly",
        "price": 0.01,
        "currency": "usd",
        "stripe_price_id": os.getenv("STRIPE_BASIC_MONTHLY_PRICE_ID"),
        "features": ["Stock Analysis", "Basic Reports", "Google Drive Export"],
        "expiry_days": 30
    },
    "basic_yearly": {
        "name": "Basic Yearly",
        "price": 00.05,
        "currency": "usd",
        "stripe_price_id": os.getenv("STRIPE_BASIC_YEARLY_PRICE_ID"),
        "features": ["Stock Analysis", "Basic Reports", "Google Drive Export"],
        "expiry_days": 365
    },
    "pro_monthly": {
        "name": "Pro Monthly",
        "price": 19.99,
        "currency": "usd",
        "stripe_price_id": os.getenv("STRIPE_PRO_MONTHLY_PRICE_ID"),
        "features": ["Stock Analysis", "Advanced Reports", "Google Drive Export", "AI Insights", "Portfolio Analysis"],
        "expiry_days": 30
    },
    "pro_yearly": {
        "name": "Pro Yearly",
        "price": 199.99,
        "currency": "usd",
        "stripe_price_id": os.getenv("STRIPE_PRO_YEARLY_PRICE_ID"),
        "features": ["Stock Analysis", "Advanced Reports", "Google Drive Export", "AI Insights", "Portfolio Analysis"],
        "expiry_days": 365
    }
}

# Social Login Configuration
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_OAUTH_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8501")

# Microsoft OAuth Configuration
MICROSOFT_OAUTH_CLIENT_ID = os.getenv("MICROSOFT_OAUTH_CLIENT_ID")
MICROSOFT_OAUTH_CLIENT_SECRET = os.getenv("MICROSOFT_OAUTH_CLIENT_SECRET")
MICROSOFT_OAUTH_REDIRECT_URI = os.getenv("MICROSOFT_OAUTH_REDIRECT_URI", "http://localhost:8501")
MICROSOFT_OAUTH_TENANT_ID = os.getenv("MICROSOFT_OAUTH_TENANT_ID", "common")

# Security Configuration
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", "your-csrf-secret-key-change-in-production")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # requests per hour
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour in seconds

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
