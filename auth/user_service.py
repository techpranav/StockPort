"""
User Authentication Service

This module handles user authentication, session management, and social login.
"""

import logging
import streamlit as st
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from auth.database import AuthDatabase
from config import SESSION_TIMEOUT_HOURS, SESSION_SECRET_KEY

logger = logging.getLogger(__name__)

class UserService:
    """Service for user authentication and session management."""
    
    def __init__(self):
        self.db = AuthDatabase()
    
    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """Register a new user."""
        try:
            # Check if user already exists
            if self.db.get_user_by_email(email):
                return False, "Email already registered"
            
            if self.db.get_user_by_username(username):
                return False, "Username already taken"
            
            # Create user
            user_id = self.db.create_user(username, email, password)
            logger.info(f"User registered: {username} ({email})")
            return True, f"User {username} registered successfully"
        
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Login user and return session info."""
        try:
            # Get user by email
            user = self.db.get_user_by_email(email)
            if not user:
                return False, "Invalid email or password", None
            
            # Verify password
            if not self.db.verify_password(user['id'], password):
                return False, "Invalid email or password", None
            
            # Check if user is active
            if not user['is_active']:
                return False, "Account is deactivated", None
            
            # Create session
            session_token = self.db.create_session(user['id'], SESSION_TIMEOUT_HOURS)
            
            # Return user info (without sensitive data)
            user_info = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user['is_admin'],
                'session_token': session_token
            }
            
            logger.info(f"User logged in: {user['username']}")
            return True, "Login successful", user_info
        
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False, f"Login failed: {str(e)}", None
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user by deleting session."""
        try:
            self.db.delete_session(session_token)
            return True
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user from session."""
        try:
            session_token = st.session_state.get('session_token')
            if not session_token:
                return None
            
            session = self.db.get_session(session_token)
            if not session:
                # Session expired or invalid
                st.session_state.pop('session_token', None)
                return None
            
            return {
                'id': session['user_id'],
                'username': session['username'],
                'email': session['email'],
                'is_admin': session['is_admin'],
                'session_token': session_token
            }
        
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.get_current_user() is not None
    
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        user = self.get_current_user()
        return user and user.get('is_admin', False)
    
    def require_auth(self) -> bool:
        """Require authentication - redirect to login if not authenticated."""
        if not self.is_authenticated():
            st.session_state['auth_redirect'] = True
            return False
        return True
    
    def require_admin(self) -> bool:
        """Require admin access - redirect to login if not admin."""
        if not self.is_admin():
            st.error("Admin access required")
            return False
        return True
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            self.db.cleanup_expired_sessions()
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
    
    def social_login_google(self, google_user_info: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Handle Google OAuth login."""
        try:
            provider_user_id = google_user_info.get('sub')  # Google's unique user ID
            email = google_user_info.get('email')
            name = google_user_info.get('name', '')
            
            if not provider_user_id or not email:
                return False, "Invalid Google user info", None
            
            # Check if user exists via social login
            social_user = self.db.get_social_login('google', provider_user_id)
            if social_user:
                # User exists, create new session
                session_token = self.db.create_session(social_user['user_id'], SESSION_TIMEOUT_HOURS)
                user_info = {
                    'id': social_user['user_id'],
                    'username': social_user['username'],
                    'email': social_user['email'],
                    'is_admin': social_user['is_admin'],
                    'session_token': session_token
                }
                return True, "Google login successful", user_info
            
            # Check if email already exists
            existing_user = self.db.get_user_by_email(email)
            if existing_user:
                # Link existing account to Google
                self.db.add_social_login(existing_user['id'], 'google', provider_user_id)
                session_token = self.db.create_session(existing_user['id'], SESSION_TIMEOUT_HOURS)
                user_info = {
                    'id': existing_user['id'],
                    'username': existing_user['username'],
                    'email': existing_user['email'],
                    'is_admin': existing_user['is_admin'],
                    'session_token': session_token
                }
                return True, "Google account linked successfully", user_info
            
            # Create new user
            username = name or email.split('@')[0]
            # Ensure username is unique
            base_username = username
            counter = 1
            while self.db.get_user_by_username(username):
                username = f"{base_username}{counter}"
                counter += 1
            
            user_id = self.db.create_user(username, email, "google_oauth_user")
            self.db.add_social_login(user_id, 'google', provider_user_id)
            
            session_token = self.db.create_session(user_id, SESSION_TIMEOUT_HOURS)
            user_info = {
                'id': user_id,
                'username': username,
                'email': email,
                'is_admin': False,
                'session_token': session_token
            }
            
            logger.info(f"New user created via Google: {username} ({email})")
            return True, "Google account created successfully", user_info
        
        except Exception as e:
            logger.error(f"Error during Google login: {e}")
            return False, f"Google login failed: {str(e)}", None
    
    def social_login_microsoft(self, microsoft_user_info: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Handle Microsoft OAuth login."""
        try:
            provider_user_id = microsoft_user_info.get('sub')  # Microsoft's unique user ID
            email = microsoft_user_info.get('email')
            name = microsoft_user_info.get('name', '')
            
            if not provider_user_id or not email:
                return False, "Invalid Microsoft user info", None
            
            # Check if user exists via social login
            social_user = self.db.get_social_login('microsoft', provider_user_id)
            if social_user:
                # User exists, create new session
                session_token = self.db.create_session(social_user['user_id'], SESSION_TIMEOUT_HOURS)
                user_info = {
                    'id': social_user['user_id'],
                    'username': social_user['username'],
                    'email': social_user['email'],
                    'is_admin': social_user['is_admin'],
                    'session_token': session_token
                }
                return True, "Microsoft login successful", user_info
            
            # Check if email already exists
            existing_user = self.db.get_user_by_email(email)
            if existing_user:
                # Link existing account to Microsoft
                self.db.add_social_login(existing_user['id'], 'microsoft', provider_user_id)
                session_token = self.db.create_session(existing_user['id'], SESSION_TIMEOUT_HOURS)
                user_info = {
                    'id': existing_user['id'],
                    'username': existing_user['username'],
                    'email': existing_user['email'],
                    'is_admin': existing_user['is_admin'],
                    'session_token': session_token
                }
                return True, "Microsoft account linked successfully", user_info
            
            # Create new user
            username = name or email.split('@')[0]
            # Ensure username is unique
            base_username = username
            counter = 1
            while self.db.get_user_by_username(username):
                username = f"{base_username}{counter}"
                counter += 1
            
            user_id = self.db.create_user(username, email, "microsoft_oauth_user")
            self.db.add_social_login(user_id, 'microsoft', provider_user_id)
            
            session_token = self.db.create_session(user_id, SESSION_TIMEOUT_HOURS)
            user_info = {
                'id': user_id,
                'username': username,
                'email': email,
                'is_admin': False,
                'session_token': session_token
            }
            
            logger.info(f"New user created via Microsoft: {username} ({email})")
            return True, "Microsoft account created successfully", user_info
        
        except Exception as e:
            logger.error(f"Error during Microsoft login: {e}")
            return False, f"Microsoft login failed: {str(e)}", None
    
    def social_login(self, provider: str, user_info: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Generic social login handler."""
        if provider == 'google':
            return self.social_login_google(user_info)
        elif provider == 'microsoft':
            return self.social_login_microsoft(user_info)
        else:
            return False, f"Unsupported provider: {provider}", None
    
    def update_user_profile(self, user_id: int, **kwargs) -> bool:
        """Update user profile information."""
        try:
            # This would need to be implemented in the database class
            # For now, return True as placeholder
            return True
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password."""
        try:
            # Verify current password
            if not self.db.verify_password(user_id, current_password):
                return False, "Current password is incorrect"
            
            # Update password securely using bcrypt
            self.db.update_password(user_id, new_password)
            return True, "Password changed successfully"
        
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False, f"Password change failed: {str(e)}"
