"""
User Settings Manager for Streamlit

This module provides a centralized way to manage user-specific settings
that persist across Streamlit sessions and app restarts.
"""

import streamlit as st
import json
import os
from typing import Any, Optional, Dict, List
from pathlib import Path
from utils.debug_utils import DebugUtils
from utils.secrets_wrapper import secrets
from utils.cloud_storage import CloudStorage

class UserSettingsManager:
    """Manages user-specific settings with persistence across sessions."""
    
    def __init__(self):
        self.settings_file = "user_settings.json"
        self._ensure_settings_file_exists()
        self._init_session_state()
    
    def _is_cloud_environment(self) -> bool:
        """Check if we're running in a cloud environment."""
        try:
            # Check environment variables and known cloud path only (do not access st.secrets)
            return (
                "STREAMLIT_SERVER_RUNNING" in os.environ or
                "STREAMLIT_CLOUD" in os.environ or
                "STREAMLIT_SHARING" in os.environ or
                os.path.exists("/app/.streamlit/")
            )
        except Exception as e:
            # If there's any error with environment detection, assume local environment
            DebugUtils.log_error(e, "Error detecting cloud environment, assuming local")
            return False
    
    def _ensure_settings_file_exists(self):
        """Ensure the settings file exists with default values (local only)."""
        if not self._is_cloud_environment():
            if not os.path.exists(self.settings_file):
                default_settings = {
                    "sidebar_config": {
                        "export_word": True,
                        "export_excel": True,
                        "ai_model": "gpt-3.5-turbo",
                        "upload_to_drive": False,
                        "client_secrets_file": None,
                        "cleanup_days": 30,
                        "days_back": 365,
                        "delay_between_calls": 1
                    }
                }
                self._save_settings_to_file(default_settings)
    
    def _init_session_state(self):
        """Initialize session state variables if they don't exist."""
        if 'user_settings' not in st.session_state:
            st.session_state.user_settings = {}
        
        if 'google_drive_configured' not in st.session_state:
            st.session_state.google_drive_configured = False
        
        if 'google_drive_folder_id' not in st.session_state:
            st.session_state.google_drive_folder_id = None
        
        if 'google_drive_create_date_folders' not in st.session_state:
            st.session_state.google_drive_create_date_folders = True
        
        if 'google_drive_oauth_credentials' not in st.session_state:
            st.session_state.google_drive_oauth_credentials = None
        
        if 'google_drive_auth_token' not in st.session_state:
            st.session_state.google_drive_auth_token = None
        
        # Initialize sidebar config in session state
        if 'sidebar_config' not in st.session_state:
            st.session_state.sidebar_config = self._get_default_sidebar_config()
    
    def _get_default_sidebar_config(self) -> Dict[str, Any]:
        """Get default sidebar configuration."""
        return {
            "export_word": True,
            "export_excel": True,
            "ai_model": "gpt-3.5-turbo",
            "upload_to_drive": False,
            "client_secrets_file": None,
            "cleanup_days": 30,
            "days_back": 365,
            "delay_between_calls": 1
        }
    
    def _load_settings_from_file(self) -> Dict[str, Any]:
        """Load settings from file (local environment only)."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Error loading settings from file: {str(e)}")
        return {}
    
    def _save_settings_to_file(self, settings: Dict[str, Any]):
        """Save settings to file (local environment only)."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            st.error(f"Error saving settings to file: {str(e)}")
    
    def save_sidebar_config(self, config: Dict[str, Any]):
        """Save sidebar configuration to persistent storage."""
        if self._is_cloud_environment():
            # In cloud environment, use CloudStorage
            success = CloudStorage.update_sidebar_config(config)
            if success:
                st.session_state['sidebar_config'] = config
                DebugUtils.info("Settings saved to cloud storage")
            else:
                DebugUtils.warning("Failed to save settings to cloud storage")
        else:
            # In local environment, save to file
            settings = self._load_settings_from_file()
            settings["sidebar_config"] = config
            self._save_settings_to_file(settings)
            
            # Also update session state for immediate use
            st.session_state['sidebar_config'] = config
            DebugUtils.info("Settings saved to file (local environment)")
    
    def load_sidebar_config(self) -> Dict[str, Any]:
        """Load sidebar configuration from persistent storage."""
        if self._is_cloud_environment():
            # In cloud environment, use CloudStorage
            config = CloudStorage.get_sidebar_config()
            if config:
                st.session_state['sidebar_config'] = config
                return config
            else:
                # Fall back to default config
                default_config = self._get_default_sidebar_config()
                st.session_state['sidebar_config'] = default_config
                return default_config
        else:
            # In local environment, load from file
            settings = self._load_settings_from_file()
            config = settings.get("sidebar_config", self._get_default_sidebar_config())
            
            # Also update session state for immediate use
            st.session_state['sidebar_config'] = config
            return config

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a user setting value."""
        return st.session_state.user_settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a user setting value."""
        try:
            st.session_state.user_settings[key] = value
            return True
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to set user setting {key}")
            return False
    
    def get_google_drive_folder_id(self) -> Optional[str]:
        """Get the user's Google Drive folder ID."""
        if self._is_cloud_environment():
            drive_settings = CloudStorage.get_google_drive_settings()
            return drive_settings.get('folder_id')
        return st.session_state.google_drive_folder_id
    
    def set_google_drive_folder_id(self, folder_id: str) -> bool:
        """Set the user's Google Drive folder ID."""
        try:
            if self._is_cloud_environment():
                drive_settings = CloudStorage.get_google_drive_settings()
                drive_settings['folder_id'] = folder_id
                return CloudStorage.update_google_drive_settings(drive_settings)
            else:
                st.session_state.google_drive_folder_id = folder_id
                return True
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to set Google Drive folder ID: {folder_id}")
            return False
    
    def get_google_drive_date_folders(self) -> bool:
        """Get the user's date folder preference."""
        if self._is_cloud_environment():
            drive_settings = CloudStorage.get_google_drive_settings()
            return drive_settings.get('create_date_folders', True)
        return st.session_state.google_drive_create_date_folders
    
    def set_google_drive_date_folders(self, create_date_folders: bool) -> bool:
        """Set the user's date folder preference."""
        try:
            if self._is_cloud_environment():
                drive_settings = CloudStorage.get_google_drive_settings()
                drive_settings['create_date_folders'] = create_date_folders
                return CloudStorage.update_google_drive_settings(drive_settings)
            else:
                st.session_state.google_drive_create_date_folders = create_date_folders
                return True
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to set date folder preference: {create_date_folders}")
            return False
    
    def get_google_drive_oauth_credentials(self) -> Optional[Dict[str, Any]]:
        """Get the user's OAuth credentials."""
        if self._is_cloud_environment():
            drive_settings = CloudStorage.get_google_drive_settings()
            return drive_settings.get('oauth_credentials')
        return st.session_state.google_drive_oauth_credentials
    
    def set_google_drive_oauth_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Set the user's OAuth credentials."""
        try:
            if self._is_cloud_environment():
                drive_settings = CloudStorage.get_google_drive_settings()
                drive_settings['oauth_credentials'] = credentials
                return CloudStorage.update_google_drive_settings(drive_settings)
            else:
                st.session_state.google_drive_oauth_credentials = credentials
                return True
        except Exception as e:
            DebugUtils.log_error(e, "Failed to set OAuth credentials")
            return False
    
    def get_google_drive_auth_token(self) -> Optional[Dict[str, Any]]:
        """Get the user's authentication token."""
        if self._is_cloud_environment():
            drive_settings = CloudStorage.get_google_drive_settings()
            return drive_settings.get('auth_token')
        return st.session_state.google_drive_auth_token
    
    def set_google_drive_auth_token(self, token: Dict[str, Any]) -> bool:
        """Set the user's authentication token."""
        try:
            if self._is_cloud_environment():
                drive_settings = CloudStorage.get_google_drive_settings()
                drive_settings['auth_token'] = token
                return CloudStorage.update_google_drive_settings(drive_settings)
            else:
                st.session_state.google_drive_auth_token = token
                return True
        except Exception as e:
            DebugUtils.log_error(e, "Failed to set auth token")
            return False
    
    def is_google_drive_configured(self) -> bool:
        """Check if Google Drive is configured for the current user."""
        if self._is_cloud_environment():
            drive_settings = CloudStorage.get_google_drive_settings()
            return drive_settings.get('configured', False)
        return st.session_state.google_drive_configured
    
    def set_google_drive_configured(self, configured: bool) -> bool:
        """Set whether Google Drive is configured for the current user."""
        try:
            if self._is_cloud_environment():
                drive_settings = CloudStorage.get_google_drive_settings()
                drive_settings['configured'] = configured
                return CloudStorage.update_google_drive_settings(drive_settings)
            else:
                st.session_state.google_drive_configured = configured
                return True
        except Exception as e:
            DebugUtils.log_error(e, f"Failed to set Google Drive configured status: {configured}")
            return False
    
    def clear_google_drive_settings(self) -> bool:
        """Clear all Google Drive settings for the current user."""
        try:
            if self._is_cloud_environment():
                drive_settings = {
                    'configured': False,
                    'folder_id': None,
                    'create_date_folders': True,
                    'oauth_credentials': None,
                    'auth_token': None
                }
                return CloudStorage.update_google_drive_settings(drive_settings)
            else:
                st.session_state.google_drive_configured = False
                st.session_state.google_drive_folder_id = None
                st.session_state.google_drive_create_date_folders = True
                st.session_state.google_drive_oauth_credentials = None
                st.session_state.google_drive_auth_token = None
                return True
        except Exception as e:
            DebugUtils.log_error(e, "Failed to clear Google Drive settings")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all user settings as a dictionary."""
        if self._is_cloud_environment():
            settings = CloudStorage.load_user_settings()
            return {
                'google_drive_configured': settings.get('google_drive', {}).get('configured', False),
                'google_drive_folder_id': settings.get('google_drive', {}).get('folder_id'),
                'google_drive_create_date_folders': settings.get('google_drive', {}).get('create_date_folders', True),
                'user_settings': settings.get('user_preferences', {})
            }
        else:
            return {
                'google_drive_configured': st.session_state.google_drive_configured,
                'google_drive_folder_id': st.session_state.google_drive_folder_id,
                'google_drive_create_date_folders': st.session_state.google_drive_create_date_folders,
                'user_settings': st.session_state.user_settings
            }
    
    def export_settings(self) -> str:
        """Export user settings as a JSON string."""
        try:
            return json.dumps(self.get_all_settings(), indent=2)
        except Exception as e:
            DebugUtils.log_error(e, "Failed to export settings")
            return "{}"
    
    def import_settings(self, settings_json: str) -> bool:
        """Import user settings from a JSON string."""
        try:
            settings = json.loads(settings_json)
            
            if 'google_drive_configured' in settings:
                self.set_google_drive_configured(settings['google_drive_configured'])
            
            if 'google_drive_folder_id' in settings:
                self.set_google_drive_folder_id(settings['google_drive_folder_id'])
            
            if 'google_drive_create_date_folders' in settings:
                self.set_google_drive_date_folders(settings['google_drive_create_date_folders'])
            
            if 'user_settings' in settings:
                st.session_state.user_settings.update(settings['user_settings'])
            
            return True
        except Exception as e:
            DebugUtils.log_error(e, "Failed to import settings")
            return False
    
    def reset_all_settings(self) -> bool:
        """Reset all user settings to defaults."""
        try:
            st.session_state.user_settings = {}
            self.clear_google_drive_settings()
            return True
        except Exception as e:
            DebugUtils.log_error(e, "Failed to reset settings")
            return False
