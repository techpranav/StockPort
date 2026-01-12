"""
AuthX SQLite Storage Implementation

Thin adapter around the existing auth.database.AuthDatabase to match AuthStorage.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from auth.database import AuthDatabase
from authx.core.storage import AuthStorage

class SQLiteAuthStorage(AuthStorage):
    def __init__(self, db: Optional[AuthDatabase] = None):
        self.db = db or AuthDatabase()

    # User management
    def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> int:
        return self.db.create_user(username, email, password, is_admin)

    def update_password(self, user_id: int, new_password: str) -> None:
        self.db.update_password(user_id, new_password)

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.db.get_user_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.db.get_user_by_email(email)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self.db.get_user_by_username(username)

    def verify_password(self, user_id: int, password: str) -> bool:
        return self.db.verify_password(user_id, password)

    # Sessions
    def create_session(self, user_id: int, expires_hours: int = 24) -> str:
        return self.db.create_session(user_id, expires_hours)

    def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        return self.db.get_session(session_token)

    def delete_session(self, session_token: str) -> None:
        self.db.delete_session(session_token)

    def cleanup_expired_sessions(self) -> None:
        self.db.cleanup_expired_sessions()

    # Licensing
    def create_license(self, user_id: int, plan_type: str, expires_days: int = 365,
                       stripe_subscription_id: Optional[str] = None,
                       stripe_customer_id: Optional[str] = None) -> str:
        return self.db.create_license(user_id, plan_type, expires_days, stripe_subscription_id, stripe_customer_id)

    def get_active_license(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.db.get_active_license(user_id)

    def get_license_by_key(self, license_key: str) -> Optional[Dict[str, Any]]:
        return self.db.get_license_by_key(license_key)

    def update_license_expiry(self, license_id: int, expires_days: int) -> None:
        self.db.update_license_expiry(license_id, expires_days)

    def deactivate_license(self, license_id: int) -> None:
        self.db.deactivate_license(license_id)

    def get_user_licenses(self, user_id: int) -> List[Dict[str, Any]]:
        return self.db.get_user_licenses(user_id)

    # Admin
    def get_all_users(self) -> List[Dict[str, Any]]:
        return self.db.get_all_users()

    # Social logins
    def add_social_login(self, user_id: int, provider: str, provider_user_id: str,
                         access_token: Optional[str] = None, refresh_token: Optional[str] = None,
                         expires_at: Optional[datetime] = None) -> None:
        self.db.add_social_login(user_id, provider, provider_user_id, access_token, refresh_token, expires_at)

    def get_social_login(self, provider: str, provider_user_id: str) -> Optional[Dict[str, Any]]:
        return self.db.get_social_login(provider, provider_user_id)
