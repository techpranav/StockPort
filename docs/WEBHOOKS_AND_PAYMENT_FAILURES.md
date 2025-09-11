# Webhooks and Payment Failure Handling

## What are Webhooks?

**Webhooks** are HTTP callbacks that allow external services (like payment gateways) to send real-time notifications to your application when specific events occur.

### How Webhooks Work:

1. **Register webhook URL** with payment gateway (e.g., `https://yourapp.com/webhook/razorpay`)
2. **Payment gateway sends HTTP POST** to your webhook URL when events happen
3. **Your application processes the webhook** and takes appropriate action

### Webhook Flow Example:
```
User pays → Razorpay processes payment → Razorpay sends webhook to your app → Your app activates license
```

## Webhook Implementation in Our Project

### Current Status:
- ✅ **Stripe**: Has webhook endpoint (`/webhook/stripe`)
- ✅ **Razorpay**: Has webhook endpoint (`/webhook/razorpay`) 
- ✅ **PayPal**: Has webhook endpoint (`/webhook/paypal`)

### Webhook Events We Handle:

#### Razorpay Events:
- `payment.captured` - Payment successful, activate license
- `payment.failed` - Payment failed, log failure
- `subscription.activated` - Subscription activated
- `subscription.charged` - Subscription charged
- `subscription.cancelled` - Subscription cancelled

#### Stripe Events:
- `checkout.session.completed` - Checkout completed, activate license
- `customer.subscription.created` - Subscription created
- `customer.subscription.updated` - Subscription updated
- `customer.subscription.deleted` - Subscription deleted
- `invoice.payment_succeeded` - Payment succeeded
- `invoice.payment_failed` - Payment failed

#### PayPal Events:
- `PAYMENT.SALE.COMPLETED` - Payment completed
- `PAYMENT.SALE.DENIED` - Payment denied
- `BILLING.SUBSCRIPTION.CREATED` - Subscription created
- `BILLING.SUBSCRIPTION.CANCELLED` - Subscription cancelled

## Payment Failure Handling

### What Happens When Payment Fails?

1. **Payment Gateway Notifies Us** via webhook
2. **We Log the Failure** for monitoring
3. **User Remains on Current Plan** (no license downgrade)
4. **User Can Retry Payment** anytime

### Failure Scenarios:

#### 1. **Insufficient Funds**
- User's card/bank account doesn't have enough money
- Payment gateway rejects the transaction
- User gets error message and can retry

#### 2. **Card Declined**
- Bank blocks the transaction (fraud protection, expired card, etc.)
- Payment gateway returns decline response
- User needs to use different payment method

#### 3. **Network/Technical Issues**
- Internet connection problems during payment
- Payment gateway temporarily unavailable
- User can retry after connection restored

#### 4. **Invalid Payment Details**
- Wrong card number, CVV, or expiry date
- Payment gateway validates and rejects
- User needs to correct payment information

### How We Handle Failures:

```python
def _handle_payment_failed(self, payload: Dict[str, Any]) -> bool:
    """Handle payment failed event."""
    try:
        payment = payload.get('payment', {})
        entity = payment.get('entity', {})
        
        user_id = int(entity.get('notes', {}).get('user_id', 0))
        plan_type = entity.get('notes', {}).get('plan_type', '')
        payment_id = entity.get('id', '')
        
        if user_id and plan_type:
            logger.warning(f"Payment failed for user {user_id}, plan {plan_type}, payment ID: {payment_id}")
            
            # In production, you might want to:
            # 1. Send notification to user
            # 2. Update payment status in database
            # 3. Trigger retry mechanism
            # 4. Send alert to admin
            
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error handling payment failed: {e}")
        return False
```

## Setting Up Webhooks

### For Development (Local Testing):

1. **Use ngrok or similar** to expose your local server:
   ```bash
   ngrok http 5000
   ```

2. **Register webhook URL** with payment gateway:
   - Razorpay: `https://your-ngrok-url.ngrok.io/webhook/razorpay`
   - Stripe: `https://your-ngrok-url.ngrok.io/webhook/stripe`
   - PayPal: `https://your-ngrok-url.ngrok.io/webhook/paypal`

### For Production:

1. **Deploy webhook server** to your production domain
2. **Register webhook URLs**:
   - Razorpay: `https://yourdomain.com/webhook/razorpay`
   - Stripe: `https://yourdomain.com/webhook/stripe`
   - PayPal: `https://yourdomain.com/webhook/paypal`

### Environment Variables Needed:

```bash
# Razorpay Webhook
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret

# Stripe Webhook
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# PayPal Webhook
PAYPAL_WEBHOOK_SECRET=your_paypal_webhook_secret

# Webhook Server
WEBHOOK_PORT=5000
```

## Running Webhook Server

### Option 1: Separate Webhook Server
```bash
python auth/webhook_handler.py
```

### Option 2: Integrate with Main App
Add webhook endpoints to your main Streamlit app (not recommended for production).

## Testing Webhooks

### Health Check:
```bash
curl https://yourdomain.com/webhook/health
```

### Test Webhook Processing:
```bash
# Test Razorpay webhook
curl -X POST https://yourdomain.com/webhook/razorpay \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: test_signature" \
  -d '{"event": "payment.captured", "payload": {...}}'
```

## Why Webhooks Are Important

### 1. **Reliability**
- Payment gateways guarantee webhook delivery
- Automatic retry mechanisms
- More reliable than callback redirects

### 2. **Real-time Processing**
- Immediate license activation
- Instant user experience
- No manual refresh needed

### 3. **Security**
- Webhook signatures verify authenticity
- Prevents fake payment notifications
- Secure communication

### 4. **Comprehensive Coverage**
- Handles all payment events (success, failure, cancellation)
- Covers edge cases and error scenarios
- Complete payment lifecycle management

## Fallback Mechanisms

Since webhooks might not always work (network issues, server downtime), we have fallback mechanisms:

### 1. **Manual License Activation**
- Users can manually activate licenses after payment
- "Refresh License Status" button
- "Activate License" button for upgrade mode

### 2. **Payment Success Callbacks**
- Redirect-based fallback when webhooks fail
- Query parameter-based license activation
- Immediate user feedback

### 3. **Database Polling**
- Periodic checks for new payments
- Background license activation
- Automated cleanup of failed payments

## Best Practices

### 1. **Always Implement Webhooks**
- Primary method for payment processing
- Most reliable and secure
- Required for production systems

### 2. **Provide Fallback Options**
- Manual activation buttons
- Clear user instructions
- Multiple activation methods

### 3. **Log Everything**
- Payment attempts and results
- Webhook processing status
- Error conditions and resolutions

### 4. **Monitor Webhook Health**
- Regular health checks
- Alert on webhook failures
- Monitor payment success rates

### 5. **Handle Edge Cases**
- Duplicate webhook events
- Out-of-order webhook delivery
- Network timeouts and retries

## Troubleshooting

### Common Issues:

#### 1. **Webhooks Not Received**
- Check webhook URL configuration
- Verify server is accessible
- Check firewall settings

#### 2. **Webhook Signature Verification Fails**
- Verify webhook secret is correct
- Check signature calculation
- Ensure payload is not modified

#### 3. **License Not Activated**
- Check webhook processing logs
- Verify user ID and plan type
- Use manual activation as fallback

#### 4. **Duplicate License Creation**
- Implement idempotency checks
- Use payment ID as unique identifier
- Check existing licenses before creating new ones

## Summary

Webhooks are essential for reliable payment processing and license activation. They provide:

- **Real-time payment notifications**
- **Automatic license activation**
- **Comprehensive failure handling**
- **Secure and reliable communication**

Always implement webhooks as the primary payment processing method, with manual activation as a fallback for edge cases.
