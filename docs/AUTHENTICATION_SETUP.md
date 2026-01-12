# Complete Authentication Setup Guide

This guide provides step-by-step instructions for setting up the complete authentication system with Google OAuth, Microsoft OAuth, Stripe payments, and security features.

## 🎯 Overview

The authentication system now includes:
- ✅ **Google OAuth** - Social login with Google accounts
- ✅ **Microsoft OAuth** - Social login with Microsoft accounts  
- ✅ **Stripe Payments** - License purchase and subscription management
- ✅ **Security Features** - Rate limiting, CSRF protection, input validation
- ✅ **Admin Panel** - User and license management
- ✅ **License Management** - Automatic license validation and expiry

## 📋 Prerequisites

1. **Python Environment**: Python 3.8+ with pip
2. **Database**: SQLite (automatically created)
3. **OAuth Providers**: Google Cloud Console and Microsoft Azure accounts
4. **Payment Gateway**: Stripe account for payments

## 🔧 Step 1: Environment Configuration

Create a `.env` file in your project root:

```bash
# Authentication Settings
ENABLE_AUTHENTICATION=true
ENABLE_STRIPE_PAYMENTS=true
ENABLE_SOCIAL_LOGIN=true
ENABLE_ADMIN_PANEL=true

# Session Configuration
SESSION_SECRET_KEY=your-super-secret-session-key-change-this
SESSION_TIMEOUT_HOURS=24
REMEMBER_ME_DAYS=30

# Security Configuration
CSRF_SECRET_KEY=your-csrf-secret-key-change-this
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8501/auth/callback

# Microsoft OAuth Configuration
MICROSOFT_OAUTH_CLIENT_ID=your-microsoft-client-id
MICROSOFT_OAUTH_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_OAUTH_REDIRECT_URI=http://localhost:8501/auth/microsoft/callback
MICROSOFT_OAUTH_TENANT_ID=common

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Razorpay Configuration (India)
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# PayPal Configuration (Global)
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=sandbox  # or 'live' for production

# Payment Gateway Selection
PAYMENT_GATEWAY=auto  # auto, razorpay, stripe, paypal

# Stripe Price IDs (create these in your Stripe dashboard)
STRIPE_BASIC_MONTHLY_PRICE_ID=price_basic_monthly_id
STRIPE_BASIC_YEARLY_PRICE_ID=price_basic_yearly_id
STRIPE_PRO_MONTHLY_PRICE_ID=price_pro_monthly_id
STRIPE_PRO_YEARLY_PRICE_ID=price_pro_yearly_id
```

## 🔐 Step 2: Google OAuth Setup

### 2.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google+ API and Google OAuth2 API

### 2.2 Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" (or "Internal" for Workspace)
3. Fill in required fields:
   - App name: "Stockport Stock Analysis"
   - User support email: your email
   - Developer contact information: your email
4. Add scopes:
   - `openid`
   - `email`
   - `profile`
5. Add test users (your email)
6. Save and continue

### 2.3 Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **"Web application"**
4. Name: "Stockport Web Client"
5. Authorized redirect URIs:
   - `http://localhost:8501/auth/callback` (for development)
   - `https://your-domain.com/auth/callback` (for production)
6. Copy the Client ID and Client Secret to your `.env` file

## 🏢 Step 3: Microsoft OAuth Setup

### 3.1 Create Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Fill in details:
   - Name: "Stockport Stock Analysis"
   - **Supported account types**: **"Accounts in any organizational directory and personal Microsoft accounts"** ⭐
   - Redirect URI: Web → `http://localhost:8501/auth/microsoft/callback`

### 3.2 Configure Authentication

1. Go to "Authentication" in your app registration
2. Add platform: "Web"
3. Add redirect URI: `http://localhost:8501/auth/microsoft/callback`
4. **Enable "Access tokens" and "ID tokens"**
5. **Important**: Under "Advanced settings" → "Allow public client flows" → Enable if needed
6. Save

### 3.3 Create Client Secret

1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Add description and choose expiry
4. Copy the secret value to your `.env` file

### 3.4 Copy Application ID

1. From the app registration overview, copy the "Application (client) ID"
2. Add it to your `.env` file as `MICROSOFT_OAUTH_CLIENT_ID`

### 3.5 Configure API Permissions

1. Go to "API permissions"
2. Click "Add a permission"
3. Select "Microsoft Graph" → "Delegated permissions"
4. Add these permissions:
   - `openid`
   - `email`
   - `profile`
   - `User.Read`
5. Click "Grant admin consent" if prompted

### 3.6 Hotmail/Outlook.com Support ⭐

**For Hotmail, Outlook.com, and personal Microsoft accounts:**

1. **Environment Variable**: Set `MICROSOFT_OAUTH_TENANT_ID=common` in your `.env` file
2. **Supported Account Types**: Ensure it's set to "Accounts in any organizational directory and personal Microsoft accounts"
3. **Test Accounts**: Works with @hotmail.com, @outlook.com, @live.com accounts

**Common Issues & Solutions:**

| Error | Solution |
|-------|----------|
| "Not added to tenant" | Change "Supported account types" to include personal accounts |
| "Invalid redirect URI" | Ensure exact URI match in Azure portal |
| "Insufficient privileges" | Add required API permissions and grant admin consent |
| "Application not found" | Verify client ID and secret |

**Test Configuration:**
```bash
python test_microsoft_oauth.py
```

## 💳 Step 4: Payment Gateway Setup

### 4.1 Payment Gateway Options

**Since Stripe doesn't work in India, here are alternative payment solutions:**

#### **Option A: Razorpay (Recommended for India)**
- ✅ **Works in India**: Full support for Indian payments
- ✅ **Global Cards**: Accepts international cards
- ✅ **UPI Support**: Native UPI integration
- ✅ **Net Banking**: All major Indian banks
- ✅ **Wallets**: Paytm, PhonePe, etc.

#### **Option B: PayPal (Global)**
- ✅ **Global Coverage**: Works worldwide
- ✅ **Multiple Currencies**: Supports 25+ currencies
- ✅ **Easy Integration**: Well-documented APIs
- ✅ **Trusted Brand**: Widely recognized

#### **Option C: Square (US/Canada/UK/Australia)**
- ✅ **Modern API**: Excellent developer experience
- ✅ **Multiple Markets**: US, Canada, UK, Australia
- ✅ **Subscription Support**: Built-in recurring billing

#### **Option D: Multi-Gateway Solution**
- ✅ **Razorpay for India**: Primary gateway for Indian users
- ✅ **Stripe for Global**: For international users
- ✅ **Automatic Detection**: Based on user location/IP

### 4.2 Razorpay Setup (India)

#### 4.2.1 Create Razorpay Account

1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Sign up for a business account
3. Complete KYC verification
4. Switch to test mode for development

#### 4.2.2 Get API Keys

1. Go to "Settings" → "API Keys"
2. Generate new key pair
3. Copy the "Key ID" and "Key Secret"
4. Add to your `.env` file:

```bash
# Razorpay Configuration (India)
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
```

#### 4.2.3 Configure Webhooks

1. Go to "Settings" → "Webhooks"
2. Add webhook URL: `https://your-domain.com/webhook/razorpay`
3. Select events:
   - `payment.captured`
   - `payment.failed`
   - `subscription.activated`
   - `subscription.charged`
   - `subscription.halted`
   - `subscription.cancelled`

### 4.3 PayPal Setup (Global)

#### 4.3.1 Create PayPal Developer Account

1. Go to [PayPal Developer Portal](https://developer.paypal.com/)
2. Create a developer account
3. Create a new app
4. Get client ID and secret

#### 4.3.2 Environment Variables

```bash
# PayPal Configuration (Global)
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=sandbox  # or 'live' for production
```

### 4.4 Multi-Gateway Configuration

For supporting both India and global users:

```bash
# Multi-Gateway Configuration
PAYMENT_GATEWAY=auto  # auto, razorpay, stripe, paypal
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
```

### 4.5 Stripe Setup (Global - Excluding India)

**Note**: Stripe doesn't work in India. Use for global users only.

#### 4.5.1 Create Stripe Account

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Create an account or sign in
3. Switch to test mode for development

#### 4.5.2 Get API Keys

1. Go to "Developers" → "API keys"
2. Copy the "Publishable key" and "Secret key"
3. Add them to your `.env` file

#### 4.5.3 Create Products and Prices

1. Go to "Products" → "Add product"
2. Create products for each plan:
   - Basic Monthly ($9.99/month)
   - Basic Yearly ($99.99/year)
   - Pro Monthly ($19.99/month)
   - Pro Yearly ($199.99/year)

3. For each product, create a price:
   - Set the price amount
   - Choose billing period (monthly/yearly)
   - Copy the price ID (starts with `price_`)
   - Add to your `.env` file

#### 4.5.4 Configure Webhooks

1. Go to "Developers" → "Webhooks"
2. Click "Add endpoint"
3. Endpoint URL: `https://your-domain.com/webhook/stripe`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook secret to your `.env` file

## 🚀 Step 5: Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

## 🔧 Step 6: Initialize Database

The database will be automatically created when you first run the application. However, you can manually initialize it:

```python
from auth.database import AuthDatabase

# Initialize database
db = AuthDatabase()
print("Database initialized successfully")
```

## 🧪 Step 7: Test the Setup

### 7.1 Test Authentication

1. Run the application:
```bash
streamlit run app.py
```

2. Navigate to the login page
3. Test email/password registration and login
4. Test Google OAuth login
5. Test Microsoft OAuth login

### 7.2 Test Payment Flow

1. Register a new user
2. Go to the Profile page
3. Click "Purchase License"
4. Select a plan and proceed to payment
5. Complete the Stripe checkout (use test card: 4242 4242 4242 4242)

### 7.3 Test Admin Panel

1. Create an admin user in the database:
```python
from auth.database import AuthDatabase

db = AuthDatabase()
# Update a user to be admin
db.update_user_admin(user_id=1, is_admin=True)
```

2. Login as admin
3. Access the Admin panel
4. Test user management and license creation

## 🔒 Step 8: Security Best Practices

### 8.1 Production Deployment

1. **Use HTTPS**: Always use HTTPS in production
2. **Strong Secrets**: Use strong, unique secrets for all keys
3. **Environment Variables**: Never commit secrets to version control
4. **Database Security**: Use a proper database in production (PostgreSQL, MySQL)
5. **Rate Limiting**: Adjust rate limits based on your needs

### 8.2 OAuth Security

1. **Redirect URIs**: Only use HTTPS URIs in production
2. **State Parameter**: Always validate the state parameter
3. **Token Storage**: Store tokens securely
4. **Scope Limitation**: Only request necessary scopes

### 8.3 Payment Security

1. **Webhook Verification**: Always verify Stripe webhook signatures
2. **PCI Compliance**: Don't handle raw card data
3. **Test Mode**: Use test mode for development
4. **Error Handling**: Implement proper error handling for failed payments

## 🐛 Troubleshooting

### Common Issues

1. **OAuth Redirect Errors**
   - Check redirect URIs match exactly
   - Ensure HTTPS in production
   - Verify client IDs and secrets

2. **Payment Issues**
   - Check Stripe API keys
   - Verify webhook configuration
   - Test with Stripe test cards

3. **Database Errors**
   - Check file permissions
   - Ensure SQLite is installed
   - Verify database path

4. **Session Issues**
   - Check session secret key
   - Verify cookie settings
   - Clear browser cache

### Debug Mode

Enable debug mode to see detailed logs:

```bash
export DEBUG=true
streamlit run app.py
```

## 📞 Support

For issues with the authentication system:

1. Check the logs in `logs/` directory
2. Verify all environment variables are set
3. Test each component individually
4. Check the troubleshooting section above

## 🔄 Updates and Maintenance

### Regular Tasks

1. **Monitor Logs**: Check authentication logs regularly
2. **Update Dependencies**: Keep packages updated
3. **Review Security**: Regular security audits
4. **Backup Database**: Regular database backups
5. **Monitor Stripe**: Check payment success rates

### Scaling Considerations

1. **Database**: Consider PostgreSQL for high traffic
2. **Caching**: Implement Redis for session storage
3. **Load Balancing**: Use multiple instances
4. **CDN**: Use CDN for static assets
5. **Monitoring**: Implement application monitoring

## Plugging Authentication Module into Another Project

This guide explains how to integrate the Stockport authentication module (email/password + Google + Microsoft + licensing + payments hooks) into another Streamlit-based project.

### Prerequisites
- Python 3.10+
- Streamlit 1.32+
- extra_streamlit_components (for cookies)
- requests, cryptography, itsdangerous
- If using social login:
  - Google OAuth credentials
  - Microsoft Entra App Registration (with Graph `User.Read` delegated permission, admin consent granted)

### 1) Copy Required Packages/Modules
Copy these folders/files into your target project (preserving paths):
- `auth/` (database, ui, services)
- `config/` (and subfolders `constants/`) – or merge into your existing config system
- `utils/` (only cookie/session helpers like `user_settings_manager.py` if used)
- `services/exporters/` only if you need licensing/report hooks (optional)

If you already have a config system, import the following from `config.__init__` and/or adapt names:
- Feature flags: `ENABLE_AUTHENTICATION`, `ENABLE_SOCIAL_LOGIN`
- OAuth secrets: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REDIRECT_URI`, `MICROSOFT_OAUTH_CLIENT_ID`, `MICROSOFT_OAUTH_CLIENT_SECRET`, `MICROSOFT_OAUTH_REDIRECT_URI`
- Session & DB: `SESSION_TIMEOUT_HOURS`, `SESSION_SECRET_KEY`, `AUTH_DATABASE_PATH`

### 2) Environment Variables (.env)
Provide at minimum:
```
ENABLE_AUTHENTICATION=true
ENABLE_SOCIAL_LOGIN=true
SESSION_SECRET_KEY=your_random_secret
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8501
MICROSOFT_OAUTH_CLIENT_ID=...
MICROSOFT_OAUTH_CLIENT_SECRET=...
MICROSOFT_OAUTH_REDIRECT_URI=http://localhost:8501
```

### 3) Azure/Google Console Settings
- Google: Add `http://localhost:8501` to Authorized redirect URIs
- Microsoft: App registrations → API permissions → Add Microsoft Graph `User.Read` (Delegated) → Grant admin consent; set redirect URI `http://localhost:8501`.

### 4) Initialize Auth in Your App
In your main Streamlit app (e.g. `app.py`):
```python
from auth.ui import render_auth_gate

# Early in the app code
if not render_auth_gate():
    st.stop()

# Your application content after this point is protected
```
This will display login/register and handle OAuth callbacks automatically.

### 5) Persisted Sessions (Cookies)
The module persists a `session_token` cookie for 7 days using `extra_streamlit_components.CookieManager`. Ensure you include the package and do not block cookies in the browser.

### 6) Social Login Buttons (Optional)
The login UI already includes Google/Microsoft buttons. If you need manual buttons elsewhere:
```python
from auth.oauth_service import OAuthService
import streamlit as st

svc = OAuthService()
if st.button("Login with Google"):
    st.markdown(f"<meta http-equiv='refresh' content='0; url={svc.get_google_auth_url()}'>", unsafe_allow_html=True)
```

### 7) Getting Current User
```python
from auth.user_service import UserService
user = UserService().get_current_user()
if user:
    st.write("Hello", user['email'])
```

### 8) Logout
```python
from auth.user_service import UserService
from auth.ui import _get_cookie_manager

u = UserService()
if st.button("Logout"):
    user = u.get_current_user()
    if user:
        u.logout_user(user['session_token'])
    mgr = _get_cookie_manager()
    if mgr:
        mgr.delete("session_token")
    st.session_state.clear()
    st.rerun()
```

### 9) Licensing & Payments (Optional)
- License creation/validation available via `auth.license_service.LicenseService`
- Payments hooks exist in `auth.razorpay_service.py`, `services/exporters/report_service.py`; wire these only if needed.

### 10) Troubleshooting
- If Google shows blank or "enable JavaScript": ensure we only read query parameters and immediately clear them; refresh once.
- If Microsoft `/me` returns 403: add Graph `User.Read` and grant admin consent.
- If sessions don’t persist: verify `session_token` cookie is present at `http://localhost:8501` and the browser isn’t blocking cookies.

This module is self-contained; you can progressively adopt features (only email/password, or add social, or add licensing) by toggling the corresponding feature flags.
