# Webhook Setup Guide for Automatic License Activation

## Overview

This guide will help you set up webhooks for automatic license activation after successful payments. Webhooks ensure that licenses are activated immediately when payments are completed, without requiring manual intervention.

## Step 1: Environment Configuration

Add these environment variables to your `.env` file:

```bash
# Webhook Configuration
WEBHOOK_PORT=5000
WEBHOOK_HOST=0.0.0.0
WEBHOOK_DEBUG=false

# Razorpay Webhook Secret (get this from Razorpay Dashboard)
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret_here

# Stripe Webhook Secret (get this from Stripe Dashboard)
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# PayPal Webhook Secret (get this from PayPal Dashboard)
PAYPAL_WEBHOOK_SECRET=your_paypal_webhook_secret_here
```

## Step 2: Running the Webhook Server

### Option 1: Run Webhook Server Separately
```bash
# Terminal 1: Run your Streamlit app
streamlit run app.py --server.port 8503

# Terminal 2: Run webhook server
python run_webhook_server.py
```

### Option 2: Run Both Together (Development)
```bash
# Run webhook server in background
python run_webhook_server.py &

# Run Streamlit app
streamlit run app.py --server.port 8503
```

## Step 3: Configure Razorpay Webhooks

### For Local Development:

1. **Install ngrok** (if not already installed):
   - Download from [ngrok.com](https://ngrok.com/download)
   - Or install via package manager: `npm install -g ngrok`

2. **Expose your local webhook server**:
   ```bash
   ngrok http 5000
   ```
   This will give you a public URL like: `https://abc123.ngrok.io`

3. **Configure Razorpay Webhook**:
   - Go to [Razorpay Dashboard](https://dashboard.razorpay.com/)
   - Navigate to **Settings** → **Webhooks**
   - Click **Add New Webhook**
   - **Webhook URL**: `https://abc123.ngrok.io/webhook/razorpay`
   - **Events to Subscribe**:
     - `payment.captured` ✅
     - `payment.failed` ✅
     - `subscription.activated` ✅
     - `subscription.cancelled` ✅
   - **Secret**: Generate a webhook secret and add it to your `.env` file

### For Production:

1. **Deploy webhook server** to your production domain
2. **Configure Razorpay Webhook**:
   - **Webhook URL**: `https://yourdomain.com/webhook/razorpay`
   - **Events**: Same as above
   - **Secret**: Add to production environment variables

## Step 4: Test Webhook Integration

### Test Webhook Health:
```bash
curl http://localhost:5000/webhook/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-10T20:53:41.979000",
  "gateways": {
    "razorpay": true,
    "stripe": false,
    "paypal": true
  }
}
```

### Test Razorpay Webhook:
```bash
curl -X POST http://localhost:5000/webhook/razorpay \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: test_signature" \
  -d '{
    "event": "payment.captured",
    "payload": {
      "payment": {
        "entity": {
          "id": "pay_test123",
          "notes": {
            "user_id": "3",
            "plan_type": "pro_monthly"
          }
        }
      }
    }
  }'
```

## Step 5: Verify Automatic License Activation

1. **Make a test payment** through your app
2. **Check webhook logs** in the webhook server console
3. **Verify license activation** in your app's profile page
4. **Check database** for new license records

## Webhook Events We Handle

### Razorpay Events:
- `payment.captured` - Payment successful, activate license
- `payment.failed` - Payment failed, log failure
- `subscription.activated` - Subscription activated
- `subscription.charged` - Subscription charged
- `subscription.cancelled` - Subscription cancelled

### Stripe Events:
- `checkout.session.completed` - Checkout completed, activate license
- `customer.subscription.created` - Subscription created
- `customer.subscription.updated` - Subscription updated
- `customer.subscription.deleted` - Subscription deleted
- `invoice.payment_succeeded` - Payment succeeded
- `invoice.payment_failed` - Payment failed

### PayPal Events:
- `PAYMENT.SALE.COMPLETED` - Payment completed
- `PAYMENT.SALE.DENIED` - Payment denied
- `BILLING.SUBSCRIPTION.CREATED` - Subscription created
- `BILLING.SUBSCRIPTION.CANCELLED` - Subscription cancelled

## Troubleshooting

### Common Issues:

#### 1. **Webhook Server Not Starting**
- Check if port 5000 is available
- Verify Flask is installed: `pip install flask`
- Check for import errors in webhook_handler.py

#### 2. **Webhooks Not Received**
- Verify ngrok is running and URL is accessible
- Check Razorpay webhook configuration
- Ensure webhook URL is correct in Razorpay dashboard

#### 3. **License Not Activated**
- Check webhook server logs for errors
- Verify user ID and plan type in webhook payload
- Use manual activation as fallback

#### 4. **Signature Verification Fails**
- Verify webhook secret is correct
- Check signature calculation
- Ensure payload is not modified

### Debug Mode:

Enable debug mode for detailed logging:
```bash
export WEBHOOK_DEBUG=true
python run_webhook_server.py
```

## Production Deployment

### Using Docker:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run_webhook_server.py"]
```

### Using Systemd Service:
```ini
[Unit]
Description=Webhook Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/app
ExecStart=/usr/bin/python3 run_webhook_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Security Considerations

1. **Webhook Signature Verification**: Always verify webhook signatures
2. **HTTPS Only**: Use HTTPS for webhook URLs in production
3. **Rate Limiting**: Implement rate limiting for webhook endpoints
4. **IP Whitelisting**: Whitelist payment gateway IPs if possible
5. **Secret Management**: Store webhook secrets securely

## Monitoring

### Health Checks:
- Regular health check endpoint: `/webhook/health`
- Monitor webhook processing success rates
- Alert on webhook failures

### Logging:
- Log all webhook events
- Monitor payment success/failure rates
- Track license activation success

## Summary

With webhooks properly configured:

1. **Automatic License Activation**: Licenses activate immediately after successful payment
2. **Reliable Processing**: Payment gateways guarantee webhook delivery
3. **Comprehensive Coverage**: Handles all payment events and edge cases
4. **Fallback Mechanisms**: Manual activation available when webhooks fail

The webhook system ensures your license upgrades work reliably and automatically! 🎉
