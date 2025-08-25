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
