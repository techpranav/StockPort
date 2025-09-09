"""
Simple Microsoft OAuth Implementation
This bypasses MSAL complexity and uses direct HTTP calls
"""

import requests
import logging
from typing import Dict, Optional, Any
from urllib.parse import urlencode
from config.app_config import (
    MICROSOFT_OAUTH_CLIENT_ID, 
    MICROSOFT_OAUTH_CLIENT_SECRET, 
    MICROSOFT_OAUTH_REDIRECT_URI
)

logger = logging.getLogger(__name__)

class SimpleMicrosoftOAuth:
    """Simple Microsoft OAuth implementation using direct HTTP calls"""
    
    def __init__(self):
        self.client_id = MICROSOFT_OAUTH_CLIENT_ID
        self.client_secret = MICROSOFT_OAUTH_CLIENT_SECRET
        self.redirect_uri = MICROSOFT_OAUTH_REDIRECT_URI
        self.authority = "https://login.microsoftonline.com/common"
        
        logger.info(f"Simple Microsoft OAuth initialized for client: {self.client_id[:8]}...")
    
    def get_auth_url(self) -> str:
        """Generate Microsoft OAuth authorization URL"""
        try:
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'scope': 'openid email profile',
                'response_type': 'code',
                'response_mode': 'query',
                'prompt': 'select_account',
                'state': 'microsoft'
            }
            
            query_string = urlencode(params)
            auth_url = f"{self.authority}/oauth2/v2.0/authorize?{query_string}"
            
            logger.info(f"Generated simple auth URL: {auth_url[:100]}...")
            return auth_url
            
        except Exception as e:
            logger.error(f"Error generating auth URL: {e}")
            return ""
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        try:
            token_url = f"{self.authority}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code',
                'scope': 'openid email profile'
            }
            
            logger.info(f"Exchanging code for token: redirect_uri={self.redirect_uri}")
            logger.info(f"Code length: {len(code)}")
            logger.info(f"Code preview: {code[:20]}...")
            
            response = requests.post(token_url, data=data)
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
            
            token_data = response.json()
            logger.info(f"Token exchange successful: access_token_length={len(token_data.get('access_token', ''))}")
            return token_data
            
        except Exception as e:
            logger.error(f"Error in token exchange: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Microsoft Graph API"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get user info from Microsoft Graph
            graph_url = "https://graph.microsoft.com/v1.0/me"
            response = requests.get(graph_url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"User info request failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
            
            user_info = response.json()
            logger.info(f"Retrieved user info: {user_info.get('mail', 'no email')}")
            
            # Normalize user info to match our expected format
            normalized_info = {
                'id': user_info.get('id'),
                'email': user_info.get('mail') or user_info.get('userPrincipalName'),
                'name': user_info.get('displayName'),
                'first_name': user_info.get('givenName'),
                'last_name': user_info.get('surname'),
                'provider': 'microsoft'
            }
            
            return normalized_info
            
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def handle_oauth_callback(self, code: str) -> Optional[Dict[str, Any]]:
        """Handle complete OAuth callback flow"""
        try:
            logger.info(f"Handling simple OAuth callback: code_length={len(code)}")
            
            # Exchange code for token
            token_data = self.exchange_code_for_token(code)
            if not token_data:
                logger.error("Failed to exchange code for token")
                return None
            
            # Get user info
            access_token = token_data.get('access_token')
            if not access_token:
                logger.error("No access token in response")
                return None
            
            user_info = self.get_user_info(access_token)
            if not user_info:
                logger.error("Failed to get user info")
                return None
            
            logger.info(f"Simple OAuth callback successful: {user_info.get('email', 'no email')}")
            return user_info
            
        except Exception as e:
            logger.error(f"Error handling simple OAuth callback: {e}")
            return None
