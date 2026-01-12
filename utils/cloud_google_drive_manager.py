"""
Cloud Google Drive Manager for Streamlit Cloud

This module provides Google Drive integration specifically designed for
multi-user environments like Streamlit Cloud, where each user has their
own isolated session and settings.
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

try:
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from pydrive2.auth import ServiceAccountCredentials
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

from utils.user_settings_manager import UserSettingsManager
from utils.debug_utils import DebugUtils

class CloudGoogleDriveManager:
    """
    Google Drive manager for Streamlit Cloud that stores settings per user.
    
    This manager handles OAuth authentication and file operations without
    requiring persistent file storage, making it suitable for cloud deployments.
    """
    
    def __init__(self):
        """Initialize the cloud Google Drive manager."""
        self.user_settings = UserSettingsManager()
        self.drive = None
        self.authenticated = False
        
        if GOOGLE_DRIVE_AVAILABLE:
            self._authenticate()
    
    def _authenticate(self) -> bool:
        """
        Authenticate with Google Drive using user's OAuth credentials.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Check if user has OAuth credentials
            oauth_credentials = self.user_settings.get_google_drive_oauth_credentials()
            if not oauth_credentials:
                return False
            
            # Create temporary credentials file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(oauth_credentials, f)
                temp_creds_path = f.name
            
            try:
                # Set up Google Auth
                gauth = GoogleAuth()
                gauth.LoadClientConfigFile(temp_creds_path)
                
                # Check for existing token
                auth_token = self.user_settings.get_google_drive_auth_token()
                if auth_token:
                    gauth.LoadCredentials(auth_token)
                
                # Authenticate
                if gauth.credentials is None:
                    # First time authentication
                    gauth.LocalWebserverAuth()
                    # Save token for future use
                    self.user_settings.set_google_drive_auth_token(gauth.credentials)
                elif gauth.access_token_expired:
                    # Refresh expired token
                    gauth.Refresh()
                    # Update saved token
                    self.user_settings.set_google_drive_auth_token(gauth.credentials)
                else:
                    # Token is valid
                    gauth.Authorize()
                
                # Create drive instance
                self.drive = GoogleDrive(gauth)
                self.authenticated = True
                
                return True
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_creds_path):
                    os.unlink(temp_creds_path)
                    
        except Exception as e:
            DebugUtils.log_error(e, "Failed to authenticate with Google Drive")
            self.authenticated = False
            return False
    
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated with Google Drive."""
        return self.authenticated and self.drive is not None
    
    def is_configured(self) -> bool:
        """Check if Google Drive is configured for the current user."""
        return self.user_settings.is_google_drive_configured()
    
    def get_saved_folder_id(self) -> Optional[str]:
        """Get the user's saved Google Drive folder ID."""
        return self.user_settings.get_google_drive_folder_id()
    
    def save_folder_id(self, folder_id: str) -> bool:
        """Save the user's Google Drive folder ID."""
        success = self.user_settings.set_google_drive_folder_id(folder_id)
        if success:
            self.user_settings.set_google_drive_configured(True)
        return success
    
    def get_saved_date_folder_preference(self) -> bool:
        """Get the user's date folder preference."""
        return self.user_settings.get_google_drive_date_folders()
    
    def save_date_folder_preference(self, create_date_folders: bool) -> bool:
        """Save the user's date folder preference."""
        return self.user_settings.set_google_drive_date_folders(create_date_folders)
    
    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
        """
        Create a folder in Google Drive.
        
        Args:
            folder_name: Name of the folder to create
            parent_folder_id: ID of the parent folder (optional)
            
        Returns:
            str: Folder ID if successful, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        try:
            folder_metadata = {
                'title': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [{'id': parent_folder_id}]
            
            folder = self.drive.CreateFile(folder_metadata)
            folder.Upload()
            
            return folder['id']
            
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to create folder: {folder_name}")
            return None
    
    def create_date_folder(self, base_folder_id: Optional[str] = None, 
                          date_format: str = "%Y-%m-%d") -> Optional[str]:
        """
        Create a date-based folder in Google Drive.
        
        Args:
            base_folder_id: ID of the base folder (optional)
            date_format: Format for the date folder name
            
        Returns:
            str: Date folder ID if successful, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        try:
            # Create date folder name
            date_str = datetime.now().strftime(date_format)
            folder_name = f"Stock Analysis - {date_str}"
            
            # Create the folder
            folder_id = self.create_folder(folder_name, base_folder_id)
            
            if folder_id:
                st.info(f"📁 Created date folder: {folder_name}")
            
            return folder_id
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to create date folder")
            return None
    
    def upload_file(self, file_path: str, folder_id: Optional[str] = None,
                   new_filename: Optional[str] = None, create_date_folder: bool = False,
                   symbol: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Google Drive.
        
        Args:
            file_path: Path to the file to upload
            folder_id: ID of the target folder (optional)
            new_filename: New name for the file (optional)
            create_date_folder: Whether to create a date-based subfolder
            symbol: Stock symbol for organization (optional)
            
        Returns:
            str: File ID if successful, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        try:
            # Determine target folder
            target_folder_id = folder_id or self.get_saved_folder_id()
            
            # Create date folder if requested
            if create_date_folder and target_folder_id:
                date_folder_id = self.create_date_folder(target_folder_id)
                if date_folder_id:
                    target_folder_id = date_folder_id
            
            # Create symbol folder if specified
            if symbol and target_folder_id:
                symbol_folder_id = self.create_folder(symbol, target_folder_id)
                if symbol_folder_id:
                    target_folder_id = symbol_folder_id
            
            # Prepare file metadata
            file_metadata = {}
            if target_folder_id:
                file_metadata['parents'] = [{'id': target_folder_id}]
            
            if new_filename:
                file_metadata['title'] = new_filename
            
            # Upload the file
            file = self.drive.CreateFile(file_metadata)
            file.SetContentFile(file_path)
            file.Upload()
            
            return file['id']
            
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to upload file: {file_path}")
            return None
    
    def test_folder_access(self, folder_id: str) -> Dict[str, Any]:
        """
        Test access to a Google Drive folder.
        
        Args:
            folder_id: ID of the folder to test
            
        Returns:
            Dict containing access test results
        """
        if not self.is_authenticated():
            return {
                'accessible': False,
                'exists': False,
                'is_folder': False,
                'error': 'Not authenticated with Google Drive'
            }
        
        try:
            # Try to get folder information
            folder = self.drive.CreateFile({'id': folder_id})
            folder.FetchMetadata()
            
            # Check if it's actually a folder
            is_folder = folder['mimeType'] == 'application/vnd.google-apps.folder'
            
            if is_folder:
                return {
                    'accessible': True,
                    'exists': True,
                    'is_folder': True,
                    'title': folder['title'],
                    'permissions': 'Read/Write',
                    'error': None
                }
            else:
                return {
                    'accessible': False,
                    'exists': True,
                    'is_folder': False,
                    'title': folder['title'],
                    'permissions': 'Unknown',
                    'error': 'The ID points to a file, not a folder'
                }
                
        except Exception as e:
            error_msg = str(e)
            if 'File not found' in error_msg:
                return {
                    'accessible': False,
                    'exists': False,
                    'is_folder': False,
                    'error': 'Folder not found or access denied'
                }
            else:
                return {
                    'accessible': False,
                    'exists': False,
                    'is_folder': False,
                    'error': f'Error accessing folder: {error_msg}'
                }
    
    def get_folder_info(self, folder_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a Google Drive folder.
        
        Args:
            folder_id: ID of the folder
            
        Returns:
            Dict containing folder information or None if failed
        """
        if not self.is_authenticated():
            return None
        
        try:
            folder = self.drive.CreateFile({'id': folder_id})
            folder.FetchMetadata()
            
            return {
                'id': folder['id'],
                'title': folder['title'],
                'mimeType': folder['mimeType'],
                'createdDate': folder.get('createdDate'),
                'modifiedDate': folder.get('modifiedDate'),
                'size': folder.get('fileSize')
            }
            
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to get folder info: {folder_id}")
            return None
    
    def list_files(self, folder_id: Optional[str] = None, 
                  query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in a Google Drive folder.
        
        Args:
            folder_id: ID of the folder to list (optional)
            query: Search query (optional)
            
        Returns:
            List of file dictionaries
        """
        if not self.is_authenticated():
            return []
        
        try:
            # Build query
            if folder_id:
                if query:
                    full_query = f"'{folder_id}' in parents and {query}"
                else:
                    full_query = f"'{folder_id}' in parents"
            else:
                full_query = query or ""
            
            # List files
            file_list = self.drive.ListFile({'q': full_query}).GetList()
            
            return [
                {
                    'id': file['id'],
                    'title': file['title'],
                    'mimeType': file['mimeType'],
                    'size': file.get('fileSize'),
                    'createdDate': file.get('createdDate'),
                    'modifiedDate': file.get('modifiedDate')
                }
                for file in file_list
            ]
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to list files")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive.
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_authenticated():
            return False
        
        try:
            file = self.drive.CreateFile({'id': file_id})
            file.Delete()
            return True
            
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to delete file: {file_id}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Google Drive and clear user settings."""
        try:
            self.drive = None
            self.authenticated = False
            self.user_settings.clear_google_drive_settings()
            return True
        except Exception as e:
            DebugUtils.log_error(e, "Failed to disconnect from Google Drive")
            return False
