# Data providers (overview)

Stockport is designed to support multiple market data sources. Provider integration should be:

- Validated (guard against missing/invalid candles)
- Rate-limited (avoid bans / throttling)
- Observable (health status surfaced to UI)

## Where to look

- Provider implementations: `services/data_providers/`
- Backend docs: [Backend data providers](../backend/data-providers.md)


