"""
Stockport v5 Main Application

Trading operating system with 5 core workspaces:
Insight, Discover, Decide, Execute, Review.

Terminal-style UI with 5-zone layout (Z1-Z5):
- Z1: System Bar (always visible, compact)
- Z2: Context Bar (market environment, glanceable)
- Z3: Hero Canvas (workspace-specific primary focus)
- Z4: Stream (dense, scrollable, actionable items)
- Z5: Detail Panel (sidebar, on selection)

DEVELOPER MODE: Authentication is disabled for development.
"""

import streamlit as st
import os

from utils.debug_utils import DebugUtils
from ui.theme import inject_theme
from ui.components.bars import render_context_bar, render_system_bar
from ui.components.layout import render_terminal_shell
from ui.components.panels import render_detail_panel
from ui.workspaces.router import get_active_workspace
from ui.workspaces.insight import render_insight_workspace
from ui.workspaces.discover import render_discover_workspace
from ui.workspaces.decide import render_decide_workspace
from ui.workspaces.execute import render_execute_workspace
from ui.workspaces.review import render_review_workspace


# DEVELOPER MODE: Disable authentication
# Set environment variable to skip auth checks
os.environ['ENABLE_AUTHENTICATION'] = 'false'
os.environ['DISABLE_AUTH'] = 'true'

# Set page config - Full width layout
st.set_page_config(
    page_title="Stockport v5 - Trading OS",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",  # Hide sidebar in v5
    menu_items=None  # Hide menu
)

# Inject CSS to force full width and remove padding
st.markdown("""
<style>
    /* Force full width - override all Streamlit constraints */
    .stApp {
        max-width: 100% !important;
        width: 100% !important;
        padding: 0 !important;
    }
    
    section[data-testid="stAppViewContainer"] {
        max-width: 100% !important;
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    div[data-testid="stAppViewContainer"] > div {
        max-width: 100% !important;
        width: 100% !important;
        padding: 0 !important;
    }
    
    .main .block-container {
        max-width: 100% !important;
        width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Remove Streamlit's default max-width wrapper */
    [data-testid="stAppViewContainer"] > div > div {
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* Hide Streamlit header */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Hide Streamlit menu */
    #MainMenu {
        visibility: hidden;
        height: 0;
    }
    
    footer {
        visibility: hidden;
        height: 0;
    }
    
    /* Full width for columns */
    .stColumn {
        width: 100% !important;
    }
    
    /* Remove side padding from tabs */
    .stTabs [data-baseweb="tab-list"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


def main() -> None:
    """
    Main application entry point.
    
    Renders:
    1. Dark theme injection
    2. Z1 System Bar (always visible)
    3. Z2 Context Bar (market environment)
    4. Z3 Hero Canvas (workspace-specific)
    5. Z4 Stream (workspace-specific, dense)
    6. Z5 Detail Panel (sidebar, on selection)
    
    Auto-refresh: Streamlit auto-refreshes every 2 seconds for live data.
    """
    try:
        # Inject dark theme CSS
        inject_theme()

        # Z5 is sidebar-only and only appears when a selection exists.
        render_detail_panel()

        active_workspace = get_active_workspace()

        def _render_z3() -> None:
            if active_workspace == "insight":
                render_insight_workspace()
            elif active_workspace == "discover":
                render_discover_workspace()
            elif active_workspace == "decide":
                render_decide_workspace()
            elif active_workspace == "execute":
                render_execute_workspace()
            elif active_workspace == "review":
                render_review_workspace()
            else:
                render_insight_workspace()

        def _render_z4() -> None:
            # Z4 is owned by each workspace renderer (they render into the provided container).
            # Keep Z4 empty here to avoid duplicated streams.
            return

        render_terminal_shell(
            render_z1=render_system_bar,
            render_z2=render_context_bar,
            render_z3=_render_z3,
            render_z4=None,
        )
        
        # Manual refresh button for live data (trader-centric)
        # Auto-refresh can be enabled via Streamlit config if needed
        refresh_col1, refresh_col2 = st.columns([1, 0.1])
        with refresh_col2:
            if st.button("🔄", key="manual_refresh", help="Refresh data"):
                st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        DebugUtils.log_error(e, "Error in main application")
        st.exception(e)


if __name__ == "__main__":
    main()

