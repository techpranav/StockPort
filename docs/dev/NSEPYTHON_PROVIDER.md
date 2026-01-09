# NSEPython Provider Documentation

## Overview

The NSEPython provider is an additional data provider for Indian stock markets (NSE) that uses the `nsepython` library to fetch data directly from NSE APIs.

## Features

✅ **Live/Real-time Data**: Fetches current stock prices and quote information  
✅ **Company Information**: Retrieves company details, sector, industry, market cap  
✅ **Quote Data**: Comprehensive quote information from NSE  
⚠️ **Historical Data**: Limited support (API limitations may apply)

## Installation

The provider requires the `nsepython` library:

```bash
pip install nsepython
```

## Usage

### Basic Usage

```python
from services.stock_data_factory import StockDataFactory

# Get NSEPython provider
provider = StockDataFactory.get_provider('nsepython')

# Fetch current price
price = provider.fetch_current_price('RELIANCE')
print(f"RELIANCE Price: Rs.{price}")

# Fetch company info
info = provider.fetch_company_info('TCS')
print(f"Company: {info.get('companyName')}")
print(f"Sector: {info.get('industry')}")
```

### Using with StockService

```python
from services.stock_service import StockService

# Create service with NSEPython provider
service = StockService(provider_name='nsepython')

# Fetch comprehensive stock data
stock_data = service.fetch_stock_data('HDFCBANK')
print(f"Company: {stock_data.company_info.name}")
print(f"Current Price: {stock_data.technical_analysis.current_price}")
```

## Supported Methods

### `fetch_current_price(symbol: str) -> Optional[float]`

Fetches the current/live price for an Indian stock.

**Parameters:**
- `symbol`: Stock symbol (e.g., 'RELIANCE', 'TCS', 'HDFCBANK')

**Returns:**
- Current price as float, or None if unavailable

**Example:**
```python
price = provider.fetch_current_price('RELIANCE')
# Returns: 1478.5
```

### `fetch_company_info(symbol: str) -> Dict[str, Any]`

Fetches company information for an Indian stock.

**Parameters:**
- `symbol`: Stock symbol

**Returns:**
- Dictionary containing company information including:
  - `companyName`: Company name
  - `industry`: Industry/sector
  - `marketCap`: Market capitalization
  - `lastPrice`: Last traded price
  - `previousClose`: Previous close price
  - `open`, `high`, `low`: Price data
  - `volume`: Trading volume

**Example:**
```python
info = provider.fetch_company_info('TCS')
print(info['companyName'])  # Tata Consultancy Services Limited
print(info['industry'])      # IT Services
```

### `fetch_historical_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame`

Fetches historical price data. **Note**: Historical data may have limitations due to NSE API restrictions.

**Parameters:**
- `symbol`: Stock symbol
- `period`: Period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
- `interval`: Data interval (primarily supports daily: 1d)

**Returns:**
- DataFrame with historical OHLCV data (may be empty if API limitations apply)

### `fetch_stock_data(symbol: str) -> StockData`

Fetches comprehensive stock data including company info, current price, and historical data.

**Parameters:**
- `symbol`: Stock symbol

**Returns:**
- `StockData` object with all available information

## Tested Sectors

The provider has been tested with stocks from multiple sectors:

- ✅ **Banking**: HDFCBANK, ICICIBANK, SBIN
- ✅ **IT**: TCS, INFY, WIPRO
- ✅ **Energy**: RELIANCE, ONGC, IOC
- ✅ **Pharma**: SUNPHARMA, DRREDDY, CIPLA
- ✅ **FMCG**: HINDUNILVR, ITC, NESTLEIND
- ✅ **Automobile**: MARUTI, M&M, TATAMOTORS
- ✅ **Telecom**: BHARTIARTL
- ✅ **Metals**: TATASTEEL, JSWSTEEL, HINDALCO

## Advantages

1. **Direct NSE API Access**: Fetches data directly from NSE, ensuring accuracy
2. **Real-time Data**: Provides current/live prices
3. **Comprehensive Quote Data**: Includes detailed company and market information
4. **No API Key Required**: Uses public NSE APIs

## Limitations

1. **Historical Data**: Historical data fetching may have limitations or rate restrictions
2. **NSE Only**: Currently supports only NSE (National Stock Exchange), not BSE
3. **API Rate Limits**: Subject to NSE API rate limits and availability

## Comparison with Other Providers

| Feature | NSEPython | Yahoo Finance (yfinance) |
|---------|----------|------------------------|
| Live Data | ✅ | ✅ |
| Historical Data | ⚠️ Limited | ✅ |
| Company Info | ✅ | ✅ |
| NSE Support | ✅ Direct | ✅ (via .NS suffix) |
| BSE Support | ❌ | ✅ (via .BO suffix) |
| API Key Required | ❌ | ❌ |

## Error Handling

The provider handles errors gracefully:

- Returns `None` for unavailable prices
- Returns empty dictionaries for unavailable company info
- Returns empty DataFrames for unavailable historical data
- Logs errors using `DebugUtils` for troubleshooting

## Testing

Comprehensive tests are available in:
- `tests/integration/test_indstocks_provider_comprehensive.py`

Run tests:
```bash
pytest tests/integration/test_indstocks_provider_comprehensive.py -v
```

## Notes

- The provider automatically normalizes symbols (removes .NS/.BO suffixes if present)
- All symbols are converted to uppercase
- The provider is registered in `StockDataFactory` with name `'nsepython'` and alias `'nse_python'`

