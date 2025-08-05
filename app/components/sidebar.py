import streamlit as st
from typing import Dict, Any
from core.config import ENABLE_AI_FEATURES, ENABLE_GOOGLE_DRIVE
from constants.StringConstants import (
    # Default values
    DEFAULT_PERIOD,
    DEFAULT_LIMIT,
    DELAY_BETWEEN_CALLS,
    # Options
    AI_MODEL_OPTIONS
)
from constants.Messages import (
    # UI strings
    HEADER_CONFIGURATION,
    HEADER_EXPORT_OPTIONS,
    HEADER_AI_ANALYSIS_OPTIONS,
    HEADER_GOOGLE_DRIVE_OPTIONS,
    HEADER_CLEANUP_OPTIONS,
    HEADER_ANALYSIS_OPTIONS,
    # Labels
    LABEL_EXPORT_WORD_REPORT,
    LABEL_EXPORT_EXCEL_REPORT,
    LABEL_AI_MODEL,
    LABEL_UPLOAD_TO_DRIVE,
    LABEL_CLIENT_SECRETS_FILE,
    LABEL_DELETE_REPORTS_OLDER,
    LABEL_DAYS_HISTORICAL_DATA,
    LABEL_DELAY_API_CALLS,
    # Help text
    HELP_DISABLE_CLEANUP,
    HELP_DISABLE_RATE_LIMITING
)

def render_sidebar() -> Dict[str, Any]:
    """Render the sidebar with configuration options."""
    st.sidebar.title(HEADER_CONFIGURATION)
    
    # Export options
    st.sidebar.subheader(HEADER_EXPORT_OPTIONS)
    export_word = st.sidebar.checkbox(LABEL_EXPORT_WORD_REPORT, value=True)
    export_excel = st.sidebar.checkbox(LABEL_EXPORT_EXCEL_REPORT, value=True)
    
    # AI options only if AI features are enabled
    if ENABLE_AI_FEATURES:
        st.sidebar.subheader(HEADER_AI_ANALYSIS_OPTIONS)
        ai_mode = st.sidebar.selectbox(
            LABEL_AI_MODEL,
            options=AI_MODEL_OPTIONS,
            index=0
        )
    else:
        ai_mode = None
    
    # Google Drive options only if enabled
    if ENABLE_GOOGLE_DRIVE:
        st.sidebar.subheader(HEADER_GOOGLE_DRIVE_OPTIONS)
        upload_to_drive = st.sidebar.checkbox(LABEL_UPLOAD_TO_DRIVE, value=True)
        client_secrets = st.sidebar.file_uploader(
            LABEL_CLIENT_SECRETS_FILE,
            type=['json'],
            key="client_secrets"
        )
    else:
        upload_to_drive = False
        client_secrets = None
    
    # Cleanup options
    st.sidebar.subheader(HEADER_CLEANUP_OPTIONS)
    cleanup_days = st.sidebar.number_input(
        LABEL_DELETE_REPORTS_OLDER,
        min_value=0,
        max_value=365,
        value=30,
        help=HELP_DISABLE_CLEANUP
    )
    
    # Analysis options
    st.sidebar.subheader(HEADER_ANALYSIS_OPTIONS)
    days_back = st.sidebar.number_input(
        LABEL_DAYS_HISTORICAL_DATA,
        min_value=1,
        max_value=365,
        value=30
    )
    delay_between_calls = st.sidebar.number_input(
        LABEL_DELAY_API_CALLS,
        min_value=0,
        max_value=300,
        value=DELAY_BETWEEN_CALLS,
        help=HELP_DISABLE_RATE_LIMITING
    )
    
    return {
        "export_word": export_word,
        "export_excel": export_excel,
        "ai_mode": ai_mode,
        "upload_to_drive": upload_to_drive,
        "client_secrets": client_secrets,
        "cleanup_days": cleanup_days,
        "days_back": days_back,
        "delay_between_calls": delay_between_calls
    } 