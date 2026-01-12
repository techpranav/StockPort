"""
Unified Webhook Handler for Payment Gateways

This module handles webhooks from all payment gateways (Stripe, Razorpay, PayPal)
for license activation and management.
"""

import logging
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

from flask import Flask, request, jsonify
from authx.integrations.sqlite_storage import SQLiteAuthStorage
from authx.core.services import AuthService, LicenseService
from config import AppConfig
from auth.razorpay_service import RazorpayService
# Note: Stripe and PayPal services will be imported when available
try:
    from auth.stripe_service import StripeService
except ImportError:
    StripeService = None

try:
    from auth.paypal_service import PayPalService
except ImportError:
    PayPalService = None

logger = logging.getLogger(__name__)

# Initialize Flask app for webhook endpoints
app = Flask(__name__)

# Initialize services
storage = SQLiteAuthStorage()
license_service = LicenseService(storage, plans=AppConfig.get_auth_settings().get('license_plans', {}))
razorpay_service = RazorpayService()
stripe_service = StripeService() if StripeService else None
paypal_service = PayPalService() if PayPalService else None

@app.route('/webhook/razorpay', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay webhooks."""
    try:
        # Get the webhook payload
        payload = request.get_json()
        signature = request.headers.get('X-Razorpay-Signature')
        
        if not payload:
            logger.error("Empty webhook payload")
            return jsonify({'error': 'Empty payload'}), 400
        
        # Process webhook
        success = razorpay_service.process_webhook(payload, signature)
        
        if success:
            logger.info("Razorpay webhook processed successfully")
            return jsonify({'status': 'success'}), 200
        else:
            logger.error(f"Failed to process Razorpay webhook. Payload: {payload}")
            return jsonify({'error': 'Processing failed', 'payload': payload}), 400
            
    except Exception as e:
        logger.error(f"Error processing Razorpay webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks."""
    if not stripe_service:
        logger.error("Stripe service not available")
        return jsonify({'error': 'Stripe service not configured'}), 400
        
    try:
        # Get the webhook payload
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        
        if not payload:
            logger.error("Empty webhook payload")
            return jsonify({'error': 'Empty payload'}), 400
        
        # Process webhook
        success = stripe_service.process_webhook(payload, sig_header)
        
        if success:
            logger.info("Stripe webhook processed successfully")
            return jsonify({'status': 'success'}), 200
        else:
            logger.error("Failed to process Stripe webhook")
            return jsonify({'error': 'Processing failed'}), 400
            
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    """Handle PayPal webhooks."""
    if not paypal_service:
        logger.error("PayPal service not available")
        return jsonify({'error': 'PayPal service not configured'}), 400
        
    try:
        # Get the webhook payload
        payload = request.get_json()
        signature = request.headers.get('PAYPAL-TRANSMISSION-SIG')
        
        if not payload:
            logger.error("Empty webhook payload")
            return jsonify({'error': 'Empty payload'}), 400
        
        # Process webhook
        success = paypal_service.process_webhook(payload, signature)
        
        if success:
            logger.info("PayPal webhook processed successfully")
            return jsonify({'status': 'success'}), 200
        else:
            logger.error("Failed to process PayPal webhook")
            return jsonify({'error': 'Processing failed'}), 400
            
    except Exception as e:
        logger.error(f"Error processing PayPal webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/webhook/health', methods=['GET'])
def webhook_health():
    """Health check endpoint for webhooks."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'gateways': {
            'razorpay': razorpay_service.is_configured(),
            'stripe': stripe_service.is_configured() if stripe_service else False,
            'paypal': paypal_service.is_configured() if paypal_service else False
        }
    }), 200

if __name__ == '__main__':
    # Run webhook server
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
