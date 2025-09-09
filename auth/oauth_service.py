"""
OAuth Authentication Service

This module handles OAuth authentication for Google and Microsoft.
"""

import logging
import streamlit as st
import requests
import json
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode, parse_qs, urlparse
import msal
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from config import (
    GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, GOOGLE_OAUTH_REDIRECT_URI,
    MICROSOFT_OAUTH_CLIENT_ID, MICROSOFT_OAUTH_CLIENT_SECRET, 
    MICROSOFT_OAUTH_REDIRECT_URI, MICROSOFT_OAUTH_TENANT_ID
)
from auth.simple_microsoft_oauth import SimpleMicrosoftOAuth

logger = logging.getLogger(__name__)

class OAuthService:
    """Service for handling OAuth authentication flows."""
    
    def __init__(self):
        self.google_client_id = GOOGLE_OAUTH_CLIENT_ID
        self.google_client_secret = GOOGLE_OAUTH_CLIENT_SECRET
        self.google_redirect_uri = GOOGLE_OAUTH_REDIRECT_URI
        
        self.microsoft_client_id = MICROSOFT_OAUTH_CLIENT_ID
        self.microsoft_client_secret = MICROSOFT_OAUTH_CLIENT_SECRET
        self.microsoft_redirect_uri = MICROSOFT_OAUTH_REDIRECT_URI
        self.microsoft_tenant_id = MICROSOFT_OAUTH_TENANT_ID
        
        # Initialize simple Microsoft OAuth service
        self.simple_microsoft_service = SimpleMicrosoftOAuth()
    
    def get_google_auth_url(self) -> str:
        """Generate Google OAuth authorization URL."""
        if not self.google_client_id:
            raise ValueError("Google OAuth client ID not configured")
        
        params = {
            'client_id': self.google_client_id,
            'redirect_uri': self.google_redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': 'google'  # Add state parameter to identify the provider
        }
        
        return f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    
    def get_microsoft_auth_url(self) -> str:
        """Generate Microsoft OAuth authorization URL using simple implementation."""
        if not self.microsoft_client_id:
            raise ValueError("Microsoft OAuth client ID not configured")
        
        # Use simple service to generate auth URL
        return self.simple_microsoft_service.get_auth_url()
    
    def exchange_google_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for Google access token."""
        try:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': self.google_client_id,
                'client_secret': self.google_client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.google_redirect_uri
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data
            
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Google token exchange failed: {http_err.response.status_code}")
            logger.error(f"Response: {http_err.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error exchanging Google code for token: {e}")
            return None
    
    def exchange_microsoft_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for Microsoft access token using simple implementation."""
        try:
            # Use simple service to exchange code for token
            return self.simple_microsoft_service.exchange_code_for_token(code)
            
        except Exception as e:
            logger.error(f"Error exchanging Microsoft code for token: {e}")
            return None
    
    def get_google_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google using access token."""
        try:
            # First try to get user info from Google's userinfo endpoint
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(userinfo_url, headers=headers)
            response.raise_for_status()
            
            user_info = response.json()
            
            # Add provider identifier
            user_info['provider'] = 'google'
            user_info['sub'] = user_info.get('id')  # Use 'id' as 'sub' for consistency
            
            return user_info
            
        except Exception as e:
            logger.error(f"Error getting Google user info: {e}")
            return None
    
    def get_microsoft_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Microsoft using access token via simple implementation."""
        try:
            # Use simple service to get user info
            return self.simple_microsoft_service.get_user_info(access_token)
            
        except Exception as e:
            logger.error(f"Error getting Microsoft user info: {e}")
            return None
    
    def verify_google_id_token(self, id_token_str: str) -> Optional[Dict[str, Any]]:
        """Verify Google ID token and extract user information."""
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                self.google_client_id
            )
            
            # Add provider identifier
            idinfo['provider'] = 'google'
            idinfo['sub'] = idinfo.get('sub')
            
            return idinfo
            
        except Exception as e:
            logger.error(f"Error verifying Google ID token: {e}")
            return None
    
    def handle_oauth_callback(self, provider: str, code: str) -> Optional[Dict[str, Any]]:
        """Handle OAuth callback and return user information."""
        try:
            if provider == 'google':
                token_data = self.exchange_google_code_for_token(code)
                if token_data and 'access_token' in token_data:
                    return self.get_google_user_info(token_data['access_token'])
                    
            elif provider == 'microsoft':
                # Use simple service for complete Microsoft OAuth flow
                return self.simple_microsoft_service.handle_oauth_callback(code)
            
            return None
            
        except Exception as e:
            logger.error(f"Error handling OAuth callback for {provider}: {e}")
            return None
    
    def is_configured(self, provider: str) -> bool:
        """Check if OAuth provider is properly configured."""
        if provider == 'google':
            return bool(self.google_client_id and self.google_client_secret)
        elif provider == 'microsoft':
            return bool(self.microsoft_client_id and self.microsoft_client_secret)
        return False
