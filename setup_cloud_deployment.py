#!/usr/bin/env python3
"""
Streamlit Cloud Deployment Setup Script

This script helps set up environment variables and configuration for Streamlit Cloud deployment.
"""

import os
import sys
from pathlib import Path

def create_env_template():
    """Create a .env template for cloud deployment."""
    env_content = """# Streamlit Cloud Deployment Environment Variables
# Copy this file to .env and fill in your actual values

# Base URL (replace with your actual Streamlit Cloud URL)
STREAMLIT_BASE_URL=https://your-app-name.streamlit.app

# Authentication Settings
ENABLE_AUTHENTICATION=true
SESSION_SECRET_KEY=your-super-secret-session-key-change-this
CSRF_SECRET_KEY=your-csrf-secret-key-change-this

# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=https://your-app-name.streamlit.app

# Microsoft OAuth Configuration
MICROSOFT_OAUTH_CLIENT_ID=your-microsoft-client-id
MICROSOFT_OAUTH_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_OAUTH_REDIRECT_URI=https://your-app-name.streamlit.app
MICROSOFT_OAUTH_TENANT_ID=common

# Payment Gateway Configuration
# Stripe (Global)
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret

# Razorpay (India)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# PayPal (Global)
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=live

# Database
DATABASE_URL=sqlite:///data/auth.db
"""
    
    with open('.env.cloud', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.cloud template file")
    print("📝 Please copy .env.cloud to .env and fill in your actual values")

def create_secrets_template():
    """Create a secrets.toml template for Streamlit Cloud."""
    secrets_content = """# Streamlit Cloud Secrets Configuration
# This file should be added to your Streamlit Cloud app's secrets

[oauth]
google_client_id = "your-google-client-id"
google_client_secret = "your-google-client-secret"
microsoft_client_id = "your-microsoft-client-id"
microsoft_client_secret = "your-microsoft-client-secret"

[payment]
stripe_publishable_key = "pk_live_your_stripe_publishable_key"
stripe_secret_key = "sk_live_your_stripe_secret_key"
stripe_webhook_secret = "whsec_your_stripe_webhook_secret"
razorpay_key_id = "your_razorpay_key_id"
razorpay_key_secret = "your_razorpay_key_secret"
paypal_client_id = "your_paypal_client_id"
paypal_client_secret = "your_paypal_client_secret"

[app]
base_url = "https://your-app-name.streamlit.app"
"""
    
    # Create .streamlit directory if it doesn't exist
    streamlit_dir = Path('.streamlit')
    streamlit_dir.mkdir(exist_ok=True)
    
    with open('.streamlit/secrets.toml', 'w') as f:
        f.write(secrets_content)
    
    print("✅ Created .streamlit/secrets.toml template file")

def create_requirements():
    """Create requirements.txt for Streamlit Cloud."""
    requirements = """streamlit>=1.28.0
extra-streamlit-components>=0.1.60
requests>=2.31.0
python-dotenv>=1.0.0
cryptography>=41.0.0
itsdangerous>=2.1.0
razorpay>=1.3.0
stripe>=7.0.0
google-auth-oauthlib>=1.0.0
google-auth>=2.23.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created requirements.txt file")

def check_configuration():
    """Check if the application is properly configured for cloud deployment."""
    print("\n🔍 Checking configuration...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("❌ .env file not found - please create one")
    
    # Check if secrets.toml exists
    if os.path.exists('.streamlit/secrets.toml'):
        print("✅ .streamlit/secrets.toml found")
    else:
        print("❌ .streamlit/secrets.toml not found - please create one")
    
    # Check if requirements.txt exists
    if os.path.exists('requirements.txt'):
        print("✅ requirements.txt found")
    else:
        print("❌ requirements.txt not found - please create one")
    
    # Check if app.py exists
    if os.path.exists('app.py'):
        print("✅ app.py found")
    else:
        print("❌ app.py not found - this is required for Streamlit Cloud")

def print_deployment_instructions():
    """Print deployment instructions."""
    print("\n🚀 Streamlit Cloud Deployment Instructions:")
    print("=" * 50)
    print("1. Push your code to GitHub repository")
    print("2. Go to https://share.streamlit.io/")
    print("3. Connect your GitHub repository")
    print("4. Configure deployment settings:")
    print("   - Main file: app.py")
    print("   - Python version: 3.9+")
    print("5. Add environment variables in Streamlit Cloud dashboard")
    print("6. Deploy your application")
    print("\n📚 For detailed instructions, see docs/STREAMLIT_CLOUD_DEPLOYMENT.md")

def main():
    """Main function."""
    print("🌐 Streamlit Cloud Deployment Setup")
    print("=" * 40)
    
    # Create template files
    create_env_template()
    create_secrets_template()
    create_requirements()
    
    # Check configuration
    check_configuration()
    
    # Print instructions
    print_deployment_instructions()
    
    print("\n✨ Setup complete! Follow the instructions above to deploy to Streamlit Cloud.")

if __name__ == "__main__":
    main()
