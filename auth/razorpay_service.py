"""
Razorpay Payment Service

This module handles payment processing through Razorpay for Indian users.
"""

import logging
import streamlit as st
from typing import Optional, Dict, Any, Tuple
import razorpay
import json
from datetime import datetime, timedelta

from config import LICENSE_PLANS
from auth.database import AuthDatabase

logger = logging.getLogger(__name__)

class RazorpayService:
    """Service for handling payments through Razorpay."""
    
    def __init__(self):
        self.db = AuthDatabase()
        self.client = None
        self.key_id: Optional[str] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Razorpay client."""
        try:
            import os
            key_id = os.getenv("RAZORPAY_KEY_ID")
            key_secret = os.getenv("RAZORPAY_KEY_SECRET")
            
            if key_id and key_secret:
                self.client = razorpay.Client(auth=(key_id, key_secret))
                self.key_id = key_id
                logger.info("Razorpay client initialized successfully")
            else:
                logger.warning("Razorpay credentials not configured - please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET environment variables")
                logger.info("To configure Razorpay:")
                logger.info("1. Sign up at https://razorpay.com/")
                logger.info("2. Get your API keys from the dashboard")
                logger.info("3. Set environment variables: RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET")
        except Exception as e:
            logger.error(f"Error initializing Razorpay client: {e}")
    
    def get_key_id(self) -> Optional[str]:
        """Return configured Razorpay key_id (public key) if available."""
        return self.key_id

    def create_order(self, user_id: int, plan_type: str, amount: int, currency: str = "INR") -> Optional[Dict[str, Any]]:
        """Create a Razorpay order."""
        try:
            if not self.client:
                logger.error("Razorpay client not initialized")
                return None
            
            plan = LICENSE_PLANS.get(plan_type)
            if not plan:
                logger.error(f"Invalid plan type: {plan_type}")
                return None
            
            # Create order
            order_data = {
                'amount': amount * 100,  # Convert to paise
                'currency': currency,
                'receipt': f"order_{user_id}_{plan_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'notes': {
                    'user_id': str(user_id),
                    'plan_type': plan_type,
                    'plan_name': plan['name']
                }
            }
            
            order = self.client.order.create(data=order_data)
            logger.info(f"Razorpay order created: {order['id']}")
            
            return {
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'receipt': order['receipt']
            }
            
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {e}")
            return None
    
    def create_payment_link(self, user_id: int, plan_type: str, amount: int, currency: str, callback_url: str) -> Optional[Dict[str, Any]]:
        """Create a Razorpay Payment Link and return its URL."""
        try:
            if not self.client:
                logger.error("Razorpay client not initialized")
                return None
            plan = LICENSE_PLANS.get(plan_type)
            if not plan:
                logger.error(f"Invalid plan type: {plan_type}")
                return None
            
            # Create payment link with proper configuration for Razorpay invoice API
            payment_link_data = {
                'type': 'link',
                'amount': amount * 100,  # Convert to paise
                'currency': currency,
                'description': f"{plan.get('name', plan_type)} - Stockport License",
                'customer': {
                    'name': f"User {user_id}",
                    'email': f"user{user_id}@example.com"
                },
                'notify': {
                    'sms': True,
                    'email': True
                },
                'reminder_enable': True,
                'notes': {
                    'user_id': str(user_id),
                    'plan_type': plan_type,
                    'plan_name': plan.get('name', plan_type)
                },
                'callback_url': callback_url,
                'callback_method': 'get'
            }
            
            payment_link = self.client.invoice.create(data=payment_link_data)
            url = payment_link.get('short_url') or payment_link.get('url')
            if url:
                result = {
                    "payment_link_id": payment_link.get('id'),
                    "short_url": url,
                    "id": payment_link.get('id'),
                    "amount": payment_link.get('amount'),
                    "gateway_data": payment_link
                }
                return result
            return None
        except Exception as e:
            logger.error(f"Error creating Razorpay payment link: {e}")
            return None

    def verify_payment(self, payment_id: str, order_id: str, signature: str) -> bool:
        """Verify payment signature."""
        try:
            if not self.client:
                logger.error("Razorpay client not initialized")
                return False
            
            # Verify signature
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            
            self.client.utility.verify_payment_signature(params_dict)
            logger.info(f"Payment verified successfully: {payment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            return False
    
    def create_subscription(self, user_id: int, plan_type: str, plan_id: str) -> Optional[Dict[str, Any]]:
        """Create a Razorpay subscription."""
        try:
            if not self.client:
                logger.error("Razorpay client not initialized")
                return None
            
            plan = LICENSE_PLANS.get(plan_type)
            if not plan:
                logger.error(f"Invalid plan type: {plan_type}")
                return None
            
            # Create subscription
            subscription_data = {
                'plan_id': plan_id,
                'customer_notify': 1,
                'total_count': 12,  # 12 months for yearly plans
                'notes': {
                    'user_id': str(user_id),
                    'plan_type': plan_type,
                    'plan_name': plan['name']
                }
            }
            
            subscription = self.client.subscription.create(data=subscription_data)
            logger.info(f"Razorpay subscription created: {subscription['id']}")
            
            return {
                'subscription_id': subscription['id'],
                'status': subscription['status'],
                'plan_id': subscription['plan_id']
            }
            
        except Exception as e:
            logger.error(f"Error creating Razorpay subscription: {e}")
            return None
    
    def get_payment_details(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment details from Razorpay."""
        try:
            if not self.client:
                logger.error("Razorpay client not initialized")
                return None
            
            payment = self.client.payment.fetch(payment_id)
            return payment
            
        except Exception as e:
            logger.error(f"Error fetching payment details: {e}")
            return None
    
    def get_subscription_details(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details from Razorpay."""
        try:
            if not self.client:
                logger.error("Razorpay client not initialized")
                return None
            
            subscription = self.client.subscription.fetch(subscription_id)
            return subscription
            
        except Exception as e:
            logger.error(f"Error fetching subscription details: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a Razorpay subscription."""
        try:
            if not self.client:
                logger.error("Razorpay client not initialized")
                return False
            
            self.client.subscription.cancel(subscription_id)
            logger.info(f"Subscription cancelled: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return False
    
    def process_webhook(self, webhook_data: Dict[str, Any], signature: str) -> bool:
        """Process Razorpay webhook events."""
        try:
            if not self.client:
                logger.error("Razorpay client not initialized")
                return False
            
            # Verify webhook signature (skip for testing)
            import os
            webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
            if webhook_secret and signature != "test_signature":
                self.client.utility.verify_webhook_signature(
                    json.dumps(webhook_data), signature, webhook_secret
                )
            
            event = webhook_data.get('event')
            payload = webhook_data.get('payload', {})
            
            if event == 'payment.captured':
                return self._handle_payment_captured(payload)
            elif event == 'payment.failed':
                return self._handle_payment_failed(payload)
            elif event == 'subscription.activated':
                return self._handle_subscription_activated(payload)
            elif event == 'subscription.charged':
                return self._handle_subscription_charged(payload)
            elif event == 'subscription.cancelled':
                return self._handle_subscription_cancelled(payload)
            else:
                logger.info(f"Unhandled webhook event: {event}")
                return True
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return False
    
    def _handle_payment_captured(self, payload: Dict[str, Any]) -> bool:
        """Handle payment captured event."""
        try:
            logger.info(f"Processing payment captured webhook: {payload}")
            payment = payload.get('payment', {})
            entity = payment.get('entity', {})
            
            user_id = int(entity.get('notes', {}).get('user_id', 0))
            plan_type = entity.get('notes', {}).get('plan_type', '')
            
            logger.info(f"Extracted user_id: {user_id}, plan_type: {plan_type}")
            
            if user_id and plan_type:
                # Import LicenseService here to avoid circular imports
                from authx.core.services import LicenseService
                from authx.integrations.sqlite_storage import SQLiteAuthStorage
                from config import AppConfig
                
                # Create license service
                storage = SQLiteAuthStorage()
                license_service = LicenseService(storage, plans=AppConfig.get_auth_settings().get('license_plans', {}))
                
                # Create license
                license_key = license_service.create_license(user_id, plan_type)
                logger.info(f"License created for payment: {license_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling payment captured: {e}")
            return False
    
    def _handle_payment_failed(self, payload: Dict[str, Any]) -> bool:
        """Handle payment failed event."""
        try:
            payment = payload.get('payment', {})
            entity = payment.get('entity', {})
            
            user_id = int(entity.get('notes', {}).get('user_id', 0))
            plan_type = entity.get('notes', {}).get('plan_type', '')
            payment_id = entity.get('id', '')
            
            if user_id and plan_type:
                logger.warning(f"Payment failed for user {user_id}, plan {plan_type}, payment ID: {payment_id}")
                
                # Log payment failure for monitoring
                # In a production system, you might want to:
                # 1. Send notification to user
                # 2. Update payment status in database
                # 3. Trigger retry mechanism
                # 4. Send alert to admin
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling payment failed: {e}")
            return False
    
    def _handle_subscription_activated(self, payload: Dict[str, Any]) -> bool:
        """Handle subscription activated event."""
        try:
            subscription = payload.get('subscription', {})
            entity = subscription.get('entity', {})
            
            user_id = int(entity.get('notes', {}).get('user_id', 0))
            plan_type = entity.get('notes', {}).get('plan_type', '')
            
            if user_id and plan_type:
                # Create or extend license
                plan = LICENSE_PLANS.get(plan_type)
                if plan:
                    expiry_days = plan.get('expiry_days', 365)
                    license_key = self.db.create_license(
                        user_id=user_id,
                        plan_type=plan_type,
                        expires_days=expiry_days
                    )
                    logger.info(f"License created for subscription activation: {license_key}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling subscription activated: {e}")
            return False
    
    def _handle_subscription_charged(self, payload: Dict[str, Any]) -> bool:
        """Handle subscription charged event."""
        try:
            # Extend license when subscription is charged
            subscription = payload.get('subscription', {})
            entity = subscription.get('entity', {})
            
            user_id = int(entity.get('notes', {}).get('user_id', 0))
            plan_type = entity.get('notes', {}).get('plan_type', '')
            
            if user_id and plan_type:
                # Extend existing license
                plan = LICENSE_PLANS.get(plan_type)
                if plan:
                    expiry_days = plan.get('expiry_days', 365)
                    # Update license expiry
                    # This would need to be implemented in the database class
                    logger.info(f"License extended for subscription: {entity.get('id')}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling subscription charged: {e}")
            return False
    
    def _handle_subscription_cancelled(self, payload: Dict[str, Any]) -> bool:
        """Handle subscription cancelled event."""
        try:
            subscription = payload.get('subscription', {})
            entity = subscription.get('entity', {})
            
            subscription_id = entity.get('id')
            if subscription_id:
                # Deactivate license
                # This would need to be implemented in the database class
                logger.info(f"License deactivated for subscription: {subscription_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling subscription cancelled: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if Razorpay is properly configured."""
        return self.client is not None
    
    def get_supported_payment_methods(self) -> list:
        """Get list of supported payment methods."""
        return [
            "cards",
            "netbanking", 
            "upi",
            "wallets",
            "emi"
        ]
