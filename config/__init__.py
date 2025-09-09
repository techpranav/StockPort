"""
Configuration package for the Stockport application.

This package provides unified access to all application configuration.
"""

from .app_config import (
    # Feature flags
    ENABLE_AI_FEATURES,
    ENABLE_GOOGLE_DRIVE,
    ENABLE_TECHNICAL_ANALYSIS,
    ENABLE_FUNDAMENTAL_ANALYSIS,
    ENABLE_PORTFOLIO_ANALYSIS,
    
    # Export flags
    ENABLE_EXCEL_EXPORT,
    ENABLE_WORD_EXPORT,
    ENABLE_CSV_EXPORT,
    ENABLE_JSON_EXPORT,
    AI_API_KEY,
    
    # Paths
    BASE_DIR,
    DATA_DIR,
    EXPORT_DIR,
    LOG_DIR,
    INPUT_DIR,
    OUTPUT_DIR,
    REPORTS_DIR,
    
    # Configuration management
    AppConfig,
    is_cloud_environment,
    
    # Legacy compatibility
    EXPORT_EXCEL,
    EXPORT_WORD,
    EXPORT_JSON,

    # Google Drive constants
    GOOGLE_DRIVE_USE_SERVICE_ACCOUNT,
    GOOGLE_DRIVE_SCOPES,
    GOOGLE_DRIVE_CREDENTIALS_FILE,
    GOOGLE_APPLICATION_CREDENTIALS,
    GOOGLE_DRIVE_FOLDER_ID,
    
    # Authentication and Licensing constants
    ENABLE_AUTHENTICATION,
    ENABLE_STRIPE_PAYMENTS,
    ENABLE_SOCIAL_LOGIN,
    ENABLE_ADMIN_PANEL,
    AUTH_DATABASE_PATH,
    SESSION_TIMEOUT_HOURS,
    SESSION_SECRET_KEY,
    STRIPE_SECRET_KEY,
    STRIPE_PUBLISHABLE_KEY,
    STRIPE_WEBHOOK_SECRET,
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
    RAZORPAY_WEBHOOK_SECRET,
    PAYPAL_CLIENT_ID,
    PAYPAL_CLIENT_SECRET,
    PAYPAL_MODE,
    PAYMENT_GATEWAY,
    LICENSE_PLANS,
    GOOGLE_OAUTH_CLIENT_ID,
    GOOGLE_OAUTH_CLIENT_SECRET,
    GOOGLE_OAUTH_REDIRECT_URI,
    MICROSOFT_OAUTH_CLIENT_ID,
    MICROSOFT_OAUTH_CLIENT_SECRET,
    MICROSOFT_OAUTH_REDIRECT_URI,
    MICROSOFT_OAUTH_TENANT_ID,
    CSRF_SECRET_KEY,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
)

# Convenience function for getting all settings
def get_all_settings():
    """Get all application settings as a dictionary."""
    return {
        "features": AppConfig.get_feature_flags(),
        "api": AppConfig.get_api_settings(),
        "google_drive": AppConfig.get_google_drive_config(),
        "export": AppConfig.get_export_settings(),
        "analysis": AppConfig.get_analysis_settings(),
        "auth": AppConfig.get_auth_settings(),
        "paths": {
            "base_dir": str(BASE_DIR),
            "data_dir": str(DATA_DIR),
            "export_dir": str(EXPORT_DIR),
            "log_dir": str(LOG_DIR),
            "input_dir": str(INPUT_DIR),
            "output_dir": str(OUTPUT_DIR),
            "reports_dir": str(REPORTS_DIR),
        }
    }

# Initialize configuration when package is imported
AppConfig.initialize()
