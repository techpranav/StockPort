# Data Adapter Pattern Documentation

## Overview

The Data Adapter Pattern provides a unified interface for accessing stock data from multiple providers. This abstraction layer ensures that all analysis calculations work consistently regardless of the data source.

## Architecture

```
┌─────────────────┐
│  Data Providers │
│ (Yahoo, NSE...) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Adapters  │
│ (Normalization) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Standard Schema │
│  (Internal Use) │
└─────────────────┘
```

## Standard Data Schema

All data is normalized to a standard internal format defined in `models/data_schema.py`:

- **OPEN**: Opening price
- **HIGH**: High price
- **LOW**: Low price
- **CLOSE**: Closing price
- **VOLUME**: Trading volume
- **ADJ_CLOSE**: Adjusted closing price

## Adapter Implementation

### Base Adapter

All adapters inherit from `DataAdapter`:

```python
from services.data_providers.adapters.data_adapter import DataAdapter

class MyProviderAdapter(DataAdapter):
    def _get_column_mappings(self) -> Dict[str, str]:
        """Map provider columns to standard columns."""
        return {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
```

### Using Adapters

```python
from services.data_providers.adapters.adapter_factory import AdapterFactory

# Get adapter for provider
adapter = AdapterFactory.get_adapter('yahoo_finance')

# Normalize data
normalized_df = adapter.normalize_dataframe(raw_data)

# Access columns safely
close_prices = adapter.get_column(normalized_df, 'close')
```

## Available Adapters

1. **YahooFinanceAdapter** - For Yahoo Finance data
2. **AlphaVantageAdapter** - For Alpha Vantage data
3. **NSEAdapter** - For NSE (Indian) data
4. **BSEAdapter** - For BSE (Indian) data

## Benefits

1. **Provider Independence** - Analysis code works with any provider
2. **Consistent Data Format** - No need to handle different column names
3. **Easy Extension** - Add new providers by creating new adapters
4. **Type Safety** - Validated column access prevents KeyErrors
5. **Data Validation** - Automatic validation of required columns

## Usage in Analysis

All analysis modules use adapters instead of direct DataFrame access:

```python
# ❌ Bad - Direct column access
close = df['Close']

# ✅ Good - Using adapter
adapter = AdapterFactory.get_adapter(provider_name)
close = adapter.get_column(df, 'close')
```

## Adding New Providers

1. Create adapter class inheriting from `DataAdapter`
2. Implement `_get_column_mappings()` method
3. Register in `AdapterFactory`
4. All existing analysis code will work automatically!

