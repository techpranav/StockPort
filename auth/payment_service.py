"""
Payment Service

This module handles payment processing and license purchases through Stripe.
"""

import logging
import streamlit as st
from typing import Optional, Dict, Any, Tuple
import stripe

from config import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, LICENSE_PLANS
from auth.database import AuthDatabase

logger = logging.getLogger(__name__)

# Initialize Stripe
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

class PaymentService:
    """Service for handling payments and license purchases."""
    
    def __init__(self):
        self.db = AuthDatabase()
        self.stripe_publishable_key = STRIPE_PUBLISHABLE_KEY
    
    def create_checkout_session(self, user_id: int, plan_type: str, success_url: str, cancel_url: str) -> Optional[str]:
        """Create a Stripe checkout session for license purchase."""
        try:
            if not STRIPE_SECRET_KEY:
                logger.error("Stripe secret key not configured")
                return None
            
            plan = LICENSE_PLANS.get(plan_type)
            if not plan:
                logger.error(f"Invalid plan type: {plan_type}")
                return None
            
            stripe_price_id = plan.get('stripe_price_id')
            if not stripe_price_id:
                logger.error(f"No Stripe price ID configured for plan: {plan_type}")
                return None
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': stripe_price_id,
                    'quantity': 1,
                }],
                mode='subscription' if 'monthly' in plan_type or 'yearly' in plan_type else 'payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(user_id),
                metadata={
                    'user_id': str(user_id),
                    'plan_type': plan_type,
                    'plan_name': plan['name']
                }
            )
            
            logger.info(f"Created checkout session for user {user_id}, plan {plan_type}")
            return session.url
            
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            return None
    
    def create_payment_intent(self, user_id: int, plan_type: str) -> Optional[Dict[str, Any]]:
        """Create a payment intent for one-time payments."""
        try:
            if not STRIPE_SECRET_KEY:
                logger.error("Stripe secret key not configured")
                return None
            
            plan = LICENSE_PLANS.get(plan_type)
            if not plan:
                logger.error(f"Invalid plan type: {plan_type}")
                return None
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(plan['price'] * 100),  # Convert to cents
                currency=plan.get('currency', 'usd'),
                metadata={
                    'user_id': str(user_id),
                    'plan_type': plan_type,
                    'plan_name': plan['name']
                }
            )
            
            logger.info(f"Created payment intent for user {user_id}, plan {plan_type}")
            return {
                'client_secret': intent.client_secret,
                'amount': intent.amount,
                'currency': intent.currency
            }
            
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            return None
    
    def get_available_plans(self) -> Dict[str, Any]:
        """Get available license plans with pricing information."""
        return LICENSE_PLANS
    
    def get_plan_details(self, plan_type: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific plan."""
        return LICENSE_PLANS.get(plan_type)
    
    def process_webhook_event(self, event: Dict[str, Any]) -> bool:
        """Process Stripe webhook events."""
        try:
            event_type = event['type']
            
            if event_type == 'checkout.session.completed':
                return self._handle_checkout_completed(event['data']['object'])
            elif event_type == 'customer.subscription.created':
                return self._handle_subscription_created(event['data']['object'])
            elif event_type == 'customer.subscription.updated':
                return self._handle_subscription_updated(event['data']['object'])
            elif event_type == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event['data']['object'])
            elif event_type == 'invoice.payment_succeeded':
                return self._handle_payment_succeeded(event['data']['object'])
            elif event_type == 'invoice.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            else:
                logger.info(f"Unhandled event type: {event_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error processing webhook event: {e}")
            return False
    
    def _handle_checkout_completed(self, session: Dict[str, Any]) -> bool:
        """Handle completed checkout session."""
        try:
            user_id = int(session['metadata']['user_id'])
            plan_type = session['metadata']['plan_type']
            
            # Create license
            plan = LICENSE_PLANS.get(plan_type)
            if not plan:
                logger.error(f"Invalid plan type in webhook: {plan_type}")
                return False
            
            # Calculate expiry based on plan
            expiry_days = plan.get('expiry_days', 365)
            
            # Create license
            license_key = self.db.create_license(
                user_id=user_id,
                plan_type=plan_type,
                expires_days=expiry_days,
                stripe_subscription_id=session.get('subscription'),
                stripe_customer_id=session.get('customer')
            )
            
            logger.info(f"License created for user {user_id}: {license_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling checkout completed: {e}")
            return False
    
    def _handle_subscription_created(self, subscription: Dict[str, Any]) -> bool:
        """Handle subscription creation."""
        try:
            # This is handled by checkout.session.completed for new subscriptions
            logger.info(f"Subscription created: {subscription['id']}")
            return True
        except Exception as e:
            logger.error(f"Error handling subscription created: {e}")
            return False
    
    def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> bool:
        """Handle subscription updates."""
        try:
            # Update license status based on subscription status
            subscription_id = subscription['id']
            status = subscription['status']
            
            # Find license by subscription ID and update
            # This would need to be implemented in the database class
            logger.info(f"Subscription updated: {subscription_id}, status: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling subscription updated: {e}")
            return False
    
    def _handle_subscription_deleted(self, subscription: Dict[str, Any]) -> bool:
        """Handle subscription deletion."""
        try:
            # Deactivate license when subscription is cancelled
            subscription_id = subscription['id']
            
            # Find license by subscription ID and deactivate
            # This would need to be implemented in the database class
            logger.info(f"Subscription deleted: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling subscription deleted: {e}")
            return False
    
    def _handle_payment_succeeded(self, invoice: Dict[str, Any]) -> bool:
        """Handle successful payment."""
        try:
            # Extend license or reactivate if payment succeeds
            subscription_id = invoice.get('subscription')
            if subscription_id:
                logger.info(f"Payment succeeded for subscription: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment succeeded: {e}")
            return False
    
    def _handle_payment_failed(self, invoice: Dict[str, Any]) -> bool:
        """Handle failed payment."""
        try:
            # Handle failed payment (e.g., send notification, deactivate license)
            subscription_id = invoice.get('subscription')
            if subscription_id:
                logger.warning(f"Payment failed for subscription: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment failed: {e}")
            return False
    
    def get_customer_portal_url(self, customer_id: str, return_url: str) -> Optional[str]:
        """Get Stripe customer portal URL for subscription management."""
        try:
            if not STRIPE_SECRET_KEY:
                return None
            
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            
            return session.url
            
        except Exception as e:
            logger.error(f"Error creating customer portal session: {e}")
            return None
    
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return STRIPE_SECRET_KEY is not None and STRIPE_PUBLISHABLE_KEY is not None
