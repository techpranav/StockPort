"""
Cloud Google Drive Setup Component

This component provides a user-friendly interface for setting up Google Drive
integration in Streamlit Cloud, where each user configures their own settings.
"""

import streamlit as st
import json
from pathlib import Path
from typing import Optional, Dict, Any
from utils.cloud_google_drive_manager import CloudGoogleDriveManager
from utils.user_settings_manager import UserSettingsManager
from utils.debug_utils import DebugUtils

def render_cloud_google_drive_setup():
    """Render the cloud Google Drive setup interface."""
    st.header("☁️ Google Drive Setup")
    
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
    
    # OAuth credentials input
    st.subheader("📥 OAuth Credentials")
    
    oauth_json = st.text_area(
        "Paste your OAuth client JSON here:",
        height=200,
        placeholder='{"web": {"client_id": "...", "client_secret": "..."}}',
        help="Copy the entire contents of your OAuth client JSON file"
    )
    
    if oauth_json:
        try:
            # Validate JSON
            credentials = json.loads(oauth_json)
            
            # Basic validation
            if 'installed' in credentials or 'web' in credentials:
                st.success("✅ Valid OAuth credentials format detected")
                
                # Store credentials
                user_settings.set_google_drive_oauth_credentials(credentials)
                
                # Test connection
                if st.button("🧪 Test Connection", key="test_oauth_connection"):
                    test_oauth_connection(credentials)
                
            else:
                st.error("❌ Invalid OAuth credentials format. Expected 'installed' or 'web' section.")
                
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON format. Please check your OAuth credentials.")
        except Exception as e:
            st.error(f"❌ Error processing credentials: {str(e)}")
    
    # Folder configuration
    render_folder_configuration(user_settings)

def render_manual_setup(user_settings: UserSettingsManager):
    """Render manual folder ID setup interface."""
    st.subheader("📁 Manual Folder Setup")
    
    st.info("""
    **ℹ️ Manual Setup:**
    This option only stores your Google Drive folder ID.
    You'll need to manually upload reports to Google Drive.
    """)
    
    render_folder_configuration(user_settings)

def render_folder_configuration(user_settings: UserSettingsManager):
    """Render folder configuration interface."""
    st.subheader("📁 Upload Folder Configuration")
    
    # Folder ID input
    folder_id = st.text_input(
        "Google Drive Folder ID (Optional):",
        value=user_settings.get_google_drive_folder_id() or "",
        placeholder="e.g., 1ABC123def456ghi789jkl",
        help="Leave empty to upload to Drive root, or enter a specific folder ID"
    )
    
    if folder_id:
        # Folder testing
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
        help="Automatically create date folders (e.g., '2025-08-08') for better organization"
    )
    
    # Save configuration
    if st.button("💾 Save Configuration", key="save_gdrive_config"):
        save_google_drive_config(user_settings, folder_id, create_date_folders)

def test_oauth_connection(credentials: Dict[str, Any]):
    """Test OAuth connection with provided credentials."""
    with st.spinner("Testing OAuth connection..."):
        try:
            # Create temporary manager for testing
            temp_manager = CloudGoogleDriveManager()
            
            # Test authentication
            if temp_manager.is_authenticated():
                st.success("✅ OAuth connection successful!")
                st.info("You can now configure your upload folder.")
            else:
                st.error("❌ OAuth connection failed. Please check your credentials.")
                
        except Exception as e:
            st.error(f"❌ Connection test failed: {str(e)}")

def test_folder_access(folder_id: str):
    """Test access to a Google Drive folder."""
    with st.spinner("Testing folder access..."):
        try:
            manager = CloudGoogleDriveManager()
            
            if manager.is_authenticated():
                test_result = manager.test_folder_access(folder_id)
                
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
                st.error("❌ Google Drive not authenticated. Please complete OAuth setup first.")
                
        except Exception as e:
            st.error(f"❌ Error testing folder: {str(e)}")

def get_folder_info(folder_id: str):
    """Get information about a Google Drive folder."""
    with st.spinner("Getting folder information..."):
        try:
            manager = CloudGoogleDriveManager()
            
            if manager.is_authenticated():
                folder_info = manager.get_folder_info(folder_id)
                if folder_info:
                    st.success(f"✅ Folder found: '{folder_info['title']}'")
                    st.info(f"📁 Created: {folder_info.get('createdDate', 'Unknown')}")
                    st.info(f"📁 Modified: {folder_info.get('modifiedDate', 'Unknown')}")
                    st.info(f"📁 Type: {folder_info['mimeType']}")
                else:
                    st.error("❌ Could not retrieve folder information")
            else:
                st.error("❌ Google Drive not authenticated. Please complete OAuth setup first.")
                
        except Exception as e:
            st.error(f"❌ Error getting folder info: {str(e)}")

def save_google_drive_config(user_settings: UserSettingsManager, folder_id: str, create_date_folders: bool):
    """Save Google Drive configuration."""
    try:
        # Save folder ID if provided
        if folder_id:
            user_settings.set_google_drive_folder_id(folder_id)
        
        # Save date folder preference
        user_settings.set_google_drive_date_folders(create_date_folders)
        
        # Mark as configured
        user_settings.set_google_drive_configured(True)
        
        st.success("✅ Google Drive configuration saved successfully!")
        
        # Show summary
        st.info(f"""
        **📋 Configuration Summary:**
        - 📁 Upload Folder: `{folder_id or 'Drive Root'}`
        - 📅 Date Folders: {'Enabled' if create_date_folders else 'Disabled'}
        - 🔐 Status: Configured
        
        **📤 Next Steps:**
        - Reports will now automatically upload to Google Drive
        - You can change settings anytime from the sidebar
        """)
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error saving configuration: {str(e)}")

def render_configured_status(user_settings: UserSettingsManager):
    """Render status for already configured Google Drive."""
    st.success("✅ Google Drive is already configured!")
    
    folder_id = user_settings.get_google_drive_folder_id()
    date_folders = user_settings.get_google_drive_date_folders()
    
    st.info(f"""
    **📋 Current Settings:**
    - 📁 Upload Folder: `{folder_id or 'Drive Root'}`
    - 📅 Date Folders: {'Enabled' if date_folders else 'Disabled'}
    - 🔐 Authentication: Active
    """)
    
    # Options to modify
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⚙️ Modify Settings", key="modify_gdrive_settings"):
            user_settings.set_google_drive_configured(False)
            st.rerun()
    
    with col2:
        if st.button("🔌 Disconnect", key="disconnect_gdrive"):
            if user_settings.clear_google_drive_settings():
                st.success("✅ Google Drive disconnected successfully!")
                st.rerun()
            else:
                st.error("❌ Error disconnecting Google Drive")

def render_google_drive_help():
    """Render help information for Google Drive setup."""
    with st.expander("❓ Need help with Google Drive setup?"):
        st.markdown("""
        **🔗 Google Drive Setup Guide:**
        
        ### **Method 1: OAuth Setup (Recommended)**
        1. **Create Google Cloud Project**
           - Go to [Google Cloud Console](https://console.cloud.google.com/)
           - Create new project or select existing one
        
        2. **Enable Google Drive API**
           - Go to "APIs & Services" > "Library"
           - Search for "Google Drive API"
           - Click "Enable"
        
        3. **Create OAuth Credentials**
           - Go to "APIs & Services" > "Credentials"
           - Click "Create Credentials" > "OAuth 2.0 Client IDs"
           - Choose "Desktop application"
           - Download the JSON file
        
        4. **Paste Credentials**
           - Copy the entire contents of the JSON file
           - Paste it in the OAuth credentials field above
        
        ### **Method 2: Manual Folder ID**
        1. **Find Your Folder ID**
           - Go to [Google Drive](https://drive.google.com)
           - Navigate to your target folder
           - Copy the folder ID from the URL:
           ```
           https://drive.google.com/drive/folders/FOLDER_ID_HERE
           ```
        
        2. **Enter Folder ID**
           - Paste the folder ID in the field above
           - This will store your preference for future use
        
        ### **📁 Folder Organization Options**
        - **Date Folders**: Automatically create date-based subfolders
        - **Symbol Folders**: Create separate folders for each stock symbol
        - **Combined**: Use both date and symbol folders for maximum organization
        
        **💡 Pro Tips:**
        - Use OAuth setup for automatic uploads
        - Test folder access before saving configuration
        - You can change settings anytime from the sidebar
        """)
