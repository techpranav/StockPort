#!/usr/bin/env python3
"""
Payment Gateway Setup Helper

This script helps you set up payment gateway credentials for the Stockport application.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

def create_env_file():
    """Create a .env file with payment gateway configuration."""
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists. Backing up to .env.backup")
        env_file.rename(".env.backup")
    
    print("🔧 Creating .env file for payment gateway configuration...")
    
    env_content = """# Payment Gateway Configuration
# Copy this file to .env and fill in your actual credentials

# Razorpay Configuration (Recommended for India)
RAZORPAY_KEY_ID=your_razorpay_key_id_here
RAZORPAY_KEY_SECRET=your_razorpay_key_secret_here
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret_here

# Stripe Configuration (Global)
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# PayPal Configuration (Global)
PAYPAL_CLIENT_ID=your_paypal_client_id_here
PAYPAL_CLIENT_SECRET=your_paypal_client_secret_here
PAYPAL_WEBHOOK_ID=your_paypal_webhook_id_here

# Application Configuration
APP_BASE_URL=http://localhost:8501
SECRET_KEY=your_secret_key_here

# Authentication Configuration
ENABLE_AUTHENTICATION=true
ENABLE_SOCIAL_LOGIN=true
ENABLE_STRIPE_PAYMENTS=true

# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here

# Microsoft OAuth Configuration
MICROSOFT_OAUTH_CLIENT_ID=your_microsoft_client_id_here
MICROSOFT_OAUTH_CLIENT_SECRET=your_microsoft_client_secret_here

# AI Configuration
ENABLE_AI_FEATURES=true
OPENAI_API_KEY=your_openai_api_key_here

# Google Drive Configuration
ENABLE_GOOGLE_DRIVE=true
GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project_id_here
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created {env_file}")
    print("\n📝 Next steps:")
    print("1. Edit the .env file and replace the placeholder values with your actual credentials")
    print("2. Get your credentials from:")
    print("   - Razorpay: https://razorpay.com/ (for Indian users)")
    print("   - Stripe: https://stripe.com/ (global)")
    print("   - PayPal: https://developer.paypal.com/ (global)")
    print("3. Restart the application")

def check_credentials():
    """Check which payment gateways are configured."""
    print("🔍 Checking payment gateway configuration...")
    
    # Check Razorpay
    razorpay_key_id = os.getenv("RAZORPAY_KEY_ID")
    razorpay_key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    razorpay_configured = bool(razorpay_key_id and razorpay_key_secret)
    
    # Check Stripe
    stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
    stripe_configured = bool(stripe_publishable_key and stripe_secret_key)
    
    # Check PayPal
    paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
    paypal_client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    paypal_configured = bool(paypal_client_id and paypal_client_secret)
    
    print("\n📊 Payment Gateway Status:")
    print(f"Razorpay: {'✅ Configured' if razorpay_configured else '❌ Not configured'}")
    print(f"Stripe:   {'✅ Configured' if stripe_configured else '❌ Not configured'}")
    print(f"PayPal:   {'✅ Configured' if paypal_configured else '❌ Not configured'}")
    
    if not any([razorpay_configured, stripe_configured, paypal_configured]):
        print("\n⚠️  No payment gateways are configured!")
        print("Run this script with --setup to create a .env file template.")
    else:
        print(f"\n✅ {sum([razorpay_configured, stripe_configured, paypal_configured])} payment gateway(s) configured")

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        create_env_file()
    else:
        check_credentials()
        print("\n💡 To set up payment gateways, run: python setup_payment_gateways.py --setup")

if __name__ == "__main__":
    main()
