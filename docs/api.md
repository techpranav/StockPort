# API Documentation

This document provides detailed API documentation for the Stock Analysis Tool.

## Stock Service API

### `StockService`

Main service for fetching and analyzing stock data.

#### Constructor
```python
def __init__(self, provider_name: str = None)
```
- `provider_name`: Optional name of the data provider to use. If None, uses default provider.

#### Methods

##### `fetch_stock_data`
```python
def fetch_stock_data(self, symbol: str) -> StockData
```
Fetches complete stock data including company info, metrics, and analysis.

Parameters:
- `symbol`: Stock symbol (e.g., "AAPL")

Returns:
- `StockData` object containing all stock information

Example:
```python
service = StockService()
stock_data = service.fetch_stock_data("AAPL")
print(f"Company: {stock_data.company_info.name}")
print(f"Current Price: {stock_data.technical_analysis.current_price}")
```

##### `fetch_historical_data`
```python
def fetch_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame
```
Fetches historical price data.

Parameters:
- `symbol`: Stock symbol
- `period`: Time period ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
- `interval`: Data interval ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")

Returns:
- DataFrame with historical price data

Example:
```python
historical_data = service.fetch_historical_data("AAPL", period="1y", interval="1d")
print(historical_data.head())
```

##### `fetch_financials`
```python
def fetch_financials(self, symbol: str) -> Dict[str, Any]
```
Fetches financial statements.

Parameters:
- `symbol`: Stock symbol

Returns:
- Dictionary containing financial statements

Example:
```python
financials = service.fetch_financials("AAPL")
print(financials['income_statement'].head())
```

## Report Service API

### `ReportService`

Service for generating analysis reports.

#### Constructor
```python
def __init__(self)
```
Creates a new ReportService instance and initializes the reports directory.

#### Methods

##### `generate_excel_report`
```python
def generate_excel_report(self, symbol: str, data: Dict[str, Any]) -> str
```
Generates an Excel report for stock analysis.

Parameters:
- `symbol`: Stock symbol
- `data`: Stock data dictionary

Returns:
- Path to the generated Excel file

Example:
```python
report_service = ReportService()
excel_path = report_service.generate_excel_report("AAPL", stock_data.to_dict())
print(f"Report generated at: {excel_path}")
```

##### `generate_word_report`
```python
def generate_word_report(self, symbol: str, data: Dict[str, Any]) -> str
```
Generates a Word report for stock analysis.

Parameters:
- `symbol`: Stock symbol
- `data`: Stock data dictionary

Returns:
- Path to the generated Word file

Example:
```python
word_path = report_service.generate_word_report("AAPL", stock_data.to_dict())
print(f"Report generated at: {word_path}")
```

## Technical Analysis Service API

### `TechnicalAnalysisService`

Service for calculating technical indicators and signals.

#### Methods

##### `calculate_indicators`
```python
def calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]
```
Calculates technical indicators from price data.

Parameters:
- `data`: DataFrame with OHLCV data

Returns:
- Dictionary of technical indicators

Example:
```python
tech_service = TechnicalAnalysisService()
indicators = tech_service.calculate_indicators(historical_data)
print(f"RSI: {indicators['rsi']}")
print(f"MACD: {indicators['macd']}")
```

##### `calculate_signals`
```python
def calculate_signals(self, data: pd.DataFrame) -> Dict[str, str]
```
Calculates trading signals from price data.

Parameters:
- `data`: DataFrame with OHLCV data

Returns:
- Dictionary of trading signals

Example:
```python
signals = tech_service.calculate_signals(historical_data)
print(f"Trend: {signals['trend']}")
print(f"Momentum: {signals['momentum']}")
```

## Fundamental Analysis Service API

### `FundamentalAnalysisService`

Service for calculating fundamental metrics.

#### Methods

##### `calculate_metrics`
```python
def calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]
```
Calculates fundamental metrics from financial data.

Parameters:
- `data`: Dictionary containing financial data

Returns:
- Dictionary of fundamental metrics

Example:
```python
fund_service = FundamentalAnalysisService()
metrics = fund_service.calculate_metrics(stock_data.to_dict())
print(f"P/E Ratio: {metrics['pe_ratio']}")
print(f"ROE: {metrics['roe']}")
```

## Portfolio Analysis Service API

### `PortfolioAnalysisService`

Service for calculating portfolio metrics.

#### Methods

##### `calculate_metrics`
```python
def calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]
```
Calculates portfolio metrics from stock data.

Parameters:
- `data`: Dictionary containing stock data

Returns:
- Dictionary of portfolio metrics

Example:
```python
port_service = PortfolioAnalysisService()
metrics = port_service.calculate_metrics(stock_data.to_dict())
print(f"Beta: {metrics['beta']}")
print(f"Sharpe Ratio: {metrics['sharpe_ratio']}")
```

## Data Provider API

### `StockDataProvider`

Abstract base class for data providers.

#### Methods

##### `get_provider_name`
```python
def get_provider_name(self) -> str
```
Returns the name of the provider.

##### `fetch_stock_data`
```python
def fetch_stock_data(self, symbol: str) -> StockData
```
Fetches complete stock data.

Parameters:
- `symbol`: Stock symbol

Returns:
- `StockData` object

##### `fetch_historical_data`
```python
def fetch_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame
```
Fetches historical price data.

Parameters:
- `symbol`: Stock symbol
- `period`: Time period
- `interval`: Data interval

Returns:
- DataFrame with historical data

##### `fetch_financials`
```python
def fetch_financials(self, symbol: str) -> Dict[str, Any]
```
Fetches financial statements.

Parameters:
- `symbol`: Stock symbol

Returns:
- Dictionary of financial statements

##### `fetch_company_info`
```python
def fetch_company_info(self, symbol: str) -> Dict[str, Any]
```
Fetches company information.

Parameters:
- `symbol`: Stock symbol

Returns:
- Dictionary of company information

##### `fetch_news`
```python
def fetch_news(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]
```
Fetches company news.

Parameters:
- `symbol`: Stock symbol
- `limit`: Maximum number of news items to fetch

Returns:
- List of news items 