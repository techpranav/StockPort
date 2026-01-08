# Provider Validation

## Overview

All market data providers must pass mandatory validation before they can be enabled. This ensures data quality and system reliability.

## Validation Process

### Automatic Validation on Startup

When the system starts, `SystemIntegrator` runs the `ProviderTestSuite` for all providers:

1. **Provider Initialization**: All providers are initialized from config
2. **Validation Suite**: Each provider runs through full test suite
3. **Health Assessment**: ProviderHealth is generated with test results
4. **Auto-Disable**: Providers with DISABLED status are automatically disabled

### Validation Tests

#### 1. Historical Equity Test

**What it tests:**
- OHLC continuity (no missing candles)
- Timestamp alignment (timezone correctness)
- OHLC relationships (High >= Open/Low/Close, Low <= Open/High/Close)
- Negative value detection
- Zero volume handling

**Test Symbol**: RELIANCE (last 7 days)

**Validators Used:**
- `OHLCValidator`: Checks OHLC continuity and relationships
- `TimestampValidator`: Verifies timestamp alignment

#### 2. Options Chain Test

**What it tests:**
- Options chain completeness
- Strike coverage (minimum 5 strikes)
- Call and put data presence
- OI data completeness
- Negative OI detection

**Test Symbol**: RELIANCE

**Validators Used:**
- `OptionsValidator`: Validates options chain structure

#### 3. Futures Test

**What it tests:**
- Futures data structure
- OI consistency
- Price validity
- Expiry handling

**Test Symbol**: NIFTY

**Validators Used:**
- `FuturesValidator`: Validates futures data quality

#### 4. Latency Test

**What it tests:**
- Live data latency
- Response time consistency

**Test Symbol**: RELIANCE

**Validators Used:**
- `LatencyValidator`: Measures and validates latency

## Validation Results

### ProviderHealth Structure

```python
@dataclass
class ProviderHealth:
    provider_name: str
    status: str  # "ENABLED", "DISABLED", "DEGRADED"
    equity: str  # "PASS", "FAIL", "UNKNOWN"
    options: str  # "PASS", "FAIL", "UNKNOWN"
    futures: str  # "PASS", "FAIL", "UNKNOWN"
    latency_ms: Optional[float]
    last_check: Optional[datetime]
    issues: List[str]
```

### Status Determination

- **ENABLED**: All applicable tests pass, latency acceptable
- **DEGRADED**: Some tests fail or latency high
- **DISABLED**: All applicable tests fail

### Example Health Report

```json
{
  "provider": "AngelSmartAPI",
  "equity": "PASS",
  "options": "PASS",
  "futures": "PASS",
  "latency_ms": 185,
  "status": "ENABLED",
  "last_check": "2024-01-15T10:30:00Z",
  "issues": []
}
```

## Validators

### OHLCValidator

**Location**: `backend/data/providers/validation/validators/ohlc_validator.py`

**Checks:**
- Missing candles (gaps in time series)
- Invalid OHLC relationships
- Negative values
- Zero volume percentage

**Usage:**
```python
from backend.data.providers.validation.validators.ohlc_validator import OHLCValidator

is_valid, issues = OHLCValidator.validate(df, "1d")
```

### TimestampValidator

**Location**: `backend/data/providers/validation/validators/timestamp_validator.py`

**Checks:**
- DatetimeIndex type
- Duplicate timestamps
- Timezone correctness (IST for NSE)
- Market hours alignment
- Future timestamps
- Very old timestamps

**Usage:**
```python
from backend.data.providers.validation.validators.timestamp_validator import TimestampValidator

is_valid, issues = TimestampValidator.validate(df)
```

### OptionsValidator

**Location**: `backend/data/providers/validation/validators/options_validator.py`

**Checks:**
- Required columns (strike, expiry)
- Call and put data presence
- Strike coverage (minimum 5 strikes)
- OI data completeness
- Negative OI values

**Usage:**
```python
from backend.data.providers.validation.validators.options_validator import OptionsValidator

is_valid, issues = OptionsValidator.validate(df)
```

### FuturesValidator

**Location**: `backend/data/providers/validation/validators/futures_validator.py`

**Checks:**
- Required columns (price, oi)
- Negative OI values
- Missing OI data
- Negative prices
- Zero volume percentage
- Past expiry dates

**Usage:**
```python
from backend.data.providers.validation.validators.futures_validator import FuturesValidator

is_valid, issues = FuturesValidator.validate(df)
```

### LatencyValidator

**Location**: `backend/data/providers/validation/validators/latency_validator.py`

**Checks:**
- Response latency
- Latency consistency

**Thresholds:**
- **GOOD**: < 500ms
- **ACCEPTABLE**: < 1000ms
- **HIGH**: >= 1000ms

**Usage:**
```python
from backend.data.providers.validation.validators.latency_validator import LatencyValidator

latency_ms, is_valid = LatencyValidator.measure_latency(
    provider.get_live_quote,
    "RELIANCE"
)
```

## Manual Validation

You can manually run validation:

```python
from backend.data.providers.validation.provider_test_suite import ProviderTestSuite
from backend.data.providers.equity.jugaad_provider import JugaadDataProvider

provider = JugaadDataProvider()
test_suite = ProviderTestSuite()
health = test_suite.validate_provider(provider)

print(f"Status: {health.status}")
print(f"Issues: {health.issues}")
```

## Validation Failures

### Common Issues

1. **Library Not Installed**
   - Issue: "library not installed"
   - Fix: Install required library (e.g., `pip install jugaad-data`)

2. **Authentication Failed**
   - Issue: "Authentication failed"
   - Fix: Check credentials in environment variables or config

3. **No Data Returned**
   - Issue: "No data returned"
   - Fix: Check symbol format, network connectivity, NSE blocking

4. **High Latency**
   - Issue: "Latency too high"
   - Fix: Check network connection, provider status

5. **OHLC Validation Failed**
   - Issue: "Found gaps in data" or "Invalid OHLC relationships"
   - Fix: Provider data quality issue, may need to use fallback provider

## Best Practices

1. **Run Validation on Startup**: Always validate providers before use
2. **Monitor Health**: Check provider health regularly
3. **Handle Failures**: Gracefully handle validation failures
4. **Log Issues**: All validation issues are logged for debugging
5. **Use Fallbacks**: Always configure fallback providers

## See Also

- [Data Providers Architecture](DATA_PROVIDERS.md)
- [Angel SmartAPI Setup](ANGEL_SMARTAPI_SETUP.md)
- [NSE Blocking](NSE_BLOCKING.md)

