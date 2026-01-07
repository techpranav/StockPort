"""
Stripe Webhook Handler

This module handles Stripe webhooks for license activation and management.
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

import stripe
from flask import Flask, request, jsonify

from authx.integrations.sqlite_storage import SQLiteAuthStorage
from authx.core.services import AuthService, LicenseService
from config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, AppConfig

logger = logging.getLogger(__name__)

# Initialize Stripe
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Initialize Flask app for webhook endpoint
app = Flask(__name__)

storage = SQLiteAuthStorage()
user_service = AuthService(storage, session_timeout_hours=AppConfig.get_auth_settings().get('session_timeout_hours', 24))
license_service = LicenseService(storage, plans=AppConfig.get_auth_settings().get('license_plans', {}))

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks."""
    try:
        # Get the webhook payload
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        
        if not STRIPE_WEBHOOK_SECRET:
            logger.error("Stripe webhook secret not configured")
            return jsonify({'error': 'Webhook secret not configured'}), 400
        
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return jsonify({'error': 'Invalid payload'}), 400
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            handle_checkout_completed(event['data']['object'])
        elif event['type'] == 'customer.subscription.created':
            handle_subscription_created(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_deleted(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            handle_payment_failed(event['data']['object'])
        else:
            logger.info(f"Unhandled event type: {event['type']}")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def handle_checkout_completed(session: Dict[str, Any]):
    """Handle completed checkout session."""
    try:
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')
        
        if not customer_id or not subscription_id:
            logger.error("Missing customer or subscription ID in checkout session")
            return
        
        # Get subscription details
        subscription = stripe.Subscription.retrieve(subscription_id)
        plan_type = get_plan_type_from_subscription(subscription)
        
        if not plan_type:
            logger.error(f"Could not determine plan type for subscription {subscription_id}")
            return
        
        # Find or create user
        user = find_or_create_user_from_customer(customer_id)
        if not user:
            logger.error(f"Could not find or create user for customer {customer_id}")
            return
        
        # Create license
        try:
            license_key = license_service.create_stripe_license(
                user['id'], plan_type, subscription_id, customer_id
            )
            logger.info(f"License created for user {user['id']}: {license_key}")
        except Exception as e:
            logger.error(f"Error creating license: {e}")
            
    except Exception as e:
        logger.error(f"Error handling checkout completed: {e}")

def handle_subscription_created(subscription: Dict[str, Any]):
    """Handle subscription creation."""
    try:
        customer_id = subscription.get('customer')
        subscription_id = subscription.get('id')
        plan_type = get_plan_type_from_subscription(subscription)
        
        if not plan_type:
            logger.error(f"Could not determine plan type for subscription {subscription_id}")
            return
        
        # Find user
        user = find_user_from_customer(customer_id)
        if not user:
            logger.error(f"Could not find user for customer {customer_id}")
            return
        
        # Create license
        try:
            license_key = license_service.create_stripe_license(
                user['id'], plan_type, subscription_id, customer_id
            )
            logger.info(f"License created for user {user['id']}: {license_key}")
        except Exception as e:
            logger.error(f"Error creating license: {e}")
            
    except Exception as e:
        logger.error(f"Error handling subscription created: {e}")

def handle_subscription_updated(subscription: Dict[str, Any]):
    """Handle subscription updates."""
    try:
        subscription_id = subscription.get('id')
        plan_type = get_plan_type_from_subscription(subscription)
        
        if not plan_type:
            logger.error(f"Could not determine plan type for subscription {subscription_id}")
            return
        
        # Update license
        try:
            success = license_service.update_stripe_subscription(subscription_id, plan_type)
            if success:
                logger.info(f"License updated for subscription {subscription_id}")
            else:
                logger.error(f"Failed to update license for subscription {subscription_id}")
        except Exception as e:
            logger.error(f"Error updating license: {e}")
            
    except Exception as e:
        logger.error(f"Error handling subscription updated: {e}")

def handle_subscription_deleted(subscription: Dict[str, Any]):
    """Handle subscription deletion."""
    try:
        subscription_id = subscription.get('id')
        
        # Cancel license
        try:
            success = license_service.cancel_stripe_subscription(subscription_id)
            if success:
                logger.info(f"License cancelled for subscription {subscription_id}")
            else:
                logger.error(f"Failed to cancel license for subscription {subscription_id}")
        except Exception as e:
            logger.error(f"Error cancelling license: {e}")
            
    except Exception as e:
        logger.error(f"Error handling subscription deleted: {e}")

def handle_payment_succeeded(invoice: Dict[str, Any]):
    """Handle successful payment."""
    try:
        subscription_id = invoice.get('subscription')
        if subscription_id:
            # Payment succeeded for subscription - extend license
            logger.info(f"Payment succeeded for subscription {subscription_id}")
            
    except Exception as e:
        logger.error(f"Error handling payment succeeded: {e}")

def handle_payment_failed(invoice: Dict[str, Any]):
    """Handle failed payment."""
    try:
        subscription_id = invoice.get('subscription')
        if subscription_id:
            # Payment failed for subscription - may need to suspend license
            logger.warning(f"Payment failed for subscription {subscription_id}")
            
    except Exception as e:
        logger.error(f"Error handling payment failed: {e}")

def get_plan_type_from_subscription(subscription: Dict[str, Any]) -> Optional[str]:
    """Extract plan type from Stripe subscription."""
    try:
        items = subscription.get('items', {}).get('data', [])
        if not items:
            return None
        
        price_id = items[0].get('price', {}).get('id')
        if not price_id:
            return None
        
        # Map Stripe price IDs to plan types
        plan_mapping = {
            'price_basic_monthly': 'basic_monthly',
            'price_basic_yearly': 'basic_yearly',
            'price_pro_monthly': 'pro_monthly',
            'price_pro_yearly': 'pro_yearly',
        }
        
        return plan_mapping.get(price_id)
        
    except Exception as e:
        logger.error(f"Error extracting plan type: {e}")
        return None

def find_user_from_customer(customer_id: str) -> Optional[Dict[str, Any]]:
    """Find user by Stripe customer ID."""
    try:
        # This would need to be implemented in the database
        # For now, return None as placeholder
        return None
    except Exception as e:
        logger.error(f"Error finding user from customer: {e}")
        return None

def find_or_create_user_from_customer(customer_id: str) -> Optional[Dict[str, Any]]:
    """Find or create user from Stripe customer ID."""
    try:
        # Get customer details from Stripe
        customer = stripe.Customer.retrieve(customer_id)
        email = customer.get('email')
        
        if not email:
            logger.error(f"No email found for customer {customer_id}")
            return None
        
        # Find existing user by email
        user = user_service.db.get_user_by_email(email)
        if user:
            return user
        
        # Create new user
        name = customer.get('name', '')
        username = name or email.split('@')[0]
        
        # Ensure username is unique
        base_username = username
        counter = 1
        while user_service.db.get_user_by_username(username):
            username = f"{base_username}{counter}"
            counter += 1
        
        user_id = user_service.db.create_user(username, email, "stripe_user")
        
        return user_service.db.get_user_by_id(user_id)
        
    except Exception as e:
        logger.error(f"Error finding or creating user from customer: {e}")
        return None

def run_webhook_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """Run the webhook server."""
    try:
        logger.info(f"Starting Stripe webhook server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.error(f"Error starting webhook server: {e}")

if __name__ == '__main__':
    run_webhook_server()
