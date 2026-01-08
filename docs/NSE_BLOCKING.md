# NSE Blocking Detection and Mitigation

## Overview

NSE (National Stock Exchange) may block excessive requests or suspicious activity. Stockport v4 includes automatic detection and mitigation for NSE blocking.

## What is NSE Blocking?

NSE blocking occurs when:
- Too many requests are made in a short time
- Requests come from suspicious IP addresses
- Automated scraping is detected
- Rate limits are exceeded

### Symptoms

- **Connection Refused**: "Connection refused" errors
- **Connection Reset**: "Connection reset by peer" errors
- **Timeouts**: Requests timing out
- **503 Errors**: Service unavailable errors
- **429 Errors**: Too many requests errors

## Detection

### Automatic Detection

ProviderRouter automatically detects NSE blocking by checking error messages for:

- "connection refused"
- "connection reset"
- "timeout"
- "503"
- "429"
- "rate limit"
- "too many requests"

### Detection Code

```python
def _is_nse_blocking(self, error_msg: str) -> bool:
    """Check if error indicates NSE blocking."""
    nse_blocking_indicators = [
        "connection refused",
        "connection reset",
        "timeout",
        "503",
        "429",
        "rate limit",
        "too many requests"
    ]
    
    error_lower = error_msg.lower()
    return any(indicator in error_lower for indicator in nse_blocking_indicators)
```

## Mitigation

### Automatic Fallback

When NSE blocking is detected:

1. **Immediate Fallback**: ProviderRouter immediately falls back to next provider
2. **No Retry**: Blocked provider is not retried (avoids further blocking)
3. **Health Degradation**: Provider health is degraded to RED
4. **Auto-Disable**: After 10+ failures, provider is auto-disabled

### Fallback Chain

Example for historical data:

```
jugaad (primary)
    ↓ [NSE Blocking Detected]
nsedownload (fallback)
    ↓ [If also blocked]
nsepython (if configured)
```

## Prevention

### Rate Limiting

All providers implement rate limiting:

```yaml
provider_settings:
  jugaad:
    rate_limit_per_minute: 10
  nsedownload:
    rate_limit_per_minute: 5
  nsepython:
    rate_limit_per_minute: 20
```

### Best Practices

1. **Respect Rate Limits**: Stay within configured rate limits
2. **Use Multiple Providers**: Distribute load across providers
3. **Implement Caching**: Cache data to reduce API calls
4. **Use Fallbacks**: Always configure fallback providers
5. **Monitor Health**: Monitor provider health regularly

### Configuration Recommendations

```yaml
data_providers:
  historical:
    primary: jugaad
    fallback: nsedownload  # Different provider to avoid same blocking
    timeout_seconds: 10
    retry_attempts: 3  # Don't retry too many times
```

## Recovery

### Automatic Recovery

Providers can recover from blocking:

1. **Health Improvement**: After successful requests, health improves
2. **Re-enable**: Disabled providers can be manually re-enabled
3. **Time-Based**: Blocking may be temporary (wait and retry)

### Manual Recovery

```python
# Check provider health
health = router.provider_health["jugaad"]
print(f"Status: {health.status}")
print(f"Issues: {health.issues}")

# Re-enable provider (if needed)
router.disabled_providers.remove("jugaad")
```

## Monitoring

### Health Monitoring

Provider health is tracked in real-time:

- **GREEN**: Provider is healthy
- **YELLOW**: Minor issues (degraded)
- **RED**: Major issues (blocking detected)

### Logging

All NSE blocking events are logged:

```
WARNING: Provider jugaad blocked: NSE blocking
WARNING: Falling back to nsedownload
WARNING: Provider jugaad disabled due to 10 failures
```

## Compliance

### NSE Terms of Service

All providers must comply with NSE terms of service:

1. **No Scraping**: Don't scrape NSE website directly
2. **Use APIs**: Use official APIs when available
3. **Respect Limits**: Stay within rate limits
4. **No Automation**: Don't automate excessive requests

### Legal Considerations

- **Terms of Service**: Review NSE terms of service
- **Rate Limits**: Respect documented rate limits
- **Data Usage**: Use data only for personal trading
- **Commercial Use**: Commercial use may require licensing

## Troubleshooting

### Persistent Blocking

If blocking persists:

1. **Check IP**: Your IP may be blocked
2. **Wait**: Blocking may be temporary (wait 24-48 hours)
3. **Use VPN**: Change IP address (if allowed)
4. **Contact NSE**: Contact NSE support if legitimate use

### All Providers Blocked

If all providers are blocked:

1. **Check Network**: Verify network connectivity
2. **Check Firewall**: Check firewall settings
3. **Review Logs**: Review logs for patterns
4. **Use Alternative**: Consider alternative data sources

## Best Practices Summary

1. ✅ **Respect Rate Limits**: Stay within configured limits
2. ✅ **Use Fallbacks**: Always configure fallback providers
3. ✅ **Monitor Health**: Check provider health regularly
4. ✅ **Handle Failures**: Gracefully handle blocking
5. ✅ **Cache Data**: Reduce API calls with caching
6. ✅ **Comply with ToS**: Follow NSE terms of service

## See Also

- [Data Providers Architecture](DATA_PROVIDERS.md)
- [Provider Validation](PROVIDER_VALIDATION.md)
- [Angel SmartAPI Setup](ANGEL_SMARTAPI_SETUP.md)

