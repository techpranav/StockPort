# OAuth Redirect URI Setup Guide

This guide explains how to configure OAuth providers to work with dynamic ports and multiple redirect URIs.

## Problem

OAuth providers (Google, Microsoft) require exact redirect URI matches. When you run Streamlit on different ports (8501, 8502, 8503, etc.), the redirect URIs don't match what's configured in the OAuth provider dashboards.

## Solution

Configure your OAuth providers to accept multiple redirect URIs covering the ports you commonly use.

## Google OAuth Setup

### 1. Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Select your project

### 2. Navigate to OAuth Configuration
- Go to "APIs & Services" > "Credentials"
- Find your OAuth 2.0 Client ID
- Click "Edit" (pencil icon)

### 3. Add Multiple Redirect URIs
Add these redirect URIs to your Google OAuth client:

```
http://localhost:8501
http://localhost:8502
http://localhost:8503
http://localhost:8504
http://localhost:8505
http://localhost:8506
http://localhost:8507
http://localhost:8508
http://localhost:8509
http://localhost:8510
http://localhost:8511
http://localhost:8512
http://localhost:8513
http://localhost:8514
http://localhost:8515
http://localhost:8516
http://localhost:8517
http://localhost:8518
http://localhost:8519
http://localhost:8520
```

### 4. Add JavaScript Origins
Also add these JavaScript origins:

```
http://localhost:8501
http://localhost:8502
http://localhost:8503
http://localhost:8504
http://localhost:8505
http://localhost:8506
http://localhost:8507
http://localhost:8508
http://localhost:8509
http://localhost:8510
http://localhost:8511
http://localhost:8512
http://localhost:8513
http://localhost:8514
http://localhost:8515
http://localhost:8516
http://localhost:8517
http://localhost:8518
http://localhost:8519
http://localhost:8520
```

### 5. Save Changes
Click "Save" to apply the changes.

## Microsoft OAuth Setup

### 1. Go to Azure Portal
- Visit: https://portal.azure.com/
- Navigate to "Azure Active Directory" > "App registrations"

### 2. Select Your App
- Find your "Stock Analysis Tool" app registration
- Click on it

### 3. Navigate to Authentication
- Click "Authentication" in the left menu

### 4. Add Multiple Redirect URIs
In the "Single-page application" section, add these redirect URIs:

```
http://localhost:8501
http://localhost:8502
http://localhost:8503
http://localhost:8504
http://localhost:8505
http://localhost:8506
http://localhost:8507
http://localhost:8508
http://localhost:8509
http://localhost:8510
http://localhost:8511
http://localhost:8512
http://localhost:8513
http://localhost:8514
http://localhost:8515
http://localhost:8516
http://localhost:8517
http://localhost:8518
http://localhost:8519
http://localhost:8520
```

### 5. Save Changes
Click "Save" to apply the changes.

## Alternative: Use Fixed Port

If you prefer to use a fixed port, you can:

### 1. Always run Streamlit on port 8501
```bash
streamlit run app.py --server.port 8501
```

### 2. Set environment variable
Create a `.env` file with:
```bash
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8501
MICROSOFT_OAUTH_REDIRECT_URI=http://localhost:8501
```

## Testing

After configuring the OAuth providers:

1. Start your Streamlit app on any port:
   ```bash
   streamlit run app.py --server.port 8515
   ```

2. Try logging in with Google/Microsoft
3. The redirect should work correctly

## Troubleshooting

### Common Issues

1. **"redirect_uri_mismatch" error**
   - The redirect URI in the OAuth request doesn't match what's configured
   - Check that you've added the correct port to your OAuth provider

2. **"invalid_client" error**
   - Client ID or secret is incorrect
   - Check your environment variables

3. **"access_denied" error**
   - User denied permission or scope issues
   - Check OAuth scopes and permissions

### Debug Steps

1. Check what redirect URI is being generated:
   - Look at the console output for "DEBUG: Using Google OAuth redirect URI..."
   - Verify it matches what's configured in your OAuth provider

2. Check OAuth provider logs:
   - Google Cloud Console > APIs & Services > OAuth consent screen > Domain verification
   - Azure Portal > App registrations > Your app > Sign-in logs

3. Test with a simple redirect URI first:
   - Use `http://localhost:8501` only
   - Once working, add more ports

## Production Deployment

For production (Streamlit Cloud), you'll need to:

1. Add your production URL to OAuth providers:
   - Google: `https://your-app-name.streamlit.app`
   - Microsoft: `https://your-app-name.streamlit.app`

2. Update environment variables:
   ```bash
   GOOGLE_OAUTH_REDIRECT_URI=https://your-app-name.streamlit.app
   MICROSOFT_OAUTH_REDIRECT_URI=https://your-app-name.streamlit.app
   ```

This setup ensures OAuth works correctly across all your development ports and production deployment.
