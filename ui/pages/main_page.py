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
    ENABLE_GOOGLE_DRIVE
)

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
                st.info("🔄 Falling back to local setup...")
                # Fall back to local setup if cloud component fails
                is_cloud = False
            else:
                return

        # Local environment - use unified user-specific approach
        user_settings = UserSettingsManager()
        
        # Check if already configured
        if user_settings.is_google_drive_configured():
            render_configured_status(user_settings)
            return
        
        # Show setup options
        st.info("""
        **🔐 Google Drive Integration**
        
        Connect your Google Drive to automatically upload stock analysis reports.
        Each user configures their own Google Drive connection.
        
        **📋 What you'll get:**
        - ✅ Automatic report uploads to your Google Drive
        - ✅ Organized folder structure (optional date-based subfolders)
        - ✅ Secure OAuth authentication (no passwords stored)
        - ✅ Per-user settings (works for multiple users)
        """)
        
        # Setup method selection
        setup_method = st.radio(
            "Choose setup method:",
            ["🔑 OAuth Client Setup (Recommended)", "📁 Manual Folder ID Only"],
            help="OAuth setup allows automatic uploads, manual setup just stores your folder ID"
        )
        
        if setup_method == "🔑 OAuth Client Setup (Recommended)":
            render_oauth_setup(user_settings)
        else:
            render_manual_setup(user_settings)
            
    except Exception as e:
        DebugUtils.log_error(e, "Error in Google Drive setup")
        st.error(f"❌ Error loading Google Drive setup: {str(e)}")
        st.info("Please try refreshing the page or contact support if the issue persists.")

def render_oauth_setup(user_settings: UserSettingsManager):
    """Render OAuth client setup interface."""
    st.subheader("🔑 OAuth Client Setup")
    
    st.info("""
    **📋 Prerequisites:**
    1. **Google Cloud Project** with Drive API enabled
    2. **OAuth 2.0 Client ID** (Desktop application type)
    3. **Google account** with Drive access
    
    **🔗 Quick Setup:**
    1. Go to [Google Cloud Console](https://console.cloud.google.com/)
    2. Create a new project or select existing one
    3. Enable Google Drive API
    4. Create OAuth 2.0 credentials (Desktop app)
    5. Download the JSON file
    """)
    
    # Check for existing client_secret.json
    existing_creds_path = "config/credentials/client_secret.json"
    existing_credentials = None
    
    if os.path.exists(existing_creds_path):
        try:
            with open(existing_creds_path, 'r') as f:
                existing_credentials = json.load(f)
            st.success("✅ Found existing OAuth credentials in config/credentials/client_secret.json")
        except Exception as e:
            st.warning(f"⚠️ Found client_secret.json but couldn't read it: {str(e)}")
    
    # OAuth credentials input
    st.subheader("📥 OAuth Credentials")
    
    if existing_credentials:
        st.info("""
        **📋 You have existing credentials:**
        - If you want to use the existing credentials, leave the field below empty
        - If you want to use new credentials, paste them below
        """)
    
    oauth_json = st.text_area(
        "Paste your OAuth client JSON here (optional if you have existing credentials):",
        height=200,
        placeholder='{"installed": {"client_id": "...", "client_secret": "..."}}',
        help="Copy the entire contents of your OAuth client JSON file, or leave empty to use existing credentials"
    )
    
    # Determine which credentials to use
    credentials_to_use = None
    if oauth_json:
        try:
            # Validate JSON
            credentials_to_use = json.loads(oauth_json)
            
            # Basic validation
            if 'installed' in credentials_to_use or 'web' in credentials_to_use:
                st.success("✅ Valid OAuth credentials format detected")
            else:
                st.error("❌ Invalid OAuth credentials format. Expected 'installed' or 'web' section.")
                credentials_to_use = None
                
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON format. Please check your OAuth credentials.")
            credentials_to_use = None
        except Exception as e:
            st.error(f"❌ Error processing credentials: {str(e)}")
            credentials_to_use = None
    elif existing_credentials:
        # Use existing credentials
        credentials_to_use = existing_credentials
        st.success("✅ Using existing OAuth credentials from config/credentials/client_secret.json")
    
    if credentials_to_use:
        # Store credentials
        user_settings.set_google_drive_oauth_credentials(credentials_to_use)
        
        # Test connection
        if st.button("🧪 Test Connection", key="test_oauth_connection"):
            test_oauth_connection(credentials_to_use)
    elif not existing_credentials:
        st.warning("⚠️ Please provide OAuth credentials or ensure client_secret.json exists in config/credentials/")
    
    # Folder configuration
    render_folder_configuration(user_settings)
    
    # Admin setup help
    st.markdown("---")
    st.subheader("🔧 Need Help Setting Up OAuth?")
    st.info("""
    **For Administrators or Advanced Users:**
    - If you need help creating OAuth credentials
    - If you want to set up shared credentials for your organization
    - If you encounter any issues with the setup process
    """)
    
    if st.expander("📋 Show Admin Setup Steps"):
        render_admin_setup_steps()

def render_manual_setup(user_settings: UserSettingsManager):
    """Render manual folder ID setup interface."""
    st.subheader("📁 Manual Folder ID Setup")
    
    st.info("""
    **📋 Manual Setup:**
    - Enter your Google Drive folder ID manually
    - Reports will be uploaded to the specified folder
    - No automatic authentication (you'll need to handle uploads manually)
    """)
    
    # Folder configuration
    render_folder_configuration(user_settings)

def render_folder_configuration(user_settings: UserSettingsManager):
    """Render folder configuration interface."""
    st.subheader("📁 Folder Configuration")
    
    # Add a collapsible folder picker helper
    with st.expander("🔍 Need help finding your folder ID? Click here for step-by-step guide"):
        st.markdown("""
        **📋 Step-by-Step Folder ID Finder:**
        
        1. **🌐 Open Google Drive**
           - Go to [drive.google.com](https://drive.google.com) in your browser
           - Sign in with your Google account
        
        2. **📁 Navigate to your target folder**
           - Browse to the folder where you want reports uploaded
           - You can create a new folder if needed
        
        3. **🔗 Copy the folder ID from the URL**
           - Look at your browser's address bar
           - The URL will look like this:
           ```
           https://drive.google.com/drive/folders/1ABC123def456ghi789jkl
           ```
           - The long string after `/folders/` is your folder ID
        
        4. **📋 Copy and paste**
           - Select the folder ID (e.g., `1ABC123def456ghi789jkl`)
           - Copy it (Ctrl+C or Cmd+C)
           - Paste it in the input field below
        
        **💡 Pro Tips:**
        - You can also right-click on a folder and select "Get link" to get the URL
        - The folder ID is always the long string of letters and numbers
        - Leave the field empty if you want reports in your Drive root
        """)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **How to find your folder ID:**
        1. Go to [Google Drive](https://drive.google.com) in your browser
        2. Navigate to the folder where you want reports uploaded
        3. Copy the folder ID from the URL:
           ```
           https://drive.google.com/drive/folders/FOLDER_ID_HERE
           ```
        4. Paste it below
        """)
    
    with col2:
        st.markdown("""
        **Example:**
        - URL: `https://drive.google.com/drive/folders/1ABC123def456ghi789jkl`
        - Folder ID: `1ABC123def456ghi789jkl`
        """)
    
    folder_id = st.text_input(
        "📁 Google Drive Folder ID:",
        value=user_settings.get_google_drive_folder_id() or "",
        placeholder="e.g., 1ABC123def456ghi789jkl",
        help="Leave empty to upload to Drive root, or enter a specific folder ID",
        key="gdrive_folder_id"
    )
    
    # Add folder testing feature
    if folder_id:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🧪 Test Folder Access", key="test_folder_access"):
                test_folder_access(folder_id)
        
        with col2:
            if st.button("ℹ️ Get Folder Info", key="get_folder_info"):
                get_folder_info(folder_id)
    
    # Date folder option
    create_date_folders = st.checkbox(
        "📅 Create date-based subfolders",
        value=user_settings.get_google_drive_date_folders(),
        help="Automatically create date folders (e.g., '2025-08-08') in the selected folder for better organization",
        key="gdrive_create_date_folders"
    )
    
    if folder_id:
        st.info(f"📁 Reports will be uploaded to folder: `{folder_id}`")
        if create_date_folders:
            st.info("📅 Date-based subfolders will be created automatically")
    else:
        st.info("📁 Reports will be uploaded to your Google Drive root")
    
    # Save configuration
    if st.button("💾 Save Configuration", key="save_gdrive_config"):
        save_google_drive_config(user_settings, folder_id, create_date_folders)

def test_oauth_connection(credentials: Dict[str, Any]):
    """Test OAuth connection with provided credentials."""
    try:
        # Create temporary credentials file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials, f)
            temp_creds_path = f.name
        
        # Test connection
        mgr = GoogleDriveManager(credentials_path=temp_creds_path)
        if mgr.is_authenticated():
            st.success("✅ OAuth connection successful!")
            st.info("🔐 You can now configure your folder settings below.")
        else:
            st.error("❌ OAuth connection failed. Please check your credentials.")
        
        # Clean up temp file
        import os
        os.unlink(temp_creds_path)
        
    except Exception as e:
        st.error(f"❌ Error testing connection: {str(e)}")

def test_folder_access(folder_id: str):
    """Test access to a specific Google Drive folder."""
    try:
        # Get user's OAuth credentials
        user_settings = UserSettingsManager()
        oauth_credentials = user_settings.get_google_drive_oauth_credentials()
        
        if not oauth_credentials:
            st.error("❌ No OAuth credentials found. Please set up OAuth first.")
            return
        
        # Create temporary credentials file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(oauth_credentials, f)
            temp_creds_path = f.name
        
        try:
            # Test folder access
            mgr = GoogleDriveManager(credentials_path=temp_creds_path)
            if mgr.is_authenticated():
                test_result = mgr.test_folder_access(folder_id)
                
                if test_result['accessible']:
                    st.success(f"✅ Folder accessible: '{test_result['title']}'")
                    st.info(f"📁 Folder ID: `{folder_id}`")
                    st.info(f"🔐 Permissions: {test_result['permissions']}")
                elif test_result['exists'] and test_result['is_folder']:
                    st.warning(f"⚠️ Folder exists but limited access: '{test_result['title']}'")
                    st.info(f"📁 Folder ID: `{folder_id}`")
                    st.info(f"🔐 Permissions: {test_result['permissions']}")
                    if test_result['error']:
                        st.warning(f"⚠️ {test_result['error']}")
                else:
                    st.error(f"❌ Folder not accessible: {test_result['error']}")
                    st.info(f"📁 Folder ID: `{folder_id}`")
            else:
                st.error("❌ Google Drive not authenticated")
        finally:
            # Clean up temp file
            import os
            os.unlink(temp_creds_path)
            
    except Exception as e:
        st.error(f"❌ Error testing folder access: {str(e)}")

def get_folder_info(folder_id: str):
    """Get information about a specific Google Drive folder."""
    try:
        # Get user's OAuth credentials
        user_settings = UserSettingsManager()
        oauth_credentials = user_settings.get_google_drive_oauth_credentials()
        
        if not oauth_credentials:
            st.error("❌ No OAuth credentials found. Please set up OAuth first.")
            return
        
        # Create temporary credentials file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(oauth_credentials, f)
            temp_creds_path = f.name
        
        try:
            # Get folder info
            mgr = GoogleDriveManager(credentials_path=temp_creds_path)
            if mgr.is_authenticated():
                folder_info = mgr.get_folder_info(folder_id)
                if folder_info:
                    st.success(f"✅ Folder found: '{folder_info['title']}'")
                    st.info(f"📁 Created: {folder_info.get('createdDate', 'Unknown')}")
                    st.info(f"📁 Modified: {folder_info.get('modifiedDate', 'Unknown')}")
                    st.info(f"📁 Type: {folder_info['mimeType']}")
                else:
                    st.error("❌ Could not retrieve folder information")
            else:
                st.error("❌ Google Drive not authenticated")
        finally:
            # Clean up temp file
            import os
            os.unlink(temp_creds_path)
            
    except Exception as e:
        st.error(f"❌ Error getting folder info: {str(e)}")

def save_google_drive_config(user_settings: UserSettingsManager, folder_id: str, create_date_folders: bool):
    """Save Google Drive configuration."""
    try:
        # Save folder ID
        if folder_id:
            user_settings.set_google_drive_folder_id(folder_id)
        else:
            user_settings.set_google_drive_folder_id(None)
        
        # Save date folder preference
        user_settings.set_google_drive_date_folders(create_date_folders)
        
        # Mark as configured
        user_settings.set_google_drive_configured(True)
        
        st.success("✅ Google Drive configuration saved successfully!")
        st.info("🔄 Refreshing page to show configured status...")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error saving configuration: {str(e)}")

def render_configured_status(user_settings: UserSettingsManager):
    """Render status for configured Google Drive."""
    st.success("✅ Google Drive is already configured!")
    
    folder_id = user_settings.get_google_drive_folder_id()
    date_folders = user_settings.get_google_drive_date_folders()
    
    st.info(f"""
    **Current Settings:**
    - 📁 Folder ID: `{folder_id or 'Not set (Drive root)'}`
    - 📅 Date folders: {'Enabled' if date_folders else 'Disabled'}
    - 🔐 Authentication: Active
    """)
    
    # Option to change settings
    if st.expander("⚙️ Change Settings"):
        render_folder_configuration(user_settings)
    
    # Option to disconnect
    if st.button("🔌 Disconnect Google Drive", key="disconnect_gdrive"):
        try:
            user_settings.clear_google_drive_settings()
            st.success("✅ Google Drive disconnected successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error disconnecting: {str(e)}")

def render_admin_setup_steps():
    """Render admin setup steps for shared OAuth client."""
    st.subheader("Admin Setup Steps")
    
    # Step 1: Project Setup
    st.markdown("**Step 1: Google Cloud Project Setup**")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Create or select a Google Cloud project:**
        1. Click the link below to open Google Cloud Console in a new tab
        2. Create a new project or select existing one
        3. Note down your Project ID
        """)
    
    with col2:
        st.markdown("""
        <a href="https://console.cloud.google.com/" target="_blank">
            <button style="background-color: #4285f4; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                🚀 Open Google Cloud Console
            </button>
        </a>
        """, unsafe_allow_html=True)
    
    project_id = st.text_input("Enter your Project ID:", key="admin_gcp_project_id")
    
    # Step 2: Enable Drive API
    st.markdown("**Step 2: Enable Google Drive API**")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Enable the Google Drive API:**
        1. Click the link below to go directly to Drive API in a new tab
        2. Click "Enable" if not already enabled
        """)
    
    with col2:
        drive_api_url = f"https://console.cloud.google.com/apis/library/drive.googleapis.com?project={project_id}" if project_id else "https://console.cloud.google.com/apis/library/drive.googleapis.com"
        st.markdown(f"""
        <a href="{drive_api_url}" target="_blank">
            <button style="background-color: #34a853; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                📊 Enable Drive API
            </button>
        </a>
        """, unsafe_allow_html=True)
    
    # Step 3: OAuth Consent Screen
    st.markdown("**Step 3: Configure OAuth Consent Screen**")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Set up OAuth consent screen:**
        1. Click the link below to configure OAuth consent in a new tab
        2. Choose "External" (or "Internal" for Workspace)
        3. Fill in required fields:
           - App name: "Stock Analysis Tool"
           - User support email: your email
           - Developer contact: your email
        4. Add scope: `https://www.googleapis.com/auth/drive.file`
        5. Add your email as test user
        6. **Important:** Click "Publish App" to allow unlimited users
        """)
    
    with col2:
        oauth_consent_url = f"https://console.cloud.google.com/apis/credentials/consent?project={project_id}" if project_id else "https://console.cloud.google.com/apis/credentials/consent"
        st.markdown(f"""
        <a href="{oauth_consent_url}" target="_blank">
            <button style="background-color: #ea4335; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                🔐 Configure OAuth Consent
            </button>
        </a>
        """, unsafe_allow_html=True)
    
    # Step 4: Create OAuth Client
    st.markdown("**Step 4: Create OAuth Client ID**")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Create OAuth client credentials:**
        1. Click the link below to create credentials in a new tab
        2. Choose "OAuth client ID"
        3. Application type: **"Desktop App"**
        4. Name: "Stock Analysis Tool Desktop"
        5. Click "Create"
        6. **Download the JSON file** (important!)
        7. Place it in `config/credentials/client_secret.json`
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

# Individual setup function removed - no longer needed for end users

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
        
        # Render the sidebar (this will also save any changes back to persistent storage)
        config = render_sidebar()
        
        # Main content
        st.title("📈 Stock Analysis Tool")
        st.markdown("---")
        
        # Navigation tabs (re-added Report History)
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