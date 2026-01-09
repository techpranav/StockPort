# Market Data Providers Architecture

## Overview

Stockport v4 uses a hybrid market data provider architecture that supports multiple data sources with automatic fallback, health monitoring, and mandatory validation. This ensures high availability and data quality for trading operations.

## Architecture

### Component Structure

```
backend/data/providers/
├── interfaces/          # MarketDataProvider ABC interface
├── router/             # ProviderRouter with fallback logic
├── equity/             # Equity data providers (jugaad, nsedownload, nsepython)
├── broker/             # Broker-based providers (Angel SmartAPI)
├── health/             # Provider health monitoring
└── validation/         # Mandatory validation suite
```

### Data Flow

```
Market Scanner / Truth Layer
    │
    ▼
ProviderRouter
    │
    ├─→ Primary Provider (e.g., jugaad for historical)
    │   │
    │   └─→ [Failure] → Fallback Provider (e.g., nsedownload)
    │
    └─→ Health Monitor (tracks provider health)
```

## Supported Providers

### Historical Data Providers

#### 1. JugaadDataProvider (Primary)
- **Library**: `jugaad-data`
- **Capabilities**: Historical equity/index data
- **Rate Limit**: 10 requests/minute (configurable)
- **Use Case**: Primary source for historical data

#### 2. NSEDownloadProvider (Fallback)
- **Library**: `NSEDownload`
- **Capabilities**: Bulk historical data
- **Rate Limit**: 5 requests/minute (configurable)
- **Use Case**: Fallback when jugaad fails

### Live Data Providers

#### 3. NSEPythonProvider (Fallback)
- **Library**: `nsepython`
- **Capabilities**: Live quotes, intraday, options chain
- **Rate Limit**: 20 requests/minute (configurable)
- **Use Case**: Fallback for live data and options

#### 4. AngelSmartAPIDataProvider (Primary)
- **Library**: `smartapi` (Angel One SmartAPI)
- **Capabilities**: 
  - Intraday candles
  - Live quotes
  - WebSocket streaming
  - Options chain
  - Futures (NFO)
- **Rate Limit**: 60 requests/minute (configurable)
- **Use Case**: PRIMARY live data provider (FREE)

## Provider Capabilities Matrix

| Provider | Historical | Intraday | Live | Options | Futures |
|----------|-----------|----------|------|---------|---------|
| jugaad | ✅ | ❌ | ❌ | ❌ | ❌ |
| nsedownload | ✅ | ❌ | ❌ | ❌ | ❌ |
| nsepython | ❌ | ✅ | ✅ | ✅ | ❌ |
| angel | ✅ | ✅ | ✅ | ✅ | ✅ |

## Configuration

Provider configuration is defined in `config/data_providers.yaml`:

```yaml
data_providers:
  historical:
    primary: jugaad
    fallback: nsedownload
    timeout_seconds: 10
    retry_attempts: 3
  
  live:
    primary: angel
    fallback: nsepython
    timeout_seconds: 5
    retry_attempts: 2
```

## Fallback Logic

The ProviderRouter implements intelligent fallback:

1. **Primary Provider**: Attempts to fetch from primary provider
2. **Timeout Handling**: Falls back on timeout (configurable per data type)
3. **Bad Data Detection**: Falls back if data validation fails
4. **Rate Limit**: Falls back on rate limit (429) errors
5. **NSE Blocking**: Detects and falls back on NSE blocking
6. **Health-Based**: Skips providers with DISABLED status

### Fallback Triggers

- **Timeout**: Request exceeds configured timeout
- **Bad Data**: Data validation fails (missing candles, invalid OHLC)
- **Rate Limit**: Provider returns 429 status
- **NSE Blocking**: Connection refused or reset
- **Provider Health**: Provider status is DISABLED

## Health Monitoring

### Provider Health States

- **ENABLED**: Provider is healthy and operational
- **DEGRADED**: Provider has issues but still usable
- **DISABLED**: Provider is disabled (auto-disabled after validation failure or too many failures)

### Health Degradation

- **Success**: Maintains or improves health
- **Timeout**: Degrades to YELLOW
- **Bad Data**: Degrades to YELLOW
- **Rate Limit**: Degrades to RED (temporary)
- **NSE Blocking**: Degrades to RED
- **10+ Failures**: Auto-disabled

## Integration Points

### Truth Layer Integration

The TruthLayer can optionally use ProviderRouter for data fetching:

```python
truth_layer = TruthLayer(
    health_monitor,
    price_reconciler,
    broker=None,
    data_provider_router=provider_router  # Optional
)
```

### System Integrator

ProviderRouter is initialized in SystemIntegrator:

1. Loads configuration from `config/data_providers.yaml`
2. Initializes all providers
3. Runs mandatory validation suite
4. Disables providers that fail validation
5. Injects ProviderRouter into TruthLayer

## Usage Examples

### Fetching Historical Data

```python
from backend.data.providers.router.provider_router import ProviderRouter

router = ProviderRouter(config, health_monitor)
df = router.get_historical_equity("RELIANCE", start_date, end_date, "1d")
```

### Fetching Live Quote

```python
quote = router.get_live_quote("RELIANCE")
price = quote['price']
```

### Fetching Options Chain

```python
chain = router.get_options_chain("RELIANCE", expiry_date)
```

## Best Practices

1. **Always use ProviderRouter**: Don't call providers directly
2. **Respect Rate Limits**: Configuration enforces rate limits
3. **Monitor Health**: Check provider health before critical operations
4. **Handle Failures**: Always handle None returns from router methods
5. **Use Timeouts**: Configure appropriate timeouts per data type

## Troubleshooting

### Provider Not Working

1. Check provider health: `router.provider_health[provider_name]`
2. Check validation results: Look for issues in ProviderHealth
3. Check logs: DebugUtils logs all provider operations
4. Check credentials: Angel SmartAPI requires valid credentials

### All Providers Failing

1. Check network connectivity
2. Check NSE blocking status
3. Review rate limit settings
4. Check provider library installations

## See Also

- [Provider Validation](PROVIDER_VALIDATION.md)
- [Angel SmartAPI Setup](ANGEL_SMARTAPI_SETUP.md)
- [NSE Blocking](NSE_BLOCKING.md)

