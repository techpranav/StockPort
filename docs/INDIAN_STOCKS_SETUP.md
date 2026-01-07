# Indian Stock Market Support

## Overview

The application supports Indian stock markets (NSE and BSE) through dedicated providers and adapters.

## Supported Markets

- **NSE (National Stock Exchange)**: Use `.NS` suffix with yfinance
- **BSE (Bombay Stock Exchange)**: Use `.BO` suffix with yfinance

## Usage

### NSE Stocks

```python
from services.stock_data_factory import StockDataFactory

# Get NSE provider
provider = StockDataFactory.get_provider('nse')

# Fetch NSE stock data
data = provider.fetch_stock_data('RELIANCE.NS')
```

### BSE Stocks

```python
# Get BSE provider
provider = StockDataFactory.get_provider('bse')

# Fetch BSE stock data
data = provider.fetch_stock_data('RELIANCE.BO')
```

## Symbol Format

### NSE Symbols
- Format: `SYMBOL.NS`
- Examples: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`

### BSE Symbols
- Format: `SYMBOL.BO`
- Examples: `RELIANCE.BO`, `TCS.BO`, `INFY.BO`

## Data Providers

### NSE Provider
- **Class**: `NSEProvider`
- **Library**: `yfinance` with `.NS` suffix
- **Adapter**: `NSEAdapter`
- **Features**: Historical and live data

### BSE Provider
- **Class**: `BSEProvider`
- **Library**: `yfinance` with `.BO` suffix
- **Adapter**: `BSEAdapter`
- **Features**: Historical and live data

## Testing Libraries

The following libraries were tested for Indian stock data:

1. **yfinance** ✅ (Selected)
   - Pros: Stable, good data coverage, easy to use
   - Cons: Rate limits, occasional data gaps
   - Usage: Works with `.NS` and `.BO` suffixes

2. **nsepy** ⚠️
   - Pros: NSE-specific, official data
   - Cons: Limited functionality, maintenance issues

3. **nsetools** ⚠️
   - Pros: Real-time data
   - Cons: Unstable, limited historical data

4. **investpy** ⚠️
   - Pros: Multiple markets
   - Cons: Rate limits, data quality issues

## Configuration

No special configuration required. The providers are automatically registered in `StockDataFactory`.

## Data Normalization

All Indian stock data is normalized through adapters to match the standard internal format:

- NSE data → `NSEAdapter` → Standard format
- BSE data → `BSEAdapter` → Standard format

This ensures all analysis calculations work consistently with Indian stocks.

## Example

```python
from core.stock_analyzer import StockAnalyzer

analyzer = StockAnalyzer()

# Analyze NSE stock
result = analyzer.process_stock('RELIANCE.NS')

# Analyze BSE stock
result = analyzer.process_stock('RELIANCE.BO')

# Both work with all analysis features!
```

## Limitations

- **Data Availability**: Depends on yfinance data quality
- **Rate Limits**: Subject to yfinance API limits
- **Market Hours**: Data updates during market hours
- **Delayed Data**: Some data may be delayed (15-20 minutes)

## Troubleshooting

### Symbol Not Found
- Verify symbol format (`.NS` or `.BO`)
- Check if stock is listed on exchange
- Try alternative symbol format

### Data Not Available
- Check market hours (9:15 AM - 3:30 PM IST)
- Verify internet connection
- Check yfinance service status

### Rate Limiting
- Reduce number of concurrent requests
- Add delays between requests
- Use caching for frequently accessed data

