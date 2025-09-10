"""
Main Page Component

This module contains the main Streamlit application page logic.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, Any
import webbrowser
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# UI Components
from ui.components.sidebar import render_sidebar
from ui.components.analysis import display_single_stock_analysis, display_mass_stock_analysis
from ui.components.report_manager import render_report_manager

# Services
from services.exporters.report_service import ReportService
from services.ai_service import AIService

# Utilities
from utils.debug_utils import DebugUtils
from utils.google_drive_utils import GoogleDriveManager
from utils.cloud_google_drive_manager import CloudGoogleDriveManager
from ui.components.cloud_google_drive_setup import render_cloud_google_drive_setup
from utils.user_settings_manager import UserSettingsManager

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
    MSG_WELCOME,
    HEADER_SINGLE_STOCK_ANALYSIS,
    PLACEHOLDER_STOCK_SYMBOL
)

# Configuration
from config import (
    ENABLE_AI_FEATURES,
    ENABLE_GOOGLE_DRIVE,
    ENABLE_AUTHENTICATION
)

# Import authentication components
if ENABLE_AUTHENTICATION:
    from auth.ui import render_auth_gate, render_admin_panel, render_user_profile

def get_service_account_email():
    sa_path = Path("config/credentials/service_account.json")
    if sa_path.exists():
        try:
            with open(sa_path, "r") as f:
                data = json.load(f)
                return data.get("client_email")
        except Exception:
            return None
    return None

def render_google_drive_setup():
    """Render unified Google Drive setup page with user-specific settings."""
    try:
        st.header("🔗 Google Drive Setup")
        
        if not ENABLE_GOOGLE_DRIVE:
            st.info("Google Drive integration is disabled in settings. Enable ENABLE_GOOGLE_DRIVE in config.")
            return

        # Check if we're in a cloud environment (without accessing st.secrets)
        is_cloud = False
        try:
            # Check environment variables and known cloud path
            is_cloud = (
                "STREAMLIT_SERVER_RUNNING" in os.environ or
                "STREAMLIT_CLOUD" in os.environ or
                "STREAMLIT_SHARING" in os.environ or
                os.path.exists("/app/.streamlit/")
            )
        except Exception as e:
            # If there's any error with environment detection, assume local environment
            DebugUtils.log_error(e, "Error detecting cloud environment, assuming local")
            is_cloud = False
        
        # Debug info (only show in development)
        if os.environ.get("DEBUG", "false").lower() == "true":
            st.info(f"🔍 Environment detection: is_cloud={is_cloud}")
        
        if is_cloud:
            # Use cloud setup component
            try:
                render_cloud_google_drive_setup()
            except Exception as e:
                st.error(f"❌ Error loading cloud Google Drive setup: {str(e)}")
                st.info("Falling back to local setup...")
                render_local_google_drive_setup()
        else:
            # Use local setup component
            render_local_google_drive_setup()
            
    except Exception as e:
        st.error(f"❌ Error in Google Drive setup: {str(e)}")
        st.exception(e)

def render_local_google_drive_setup():
    """Render local Google Drive setup."""
    try:
        st.subheader("🔧 Local Setup (Service Account)")
        
        # Check for service account credentials
        service_account_path = Path("config/credentials/service_account.json")
        if service_account_path.exists():
            st.success("✅ Service account credentials found!")
            
            # Get service account email for display
            sa_email = get_service_account_email()
            if sa_email:
                st.info(f"Service Account: {sa_email}")
            
            # Folder ID input
            folder_id = st.text_input(
                "Google Drive Folder ID:",
                placeholder="Enter the folder ID where reports will be uploaded",
                help="This is the folder where your stock analysis reports will be uploaded"
            )
            
            if folder_id:
                # Test folder access
                if st.button("🔍 Test Folder Access"):
                    try:
                        drive_manager = GoogleDriveManager()
                        if drive_manager.test_folder_access(folder_id):
                            st.success("✅ Folder access successful!")
                            
                            # Save folder ID to user settings
                            user_settings = UserSettingsManager()
                            user_settings.save_google_drive_folder_id(folder_id)
                            st.success("✅ Folder ID saved!")
                        else:
                            st.error("❌ Cannot access folder. Please check the folder ID and permissions.")
                    except Exception as e:
                        st.error(f"❌ Error testing folder access: {str(e)}")
            
            # Show current folder info
            user_settings = UserSettingsManager()
            current_folder_id = user_settings.get_google_drive_folder_id()
            if current_folder_id:
                st.info(f"📁 Current folder ID: {current_folder_id}")
                
                if st.button("📋 Get Folder Info"):
                    try:
                        drive_manager = GoogleDriveManager()
                        folder_info = drive_manager.get_folder_info(current_folder_id)
                        if folder_info:
                            st.success("✅ Folder info retrieved!")
                            st.json(folder_info)
                        else:
                            st.error("❌ Could not retrieve folder info")
                    except Exception as e:
                        st.error(f"❌ Error getting folder info: {str(e)}")
            
            # Instructions for getting folder ID
            with st.expander("📖 How to get a Google Drive Folder ID"):
                st.markdown("""
                1. **Open Google Drive** in your browser
                2. **Navigate to the folder** where you want reports uploaded
                3. **Copy the folder ID** from the URL:
                   - URL format: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
                   - Copy the `FOLDER_ID_HERE` part
                4. **Paste it** in the input field above
                """)
            
            # Instructions for setting up service account
            with st.expander("🔧 How to set up Service Account"):
                st.markdown("""
                ### Step 1: Create a Google Cloud Project
                1. Go to [Google Cloud Console](https://console.cloud.google.com/)
                2. Create a new project or select existing one
                3. Enable the Google Drive API
                
                ### Step 2: Create Service Account
                1. Go to "IAM & Admin" > "Service Accounts"
                2. Click "Create Service Account"
                3. Name it (e.g., "Stockport Drive Upload")
                4. Click "Create and Continue"
                5. Skip role assignment, click "Done"
                
                ### Step 3: Create and Download Key
                1. Click on your service account
                2. Go to "Keys" tab
                3. Click "Add Key" > "Create new key"
                4. Choose "JSON" format
                5. Download the file
                6. Rename to `service_account.json`
                7. Place in `config/credentials/` folder
                
                ### Step 4: Share Folder
                1. In Google Drive, right-click your folder
                2. Click "Share"
                3. Add your service account email
                4. Give "Editor" permissions
                5. Click "Done"
                """)
            
            # Show service account email for sharing
            if sa_email:
                st.info(f"💡 **Share your folder with this email:** `{sa_email}`")
        
        else:
            st.warning("⚠️ Service account credentials not found!")
            st.info("Please follow the setup instructions above to create and download service account credentials.")
            
            # Instructions for setting up service account
            with st.expander("🔧 How to set up Service Account"):
                st.markdown("""
                ### Step 1: Create a Google Cloud Project
                1. Go to [Google Cloud Console](https://console.cloud.google.com/)
                2. Create a new project or select existing one
                3. Enable the Google Drive API
                
                ### Step 2: Create Service Account
                1. Go to "IAM & Admin" > "Service Accounts"
                2. Click "Create Service Account"
                3. Name it (e.g., "Stockport Drive Upload")
                4. Click "Create and Continue"
                5. Skip role assignment, click "Done"
                
                ### Step 3: Create and Download Key
                1. Click on your service account
                2. Go to "Keys" tab
                3. Click "Add Key" > "Create new key"
                4. Choose "JSON" format
                5. Download the file
                6. Rename to `service_account.json`
                7. Place in `config/credentials/` folder
                
                ### Step 4: Share Folder
                1. In Google Drive, right-click your folder
                2. Click "Share"
                3. Add your service account email
                4. Give "Editor" permissions
                5. Click "Done"
                """)
            
    except Exception as e:
        st.error(f"❌ Error in local Google Drive setup: {str(e)}")
        st.exception(e)

def render_cloud_google_drive_setup():
    """Render cloud Google Drive setup."""
    try:
        st.subheader("☁️ Cloud Setup (OAuth)")
        
        # Check if user has already set up Google Drive
        user_settings = UserSettingsManager()
        current_folder_id = user_settings.get_google_drive_folder_id()
        
        if current_folder_id:
            st.success("✅ Google Drive already configured!")
            st.info(f"📁 Current folder ID: {current_folder_id}")
            
            # Test current setup
            if st.button("🔍 Test Current Setup"):
                try:
                    cloud_drive_manager = CloudGoogleDriveManager()
                    if cloud_drive_manager.test_folder_access(current_folder_id):
                        st.success("✅ Current setup is working!")
                    else:
                        st.error("❌ Current setup failed. Please reconfigure.")
                except Exception as e:
                    st.error(f"❌ Error testing setup: {str(e)}")
            
            # Option to change folder
            if st.button("🔄 Change Folder"):
                st.session_state['change_drive_folder'] = True
        
        # Show setup form
        if not current_folder_id or st.session_state.get('change_drive_folder', False):
            st.info("🔧 Please set up Google Drive integration:")
            
            # Folder ID input
            folder_id = st.text_input(
                "Google Drive Folder ID:",
                placeholder="Enter the folder ID where reports will be uploaded",
                help="This is the folder where your stock analysis reports will be uploaded"
            )
            
            if folder_id:
                # Test folder access
                if st.button("🔍 Test Folder Access"):
                    try:
                        cloud_drive_manager = CloudGoogleDriveManager()
                        if cloud_drive_manager.test_folder_access(folder_id):
                            st.success("✅ Folder access successful!")
                            
                            # Save folder ID to user settings
                            user_settings.save_google_drive_folder_id(folder_id)
                            st.success("✅ Folder ID saved!")
                            st.session_state['change_drive_folder'] = False
                            st.rerun()
                        else:
                            st.error("❌ Cannot access folder. Please check the folder ID and permissions.")
                    except Exception as e:
                        st.error(f"❌ Error testing folder access: {str(e)}")
            
            # Instructions for getting folder ID
            with st.expander("📖 How to get a Google Drive Folder ID"):
                st.markdown("""
                1. **Open Google Drive** in your browser
                2. **Navigate to the folder** where you want reports uploaded
                3. **Copy the folder ID** from the URL:
                   - URL format: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
                   - Copy the `FOLDER_ID_HERE` part
                4. **Paste it** in the input field above
                """)
            
            # Instructions for OAuth setup
            with st.expander("🔧 How to set up OAuth"):
                st.markdown("""
                ### Step 1: Create a Google Cloud Project
                1. Go to [Google Cloud Console](https://console.cloud.google.com/)
                2. Create a new project or select existing one
                3. Enable the Google Drive API
                
                ### Step 2: Create OAuth Client
                1. Go to "APIs & Services" > "Credentials"
                2. Click "Create Credentials" > "OAuth client ID"
                3. Application type: "Desktop application"
                4. Name: "Stock Analysis Tool Desktop"
                5. Click "Create"
                6. **Download the JSON file** (important!)
                7. Place it in `config/credentials/client_secret.json`
                """)
            
            # Show OAuth client creation link
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                **Quick Setup:**
                1. Click the button to create OAuth client
                2. Download the JSON file
                3. Place it in `config/credentials/client_secret.json`
                4. Restart the application
                """)
            
            with col2:
                credentials_url = f"https://console.cloud.google.com/apis/credentials?project={project_id}" if project_id else "https://console.cloud.google.com/apis/credentials"
                st.markdown(f"""
                <a href="{credentials_url}" target="_blank">
                    <button style="background-color: #fbbc04; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                        🔑 Create OAuth Client
                    </button>
                </a>
                """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"❌ Error in cloud Google Drive setup: {str(e)}")
        st.exception(e)

def main():
    """Main function to render the Streamlit application."""
    try:
        # Set page configuration
        st.set_page_config(
            page_title="Stock Analysis Tool",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize user settings manager
        user_settings = UserSettingsManager()
        
        # Load sidebar configuration from persistent storage
        config = user_settings.load_sidebar_config()
        
        # Store config in session state for use by other components
        st.session_state['config'] = config
        
        # OAuth callback is handled inside auth.render_auth_gate()
        
        # Authentication gate
        if ENABLE_AUTHENTICATION:
            if not render_auth_gate():
                return  # Stop execution if not authenticated
        
        # Render the sidebar (this will also save any changes back to persistent storage)
        config = render_sidebar()
        
        # Main content
        st.title("📈 Stock Analysis Tool")
        st.markdown("---")
        
        # Navigation tabs (re-added Report History)
        if ENABLE_AUTHENTICATION:
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📊 Single Stock Analysis", 
                "📋 Mass Analysis", 
                "☁️ Google Drive Setup", 
                "🗂 Report History",
                "👤 Profile",
                "👨‍💼 Admin"
            ])
        else:
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Single Stock Analysis", "📋 Mass Analysis", "☁️ Google Drive Setup", "🗂 Report History"])
        
        with tab1:
            st.header("📊 Single Stock Analysis")
            
            # Stock symbol input
            symbol = st.text_input(
                "Enter Stock Symbol:",
                placeholder="e.g., AAPL, MSFT, GOOGL",
                key="single_stock_symbol"
            ).upper().strip()
            
            if symbol:
                # Display analysis interface for the entered symbol
                display_single_stock_analysis(symbol, config.get('days_back', 365))
            else:
                st.info("Please enter a stock symbol to begin analysis.")
        
        with tab2:
            # Header shown inside component to avoid duplicates
            display_mass_stock_analysis()
        
        with tab3:
            # Header shown inside component to avoid duplicates
            render_google_drive_setup()

        with tab4:
            # Report history/manager page
            render_report_manager()
        
        # Authentication tabs (only show if authentication is enabled)
        if ENABLE_AUTHENTICATION:
            with tab5:
                # User profile page
                render_user_profile()
            
            with tab6:
                # Admin panel
                render_admin_panel()
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)

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