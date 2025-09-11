#!/usr/bin/env python3
"""
Webhook Server Runner

This script runs the webhook server for handling payment gateway webhooks.
Run this alongside your main Streamlit app for production deployments.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Run the webhook server."""
    try:
        # Import and run the webhook handler
        from auth.webhook_handler import app
        
        # Get configuration
        port = int(os.getenv('WEBHOOK_PORT', 5000))
        host = os.getenv('WEBHOOK_HOST', '0.0.0.0')
        debug = os.getenv('WEBHOOK_DEBUG', 'false').lower() == 'true'
        
        logger.info(f"Starting webhook server on {host}:{port}")
        logger.info("Webhook endpoints available:")
        logger.info("  - /webhook/razorpay (Razorpay webhooks)")
        logger.info("  - /webhook/stripe (Stripe webhooks)")
        logger.info("  - /webhook/paypal (PayPal webhooks)")
        logger.info("  - /webhook/health (Health check)")
        
        # Run the Flask app
        app.run(host=host, port=port, debug=debug)
        
    except ImportError as e:
        logger.error(f"Failed to import webhook handler: {e}")
        logger.error("Make sure all dependencies are installed:")
        logger.error("  pip install flask")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running webhook server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
