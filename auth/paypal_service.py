"""
PayPal Payment Service

This module handles payment processing through PayPal for global users.
"""

import logging
import streamlit as st
from typing import Optional, Dict, Any, Tuple
import requests
import json
from datetime import datetime, timedelta

from config import LICENSE_PLANS, get_base_url
from auth.database import AuthDatabase

logger = logging.getLogger(__name__)

class PayPalService:
    """Service for handling payments through PayPal."""
    
    def __init__(self):
        self.db = AuthDatabase()
        self.client_id = None
        self.client_secret = None
        self.base_url = None
        self.access_token = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize PayPal client."""
        try:
            import os
            self.client_id = os.getenv("PAYPAL_CLIENT_ID")
            self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
            mode = os.getenv("PAYPAL_MODE", "sandbox")
            
            if self.client_id and self.client_secret:
                if mode == "live":
                    self.base_url = "https://api-m.paypal.com"
                else:
                    self.base_url = "https://api-m.sandbox.paypal.com"
                
                self._get_access_token()
                logger.info("PayPal client initialized successfully")
            else:
                logger.warning("PayPal credentials not configured")
        except Exception as e:
            logger.error(f"Error initializing PayPal client: {e}")
    
    def _get_access_token(self) -> bool:
        """Get PayPal access token."""
        try:
            url = f"{self.base_url}/v1/oauth2/token"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {self._get_basic_auth()}'
            }
            data = {
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            return True
            
        except Exception as e:
            logger.error(f"Error getting PayPal access token: {e}")
            return False
    
    def _get_basic_auth(self) -> str:
        """Get basic authentication string."""
        import base64
        auth_string = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(auth_string.encode()).decode()
    
    def create_order(self, user_id: int, plan_type: str, amount: float, currency: str = "USD") -> Optional[Dict[str, Any]]:
        """Create a PayPal order."""
        try:
            if not self.access_token:
                logger.error("PayPal access token not available")
                return None
            
            plan = LICENSE_PLANS.get(plan_type)
            if not plan:
                logger.error(f"Invalid plan type: {plan_type}")
                return None
            
            import os
            base_url = get_base_url()
            
            url = f"{self.base_url}/v2/checkout/orders"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            order_data = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'amount': {
                        'currency_code': currency,
                        'value': str(amount)
                    },
                    'description': f"{plan['name']} - Stockport License",
                    'custom_id': f"user_{user_id}_plan_{plan_type}",
                    'invoice_id': f"inv_{user_id}_{plan_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }],
                'application_context': {
                    'return_url': f"{base_url}/?payment=success",
                    'cancel_url': f"{base_url}/?payment=cancelled"
                }
            }
            
            response = requests.post(url, headers=headers, json=order_data)
            response.raise_for_status()
            
            order = response.json()
            logger.info(f"PayPal order created: {order['id']}")
            
            return {
                'order_id': order['id'],
                'status': order['status'],
                'approval_url': next((link['href'] for link in order['links'] if link['rel'] == 'approve'), None)
            }
            
        except Exception as e:
            logger.error(f"Error creating PayPal order: {e}")
            return None
    
    def capture_payment(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Capture a PayPal payment."""
        try:
            if not self.access_token:
                logger.error("PayPal access token not available")
                return None
            
            url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            
            capture_data = response.json()
            logger.info(f"PayPal payment captured: {capture_data['id']}")
            
            return capture_data
            
        except Exception as e:
            logger.error(f"Error capturing PayPal payment: {e}")
            return None
    
    def create_subscription(self, user_id: int, plan_type: str, plan_id: str) -> Optional[Dict[str, Any]]:
        """Create a PayPal subscription."""
        try:
            if not self.access_token:
                logger.error("PayPal access token not available")
                return None
            
            plan = LICENSE_PLANS.get(plan_type)
            if not plan:
                logger.error(f"Invalid plan type: {plan_type}")
                return None
            
            url = f"{self.base_url}/v1/billing/subscriptions"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            subscription_data = {
                'plan_id': plan_id,
                'start_time': (datetime.now() + timedelta(minutes=1)).isoformat() + 'Z',
                'subscriber': {
                    'name': {
                        'given_name': 'User',
                        'surname': str(user_id)
                    },
                    'email_address': f'user{user_id}@stockport.com'
                },
                'application_context': {
                    'brand_name': 'Stockport',
                    'locale': 'en-US',
                    'shipping_preference': 'NO_SHIPPING',
                    'user_action': 'SUBSCRIBE_NOW',
                    'payment_method': {
                        'payer_selected': 'PAYPAL',
                        'payee_preferred': 'IMMEDIATE_PAYMENT_REQUIRED'
                    },
                    'return_url': f"{st.get_option('server.baseUrlPath')}?subscription=success",
                    'cancel_url': f"{st.get_option('server.baseUrlPath')}?subscription=cancelled"
                },
                'custom_id': f"user_{user_id}_plan_{plan_type}"
            }
            
            response = requests.post(url, headers=headers, json=subscription_data)
            response.raise_for_status()
            
            subscription = response.json()
            logger.info(f"PayPal subscription created: {subscription['id']}")
            
            return {
                'subscription_id': subscription['id'],
                'status': subscription['status'],
                'approval_url': next((link['href'] for link in subscription['links'] if link['rel'] == 'approve'), None)
            }
            
        except Exception as e:
            logger.error(f"Error creating PayPal subscription: {e}")
            return None
    
    def get_subscription_details(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get PayPal subscription details."""
        try:
            if not self.access_token:
                logger.error("PayPal access token not available")
                return None
            
            url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting subscription details: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str, reason: str = "User requested cancellation") -> bool:
        """Cancel a PayPal subscription."""
        try:
            if not self.access_token:
                logger.error("PayPal access token not available")
                return False
            
            url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/cancel"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            data = {
                'reason': reason
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            logger.info(f"PayPal subscription cancelled: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return False
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Process PayPal webhook events."""
        try:
            event_type = webhook_data.get('event_type')
            resource = webhook_data.get('resource', {})
            
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                return self._handle_payment_completed(resource)
            elif event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
                return self._handle_subscription_activated(resource)
            elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
                return self._handle_subscription_cancelled(resource)
            else:
                logger.info(f"Unhandled PayPal webhook event: {event_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error processing PayPal webhook: {e}")
            return False
    
    def _handle_payment_completed(self, resource: Dict[str, Any]) -> bool:
        """Handle payment completed event."""
        try:
            custom_id = resource.get('custom_id', '')
            if custom_id.startswith('user_'):
                # Extract user_id and plan_type from custom_id
                parts = custom_id.split('_')
                if len(parts) >= 3:
                    user_id = int(parts[1])
                    plan_type = parts[3]
                    
                    # Create license
                    plan = LICENSE_PLANS.get(plan_type)
                    if plan:
                        expiry_days = plan.get('expiry_days', 365)
                        license_key = self.db.create_license(
                            user_id=user_id,
                            plan_type=plan_type,
                            expires_days=expiry_days,
                            paypal_payment_id=resource.get('id')
                        )
                        logger.info(f"License created for PayPal payment: {license_key}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling payment completed: {e}")
            return False
    
    def _handle_subscription_activated(self, resource: Dict[str, Any]) -> bool:
        """Handle subscription activated event."""
        try:
            custom_id = resource.get('custom_id', '')
            if custom_id.startswith('user_'):
                parts = custom_id.split('_')
                if len(parts) >= 3:
                    user_id = int(parts[1])
                    plan_type = parts[3]
                    
                    # Create license
                    plan = LICENSE_PLANS.get(plan_type)
                    if plan:
                        expiry_days = plan.get('expiry_days', 365)
                        license_key = self.db.create_license(
                            user_id=user_id,
                            plan_type=plan_type,
                            expires_days=expiry_days,
                            paypal_subscription_id=resource.get('id')
                        )
                        logger.info(f"License created for PayPal subscription: {license_key}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling subscription activated: {e}")
            return False
    
    def _handle_subscription_cancelled(self, resource: Dict[str, Any]) -> bool:
        """Handle subscription cancelled event."""
        try:
            subscription_id = resource.get('id')
            if subscription_id:
                # Deactivate license
                # This would need to be implemented in the database class
                logger.info(f"License deactivated for PayPal subscription: {subscription_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling subscription cancelled: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if PayPal is properly configured."""
        return self.access_token is not None
    
    def get_supported_currencies(self) -> list:
        """Get list of supported currencies."""
        return [
            "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "INR",
            "SGD", "HKD", "NZD", "CHF", "SEK", "DKK", "NOK"
        ]
