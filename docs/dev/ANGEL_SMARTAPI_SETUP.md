# Angel SmartAPI Setup Guide

## Overview

Angel One SmartAPI is the PRIMARY live data provider for Stockport v4. It provides FREE access to:
- Intraday candles
- Live quotes
- WebSocket streaming
- Options chain
- Futures (NFO)

## Prerequisites

1. **Angel One Account**: You need an active Angel One trading account
2. **SmartAPI Access**: Enable SmartAPI in your Angel One account
3. **API Credentials**: Get API key, client ID, and password from Angel One

**Note**: You can set up Angel One credentials later. The system will work with other providers (jugaad, nsedownload, nsepython) until Angel One is configured. Angel One is the PRIMARY live data provider but not required for basic functionality.

## Installation

### 1. Install SmartAPI Library

```bash
# Install SmartApi WITHOUT dependencies to avoid PyCrypto issues
pip install SmartApi --no-deps

# Then install pycryptodome separately (drop-in replacement for PyCrypto)
pip install pycryptodome>=3.23.0
```

**Important**: 
- Always import SmartConnect from `broker.angelone`, never directly from SmartApi
- See [SmartAPI Integration Guide](SMARTAPI_INTEGRATION.md) for complete details

### 2. Get API Credentials

1. Log in to [Angel One](https://www.angelone.in/)
2. Go to **Settings** → **API**
3. Generate API key
4. Note down:
   - **API Key**
   - **Client ID** (your Angel One client ID)
   - **Password** (your Angel One password)

## Configuration

**Important**: Angel One credentials are optional. The system will automatically fall back to other providers if Angel One is not configured. You can set up credentials later when ready.

### Option 1: Environment Variables (Recommended)

Create a `.env` file in the project root or set system environment variables:

```bash
# .env file
ANGEL_API_KEY=your_api_key_here
ANGEL_CLIENT_ID=your_client_id_here
ANGEL_PASSWORD=your_password_here
```

**Steps to get credentials:**
1. Log in to [Angel One](https://www.angelone.in/)
2. Navigate to **Settings** → **API** → **SmartAPI**
3. Click **Generate API Key**
4. Copy the API key
5. Your Client ID is your Angel One client ID (usually shown in the dashboard)
6. Your Password is your Angel One login password

**Note**: The `.env` file is gitignored, so your credentials won't be committed to version control.

### Option 2: Configuration File

Edit `config/data_providers.yaml`:

```yaml
provider_settings:
  angel:
    enabled: true
    api_key: your_api_key_here
    client_id: your_client_id_here
    password: your_password_here
    rate_limit_per_minute: 60
```

**Note**: Not recommended for production. Use environment variables instead.

## Authentication

Angel SmartAPI uses session-based authentication:

1. **Login**: Generate session token using API key, client ID, and password
2. **Token Storage**: Token is stored in provider instance
3. **Auto-Refresh**: Token is refreshed automatically when expired

## Usage

### Automatic Usage

Once configured, Angel SmartAPI is used automatically by ProviderRouter:

```python
# ProviderRouter automatically uses Angel for live data
quote = router.get_live_quote("RELIANCE")
```

### Manual Usage

```python
from backend.data.providers.broker.angel_smartapi_provider import AngelSmartAPIDataProvider
import os

provider = AngelSmartAPIDataProvider(
    api_key=os.getenv("ANGEL_API_KEY"),
    client_id=os.getenv("ANGEL_CLIENT_ID"),
    password=os.getenv("ANGEL_PASSWORD")
)

# Get live quote
quote = provider.get_live_quote("RELIANCE")
print(f"Price: {quote['price']}")

# Get intraday candles
candles = provider.get_intraday_candles("RELIANCE", "5m")

# Get options chain
chain = provider.get_options_chain("RELIANCE")
```

## Symbol Format

Angel SmartAPI uses specific symbol formats:

### Equity Symbols

- **Format**: `NSE:SYMBOL-EQ`
- **Example**: `NSE:RELIANCE-EQ`

The provider automatically formats symbols if needed.

### Futures Symbols

- **Format**: `NFO:SYMBOL-FUT`
- **Example**: `NFO:NIFTY-FUT`

## Rate Limits

- **Default**: 60 requests/minute
- **Configurable**: Set in `config/data_providers.yaml`
- **Enforcement**: ProviderRouter enforces rate limits automatically

## WebSocket Streaming

Angel SmartAPI supports WebSocket streaming for real-time data:

```python
def on_tick(symbol, tick_data):
    print(f"{symbol}: {tick_data}")

provider.get_live_stream(["RELIANCE", "INFY"], on_tick)
```

**Note**: WebSocket implementation is a skeleton and needs completion based on SmartAPI documentation.

## Troubleshooting

### Authentication Failed

**Error**: "Authentication failed"

**Solutions:**
1. Verify API key, client ID, and password are correct
2. Check if SmartAPI is enabled in your Angel One account
3. Verify account is active and not suspended

### No Data Returned

**Error**: "No quote returned" or "No data returned"

**Solutions:**
1. Check symbol format (should be `NSE:SYMBOL-EQ`)
2. Verify market is open (data only available during market hours)
3. Check network connectivity
4. Review SmartAPI documentation for symbol token requirements

### Rate Limit Exceeded

**Error**: "Rate limit reached"

**Solutions:**
1. Reduce request frequency
2. Increase `rate_limit_per_minute` in config (if allowed by Angel One)
3. Use caching to reduce API calls

### Symbol Token Issues

**Error**: "Symbol token not found"

**Solutions:**
1. Implement symbol token lookup (currently placeholder)
2. Query Angel One master contract list
3. Cache symbol token mappings

## Best Practices

1. **Use Environment Variables**: Never commit credentials to version control
2. **Monitor Rate Limits**: Stay within rate limits to avoid blocking
3. **Handle Failures**: Always handle None returns and exceptions
4. **Cache Data**: Cache frequently accessed data to reduce API calls
5. **Use Fallbacks**: Configure fallback providers for reliability

## API Documentation

For detailed API documentation, refer to:
- [Angel One SmartAPI Documentation](https://smartapi.angelone.in/)

## Security Notes

1. **Never commit credentials**: Use environment variables or secure config
2. **Rotate credentials**: Regularly rotate API keys
3. **Monitor usage**: Monitor API usage for suspicious activity
4. **Use HTTPS**: All API calls use HTTPS

## See Also

- [Data Providers Architecture](DATA_PROVIDERS.md)
- [Provider Validation](PROVIDER_VALIDATION.md)
- [NSE Blocking](NSE_BLOCKING.md)

