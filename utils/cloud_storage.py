"""
Cloud Storage for User Settings

This module provides a simple storage mechanism for user settings in cloud environments
using Streamlit's caching and session state. In a production environment, this would
be replaced with a proper database.
"""

import streamlit as st
import json
import hashlib
from typing import Dict, Any, Optional
from utils.debug_utils import DebugUtils

class CloudStorage:
    """Simple cloud storage for user settings using Streamlit caching."""
    
    @staticmethod
    def _get_user_id() -> str:
        """Generate a unique user ID based on session state."""
        # In a real implementation, you'd use proper user authentication
        # For now, we'll create a hash based on session state
        session_data = str(st.session_state.get('_user_hash', 'default_user'))
        return hashlib.md5(session_data.encode()).hexdigest()
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_user_settings(_user_id: str) -> Dict[str, Any]:
        """
        Get user settings from cache.
        
        Args:
            _user_id: User identifier
            
        Returns:
            Dictionary of user settings
        """
        # In a real implementation, this would fetch from a database
        # For now, we'll return default settings
        return {
            "sidebar_config": {
                "export_word": True,
                "export_excel": True,
                "ai_model": "gpt-3.5-turbo",
                "upload_to_drive": False,
                "client_secrets_file": None,
                "cleanup_days": 30,
                "days_back": 365,
                "delay_between_calls": 1
            },
            "google_drive": {
                "configured": False,
                "folder_id": None,
                "create_date_folders": True,
                "oauth_credentials": None,
                "auth_token": None
            },
            "user_preferences": {}
        }
    
    @staticmethod
    def save_user_settings(settings: Dict[str, Any]) -> bool:
        """
        Save user settings to cache.
        
        Args:
            settings: Dictionary of user settings to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user_id = CloudStorage._get_user_id()
            
            # Store in session state for immediate access
            st.session_state['_user_settings'] = settings
            
            # In a real implementation, you would save to a database here
            # For now, we'll just use session state
            DebugUtils.info(f"Settings saved for user {user_id[:8]}...")
            return True
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to save user settings to cloud storage")
            return False
    
    @staticmethod
    def load_user_settings() -> Dict[str, Any]:
        """
        Load user settings from cache.
        
        Returns:
            Dictionary of user settings
        """
        try:
            user_id = CloudStorage._get_user_id()
            
            # Try to get from session state first
            if '_user_settings' in st.session_state:
                return st.session_state['_user_settings']
            
            # Fall back to cached data
            settings = CloudStorage.get_user_settings(user_id)
            
            # Store in session state for future access
            st.session_state['_user_settings'] = settings
            
            return settings
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to load user settings from cloud storage")
            # Return default settings on error
            return {
                "sidebar_config": {
                    "export_word": True,
                    "export_excel": True,
                    "ai_model": "gpt-3.5-turbo",
                    "upload_to_drive": False,
                    "client_secrets_file": None,
                    "cleanup_days": 30,
                    "days_back": 365,
                    "delay_between_calls": 1
                },
                "google_drive": {
                    "configured": False,
                    "folder_id": None,
                    "create_date_folders": True,
                    "oauth_credentials": None,
                    "auth_token": None
                },
                "user_preferences": {}
            }
    
    @staticmethod
    def update_sidebar_config(config: Dict[str, Any]) -> bool:
        """
        Update sidebar configuration for the current user.
        
        Args:
            config: New sidebar configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            settings = CloudStorage.load_user_settings()
            settings["sidebar_config"] = config
            return CloudStorage.save_user_settings(settings)
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to update sidebar config")
            return False
    
    @staticmethod
    def get_sidebar_config() -> Dict[str, Any]:
        """
        Get sidebar configuration for the current user.
        
        Returns:
            Sidebar configuration dictionary
        """
        try:
            settings = CloudStorage.load_user_settings()
            return settings.get("sidebar_config", {})
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to get sidebar config")
            return {}
    
    @staticmethod
    def update_google_drive_settings(drive_settings: Dict[str, Any]) -> bool:
        """
        Update Google Drive settings for the current user.
        
        Args:
            drive_settings: New Google Drive settings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            settings = CloudStorage.load_user_settings()
            settings["google_drive"] = drive_settings
            return CloudStorage.save_user_settings(settings)
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to update Google Drive settings")
            return False
    
    @staticmethod
    def get_google_drive_settings() -> Dict[str, Any]:
        """
        Get Google Drive settings for the current user.
        
        Returns:
            Google Drive settings dictionary
        """
        try:
            settings = CloudStorage.load_user_settings()
            return settings.get("google_drive", {})
            
        except Exception as e:
            DebugUtils.log_error(e, "Failed to get Google Drive settings")
            return {}
