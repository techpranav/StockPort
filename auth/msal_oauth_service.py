"""
Microsoft OAuth Service using MSAL (Microsoft Authentication Library)
This provides a more reliable implementation for Microsoft OAuth
"""

import msal
import requests
import logging
from typing import Dict, Optional, Any
from config.app_config import (
    MICROSOFT_OAUTH_CLIENT_ID, 
    MICROSOFT_OAUTH_CLIENT_SECRET, 
    MICROSOFT_OAUTH_REDIRECT_URI
)

logger = logging.getLogger(__name__)

class MSALOAuthService:
    """Microsoft OAuth service using MSAL library"""
    
    def __init__(self):
        self.client_id = MICROSOFT_OAUTH_CLIENT_ID
        self.client_secret = MICROSOFT_OAUTH_CLIENT_SECRET
        self.redirect_uri = MICROSOFT_OAUTH_REDIRECT_URI
        self.authority = "https://login.microsoftonline.com/common"
        self.scope = ["openid", "email", "profile"]  # Include all required scopes
        
        # Create MSAL app only if client_id is configured
        if self.client_id and self.client_secret:
            self.app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )
            logger.info(f"MSAL OAuth service initialized for client: {self.client_id[:8]}...")
        else:
            self.app = None
            logger.warning("MSAL OAuth service initialized without client ID (Microsoft OAuth not configured)")
    
    def get_auth_url(self) -> str:
        """Generate Microsoft OAuth authorization URL using manual construction"""
        try:
            if not self.client_id:
                logger.error("Microsoft OAuth client ID not configured")
                return ""
            # Use manual URL construction to avoid MSAL scope restrictions
            return self._get_fallback_auth_url()
            
        except Exception as e:
            logger.error(f"Error generating auth URL: {e}")
            return ""
    
    def _get_fallback_auth_url(self) -> str:
        """Fallback method to generate auth URL manually"""
        import urllib.parse
        
        if not self.client_id:
            return ""
            
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'openid email profile',  # Use string format for fallback
            'response_type': 'code',
            'response_mode': 'query',
            'prompt': 'select_account',
            'state': 'microsoft'
        }
        
        query_string = urllib.parse.urlencode(params)
        auth_url = f"{self.authority}/oauth2/v2.0/authorize?{query_string}"
        
        logger.info(f"Generated fallback auth URL: {auth_url[:100]}...")
        return auth_url
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token using MSAL"""
        try:
            logger.info(f"Exchanging code for token using MSAL: code_length={len(code)}")
            
            # Use MSAL to exchange code for token
            result = self.app.acquire_token_by_authorization_code(
                code=code,
                scopes=["openid", "email", "profile"],  # Use explicit scope list
                redirect_uri=self.redirect_uri
            )
            
            if "error" in result:
                logger.error(f"MSAL token exchange error: {result}")
                return None
            
            logger.info(f"MSAL token exchange successful: access_token_length={len(result.get('access_token', ''))}")
            return result
            
        except Exception as e:
            logger.error(f"Error in MSAL token exchange: {e}")
            # Fallback to manual token exchange
            return self._fallback_token_exchange(code)
    
    def _fallback_token_exchange(self, code: str) -> Optional[Dict[str, Any]]:
        """Fallback method for token exchange"""
        try:
            token_url = f"{self.authority}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code',
                'scope': 'openid email profile'  # Match the authorization URL scope exactly
            }
            
            logger.info(f"Fallback token exchange: redirect_uri={self.redirect_uri}")
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info(f"Fallback token exchange successful: access_token_length={len(token_data.get('access_token', ''))}")
            return token_data
            
        except Exception as e:
            logger.error(f"Error in fallback token exchange: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
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
            response.raise_for_status()
            
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
            logger.error(f"Error getting user info from Microsoft Graph: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
    
    def handle_oauth_callback(self, code: str) -> Optional[Dict[str, Any]]:
        """Handle complete OAuth callback flow"""
        try:
            logger.info(f"Handling MSAL OAuth callback: code_length={len(code)}")
            
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
            
            logger.info(f"MSAL OAuth callback successful: {user_info.get('email', 'no email')}")
            return user_info
            
        except Exception as e:
            logger.error(f"Error handling MSAL OAuth callback: {e}")
            return None
