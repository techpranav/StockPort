"""
AuthX Core Services

Business logic for authentication and licensing using pluggable storage.
"""

from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime

from authx.core.storage import AuthStorage

class AuthService:
    def __init__(self, storage: AuthStorage, session_timeout_hours: int = 24):
        self.storage = storage
        self.session_timeout_hours = session_timeout_hours

    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        if self.storage.get_user_by_email(email):
            return False, "Email already registered"
        if self.storage.get_user_by_username(username):
            return False, "Username already taken"
        self.storage.create_user(username, email, password)
        return True, "Registration successful"

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        user = self.storage.get_user_by_email(email)
        if not user:
            return False, "Invalid email or password", None
        if not self.storage.verify_password(user['id'], password):
            return False, "Invalid email or password", None
        if not user.get('is_active', 1):
            return False, "Account is deactivated", None
        token = self.storage.create_session(user['id'], self.session_timeout_hours)
        return True, "Login successful", {**user, 'session_token': token}

    def logout(self, session_token: str) -> None:
        self.storage.delete_session(session_token)

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        if not self.storage.verify_password(user_id, current_password):
            return False, "Current password is incorrect"
        self.storage.update_password(user_id, new_password)
        return True, "Password changed"

    def get_current_user(self, session_token: str) -> Optional[Dict[str, Any]]:
        session = self.storage.get_session(session_token)
        if not session:
            return None
        return {
            'id': session['user_id'],
            'username': session['username'],
            'email': session['email'],
            'is_admin': session['is_admin'],
            'session_token': session_token
        }

class LicenseService:
    def __init__(self, storage: AuthStorage, plans: Dict[str, Any]):
        self.storage = storage
        self.plans = plans

    def validate(self, user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        lic = self.storage.get_active_license(user_id)
        if not lic:
            return False, "No active license", None
        try:
            expires_at = datetime.fromisoformat(lic['expires_at'])
        except Exception:
            return False, "Invalid license expiry", lic
        if expires_at <= datetime.now():
            return False, "License expired", lic
        if not lic.get('is_active', 1):
            return False, "License inactive", lic
        return True, "License valid", lic

    def create(self, user_id: int, plan_type: str, expires_days: Optional[int] = None,
               stripe_subscription_id: Optional[str] = None,
               stripe_customer_id: Optional[str] = None) -> str:
        plan = self.plans.get(plan_type)
        if not plan:
            raise ValueError("Invalid plan type")
        days = expires_days or plan.get('expiry_days', 365)
        return self.storage.create_license(user_id, plan_type, days, stripe_subscription_id, stripe_customer_id)

    def plans_list(self) -> Dict[str, Any]:
        return self.plans

    # Convenience helpers for UI layers
    def get_status(self, user_id: int) -> Dict[str, Any]:
        is_valid, message, lic = self.validate(user_id)
        if not lic:
            return {
                'has_license': False,
                'is_valid': False,
                'message': 'No license found',
                'plan_type': None,
                'expires_at': None,
                'days_remaining': 0
            }
        try:
            expires_at_dt = datetime.fromisoformat(lic['expires_at'])
        except Exception:
            return {
                'has_license': True,
                'is_valid': False,
                'message': 'Invalid license expiry',
                'plan_type': lic.get('plan_type'),
                'expires_at': lic.get('expires_at'),
                'days_remaining': 0,
                'license_key': lic.get('license_key')
            }
        days_remaining = max(0, (expires_at_dt - datetime.now()).days)
        return {
            'has_license': True,
            'is_valid': is_valid,
            'message': message,
            'plan_type': lic.get('plan_type'),
            'expires_at': lic.get('expires_at'),
            'days_remaining': days_remaining,
            'license_key': lic.get('license_key')
        }

    def deactivate(self, license_id: int) -> None:
        self.storage.deactivate_license(license_id)

    def user_licenses(self, user_id: int):
        return self.storage.get_user_licenses(user_id)

    def get_by_key(self, license_key: str):
        return self.storage.get_license_by_key(license_key)
