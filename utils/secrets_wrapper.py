"""
Safe Secrets Wrapper for Streamlit

This module provides a safe way to access Streamlit secrets without causing
"No secrets found" errors in local environments where secrets.toml doesn't exist.
"""

import streamlit as st
from typing import Any, Optional

class SafeSecrets:
    """Safe wrapper for Streamlit secrets that prevents errors in local environments."""
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Safely get a secret value.
        
        Args:
            key: The secret key to retrieve
            default: Default value if secret not found or secrets not available
            
        Returns:
            The secret value or default
        """
        try:
            if hasattr(st, 'secrets'):
                return st.secrets.get(key, default)
            else:
                return default
        except Exception:
            # If there's any error accessing secrets, return default
            return default
    
    @staticmethod
    def has_key(key: str) -> bool:
        """
        Check if a secret key exists.
        
        Args:
            key: The secret key to check
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            if hasattr(st, 'secrets'):
                return key in st.secrets
            else:
                return False
        except Exception:
            return False
    
    @staticmethod
    def to_dict() -> dict:
        """
        Get all secrets as a dictionary.
        
        Returns:
            Dictionary of all secrets or empty dict if not available
        """
        try:
            if hasattr(st, 'secrets'):
                return dict(st.secrets)
            else:
                return {}
        except Exception:
            return {}
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if secrets are available.
        
        Returns:
            True if secrets can be accessed, False otherwise
        """
        try:
            return hasattr(st, 'secrets') and st.secrets is not None
        except Exception:
            return False

# Create a global instance for easy access
secrets = SafeSecrets()
