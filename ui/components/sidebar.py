import streamlit as st
from typing import Dict, Any
from config.settings import ENABLE_AI_FEATURES, ENABLE_GOOGLE_DRIVE
from config.constants import *
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
    
    # Google Drive options only if Google Drive is enabled
    if ENABLE_GOOGLE_DRIVE:
        st.sidebar.subheader(HEADER_GOOGLE_DRIVE_OPTIONS)
        upload_to_drive = st.sidebar.checkbox(LABEL_UPLOAD_TO_DRIVE, value=False)
        
        if upload_to_drive:
            client_secrets_file = st.sidebar.file_uploader(
                LABEL_CLIENT_SECRETS_FILE,
                type=['json'],
                help="Upload your Google Drive API credentials file"
            )
        else:
            client_secrets_file = None
    else:
        upload_to_drive = False
        client_secrets_file = None
    
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
        min_value=30,
        max_value=3650,  # ~10 years
        value=365,  # 1 year default
        step=30
    )
    
    delay_between_calls = st.sidebar.number_input(
        LABEL_DELAY_API_CALLS,
        min_value=0,
        max_value=300,
        value=DELAY_BETWEEN_CALLS,
        help=HELP_DISABLE_RATE_LIMITING
    )
    
    return {
        'export_word': export_word,
        'export_excel': export_excel,
        'ai_model': ai_mode,
        'upload_to_drive': upload_to_drive,
        'client_secrets_file': client_secrets_file,
        'cleanup_days': cleanup_days,
        'days_back': days_back,
        'delay_between_calls': delay_between_calls
    } 