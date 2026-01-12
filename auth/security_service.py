"""
Security Service

This module provides security features like rate limiting, CSRF protection, and input validation.
"""

import logging
import time
import hashlib
import secrets
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import re

from config import CSRF_SECRET_KEY, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

logger = logging.getLogger(__name__)

class SecurityService:
    """Service for security features like rate limiting and CSRF protection."""
    
    def __init__(self):
        self.csrf_secret = CSRF_SECRET_KEY
        self.rate_limit_requests = RATE_LIMIT_REQUESTS
        self.rate_limit_window = RATE_LIMIT_WINDOW
        self._rate_limit_store: Dict[str, list] = {}
    
    def generate_csrf_token(self, user_id: int) -> str:
        """Generate a CSRF token for a user."""
        timestamp = str(int(time.time()))
        data = f"{user_id}:{timestamp}:{self.csrf_secret}"
        token = hashlib.sha256(data.encode()).hexdigest()
        return f"{timestamp}:{token}"
    
    def verify_csrf_token(self, token: str, user_id: int) -> bool:
        """Verify a CSRF token."""
        try:
            if not token or ':' not in token:
                return False
            
            timestamp_str, token_hash = token.split(':', 1)
            timestamp = int(timestamp_str)
            
            # Check if token is expired (24 hours)
            if time.time() - timestamp > 86400:
                return False
            
            # Recreate the expected token
            data = f"{user_id}:{timestamp_str}:{self.csrf_secret}"
            expected_hash = hashlib.sha256(data.encode()).hexdigest()
            
            return token_hash == expected_hash
            
        except Exception as e:
            logger.error(f"Error verifying CSRF token: {e}")
            return False
    
    def check_rate_limit(self, identifier: str) -> Tuple[bool, int, int]:
        """
        Check if a request is within rate limits.
        
        Returns:
            Tuple[bool, int, int]: (allowed, remaining_requests, reset_time)
        """
        now = time.time()
        window_start = now - self.rate_limit_window
        
        # Clean old entries
        if identifier in self._rate_limit_store:
            self._rate_limit_store[identifier] = [
                timestamp for timestamp in self._rate_limit_store[identifier]
                if timestamp > window_start
            ]
        else:
            self._rate_limit_store[identifier] = []
        
        # Check current requests
        current_requests = len(self._rate_limit_store[identifier])
        allowed = current_requests < self.rate_limit_requests
        remaining = max(0, self.rate_limit_requests - current_requests)
        reset_time = int(window_start + self.rate_limit_window)
        
        return allowed, remaining, reset_time
    
    def record_request(self, identifier: str):
        """Record a request for rate limiting."""
        now = time.time()
        if identifier not in self._rate_limit_store:
            self._rate_limit_store[identifier] = []
        self._rate_limit_store[identifier].append(now)
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent XSS."""
        # Basic XSS prevention
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        text = text.replace('&', '&amp;')
        return text
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for storage."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """
        Validate username format.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 30:
            return False, "Username must be no more than 30 characters long"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        
        return True, "Username is valid"
    
    def get_client_ip(self, request_headers: Dict[str, str]) -> str:
        """Extract client IP from request headers."""
        # Check for forwarded headers (common in proxy setups)
        for header in ['X-Forwarded-For', 'X-Real-IP', 'X-Client-IP']:
            if header in request_headers:
                return request_headers[header].split(',')[0].strip()
        
        return "unknown"
    
    def is_suspicious_request(self, user_agent: str, ip: str) -> bool:
        """Check if a request appears suspicious."""
        suspicious_patterns = [
            r'bot', r'crawler', r'spider', r'scanner',
            r'nmap', r'sqlmap', r'nikto', r'w3af'
        ]
        
        user_agent_lower = user_agent.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent_lower):
                return True
        
        return False
