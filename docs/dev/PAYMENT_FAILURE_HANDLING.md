# Payment Failure Handling Guide

## Overview

This guide explains how payment failures are handled in the application and what users can do when payments fail.

## Payment Failure Scenarios

### 1. **Insufficient Funds**
- **Cause**: User's card/bank account doesn't have enough money
- **User Experience**: Payment gateway shows error message
- **Action**: User needs to add funds or use different payment method

### 2. **Card Declined**
- **Cause**: Bank blocks transaction (fraud protection, expired card, etc.)
- **User Experience**: Payment gateway shows decline message
- **Action**: User needs to contact bank or use different card

### 3. **Invalid Payment Details**
- **Cause**: Wrong card number, CVV, or expiry date
- **User Experience**: Payment gateway shows validation error
- **Action**: User needs to correct payment information

### 4. **Network/Technical Issues**
- **Cause**: Internet connection problems or payment gateway downtime
- **User Experience**: Payment fails to process
- **Action**: User can retry after connection is restored

### 5. **User Cancellation**
- **Cause**: User manually cancels payment
- **User Experience**: Payment gateway shows cancellation message
- **Action**: User can retry anytime

## How Failures Are Handled

### **Current Implementation:**

#### **1. Payment Failure Callbacks**
```python
# Handle payment failure callback
if qp.get('purchase') == 'failed':
    st.error("❌ Payment failed. Please try again or use a different payment method.")
    # Clear payment state and allow retry
```

#### **2. Payment Cancellation Callbacks**
```python
# Handle payment cancellation callback
if qp.get('purchase') == 'cancelled':
    st.warning("⚠️ Payment was cancelled. You can try again anytime.")
    # Clear payment state and allow retry
```

#### **3. User-Friendly Error Messages**
- Clear error messages explaining what happened
- Helpful instructions on what to do next
- Retry mechanisms for failed payments

#### **4. Payment Failure Help Section**
```python
st.info("💳 **Payment Issues?** If your payment failed or was declined:")
st.markdown("""
- **Check your card details** (number, expiry, CVV)
- **Ensure sufficient funds** in your account
- **Try a different payment method** (different card/bank account)
- **Contact your bank** if payments are being blocked
- **Wait a few minutes** and try again
""")
```

## User Experience Flow

### **When Payment Fails:**

1. **Payment Gateway Shows Error**
   - User sees error message from Razorpay
   - Error explains why payment failed

2. **User Returns to App**
   - App detects payment failure via callback
   - Shows user-friendly error message
   - Provides helpful instructions

3. **User Can Retry**
   - "🔄 Try Payment Again" button available
   - Clears previous payment state
   - Allows fresh payment attempt

4. **Alternative Actions**
   - Use different payment method
   - Contact bank for assistance
   - Wait and try again later

## Technical Implementation

### **Payment Failure Detection:**

#### **Method 1: Callback URLs (Current)**
- Razorpay redirects to success/failure URLs
- App detects failure via query parameters
- Shows appropriate error messages

#### **Method 2: Webhooks (Production)**
- Razorpay sends webhook notifications
- App processes failure events automatically
- Can trigger additional actions (notifications, retry logic)

### **State Management:**
```python
# Clear payment state on failure
for key in [SSK_PAYMENT_SESSION, SSK_PAYMENT_REDIRECT_URL, SSK_SELECTED_PLAN, SSK_PAYMENT_GATEWAY]:
    if key in st.session_state:
        del st.session_state[key]
```

### **Error Handling:**
```python
try:
    # Payment processing
    result = process_payment()
except PaymentError as e:
    # Handle specific payment errors
    show_error_message(e.message)
except Exception as e:
    # Handle unexpected errors
    show_generic_error()
```

## Best Practices

### **1. Clear Error Messages**
- Explain what went wrong in simple terms
- Provide specific actions user can take
- Avoid technical jargon

### **2. Retry Mechanisms**
- Allow users to retry failed payments
- Clear previous payment state
- Provide alternative payment methods

### **3. User Guidance**
- Explain common failure reasons
- Provide troubleshooting steps
- Include contact information for support

### **4. Graceful Degradation**
- Handle network issues gracefully
- Provide offline alternatives when possible
- Maintain user session state

## Common Failure Reasons & Solutions

### **Card Issues:**
- **Expired Card**: Update expiry date
- **Wrong CVV**: Enter correct 3-digit CVV
- **Blocked Card**: Contact bank to unblock
- **Daily Limit**: Wait until next day or use different card

### **Account Issues:**
- **Insufficient Funds**: Add money to account
- **Frozen Account**: Contact bank to unfreeze
- **New Card**: Wait 24-48 hours for activation

### **Technical Issues:**
- **Network Problems**: Check internet connection
- **Browser Issues**: Try different browser
- **Cache Problems**: Clear browser cache

## Monitoring & Analytics

### **Track Payment Failures:**
- Log failure reasons
- Monitor failure rates
- Identify common issues
- Improve user experience

### **Metrics to Track:**
- Payment success rate
- Failure reasons distribution
- Retry success rate
- User abandonment rate

## Support & Troubleshooting

### **For Users:**
- Clear error messages
- Self-service troubleshooting
- Contact information for help
- Alternative payment methods

### **For Administrators:**
- Payment failure logs
- User support tickets
- System health monitoring
- Performance metrics

## Future Enhancements

### **Planned Improvements:**
1. **Automatic Retry Logic**
   - Retry failed payments automatically
   - Smart retry intervals
   - Success rate optimization

2. **Enhanced Error Handling**
   - More specific error messages
   - Contextual help
   - Proactive support

3. **Payment Analytics**
   - Failure pattern analysis
   - User behavior insights
   - Optimization recommendations

4. **Multi-Gateway Fallback**
   - Automatic gateway switching
   - Load balancing
   - Redundancy

## Summary

The payment failure handling system provides:

- ✅ **Clear error messages** for users
- ✅ **Retry mechanisms** for failed payments
- ✅ **Helpful guidance** for troubleshooting
- ✅ **State management** for clean retries
- ✅ **User-friendly interface** for error recovery

This ensures users have a smooth experience even when payments fail, with clear guidance on how to resolve issues and complete their purchase successfully.
