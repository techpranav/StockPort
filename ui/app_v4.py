"""
Stockport v4 Main Application

Multi-page Streamlit application for Stockport v4 trading platform.
"""

import streamlit as st
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Stockport v4 - Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import UI components
from ui.dashboard import render_dashboard
from ui.scanner_view import render_scanner_view
from ui.strategies_panel import render_strategies_panel
from ui.portfolio_view import render_portfolio_view
from ui.execution_view import render_execution_view
from ui.settings_panel import render_settings_panel

from utils.debug_utils import DebugUtils


def main():
    """Main application entry point."""
    try:
        # Sidebar navigation
        st.sidebar.title("📈 Stockport v4")
        st.sidebar.markdown("---")
        
        # Navigation menu
        page = st.sidebar.radio(
            "Navigation",
            [
                "📊 Dashboard",
                "🔍 Market Scanner",
                "⚙️ Strategies",
                "💼 Portfolio",
                "⚡ Execution",
                "⚙️ Settings"
            ],
            key="nav_page"
        )
        
        # System status indicator in sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("System Status")
        
        try:
            from ui.services import get_ui_data_service
            data_service = get_ui_data_service()
            status = data_service.get_system_status()
            
            # Check if backend is unavailable
            if status.get("error") == "Backend unavailable":
                st.sidebar.error("🔴 Backend Unavailable")
                st.sidebar.caption("Start backend: `python -m backend.api.rest_api`")
            else:
                is_running = status.get("is_running", False)
                mode = status.get("mode", "manual")
                
                if is_running:
                    st.sidebar.success(f"🟢 Running ({mode})")
                else:
                    st.sidebar.warning("🟡 Stopped")
        except Exception as e:
            st.sidebar.error("🔴 Backend Unavailable")
            st.sidebar.caption(f"Error: {str(e)[:50]}")
            DebugUtils.debug(f"Backend connection error: {e}")
        
        # Main content area
        if page == "📊 Dashboard":
            render_dashboard()
        elif page == "🔍 Market Scanner":
            render_scanner_view()
        elif page == "⚙️ Strategies":
            render_strategies_panel()
        elif page == "💼 Portfolio":
            render_portfolio_view()
        elif page == "⚡ Execution":
            render_execution_view()
        elif page == "⚙️ Settings":
            render_settings_panel()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        DebugUtils.log_error(e, "Error in main application")
        st.exception(e)


if __name__ == "__main__":
    main()

