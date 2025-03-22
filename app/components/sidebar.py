import streamlit as st
from typing import Dict, Any
from core.config import ENABLE_AI_FEATURES, ENABLE_GOOGLE_DRIVE

def render_sidebar() -> Dict[str, Any]:
    """Render the sidebar with configuration options."""
    st.sidebar.title("Configuration")
    
    # Export options
    st.sidebar.subheader("Export Options")
    export_word = st.sidebar.checkbox("Export Word Report", value=True)
    export_excel = st.sidebar.checkbox("Export Excel Report", value=True)
    
    # AI options only if AI features are enabled
    if ENABLE_AI_FEATURES:
        st.sidebar.subheader("AI Analysis Options")
        ai_mode = st.sidebar.selectbox(
            "AI Model",
            options=["ChatGPT", "Ollama"],
            index=0
        )
    else:
        ai_mode = None
    
    # Google Drive options only if enabled
    if ENABLE_GOOGLE_DRIVE:
        st.sidebar.subheader("Google Drive Options")
        upload_to_drive = st.sidebar.checkbox("Upload to Google Drive", value=True)
        client_secrets = st.sidebar.file_uploader(
            "Upload Client Secrets File",
            type=['json'],
            key="client_secrets"
        )
    else:
        upload_to_drive = False
        client_secrets = None
    
    # Cleanup options
    st.sidebar.subheader("Cleanup Options")
    cleanup_days = st.sidebar.number_input(
        "Delete reports older than (days)",
        min_value=0,
        max_value=365,
        value=30,
        help="Set to 0 to disable automatic cleanup"
    )
    
    # Analysis options
    st.sidebar.subheader("Analysis Options")
    days_back = st.sidebar.number_input(
        "Days of historical data",
        min_value=1,
        max_value=365,
        value=30
    )
    delay_between_calls = st.sidebar.number_input(
        "Delay between API calls (seconds)",
        min_value=0,
        max_value=300,
        value=60,
        help="Set to 0 to disable rate limiting"
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