"""
Authentication and Licensing Database

This module handles the SQLite database for user management and licensing.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import hashlib
import secrets
import bcrypt

from config import AUTH_DATABASE_PATH

logger = logging.getLogger(__name__)

class AuthDatabase:
    """SQLite database for authentication and licensing."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or AUTH_DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    salt VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    license_key VARCHAR(100) UNIQUE NOT NULL,
                    plan_type VARCHAR(50) NOT NULL,
                    stripe_subscription_id VARCHAR(100),
                    stripe_customer_id VARCHAR(100),
                    is_active BOOLEAN DEFAULT 1,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS social_logins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    provider VARCHAR(50) NOT NULL,
                    provider_user_id VARCHAR(100) NOT NULL,
                    access_token VARCHAR(500),
                    refresh_token VARCHAR(500),
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(provider, provider_user_id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_licenses_user_id ON licenses(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_licenses_key ON licenses(license_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_social_logins_user_id ON social_logins(user_id)")
            
            conn.commit()
    
    def _hash_password(self, password: str) -> Dict[str, str]:
        """Hash password using bcrypt and return dict with hash and salt (salt kept for legacy)."""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        return {"hash": password_hash, "salt": salt.decode("utf-8")}
    
    def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> int:
        """Create a new user and return the user ID."""
        pw = self._hash_password(password)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO users (username, email, password_hash, salt, is_admin)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, pw["hash"], pw["salt"], is_admin))
            return cursor.lastrowid
    
    def update_password(self, user_id: int, new_password: str) -> None:
        """Securely update user's password."""
        pw = self._hash_password(new_password)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users SET password_hash = ?, salt = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (pw["hash"], pw["salt"], user_id))
            conn.commit()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM users WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM users WHERE email = ?
            """, (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM users WHERE username = ?
            """, (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def verify_password(self, user_id: int, password: str) -> bool:
        """Verify user password using bcrypt."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        try:
            stored_hash = user['password_hash']
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        except Exception:
            return False
    
    def create_session(self, user_id: int, expires_hours: int = 24) -> str:
        """Create a new session and return the session token."""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            """, (user_id, session_token, expires_at))
            conn.commit()
        
        return session_token
    
    def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session by token if it's still valid."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT s.*, u.username, u.email, u.is_admin
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.expires_at > ?
            """, (session_token, datetime.now()))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_session(self, session_token: str):
        """Delete a session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
            conn.commit()
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (datetime.now(),))
            conn.commit()
    
    def create_license(self, user_id: int, plan_type: str, expires_days: int = 365,
                       stripe_subscription_id: Optional[str] = None,
                       stripe_customer_id: Optional[str] = None) -> str:
        """Create a new license and return the license key."""
        license_key = f"STK-{secrets.token_hex(8).upper()}"
        expires_at = datetime.now() + timedelta(days=expires_days)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO licenses (user_id, license_key, plan_type, stripe_subscription_id, 
                                    stripe_customer_id, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, license_key, plan_type, stripe_subscription_id, 
                  stripe_customer_id, expires_at))
            conn.commit()
        
        return license_key
    
    def get_active_license(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's active license."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM licenses 
                WHERE user_id = ? AND is_active = 1 AND expires_at > ?
                ORDER BY expires_at DESC
                LIMIT 1
            """, (user_id, datetime.now()))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_license_by_key(self, license_key: str) -> Optional[Dict[str, Any]]:
        """Get license by key."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT l.*, u.username, u.email
                FROM licenses l
                JOIN users u ON l.user_id = u.id
                WHERE l.license_key = ?
            """, (license_key,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_license_expiry(self, license_id: int, expires_days: int):
        """Update license expiry date."""
        expires_at = datetime.now() + timedelta(days=expires_days)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE licenses SET expires_at = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (expires_at, license_id))
            conn.commit()
    
    def deactivate_license(self, license_id: int):
        """Deactivate a license."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE licenses SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (license_id,))
            conn.commit()
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (admin only)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT u.*, l.license_key, l.plan_type, l.expires_at as license_expires_at
                FROM users u
                LEFT JOIN licenses l ON u.id = l.user_id AND l.is_active = 1
                ORDER BY u.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_licenses(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all licenses for a user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM licenses WHERE user_id = ? ORDER BY created_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def add_social_login(self, user_id: int, provider: str, provider_user_id: str,
                        access_token: Optional[str] = None, refresh_token: Optional[str] = None,
                        expires_at: Optional[datetime] = None):
        """Add or update social login information."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO social_logins 
                (user_id, provider, provider_user_id, access_token, refresh_token, expires_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, provider, provider_user_id, access_token, refresh_token, expires_at))
            conn.commit()
    
    def get_social_login(self, provider: str, provider_user_id: str) -> Optional[Dict[str, Any]]:
        """Get social login by provider and provider user ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT sl.*, u.username, u.email, u.is_admin
                FROM social_logins sl
                JOIN users u ON sl.user_id = u.id
                WHERE sl.provider = ? AND sl.provider_user_id = ?
            """, (provider, provider_user_id))
            row = cursor.fetchone()
            return dict(row) if row else None
