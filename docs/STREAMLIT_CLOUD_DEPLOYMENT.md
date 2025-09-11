# Streamlit Cloud Deployment Guide

This guide covers deploying the Stock Analysis Tool to Streamlit Cloud with proper OAuth and payment gateway configuration.

## Overview

Streamlit Cloud deployment requires separate configuration for OAuth providers and payment gateways due to different URLs and security requirements.

## 1. Environment Setup

### Required Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# Streamlit Cloud Base URL (replace with your actual app URL)
STREAMLIT_BASE_URL=https://your-app-name.streamlit.app

# Authentication Settings
ENABLE_AUTHENTICATION=true
SESSION_SECRET_KEY=your-super-secret-session-key-change-this
CSRF_SECRET_KEY=your-csrf-secret-key-change-this

# Google OAuth (Cloud Configuration)
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=https://your-app-name.streamlit.app

# Microsoft OAuth (Cloud Configuration)
MICROSOFT_OAUTH_CLIENT_ID=your-microsoft-client-id
MICROSOFT_OAUTH_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_OAUTH_REDIRECT_URI=https://your-app-name.streamlit.app
MICROSOFT_OAUTH_TENANT_ID=common

# Payment Gateways (Cloud Configuration)
# Stripe
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret

# Razorpay
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# PayPal
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=live

# Database
DATABASE_URL=sqlite:///data/auth.db
```

## 2. OAuth Provider Configuration

### Google OAuth Setup

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a new project** or select existing one
3. **Enable Google+ API** and **Google OAuth2 API**
4. **Create OAuth 2.0 credentials**:
   - Application type: Web application
   - Authorized redirect URIs: `https://your-app-name.streamlit.app`
   - Authorized JavaScript origins: `https://your-app-name.streamlit.app`

### Microsoft OAuth Setup

1. **Go to Azure Portal**: https://portal.azure.com/
2. **Navigate to Azure Active Directory > App registrations**
3. **Create new registration**:
   - Name: Stock Analysis Tool
   - Supported account types: Accounts in any organizational directory and personal Microsoft accounts
   - Redirect URI: `https://your-app-name.streamlit.app`
4. **Configure API permissions**:
   - Add Microsoft Graph permissions: `User.Read`, `openid`, `profile`, `email`
5. **Create client secret** and note the values

## 3. Payment Gateway Configuration

### Stripe Setup (Global)

1. **Create Stripe account**: https://stripe.com/
2. **Get API keys** from dashboard
3. **Configure webhooks**:
   - Endpoint URL: `https://your-app-name.streamlit.app/webhook/stripe`
   - Events: `checkout.session.completed`, `invoice.payment_succeeded`
4. **Update redirect URLs** in Stripe dashboard

### Razorpay Setup (India)

1. **Create Razorpay account**: https://razorpay.com/
2. **Get API keys** from dashboard
3. **Configure webhooks**:
   - Webhook URL: `https://your-app-name.streamlit.app/webhook/razorpay`
   - Events: `payment.captured`, `subscription.activated`
4. **Update redirect URLs** in Razorpay dashboard

### PayPal Setup (Global)

1. **Create PayPal Developer account**: https://developer.paypal.com/
2. **Create application**:
   - Application type: Web
   - Return URL: `https://your-app-name.streamlit.app/?purchase=success`
   - Cancel URL: `https://your-app-name.streamlit.app/?purchase=cancelled`
3. **Get client credentials**

## 4. Streamlit Cloud Configuration

### Repository Setup

1. **Push your code** to GitHub repository
2. **Create `requirements.txt`**:
```txt
streamlit>=1.28.0
extra-streamlit-components>=0.1.60
requests>=2.31.0
python-dotenv>=1.0.0
cryptography>=41.0.0
itsdangerous>=2.1.0
razorpay>=1.3.0
stripe>=7.0.0
google-auth-oauthlib>=1.0.0
google-auth>=2.23.0
```

3. **Create `.streamlit/secrets.toml`** (for sensitive data):
```toml
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
```

### Deployment Steps

1. **Go to Streamlit Cloud**: https://share.streamlit.io/
2. **Connect GitHub repository**
3. **Configure deployment**:
   - Main file path: `app.py`
   - Python version: 3.9+
4. **Add environment variables** in Streamlit Cloud dashboard
5. **Deploy the application**

## 5. Security Considerations

### Production Security

1. **Use strong secrets** for all keys
2. **Enable HTTPS** (automatic in Streamlit Cloud)
3. **Configure CORS** properly
4. **Set up monitoring** and logging
5. **Regular security updates**

### Database Security

1. **Use encrypted database** for production
2. **Regular backups**
3. **Access controls**
4. **Audit logging**

## 6. Testing Deployment

### Pre-deployment Checklist

- [ ] All environment variables configured
- [ ] OAuth redirect URIs updated
- [ ] Payment webhooks configured
- [ ] Database migrations completed
- [ ] Security settings reviewed
- [ ] Error handling tested

### Post-deployment Testing

1. **Test OAuth login** (Google & Microsoft)
2. **Test payment flows** (all gateways)
3. **Test license activation**
4. **Test user management**
5. **Test error scenarios**

## 7. Monitoring and Maintenance

### Key Metrics to Monitor

- Authentication success/failure rates
- Payment success/failure rates
- User registration and activity
- Error rates and types
- Performance metrics

### Regular Maintenance

- Update dependencies monthly
- Review security logs weekly
- Backup database daily
- Monitor payment gateway status
- Update OAuth configurations as needed

## 8. Troubleshooting

### Common Issues

1. **OAuth redirect mismatch**: Check redirect URIs in provider dashboards
2. **Payment webhook failures**: Verify webhook URLs and secrets
3. **Database connection issues**: Check database configuration
4. **Session management problems**: Verify secret keys

### Debug Mode

Enable debug logging by setting:
```bash
STREAMLIT_LOGGER_LEVEL=debug
```

## 9. Scaling Considerations

### Performance Optimization

- Use database connection pooling
- Implement caching for frequently accessed data
- Optimize database queries
- Use CDN for static assets

### High Availability

- Set up database replication
- Implement health checks
- Use load balancing
- Plan for disaster recovery

## 10. Cost Optimization

### Streamlit Cloud

- Monitor resource usage
- Optimize application performance
- Use appropriate instance sizes

### Payment Gateways

- Compare transaction fees
- Optimize payment flows
- Monitor chargeback rates

This deployment guide ensures a secure, scalable, and maintainable deployment of your Stock Analysis Tool on Streamlit Cloud.
