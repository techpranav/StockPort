"""
Google Drive Utilities

This module contains utility functions for Google Drive integration.
Combines functionality from drive_utils.py and googledrive.py.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

try:
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from pydrive2.auth import ServiceAccountCredentials
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

from config.constants.StringConstants import input_dir
from utils.debug_utils import DebugUtils
from config.settings import (
    ENABLE_GOOGLE_DRIVE,
    GOOGLE_DRIVE_USE_SERVICE_ACCOUNT,
    GOOGLE_DRIVE_SCOPES,
    GOOGLE_DRIVE_CREDENTIALS_FILE,
    GOOGLE_APPLICATION_CREDENTIALS,
    GOOGLE_DRIVE_FOLDER_ID,
)

class GoogleDriveSettings:
    """Manages persistent Google Drive settings."""
    
    def __init__(self, settings_file: str = "config/credentials/gdrive_settings.json"):
        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to load Google Drive settings from {self.settings_file}")
        return {}
    
    def _save_settings(self) -> bool:
        """Save settings to file."""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to save Google Drive settings to {self.settings_file}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a setting value and save."""
        self.settings[key] = value
        return self._save_settings()
    
    def is_configured(self) -> bool:
        """Check if Google Drive is configured."""
        return bool(self.settings.get('folder_id') or self.settings.get('authenticated'))

class GoogleDriveManager:
    """Manager class for Google Drive operations."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Drive manager.
        
        Args:
            credentials_path: Path to the service account credentials file
        """
        self.drive = None
        self.credentials_path = credentials_path
        self.settings = GoogleDriveSettings()
        
        if ENABLE_GOOGLE_DRIVE and GOOGLE_DRIVE_AVAILABLE:
            self._authenticate()
    
    def _authenticate(self) -> bool:
        """
        Authenticate with Google Drive using saved credentials or prompt for new ones.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            scope = [GOOGLE_DRIVE_SCOPES]

            # Service Account mode
            if GOOGLE_DRIVE_USE_SERVICE_ACCOUNT:
                path = self.credentials_path or GOOGLE_APPLICATION_CREDENTIALS
                if not os.path.exists(path):
                    DebugUtils.warning(f"Google Drive service account file not found: {path}")
                    return False
                creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
                gauth = GoogleAuth()
                gauth.credentials = creds
                self.drive = GoogleDrive(gauth)
            else:
                # User OAuth (Desktop) mode with saved credentials
                path = self.credentials_path or str(GOOGLE_DRIVE_CREDENTIALS_FILE)
                if not os.path.exists(path):
                    DebugUtils.warning(f"Google OAuth client file not found: {path}")
                    return False
                
                gauth = GoogleAuth()
                gauth.LoadClientConfigFile(path)
                
                # Try to load saved credentials first
                try:
                    gauth.LoadCredentialsFile("config/credentials/gdrive_token.json")
                except:
                    pass
                
                # If no saved credentials or they're expired, authenticate
                if gauth.credentials is None or gauth.access_token_expired:
                    gauth.LocalWebserverAuth()
                    # Save credentials for next time
                    try:
                        gauth.SaveCredentialsFile("config/credentials/gdrive_token.json")
                    except Exception as e:
                        DebugUtils.warning(f"Failed to save credentials: {e}")
                
                self.drive = GoogleDrive(gauth)
            
            DebugUtils.info("Successfully authenticated with Google Drive")
            return True
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to authenticate with Google Drive")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if Google Drive is authenticated."""
        return self.drive is not None
    
    def get_saved_folder_id(self) -> Optional[str]:
        """Get the saved folder ID from settings."""
        return self.settings.get_setting('folder_id')
    
    def save_folder_id(self, folder_id: str) -> bool:
        """Save folder ID to settings."""
        return self.settings.set_setting('folder_id', folder_id)
    
    def get_saved_date_folder_preference(self) -> bool:
        """Get the saved date folder preference from settings."""
        return self.settings.get_setting('create_date_folders', False)
    
    def save_date_folder_preference(self, create_date_folders: bool) -> bool:
        """Save date folder preference to settings."""
        return self.settings.set_setting('create_date_folders', create_date_folders)
    
    def is_configured(self) -> bool:
        """Check if Google Drive is fully configured (authenticated + folder set)."""
        return self.is_authenticated() and self.settings.is_configured()
    
    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
        """
        Create a folder in Google Drive.
        
        Args:
            folder_name: Name of the folder to create
            parent_folder_id: Parent folder ID (optional)
            
        Returns:
            str: Folder ID if successful, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        try:
            # Check if folder already exists (exclude trashed)
            query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            
            folder_list = self.drive.ListFile({'q': query}).GetList()
            
            if folder_list:
                DebugUtils.info(f"Folder '{folder_name}' already exists")
                return folder_list[0]['id']
            
            # Create new folder
            folder = self.drive.CreateFile({
                'title': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            })
            
            if parent_folder_id:
                folder['parents'] = [{'id': parent_folder_id}]
            
            folder.Upload()
            DebugUtils.info(f"Created folder '{folder_name}' with ID: {folder['id']}")
            return folder['id']
            
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to create folder '{folder_name}'")
            return None
    
    def create_date_folder(self, base_folder_id: Optional[str] = None, date_format: str = "%Y-%m-%d") -> Optional[str]:
        """
        Create a date-based folder in Google Drive.
        
        Args:
            base_folder_id: Parent folder ID (optional, uses root if not provided)
            date_format: Date format string (default: YYYY-MM-DD)
            
        Returns:
            str: Date folder ID if successful, None otherwise
        """
        if not self.is_authenticated():
            DebugUtils.warning("Google Drive not authenticated")
            return None
        
        try:
            from datetime import datetime
            date_folder_name = datetime.now().strftime(date_format)
            
            # Validate base folder exists, is accessible, and not trashed
            if base_folder_id and not self._validate_folder_access(base_folder_id):
                DebugUtils.warning(f"Base folder {base_folder_id} invalid or trashed; creating date folder under Drive root")
                base_folder_id = None
            
            # Create date folder under the base folder
            date_folder_id = self.create_folder(date_folder_name, parent_folder_id=base_folder_id)
            
            if date_folder_id:
                DebugUtils.info(f"Created date folder '{date_folder_name}' with ID: {date_folder_id}")
                return date_folder_id
            else:
                DebugUtils.error(f"Failed to create date folder '{date_folder_name}'")
                return None
                
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to create date folder")
            return None

    def upload_file(self, file_path: str, folder_id: Optional[str] = None, 
                   new_filename: Optional[str] = None, create_date_folder: bool = False, symbol: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Google Drive, optionally creating a date and/or symbol folder.
        
        Args:
            file_path: Local path to the file to upload
            folder_id: Google Drive folder ID to upload to (optional)
            new_filename: New filename for the uploaded file (optional)
            create_date_folder: Whether to create a date-based subfolder (default: False)
            symbol: Stock symbol for symbol folder (optional)
        Returns:
            str: File ID if successful, None otherwise
        """
        if not self.is_authenticated():
            DebugUtils.warning("Google Drive not authenticated")
            return None
        
        if not os.path.exists(file_path):
            DebugUtils.error(f"File not found: {file_path}")
            return None
        
        try:
            filename = new_filename or os.path.basename(file_path)
            
            # Determine base folder
            target_folder_id = folder_id or GOOGLE_DRIVE_FOLDER_ID

            # If provided base folder is invalid or trashed, fallback to Drive root
            if target_folder_id and not self._validate_folder_access(target_folder_id):
                DebugUtils.warning(f"Provided base folder {target_folder_id} is invalid or trashed; uploading to Drive root")
                target_folder_id = None
            
            # 1. Create/check date folder if requested
            if create_date_folder and target_folder_id:
                DebugUtils.info(f"Attempting to create date folder under: {target_folder_id}")
                date_folder_id = self.create_date_folder(base_folder_id=target_folder_id)
                if date_folder_id:
                    target_folder_id = date_folder_id
                    DebugUtils.info(f"Uploading to date folder: {date_folder_id}")
                else:
                    DebugUtils.warning("Failed to create date folder, attempting to upload to base folder")
                    if not self._validate_folder_access(target_folder_id):
                        DebugUtils.warning("Target folder not accessible, uploading to Drive root")
                        target_folder_id = None
            
            # 2. Create/check symbol folder if symbol is provided (inside date folder if date folder was created)
            if symbol and target_folder_id:
                DebugUtils.info(f"Ensuring symbol folder '{symbol}' exists under {target_folder_id}")
                symbol_folder_id = self.create_folder(symbol, parent_folder_id=target_folder_id)
                if symbol_folder_id:
                    target_folder_id = symbol_folder_id
                else:
                    DebugUtils.warning(f"Failed to create/find symbol folder '{symbol}', uploading to previous folder")
            
            # Create file metadata
            file_metadata = {'title': filename}
            if target_folder_id:
                file_metadata['parents'] = [{'id': target_folder_id}]
            
            # Create and upload file
            drive_file = self.drive.CreateFile(file_metadata)
            drive_file.SetContentFile(file_path)
            drive_file.Upload()
            
            upload_location = f"folder: {target_folder_id}" if target_folder_id else "Drive root"
            DebugUtils.info(f"Successfully uploaded '{filename}' to Google Drive ({upload_location})")
            return drive_file['id']
            
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to upload file: {file_path}")
            return None
    
    def _validate_folder_access(self, folder_id: str) -> bool:
        """
        Validate that a folder exists and is accessible.
        
        Args:
            folder_id: Google Drive folder ID to validate
            
        Returns:
            bool: True if folder is accessible, False otherwise
        """
        try:
            folder = self.drive.CreateFile({'id': folder_id})
            folder.FetchMetadata()
            
            # Verify it's actually a folder
            if folder['mimeType'] != 'application/vnd.google-apps.folder':
                DebugUtils.error(f"ID {folder_id} is not a folder (mimeType: {folder['mimeType']})")
                return False

            # Check if folder is trashed
            is_trashed = False
            try:
                # Drive v2 metadata
                is_trashed = folder.get('labels', {}).get('trashed', False)
            except Exception:
                pass
            # Also check Drive v3 style
            if not is_trashed:
                is_trashed = folder.get('trashed', False)
            if is_trashed:
                DebugUtils.warning(f"Folder '{folder.get('title', folder_id)}' (ID: {folder_id}) is in Trash")
                return False
            
            DebugUtils.info(f"Folder '{folder['title']}' (ID: {folder_id}) is accessible")
            return True
            
        except Exception as e:
            DebugUtils.error(f"Folder ID {folder_id} is not accessible: {str(e)}")
            return False
    
    def test_folder_access(self, folder_id: str) -> Dict[str, Any]:
        """
        Test if a folder ID is accessible and valid.
        
        Args:
            folder_id: Google Drive folder ID to test
            
        Returns:
            Dict containing test results and folder information
        """
        result = {
            'accessible': False,
            'exists': False,
            'is_folder': False,
            'title': None,
            'error': None,
            'permissions': None
        }
        
        try:
            folder = self.drive.CreateFile({'id': folder_id})
            folder.FetchMetadata()
            
            result['exists'] = True
            result['title'] = folder.get('title', 'Unknown')
            
            # Check if it's a folder
            if folder['mimeType'] == 'application/vnd.google-apps.folder':
                result['is_folder'] = True
                
                # Try to list files to check permissions (exclude trashed)
                try:
                    file_list = self.drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
                    result['permissions'] = 'read_write'
                    result['accessible'] = True
                except Exception as e:
                    result['permissions'] = 'read_only'
                    result['error'] = f"Can read folder but cannot list contents: {str(e)}"
            else:
                result['error'] = f"ID {folder_id} is not a folder (mimeType: {folder['mimeType']})"
                
        except Exception as e:
            result['error'] = str(e)
            if "not found" in str(e).lower():
                result['error'] = "Folder not found - check if the ID is correct or if you have access"
            elif "forbidden" in str(e).lower():
                result['error'] = "Access denied - check if you have permission to access this folder"
            elif "invalid" in str(e).lower():
                result['error'] = "Invalid folder ID format"
        
        return result
    
    def get_folder_info(self, folder_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a Google Drive folder.
        
        Args:
            folder_id: Google Drive folder ID
            
        Returns:
            Dict containing folder information or None if not accessible
        """
        try:
            folder = self.drive.CreateFile({'id': folder_id})
            folder.FetchMetadata()
            
            return {
                'id': folder['id'],
                'title': folder['title'],
                'mimeType': folder['mimeType'],
                'createdDate': folder.get('createdDate'),
                'modifiedDate': folder.get('modifiedDate'),
                'parents': folder.get('parents', []),
                'permissions': folder.get('permissions', [])
            }
            
        except Exception as e:
            DebugUtils.error(f"Failed to get folder info for {folder_id}: {str(e)}")
            return None
    
    def download_file(self, file_id: str, local_path: str) -> bool:
        """
        Download a file from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            local_path: Local path to save the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_authenticated():
            return False
        
        try:
            drive_file = self.drive.CreateFile({'id': file_id})
            drive_file.GetContentFile(local_path)
            
            DebugUtils.info(f"Successfully downloaded file to: {local_path}")
            return True
            
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to download file ID: {file_id}")
            return False
    
    def list_files(self, folder_id: Optional[str] = None, 
                  query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in Google Drive.
        
        Args:
            folder_id: Folder ID to list files from (optional)
            query: Custom query string (optional)
            
        Returns:
            List[Dict]: List of file metadata dictionaries
        """
        if not self.is_authenticated():
            return []
        
        try:
            if query:
                search_query = query
            elif folder_id:
                search_query = f"'{folder_id}' in parents"
            else:
                search_query = "trashed=false"
            
            file_list = self.drive.ListFile({'q': search_query}).GetList()
            return [{'id': f['id'], 'title': f['title'], 'mimeType': f['mimeType']} for f in file_list]
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to list files from Google Drive")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive.
        
        Args:
            file_id: Google Drive file ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_authenticated():
            return False
        
        try:
            drive_file = self.drive.CreateFile({'id': file_id})
            drive_file.Delete()
            
            DebugUtils.info(f"Successfully deleted file ID: {file_id}")
            return True
            
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to delete file ID: {file_id}")
            return False

# Legacy class for backward compatibility
class DriveUtils(GoogleDriveManager):
    """Legacy DriveUtils class for backward compatibility."""
    
    def __init__(self):
        super().__init__()

# Legacy functions for backward compatibility
def authenticate_drive():
    """Legacy function for authenticating with Google Drive."""
    manager = GoogleDriveManager()
    return manager.drive if manager.is_authenticated() else None

def create_drive_folder(drive, folder_name: str, parent_folder_id: Optional[str] = None):
    """Legacy function for creating a drive folder."""
    if drive:
        manager = GoogleDriveManager()
        manager.drive = drive
        return manager.create_folder(folder_name, parent_folder_id)
    return None

def upload_file_to_drive(drive, file_path: str, folder_id: Optional[str] = None):
    """Legacy function for uploading files to drive."""
    if drive:
        manager = GoogleDriveManager()
        manager.drive = drive
        return manager.upload_file(file_path, folder_id)
    return None 