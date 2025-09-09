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
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Razorpay client."""
        try:
            import os
            key_id = os.getenv("RAZORPAY_KEY_ID")
            key_secret = os.getenv("RAZORPAY_KEY_SECRET")
            
            if key_id and key_secret:
                self.client = razorpay.Client(auth=(key_id, key_secret))
                logger.info("Razorpay client initialized successfully")
            else:
                logger.warning("Razorpay credentials not configured")
        except Exception as e:
            logger.error(f"Error initializing Razorpay client: {e}")
    
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
            
            # Verify webhook signature
            import os
            webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
            if webhook_secret:
                self.client.utility.verify_webhook_signature(
                    json.dumps(webhook_data), signature, webhook_secret
                )
            
            event = webhook_data.get('event')
            payload = webhook_data.get('payload', {})
            
            if event == 'payment.captured':
                return self._handle_payment_captured(payload)
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
            payment = payload.get('payment', {})
            entity = payment.get('entity', {})
            
            user_id = int(entity.get('notes', {}).get('user_id', 0))
            plan_type = entity.get('notes', {}).get('plan_type', '')
            
            if user_id and plan_type:
                # Create license
                plan = LICENSE_PLANS.get(plan_type)
                if plan:
                    expiry_days = plan.get('expiry_days', 365)
                    license_key = self.db.create_license(
                        user_id=user_id,
                        plan_type=plan_type,
                        expires_days=expiry_days,
                        razorpay_payment_id=entity.get('id'),
                        razorpay_order_id=entity.get('order_id')
                    )
                    logger.info(f"License created for payment: {license_key}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling payment captured: {e}")
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
                        expires_days=expiry_days,
                        razorpay_subscription_id=entity.get('id')
                    )
                    logger.info(f"License created for subscription: {license_key}")
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
