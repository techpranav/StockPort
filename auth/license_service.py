"""
License Management Service

This module handles license validation, activation, and Stripe integration.
"""

import logging
import streamlit as st
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime, timedelta

from auth.database import AuthDatabase
from config import LICENSE_PLANS

logger = logging.getLogger(__name__)

class LicenseService:
    """Service for license management and validation."""
    
    def __init__(self):
        self.db = AuthDatabase()
    
    def create_license(self, user_id: int, plan_type: str, expires_days: int = 365,
                       stripe_subscription_id: Optional[str] = None,
                       stripe_customer_id: Optional[str] = None) -> str:
        """Create a new license for a user."""
        try:
            license_key = self.db.create_license(
                user_id, plan_type, expires_days, 
                stripe_subscription_id, stripe_customer_id
            )
            logger.info(f"License created for user {user_id}: {license_key}")
            return license_key
        except Exception as e:
            logger.error(f"Error creating license: {e}")
            raise
    
    def get_user_license(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's active license."""
        try:
            return self.db.get_active_license(user_id)
        except Exception as e:
            logger.error(f"Error getting user license: {e}")
            return None
    
    def validate_license(self, user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Validate if user has an active license."""
        try:
            license_info = self.get_user_license(user_id)
            if not license_info:
                return False, "No active license found", None
            
            # Check if license is expired
            expires_at = datetime.fromisoformat(license_info['expires_at'])
            if expires_at <= datetime.now():
                return False, "License has expired", None
            
            # Check if license is active
            if not license_info['is_active']:
                return False, "License is deactivated", None
            
            return True, "License is valid", license_info
        
        except Exception as e:
            logger.error(f"Error validating license: {e}")
            return False, f"License validation failed: {str(e)}", None
    
    def activate_license_key(self, user_id: int, license_key: str) -> Tuple[bool, str]:
        """Activate a license key for a user."""
        try:
            # Get license by key
            license_info = self.db.get_license_by_key(license_key)
            if not license_info:
                return False, "Invalid license key"
            
            # Check if license is already assigned
            if license_info['user_id'] != user_id:
                return False, "License key is already assigned to another user"
            
            # Check if license is active
            if not license_info['is_active']:
                return False, "License key is deactivated"
            
            # Check if license is expired
            expires_at = datetime.fromisoformat(license_info['expires_at'])
            if expires_at <= datetime.now():
                return False, "License key has expired"
            
            return True, "License activated successfully"
        
        except Exception as e:
            logger.error(f"Error activating license: {e}")
            return False, f"License activation failed: {str(e)}"
    
    def get_license_plans(self) -> Dict[str, Any]:
        """Get available license plans."""
        return LICENSE_PLANS
    
    def get_plan_info(self, plan_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plan."""
        return LICENSE_PLANS.get(plan_type)
    
    def create_stripe_license(self, user_id: int, plan_type: str, 
                             stripe_subscription_id: str, stripe_customer_id: str) -> str:
        """Create a license from Stripe subscription."""
        try:
            plan_info = self.get_plan_info(plan_type)
            if not plan_info:
                raise ValueError(f"Invalid plan type: {plan_type}")
            
            expires_days = plan_info.get('expiry_days', 365)
            license_key = self.create_license(
                user_id, plan_type, expires_days,
                stripe_subscription_id, stripe_customer_id
            )
            
            logger.info(f"Stripe license created: {license_key} for user {user_id}")
            return license_key
        
        except Exception as e:
            logger.error(f"Error creating Stripe license: {e}")
            raise
    
    def update_stripe_subscription(self, stripe_subscription_id: str, 
                                  new_plan_type: str) -> bool:
        """Update license when Stripe subscription changes."""
        try:
            # This would need to be implemented in the database class
            # For now, return True as placeholder
            return True
        except Exception as e:
            logger.error(f"Error updating Stripe subscription: {e}")
            return False
    
    def cancel_stripe_subscription(self, stripe_subscription_id: str) -> bool:
        """Cancel license when Stripe subscription is cancelled."""
        try:
            # This would need to be implemented in the database class
            # For now, return True as placeholder
            return True
        except Exception as e:
            logger.error(f"Error cancelling Stripe subscription: {e}")
            return False
    
    def get_user_licenses(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all licenses for a user."""
        try:
            return self.db.get_user_licenses(user_id)
        except Exception as e:
            logger.error(f"Error getting user licenses: {e}")
            return []
    
    def deactivate_license(self, license_id: int) -> bool:
        """Deactivate a license."""
        try:
            self.db.deactivate_license(license_id)
            return True
        except Exception as e:
            logger.error(f"Error deactivating license: {e}")
            return False
    
    def extend_license(self, license_id: int, additional_days: int) -> bool:
        """Extend a license by additional days."""
        try:
            license_info = self.db.get_license_by_key(license_id)
            if not license_info:
                return False
            
            current_expires_at = datetime.fromisoformat(license_info['expires_at'])
            new_expires_at = current_expires_at + timedelta(days=additional_days)
            
            # Update the license expiry
            self.db.update_license_expiry(license_id, (new_expires_at - datetime.now()).days)
            return True
        
        except Exception as e:
            logger.error(f"Error extending license: {e}")
            return False
    
    def require_valid_license(self) -> bool:
        """Require valid license - redirect to license activation if not licensed."""
        try:
            user = st.session_state.get('current_user')
            if not user:
                return False
            
            is_valid, message, license_info = self.validate_license(user['id'])
            if not is_valid:
                st.session_state['license_redirect'] = True
                st.session_state['license_message'] = message
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking license requirement: {e}")
            return False
    
    def get_license_status(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive license status for a user."""
        try:
            is_valid, message, license_info = self.validate_license(user_id)
            
            if not license_info:
                return {
                    'has_license': False,
                    'is_valid': False,
                    'message': 'No license found',
                    'plan_type': None,
                    'expires_at': None,
                    'days_remaining': 0
                }
            
            expires_at = datetime.fromisoformat(license_info['expires_at'])
            days_remaining = (expires_at - datetime.now()).days
            
            return {
                'has_license': True,
                'is_valid': is_valid,
                'message': message,
                'plan_type': license_info['plan_type'],
                'expires_at': license_info['expires_at'],
                'days_remaining': max(0, days_remaining),
                'license_key': license_info['license_key']
            }
        
        except Exception as e:
            logger.error(f"Error getting license status: {e}")
            return {
                'has_license': False,
                'is_valid': False,
                'message': f'Error: {str(e)}',
                'plan_type': None,
                'expires_at': None,
                'days_remaining': 0
            }
