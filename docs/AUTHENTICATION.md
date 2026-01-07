# Stockport Authentication & Licensing System

This document describes the authentication and licensing system implemented in Stockport.

## Overview

The authentication system provides:
- **User Management**: Registration, login, session management
- **License Management**: License keys, expiry dates, plan types
- **Payment Integration**: Stripe webhook support for automatic license activation
- **Social Login**: Google OAuth integration (scaffolded)
- **Admin Panel**: User and license management interface

## Features

### 🔐 Authentication
- Email/password registration and login
- Session management with configurable timeout
- Password hashing with bcrypt
- Social login support (Google OAuth)

### 🔑 Licensing
- License key activation
- Multiple plan types (Basic/Pro, Monthly/Yearly)
- Automatic expiry management
- Stripe integration for payments

### 👨‍💼 Admin Panel
- User management dashboard
- License creation and management
- System statistics
- Session cleanup

## Configuration

### Environment Variables

Add these to your `.env` file or environment:

```bash
# Authentication
ENABLE_AUTHENTICATION=true
ENABLE_STRIPE_PAYMENTS=true
ENABLE_SOCIAL_LOGIN=true
ENABLE_ADMIN_PANEL=true

# Session
SESSION_SECRET_KEY=your-secret-key-change-in-production
SESSION_TIMEOUT_HOURS=24

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Stripe Price IDs (create these in your Stripe dashboard)
STRIPE_BASIC_MONTHLY_PRICE_ID=price_...
STRIPE_BASIC_YEARLY_PRICE_ID=price_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_YEARLY_PRICE_ID=price_...

# Google OAuth (for social login)
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8501/auth/callback
```

### License Plans

Plans are configured in `config/app_config.py`:

```python
LICENSE_PLANS = {
    "basic_monthly": {
        "name": "Basic Monthly",
        "price": 9.99,
        "currency": "usd",
        "stripe_price_id": os.getenv("STRIPE_BASIC_MONTHLY_PRICE_ID"),
        "features": ["Stock Analysis", "Basic Reports", "Google Drive Export"],
        "expiry_days": 30
    },
    "basic_yearly": {
        "name": "Basic Yearly", 
        "price": 99.99,
        "currency": "usd",
        "stripe_price_id": os.getenv("STRIPE_BASIC_YEARLY_PRICE_ID"),
        "features": ["Stock Analysis", "Basic Reports", "Google Drive Export"],
        "expiry_days": 365
    },
    # ... more plans
}
```

## Setup Instructions

### 1. Enable Authentication

Set the environment variable:
```bash
export ENABLE_AUTHENTICATION=true
```

### 2. Create Admin User

Run the application and register a user, then manually set admin privileges in the database:

```python
from auth.database import AuthDatabase

db = AuthDatabase()
# Find your user ID and set is_admin = 1
```

### 3. Stripe Setup (Optional)

1. **Create Stripe Account**: Sign up at [stripe.com](https://stripe.com)
2. **Get API Keys**: From Stripe Dashboard > Developers > API Keys
3. **Create Products**: Create products for each plan type
4. **Create Price IDs**: Create recurring prices for each plan
5. **Set Webhook**: Point to your webhook endpoint

### 4. Google OAuth Setup (Optional)

1. **Create Google Cloud Project**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Enable OAuth API**: APIs & Services > OAuth consent screen
3. **Create OAuth Client**: APIs & Services > Credentials
4. **Set Redirect URI**: `http://localhost:8501/auth/callback`

## Usage

### For End Users

1. **Register**: Create account with email/password or Google
2. **Activate License**: Enter license key or purchase via Stripe
3. **Use App**: Access all features with valid license

### For Administrators

1. **Access Admin Panel**: Navigate to "👨‍💼 Admin" tab
2. **Manage Users**: View all users and their status
3. **Create Licenses**: Generate license keys for users
4. **Monitor System**: View system statistics

### For Developers

#### Authentication Gate

The main application includes an authentication gate:

```python
from auth.ui import render_auth_gate

# In your main app
if ENABLE_AUTHENTICATION:
    if not render_auth_gate():
        return  # Stop execution if not authenticated
```

#### User Service

```python
from auth.user_service import UserService

user_service = UserService()

# Register user
success, message = user_service.register_user("username", "email", "password")

# Login user
success, message, user_info = user_service.login_user("email", "password")

# Check authentication
if user_service.is_authenticated():
    user = user_service.get_current_user()
```

#### License Service

```python
from auth.license_service import LicenseService

license_service = LicenseService()

# Validate license
is_valid, message, license_info = license_service.validate_license(user_id)

# Create license
license_key = license_service.create_license(user_id, "basic_monthly", 365)

# Get license status
status = license_service.get_license_status(user_id)
```

## Database Schema

The system uses SQLite with these tables:

### Users
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email
- `password_hash`: Hashed password
- `salt`: Password salt
- `is_active`: Account status
- `is_admin`: Admin privileges
- `created_at`: Registration date

### Licenses
- `id`: Primary key
- `user_id`: Foreign key to users
- `license_key`: Unique license key
- `plan_type`: Plan type (basic_monthly, etc.)
- `stripe_subscription_id`: Stripe subscription ID
- `stripe_customer_id`: Stripe customer ID
- `is_active`: License status
- `expires_at`: Expiry date
- `created_at`: Creation date

### Sessions
- `id`: Primary key
- `user_id`: Foreign key to users
- `session_token`: Unique session token
- `expires_at`: Session expiry
- `created_at`: Session creation

### Social Logins
- `id`: Primary key
- `user_id`: Foreign key to users
- `provider`: Provider name (google, etc.)
- `provider_user_id`: Provider's user ID
- `access_token`: OAuth access token
- `refresh_token`: OAuth refresh token
- `expires_at`: Token expiry

## Stripe Webhook

The webhook handler processes these events:
- `checkout.session.completed`: License activation
- `customer.subscription.created`: New subscription
- `customer.subscription.updated`: Plan changes
- `customer.subscription.deleted`: Cancellation
- `invoice.payment_succeeded`: Payment success
- `invoice.payment_failed`: Payment failure

### Running Webhook Server

```bash
python auth/stripe_webhook.py
```

The webhook server runs on port 5000 by default.

## Security Considerations

1. **Password Hashing**: Uses bcrypt with salt
2. **Session Management**: Secure session tokens with expiry
3. **Webhook Verification**: Stripe signature verification
4. **Input Validation**: All inputs are validated
5. **SQL Injection**: Uses parameterized queries

## Troubleshooting

### Common Issues

1. **"No module named 'auth'"**: Ensure auth package is in Python path
2. **Database errors**: Check file permissions for `data/auth.db`
3. **Stripe webhook failures**: Verify webhook secret and endpoint URL
4. **Session issues**: Check SESSION_SECRET_KEY configuration

### Debug Mode

Enable debug logging:

```bash
export DEBUG=true
```

### Database Reset

To reset the authentication database:

```bash
rm data/auth.db
```

The database will be recreated on next startup.

## Future Enhancements

- [ ] Email verification
- [ ] Password reset functionality
- [ ] Two-factor authentication
- [ ] More social login providers
- [ ] Advanced admin features
- [ ] License usage analytics
- [ ] Automated billing reminders
- [ ] Multi-tenant support

## Support

For issues with the authentication system:
1. Check the logs for error messages
2. Verify environment variables
3. Test database connectivity
4. Review Stripe webhook configuration
