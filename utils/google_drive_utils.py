"""
Google Drive Utilities

This module contains utility functions for Google Drive integration.
Combines functionality from drive_utils.py and googledrive.py.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from pydrive2.auth import ServiceAccountCredentials
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

from config.constants.StringConstants import input_dir
from utils.debug_utils import DebugUtils
from config.settings import ENABLE_GOOGLE_DRIVE

class GoogleDriveManager:
    """Manager class for Google Drive operations."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Drive manager.
        
        Args:
            credentials_path: Path to the service account credentials file
        """
        self.drive = None
        self.credentials_path = credentials_path or os.path.join(input_dir, 'Service Account.json')
        
        if ENABLE_GOOGLE_DRIVE and GOOGLE_DRIVE_AVAILABLE:
            self._authenticate()
    
    def _authenticate(self) -> bool:
        """
        Authenticate with Google Drive using service account.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            if not os.path.exists(self.credentials_path):
                DebugUtils.warning(f"Google Drive credentials file not found: {self.credentials_path}")
                return False
            
            scope = ['https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
            gauth = GoogleAuth()
            gauth.credentials = creds
            self.drive = GoogleDrive(gauth)
            
            DebugUtils.info("Successfully authenticated with Google Drive")
            return True
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to authenticate with Google Drive")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if Google Drive is authenticated."""
        return self.drive is not None
    
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
            # Check if folder already exists
            query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
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
    
    def upload_file(self, file_path: str, folder_id: Optional[str] = None, 
                   new_filename: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Google Drive.
        
        Args:
            file_path: Local path to the file to upload
            folder_id: Google Drive folder ID to upload to (optional)
            new_filename: New filename for the uploaded file (optional)
            
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
            
            # Create file metadata
            file_metadata = {'title': filename}
            if folder_id:
                file_metadata['parents'] = [{'id': folder_id}]
            
            # Create and upload file
            drive_file = self.drive.CreateFile(file_metadata)
            drive_file.SetContentFile(file_path)
            drive_file.Upload()
            
            DebugUtils.info(f"Successfully uploaded '{filename}' to Google Drive")
            return drive_file['id']
            
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to upload file: {file_path}")
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