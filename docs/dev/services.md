# Services

This document describes the services used in the Stock Analysis Tool.

## Overview

The application uses several services to handle different aspects of stock analysis and report generation. Each service is responsible for a specific functionality and follows the single responsibility principle.

## Stock Service

The `StockService` class is the main service that coordinates data fetching and analysis:

```python
class StockService:
    def __init__(self, provider_name: str = None):
        self.provider = StockDataFactory.get_provider(provider_name) if provider_name else StockDataFactory.get_default_provider()
```

### Methods

- `fetch_stock_data(symbol: str) -> StockData`: Fetches all stock data
- `fetch_historical_data(symbol: str, period: str, interval: str) -> pd.DataFrame`: Fetches historical price data
- `fetch_financials(symbol: str) -> Dict[str, Any]`: Fetches financial statements
- `fetch_company_info(symbol: str) -> Dict[str, Any]`: Fetches company information
- `fetch_news(symbol: str, limit: int) -> List[Dict[str, Any]]`: Fetches company news

### Usage

```python
# Create service with default provider
service = StockService()

# Create service with specific provider
service = StockService(provider_name='yahoo')

# Fetch stock data
stock_data = service.fetch_stock_data('AAPL')
```

## Report Service

The `ReportService` class handles the generation of analysis reports:

```python
class ReportService:
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
```

### Methods

- `generate_excel_report(symbol: str, data: Dict[str, Any]) -> str`: Generates an Excel report
- `generate_word_report(symbol: str, data: Dict[str, Any]) -> str`: Generates a Word report
- `_write_company_info(writer: pd.ExcelWriter, data: Dict[str, Any])`: Writes company info to Excel
- `_write_metrics(writer: pd.ExcelWriter, data: Dict[str, Any])`: Writes metrics to Excel
- `_write_technical_analysis(writer: pd.ExcelWriter, data: Dict[str, Any])`: Writes technical analysis to Excel
- `_write_fundamental_analysis(writer: pd.ExcelWriter, data: Dict[str, Any])`: Writes fundamental analysis to Excel
- `_write_portfolio_analysis(writer: pd.ExcelWriter, data: Dict[str, Any])`: Writes portfolio analysis to Excel
- `_write_financial_statements(writer: pd.ExcelWriter, data: Dict[str, Any])`: Writes financial statements to Excel

### Usage

```python
# Create report service
report_service = ReportService()

# Generate Excel report
excel_path = report_service.generate_excel_report('AAPL', stock_data)

# Generate Word report
word_path = report_service.generate_word_report('AAPL', stock_data)
```

## Technical Analysis Service

The `TechnicalAnalysisService` class handles technical analysis calculations:

```python
class TechnicalAnalysisService:
    def calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators."""
        pass
    
    def calculate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """Calculate technical signals."""
        pass
```

### Methods

- `calculate_indicators(data: pd.DataFrame) -> Dict[str, Any]`: Calculates technical indicators
- `calculate_signals(data: pd.DataFrame) -> Dict[str, str]`: Calculates technical signals
- `_calculate_trend(data: pd.DataFrame) -> str`: Calculates trend signal
- `_calculate_momentum(data: pd.DataFrame) -> str`: Calculates momentum signal
- `_calculate_volatility(data: pd.DataFrame) -> str`: Calculates volatility signal
- `_calculate_volume(data: pd.DataFrame) -> str`: Calculates volume signal

### Usage

```python
# Create technical analysis service
tech_service = TechnicalAnalysisService()

# Calculate indicators
indicators = tech_service.calculate_indicators(historical_data)

# Calculate signals
signals = tech_service.calculate_signals(historical_data)
```

## Fundamental Analysis Service

The `FundamentalAnalysisService` class handles fundamental analysis calculations:

```python
class FundamentalAnalysisService:
    def calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate fundamental metrics."""
        pass
```

### Methods

- `calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]`: Calculates fundamental metrics
- `_calculate_profitability(data: Dict[str, Any]) -> Dict[str, float]`: Calculates profitability ratios
- `_calculate_liquidity(data: Dict[str, Any]) -> Dict[str, float]`: Calculates liquidity ratios
- `_calculate_debt(data: Dict[str, Any]) -> Dict[str, float]`: Calculates debt ratios
- `_calculate_market(data: Dict[str, Any]) -> Dict[str, float]`: Calculates market ratios

### Usage

```python
# Create fundamental analysis service
fund_service = FundamentalAnalysisService()

# Calculate metrics
metrics = fund_service.calculate_metrics(stock_data)
```

## Portfolio Analysis Service

The `PortfolioAnalysisService` class handles portfolio analysis calculations:

```python
class PortfolioAnalysisService:
    def calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate portfolio metrics."""
        pass
```

### Methods

- `calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]`: Calculates portfolio metrics
- `_calculate_risk(data: Dict[str, Any]) -> Dict[str, float]`: Calculates risk metrics
- `_calculate_returns(data: Dict[str, Any]) -> Dict[str, float]`: Calculates return metrics
- `_calculate_dividends(data: Dict[str, Any]) -> Dict[str, float]`: Calculates dividend metrics

### Usage

```python
# Create portfolio analysis service
port_service = PortfolioAnalysisService()

# Calculate metrics
metrics = port_service.calculate_metrics(stock_data)
```

## Best Practices

1. Use dependency injection for services
2. Implement proper error handling
3. Use logging for debugging
4. Cache results when appropriate
5. Validate input data
6. Use type hints
7. Document all methods
8. Write unit tests

## Error Handling

Services should handle errors appropriately:

```python
try:
    result = self._calculate_metrics(data)
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

## Logging

Services should use proper logging:

```python
import logging

logger = logging.getLogger(__name__)

def some_method(self):
    logger.debug("Starting calculation")
    try:
        result = self._calculate()
        logger.info("Calculation completed successfully")
        return result
    except Exception as e:
        logger.error(f"Calculation failed: {e}")
        raise
```

## Caching

Services can implement caching to improve performance:

```python
from functools import lru_cache

class SomeService:
    @lru_cache(maxsize=100)
    def cached_method(self, symbol: str) -> Dict[str, Any]:
        return self._calculate(symbol)
``` 