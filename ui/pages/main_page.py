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
from config.settings import (
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
    """Render Google Drive setup page with guided OAuth setup."""
    st.header("🔗 Google Drive Setup")
    
    if not ENABLE_GOOGLE_DRIVE:
        st.info("Google Drive integration is disabled in settings. Enable ENABLE_GOOGLE_DRIVE in config.")
        return

    # Check for existing shared OAuth client
    shared_client_path = Path("config/credentials/client_secret.json")
    shared_sa_path = Path("config/credentials/service_account.json")
    
    # Check for existing configuration
    mgr = GoogleDriveManager()
    is_configured = mgr.is_configured()
    saved_folder_id = mgr.get_saved_folder_id()
    saved_date_folders = mgr.get_saved_date_folder_preference()
    
    if is_configured:
        st.success("✅ Google Drive is already configured!")
        st.info(f"""
        **Current Settings:**
        - 📁 Folder ID: `{saved_folder_id or 'Not set'}`
        - 📅 Date folders: {'Enabled' if saved_date_folders else 'Disabled'}
        - 🔐 Authentication: Active
        """)
        
        # Option to change settings
        if st.expander("⚙️ Change Settings"):
            render_google_drive_settings_change(mgr)
        
        # Option to disconnect
        if st.button("🔌 Disconnect Google Drive", key="disconnect_gdrive"):
            try:
                # Clear saved settings
                mgr.settings.settings = {}
                mgr.settings._save_settings()
                
                # Remove token file
                token_file = Path("config/credentials/gdrive_token.json")
                if token_file.exists():
                    token_file.unlink()
                
                st.success("✅ Google Drive disconnected successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error disconnecting: {str(e)}")
        
        return
    
    if shared_client_path.exists():
        st.success("✅ Shared OAuth client found! Users can connect directly.")
        st.info("""
        **For Users:** 
        - Simply click "Connect Google Drive" below
        - Browser will open for Google sign-in (first time only)
        - Authorize once, then reports upload automatically
        """)
        
        # Improved folder selection with better instructions
        st.subheader("📁 Select Upload Folder (Optional)")
        
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
            value=saved_folder_id or "",
            placeholder="e.g., 1ABC123def456ghi789jkl",
            help="Leave empty to upload to Drive root, or enter a specific folder ID",
            key="gdrive_folder_id_shared"
        )
        
        # Add folder testing feature
        if folder_id:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🧪 Test Folder Access", key="test_folder_shared"):
                    with st.spinner("Testing folder access..."):
                        try:
                            mgr = GoogleDriveManager(credentials_path=str(shared_client_path))
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
                        except Exception as e:
                            st.error(f"❌ Error testing folder: {str(e)}")
            
            with col2:
                if st.button("ℹ️ Get Folder Info", key="get_folder_info_shared"):
                    with st.spinner("Getting folder information..."):
                        try:
                            mgr = GoogleDriveManager(credentials_path=str(shared_client_path))
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
                        except Exception as e:
                            st.error(f"❌ Error getting folder info: {str(e)}")
        
        # Date folder option
        create_date_folders = st.checkbox(
            "📅 Create date-based subfolders",
            value=saved_date_folders,
            help="Automatically create date folders (e.g., '2025-08-08') in the selected folder for better organization",
            key="gdrive_create_date_folders_shared"
        )
        
        if folder_id:
            st.info(f"📁 Reports will be uploaded to folder: `{folder_id}`")
            if create_date_folders:
                st.info("📅 Date-based subfolders will be created automatically")
        else:
            st.info("📁 Reports will be uploaded to your Google Drive root")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔗 Connect Google Drive", key="connect_shared_oauth"):
                with st.spinner("Connecting to Google Drive..."):
                    try:
                        # Set environment variables
                        os.environ["GOOGLE_DRIVE_USE_SERVICE_ACCOUNT"] = "false"
                        os.environ["GOOGLE_DRIVE_CREDENTIALS_FILE"] = str(shared_client_path)
                        if folder_id:
                            os.environ["GOOGLE_DRIVE_FOLDER_ID"] = folder_id
                        
                        # Test connection
                        mgr = GoogleDriveManager(credentials_path=str(shared_client_path))
                        if mgr.is_authenticated():
                            # Save settings
                            if folder_id:
                                mgr.save_folder_id(folder_id)
                            mgr.save_date_folder_preference(create_date_folders)
                            
                            st.success("✅ Successfully connected to Google Drive!")
                            st.info("✅ Settings saved! You won't need to configure again.")
                            
                            if folder_id:
                                st.info("Testing upload to your Drive folder...")
                                try:
                                    # Create a test file
                                    tmp_marker = Path(".gdrive_test.txt")
                                    tmp_marker.write_text("Drive connection test - Stock Analysis Tool")
                                    file_id = mgr.upload_file(str(tmp_marker), folder_id=folder_id, new_filename=".gdrive_test.txt")
                                    tmp_marker.unlink(missing_ok=True)
                                    
                                    if file_id:
                                        st.success(f"✅ Test upload successful! File ID: {file_id}")
                                        if create_date_folders:
                                            st.info(f"📁 Reports will be uploaded to date-based folders in your selected folder")
                                        else:
                                            st.info(f"📁 Reports will be uploaded to your selected folder")
                                    else:
                                        st.warning("⚠️ Connected, but test upload didn't return a file ID.")
                                except Exception as e:
                                    st.warning(f"⚠️ Connected, but test upload failed: {str(e)}")
                            else:
                                st.info("ℹ️ Connected! Uploads will go to your Drive root (or set a folder ID).")
                        else:
                            st.error("❌ Failed to connect. Please check your OAuth client JSON and try again.")
                            
                    except Exception as e:
                        st.error(f"❌ Error setting up Google Drive: {str(e)}")
        
        with col2:
            if st.button("📋 Copy Setup Commands", key="copy_shared_commands"):
                commands = f"""
# Environment variables for shared Google Drive OAuth
GOOGLE_DRIVE_USE_SERVICE_ACCOUNT=false
GOOGLE_DRIVE_CREDENTIALS_FILE=config/credentials/client_secret.json
GOOGLE_DRIVE_FOLDER_ID={folder_id or '<your_folder_id>'}
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.file
                """.strip()
                st.code(commands, language="bash")
                st.info("Copy these commands to your .env file or environment")
        
        st.markdown("---")
        st.subheader("🔧 Admin Setup (One-time)")
        st.info("""
        **For Administrators:**
        - The shared OAuth client is already configured
        - Users can connect directly without any setup
        - To update the client or add new features, see the setup steps below
        """)
        
        if st.expander("Show Admin Setup Steps"):
            render_admin_setup_steps()
    
    elif shared_sa_path.exists():
        st.success("✅ Shared Service Account found! Users can connect directly.")
        st.info("""
        **For Users:** 
        - Simply click "Connect Google Drive" below
        - No sign-in required (headless authentication)
        - Reports upload to the shared Drive folder
        """)
        
        # Improved folder selection with better instructions
        st.subheader("📁 Select Upload Folder (Optional)")
        
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
            value=saved_folder_id or "",
            placeholder="e.g., 1ABC123def456ghi789jkl",
            help="Leave empty to upload to Drive root, or enter a specific folder ID",
            key="gdrive_folder_id_shared_sa"
        )
        
        # Add folder testing feature
        if folder_id:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🧪 Test Folder Access", key="test_folder_shared_sa"):
                    with st.spinner("Testing folder access..."):
                        try:
                            mgr = GoogleDriveManager(credentials_path=str(shared_sa_path))
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
                        except Exception as e:
                            st.error(f"❌ Error testing folder: {str(e)}")
            
            with col2:
                if st.button("ℹ️ Get Folder Info", key="get_folder_info_shared_sa"):
                    with st.spinner("Getting folder information..."):
                        try:
                            mgr = GoogleDriveManager(credentials_path=str(shared_sa_path))
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
                        except Exception as e:
                            st.error(f"❌ Error getting folder info: {str(e)}")
        
        # Date folder option
        create_date_folders = st.checkbox(
            "📅 Create date-based subfolders",
            value=saved_date_folders,
            help="Automatically create date folders (e.g., '2025-08-08') in the selected folder for better organization",
            key="gdrive_create_date_folders_shared_sa"
        )
        
        if folder_id:
            st.info(f"📁 Reports will be uploaded to folder: `{folder_id}`")
            if create_date_folders:
                st.info("📅 Date-based subfolders will be created automatically")
        else:
            st.info("📁 Reports will be uploaded to your Google Drive root")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔗 Connect Google Drive", key="connect_shared_sa"):
                with st.spinner("Connecting to Google Drive..."):
                    try:
                        # Set environment variables
                        os.environ["GOOGLE_DRIVE_USE_SERVICE_ACCOUNT"] = "true"
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(shared_sa_path)
                        if folder_id:
                            os.environ["GOOGLE_DRIVE_FOLDER_ID"] = folder_id
                        
                        # Test connection
                        mgr = GoogleDriveManager(credentials_path=str(shared_sa_path))
                        if mgr.is_authenticated():
                            # Save settings
                            if folder_id:
                                mgr.save_folder_id(folder_id)
                            mgr.save_date_folder_preference(create_date_folders)
                            
                            st.success("✅ Successfully connected to Google Drive!")
                            st.info("✅ Settings saved! You won't need to configure again.")
                            
                            if folder_id:
                                st.info("Testing upload to your Drive folder...")
                                try:
                                    # Create a test file
                                    tmp_marker = Path(".gdrive_test.txt")
                                    tmp_marker.write_text("Drive connection test - Stock Analysis Tool")
                                    file_id = mgr.upload_file(str(tmp_marker), folder_id=folder_id, new_filename=".gdrive_test.txt")
                                    tmp_marker.unlink(missing_ok=True)
                                    
                                    if file_id:
                                        st.success(f"✅ Test upload successful! File ID: {file_id}")
                                        if create_date_folders:
                                            st.info(f"📁 Reports will be uploaded to date-based folders in your selected folder")
                                        else:
                                            st.info(f"📁 Reports will be uploaded to your selected folder")
                                    else:
                                        st.warning("⚠️ Connected, but test upload didn't return a file ID.")
                                except Exception as e:
                                    st.warning(f"⚠️ Connected, but test upload failed: {str(e)}")
                            else:
                                st.info("ℹ️ Connected! Uploads will go to your Drive root (or set a folder ID).")
                        else:
                            st.error("❌ Failed to connect. Please check your Service Account JSON and folder sharing.")
                            
                    except Exception as e:
                        st.error(f"❌ Error setting up Google Drive: {str(e)}")
        
        with col2:
            if st.button("📋 Copy Setup Commands", key="copy_shared_sa_commands"):
                commands = f"""
# Environment variables for shared Google Drive Service Account
GOOGLE_DRIVE_USE_SERVICE_ACCOUNT=true
GOOGLE_APPLICATION_CREDENTIALS=config/credentials/service_account.json
GOOGLE_DRIVE_FOLDER_ID={folder_id or '<your_folder_id>'}
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.file
                """.strip()
                st.code(commands, language="bash")
                st.info("Copy these commands to your .env file or environment")
    
    else:
        st.info("""
        **No shared credentials found.** 
        
        **For Administrators:** 
        - Set up shared OAuth client for all users
        - Follow the admin setup steps below
        - Place `client_secret.json` in `config/credentials/` folder
        - Users can then connect with one click
        
        **For End Users:**
        - Contact your administrator to set up Google Drive integration
        - Once configured, you'll see a simple "Connect" button here
        """)
        
        st.subheader("🔧 Admin Setup (One-time)")
        st.info("""
        **Administrators need to:**
        1. Create a Google Cloud project
        2. Enable Google Drive API
        3. Configure OAuth consent screen
        4. Create OAuth client credentials
        5. Download and place `client_secret.json` in `config/credentials/` folder
        """)
        
        if st.expander("Show Admin Setup Steps"):
            render_admin_setup_steps()

def render_google_drive_settings_change(mgr: GoogleDriveManager):
    """Render interface to change Google Drive settings."""
    st.subheader("Change Google Drive Settings")
    
    current_folder_id = mgr.get_saved_folder_id()
    current_date_folders = mgr.get_saved_date_folder_preference()
    
    # Improved folder selection with better instructions
    st.markdown("**📁 Select Upload Folder**")
    
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
    
    new_folder_id = st.text_input(
        "📁 Google Drive Folder ID:",
        value=current_folder_id or "",
        placeholder="e.g., 1ABC123def456ghi789jkl",
        help="Leave empty to upload to Drive root, or enter a specific folder ID",
        key="change_gdrive_folder_id"
    )
    
    # Add folder testing feature
    if new_folder_id:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🧪 Test Folder Access", key="test_folder_change"):
                with st.spinner("Testing folder access..."):
                    try:
                        if mgr.is_authenticated():
                            test_result = mgr.test_folder_access(new_folder_id)
                            
                            if test_result['accessible']:
                                st.success(f"✅ Folder accessible: '{test_result['title']}'")
                                st.info(f"📁 Folder ID: `{new_folder_id}`")
                                st.info(f"🔐 Permissions: {test_result['permissions']}")
                            elif test_result['exists'] and test_result['is_folder']:
                                st.warning(f"⚠️ Folder exists but limited access: '{test_result['title']}'")
                                st.info(f"📁 Folder ID: `{new_folder_id}`")
                                st.info(f"🔐 Permissions: {test_result['permissions']}")
                                if test_result['error']:
                                    st.warning(f"⚠️ {test_result['error']}")
                            else:
                                st.error(f"❌ Folder not accessible: {test_result['error']}")
                                st.info(f"📁 Folder ID: `{new_folder_id}`")
                        else:
                            st.error("❌ Google Drive not authenticated")
                    except Exception as e:
                        st.error(f"❌ Error testing folder: {str(e)}")
        
        with col2:
            if st.button("ℹ️ Get Folder Info", key="get_folder_info_change"):
                with st.spinner("Getting folder information..."):
                    try:
                        if mgr.is_authenticated():
                            folder_info = mgr.get_folder_info(new_folder_id)
                            if folder_info:
                                st.success(f"✅ Folder found: '{folder_info['title']}'")
                                st.info(f"📁 Created: {folder_info.get('createdDate', 'Unknown')}")
                                st.info(f"📁 Modified: {folder_info.get('modifiedDate', 'Unknown')}")
                                st.info(f"📁 Type: {folder_info['mimeType']}")
                            else:
                                st.error("❌ Could not retrieve folder information")
                        else:
                            st.error("❌ Google Drive not authenticated")
                    except Exception as e:
                        st.error(f"❌ Error getting folder info: {str(e)}")
    
    new_date_folders = st.checkbox(
        "📅 Create date-based subfolders",
        value=current_date_folders,
        help="Automatically create date folders (e.g., '2025-08-08') in the selected folder for better organization",
        key="change_gdrive_date_folders"
    )
    
    if new_folder_id:
        st.info(f"📁 Reports will be uploaded to folder: `{new_folder_id}`")
        if new_date_folders:
            st.info("📅 Date-based subfolders will be created automatically")
    else:
        st.info("📁 Reports will be uploaded to your Google Drive root")
    
    if st.button("💾 Save Changes", key="save_gdrive_changes"):
        try:
            # Save new settings
            if new_folder_id:
                mgr.save_folder_id(new_folder_id)
            else:
                mgr.settings.set_setting('folder_id', None)
            
            mgr.save_date_folder_preference(new_date_folders)
            
            st.success("✅ Settings updated successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error saving settings: {str(e)}")

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
            [NAV_SINGLE_ANALYSIS, NAV_MASS_ANALYSIS, NAV_REPORT_HISTORY, "🔗 Google Drive Setup"],
            key="navigation_radio"
        )
        
        # Initialize services
        report_service = ReportService(days_back=config['days_back'])
        
        # Main content area
        if page == NAV_SINGLE_ANALYSIS:
            st.header(HEADER_SINGLE_STOCK_ANALYSIS)
            
            # Stock symbol input
            symbol = st.text_input(
                "Enter Stock Symbol:",
                placeholder=PLACEHOLDER_STOCK_SYMBOL,
                key="single_stock_symbol"
            ).upper().strip()
            
            if symbol:
                # Get days_back from config
                days_back = config.get('days_back', 365)
                
                # Display analysis interface for the entered symbol
                display_single_stock_analysis(symbol, days_back)
            else:
                st.info("Please enter a stock symbol to begin analysis.")
            
        elif page == NAV_MASS_ANALYSIS:
            display_mass_stock_analysis()
            
        elif page == NAV_REPORT_HISTORY:
            render_report_manager()
            
        elif page == "🔗 Google Drive Setup":
            render_google_drive_setup()
        
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