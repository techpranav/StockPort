"""
Sidebar Component for Stock Analysis Tool

This module provides the sidebar interface with configuration options
for the stock analysis tool.
"""

import streamlit as st
from config.constants import *
from utils.user_settings_manager import UserSettingsManager

def render_sidebar():
    """
    Render the sidebar with configuration options.
    
    Returns:
        dict: Configuration dictionary with all sidebar settings
    """
    st.sidebar.title("⚙️ Configuration")
    
    # Initialize user settings manager
    user_settings = UserSettingsManager()
    
    # Load existing sidebar config from persistent storage
    saved_config = user_settings.load_sidebar_config()
    
    # Export Options
    st.sidebar.subheader("📊 Export Options")
    
    export_word = st.sidebar.checkbox(
        LABEL_EXPORT_WORD_REPORT,
        value=st.session_state.get('sidebar_export_word', saved_config.get('export_word', True)),
        key='sidebar_export_word'
    )
    
    export_excel = st.sidebar.checkbox(
        LABEL_EXPORT_EXCEL_REPORT,
        value=st.session_state.get('sidebar_export_excel', saved_config.get('export_excel', True)),
        key='sidebar_export_excel'
    )
    
    # AI Model Selection
    st.sidebar.subheader("🤖 AI Model")
    
    ai_mode = st.sidebar.selectbox(
        LABEL_AI_MODEL,
        options=AI_MODEL_OPTIONS,
        index=AI_MODEL_OPTIONS.index(st.session_state.get('sidebar_ai_model', saved_config.get('ai_model', 'gpt-3.5-turbo'))),
        key='sidebar_ai_model'
    )
    
    # Google Drive Integration
    st.sidebar.subheader("☁️ Google Drive")
    
    upload_to_drive = st.sidebar.checkbox(
        LABEL_UPLOAD_TO_DRIVE,
        value=st.session_state.get('sidebar_upload_to_drive', saved_config.get('upload_to_drive', False)),
        key='sidebar_upload_to_drive'
    )
    
    client_secrets_file = st.sidebar.file_uploader(
        LABEL_CLIENT_SECRETS_FILE,
        type=['json'],
        key='sidebar_client_secrets_file'
    )
    
    # Analysis Settings
    st.sidebar.subheader("📈 Analysis Settings")
    
    cleanup_days = st.sidebar.number_input(
        LABEL_DELETE_REPORTS_OLDER,
        min_value=1,
        max_value=365,
        value=st.session_state.get('sidebar_cleanup_days', saved_config.get('cleanup_days', 30)),
        key='sidebar_cleanup_days'
    )
    
    def _on_sidebar_days_back_change():
        try:
            st.session_state['days_back_current'] = int(st.session_state['sidebar_days_back'])
        except Exception:
            st.session_state['days_back_current'] = st.session_state['sidebar_days_back']

    days_back = st.sidebar.number_input(
        LABEL_DAYS_HISTORICAL_DATA,
        min_value=1,
        max_value=3650,
        value=st.session_state.get('days_back_current', st.session_state.get('sidebar_days_back', saved_config.get('days_back', 365))),
        key='sidebar_days_back',
        on_change=_on_sidebar_days_back_change
    )
    
    delay_between_calls = st.sidebar.number_input(
        LABEL_DELAY_API_CALLS,
        min_value=0.1,
        max_value=10.0,
        value=float(st.session_state.get('sidebar_delay_between_calls', saved_config.get('delay_between_calls', 1.0))),
        step=0.1,
        key='sidebar_delay_between_calls'
    )
    
    # Create config dictionary
    config = {
        'export_word': export_word,
        'export_excel': export_excel,
        'ai_model': ai_mode,
        'upload_to_drive': upload_to_drive,
        'client_secrets_file': client_secrets_file,
        'cleanup_days': cleanup_days,
        'days_back': days_back,
        'delay_between_calls': delay_between_calls
    }
    
    # Save to persistent storage whenever config changes
    user_settings.save_sidebar_config(config)
    
    # Store in session state for immediate use
    st.session_state['sidebar_config'] = config
    
    return config 