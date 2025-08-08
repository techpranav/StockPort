"""
Main Page Component

This module contains the main Streamlit application page logic.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, Any

# UI Components
from ui.components.sidebar import render_sidebar
from ui.components.analysis import display_single_stock_analysis, display_mass_stock_analysis
from ui.components.report_manager import render_report_manager

# Services
from services.exporters.report_service import ReportService
from services.ai_service import AIService

# Utilities
from utils.debug_utils import DebugUtils

# Constants
from config.constants.StringConstants import (
    input_dir,
    output_dir,
    STOCK_FILE,
    COMPLETED_FILE,
    FAILED_FILE
)
from config.constants.Messages import (
    TITLE_STOCK_ANALYSIS_TOOL,
    HEADER_NAVIGATION,
    NAV_SINGLE_ANALYSIS,
    NAV_MASS_ANALYSIS,
    NAV_REPORT_HISTORY,
    MSG_WELCOME
)

# Configuration
from config.settings import (
    ENABLE_AI_FEATURES,
    ENABLE_GOOGLE_DRIVE
)

def main():
    """Main application entry point."""
    try:
        # Page configuration
        st.set_page_config(
            page_title=TITLE_STOCK_ANALYSIS_TOOL,
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # App title
        st.title(TITLE_STOCK_ANALYSIS_TOOL)
        
        # Render sidebar and get configuration
        config = render_sidebar()
        
        # Store config in session state for use by other components
        st.session_state['config'] = config
        
        # Navigation
        st.sidebar.markdown("---")
        st.sidebar.subheader(HEADER_NAVIGATION)
        
        page = st.sidebar.radio(
            "Choose Analysis Type:",
            [NAV_SINGLE_ANALYSIS, NAV_MASS_ANALYSIS, NAV_REPORT_HISTORY],
            key="navigation_radio"
        )
        
        # Initialize services
        report_service = ReportService(days_back=config['days_back'])
        
        # Main content area
        if page == NAV_SINGLE_ANALYSIS:
            display_single_stock_analysis()
            
        elif page == NAV_MASS_ANALYSIS:
            display_mass_stock_analysis()
            
        elif page == NAV_REPORT_HISTORY:
            render_report_manager()
        
        # Cleanup old reports (only if not on report history page and cleanup is enabled)
        cleanup_days = config.get('cleanup_days', 0)
        if cleanup_days > 0 and page != NAV_REPORT_HISTORY:
            try:
                deleted_count = report_service.cleanup_old_reports(cleanup_days)
                if deleted_count > 0:
                    DebugUtils.info(f"Cleaned up {deleted_count} old reports")
            except Exception as e:
                DebugUtils.log_error(e, "Error during automatic cleanup")
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666666; font-size: 12px;'>
                Stock Analysis Tool - Powered by Yahoo Finance & Streamlit
            </div>
            """,
            unsafe_allow_html=True
        )
        
    except Exception as e:
        DebugUtils.log_error(e, "Error in main application")
        st.error(f"Application error: {str(e)}")

def read_stock_symbols(file_path: str) -> list:
    """Read stock symbols from a file."""
    try:
        symbols = []
        with open(file_path, 'r') as file:
            for line in file:
                # Strip whitespace and carriage returns
                symbol = line.strip().replace('\r', '').replace('\n', '')
                if symbol:  # Only add non-empty symbols
                    symbols.append(symbol.upper())
        return symbols
    except FileNotFoundError:
        DebugUtils.warning(f"Stock symbols file not found: {file_path}")
        return []
    except Exception as e:
        DebugUtils.log_error(e, f"Error reading stock symbols from {file_path}")
        return []

if __name__ == "__main__":
    main() 