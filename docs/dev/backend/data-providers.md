# Data Providers

Data providers fetch OHLCV and market metadata. Providers should be treated as unreliable and must be validated.

## Principles

- Validate schema and required columns
- Handle missing/stale candles gracefully
- Track provider health and latency

See:

- [Data providers](../DATA_PROVIDERS.md)
- [Provider validation](../PROVIDER_VALIDATION.md)
- [NSEPython provider](../NSEPYTHON_PROVIDER.md)
- [NSE blocking](../NSE_BLOCKING.md)


