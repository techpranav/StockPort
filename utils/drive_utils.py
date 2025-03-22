from pathlib import Path
from typing import Optional
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class DriveUtils:
    def __init__(self, client_secrets_path: Optional[str] = None):
        """Initialize Google Drive utilities."""
        self.client_secrets_path = client_secrets_path
        self.drive = None
        
    def authenticate(self) -> None:
        """Authenticate with Google Drive."""
        try:
            gauth = GoogleAuth()
            if self.client_secrets_path:
                gauth.LoadClientConfigFile(self.client_secrets_path)
            gauth.LocalWebserverAuth()
            self.drive = GoogleDrive(gauth)
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Drive: {str(e)}")
    
    def upload_file(self, file_path: str) -> str:
        """Upload a file to Google Drive."""
        try:
            if not self.drive:
                self.authenticate()
            
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file = self.drive.CreateFile({'title': file_path.name})
            file.SetContentFile(str(file_path))
            file.Upload()
            
            return file['id']
        except Exception as e:
            raise Exception(f"Failed to upload file to Google Drive: {str(e)}")
    
    def download_file(self, file_id: str, destination: str) -> None:
        """Download a file from Google Drive."""
        try:
            if not self.drive:
                self.authenticate()
            
            file = self.drive.CreateFile({'id': file_id})
            file.GetContentFile(destination)
        except Exception as e:
            raise Exception(f"Failed to download file from Google Drive: {str(e)}")
    
    def list_files(self) -> list:
        """List files in Google Drive."""
        try:
            if not self.drive:
                self.authenticate()
            
            file_list = self.drive.ListFile({'q': "'root' in parents"}).GetList()
            return [{'id': f['id'], 'title': f['title']} for f in file_list]
        except Exception as e:
            raise Exception(f"Failed to list files from Google Drive: {str(e)}") 