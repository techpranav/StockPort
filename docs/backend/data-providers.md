# Data Providers

Data providers fetch OHLCV and market metadata. Providers should be treated as unreliable and must be validated.

## Principles

- Validate schema and required columns
- Handle missing/stale candles gracefully
- Track provider health and latency

See:

- `DATA_PROVIDERS.md`
- `PROVIDER_VALIDATION.md`
- `NSEPYTHON_PROVIDER.md`
- `NSE_BLOCKING.md`


