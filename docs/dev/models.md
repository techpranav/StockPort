# Data Models

This document describes the data models used in the Stock Analysis Tool.

## Overview

The application uses dataclasses to define standardized data structures for stock information. These models ensure consistency across different data providers and make the code more maintainable.

## Models

### CompanyInfo

Represents basic company information.

```python
@dataclass
class CompanyInfo:
    symbol: str
    name: str
    sector: Optional[str]
    industry: Optional[str]
    website: Optional[str]
    description: Optional[str]
    country: Optional[str]
    currency: Optional[str]
    exchange: Optional[str]
    market_cap: Optional[float]
    employees: Optional[int]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
```

### FinancialMetrics

Contains key financial metrics for a company.

```python
@dataclass
class FinancialMetrics:
    revenue: Optional[float]
    gross_profit: Optional[float]
    operating_income: Optional[float]
    net_income: Optional[float]
    total_assets: Optional[float]
    total_liabilities: Optional[float]
    total_equity: Optional[float]
    operating_cash_flow: Optional[float]
    investing_cash_flow: Optional[float]
    financing_cash_flow: Optional[float]
    free_cash_flow: Optional[float]
    eps: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    beta: Optional[float]
```

### TechnicalIndicators

Contains technical analysis indicators.

```python
@dataclass
class TechnicalIndicators:
    current_price: Optional[float]
    sma_20: Optional[float]
    sma_50: Optional[float]
    sma_200: Optional[float]
    rsi: Optional[float]
    macd: Optional[float]
    macd_signal: Optional[float]
    macd_histogram: Optional[float]
    bb_upper: Optional[float]
    bb_middle: Optional[float]
    bb_lower: Optional[float]
    volume: Optional[float]
    volume_sma: Optional[float]
```

### TechnicalSignals

Contains technical analysis signals.

```python
@dataclass
class TechnicalSignals:
    trend: Optional[str]      # "Bullish", "Bearish", "Neutral"
    momentum: Optional[str]   # "Overbought", "Oversold", "Neutral"
    volatility: Optional[str] # "High", "Low", "Normal"
    volume: Optional[str]     # "High", "Low", "Normal"
```

### FinancialStatements

Contains financial statements data.

```python
@dataclass
class FinancialStatements:
    yearly_income_statement: Optional[pd.DataFrame]
    quarterly_income_statement: Optional[pd.DataFrame]
    yearly_balance_sheet: Optional[pd.DataFrame]
    quarterly_balance_sheet: Optional[pd.DataFrame]
    yearly_cash_flow: Optional[pd.DataFrame]
    quarterly_cash_flow: Optional[pd.DataFrame]
```

### NewsItem

Represents a news article about the company.

```python
@dataclass
class NewsItem:
    title: str
    summary: Optional[str]
    url: Optional[str]
    published_date: Optional[datetime]
    source: Optional[str]
```

### StockData

The main data structure that combines all other models.

```python
@dataclass
class StockData:
    symbol: str
    company_info: CompanyInfo
    metrics: FinancialMetrics
    technical_analysis: TechnicalIndicators
    technical_signals: TechnicalSignals
    financials: FinancialStatements
    news: List[NewsItem]
    raw_data: Dict[str, Any]
```

## Usage

These models are used throughout the application to ensure data consistency:

1. Data providers normalize their raw data into these models
2. Services use these models for analysis and processing
3. Report generation uses these models to create standardized reports

## Example

```python
# Creating a StockData object
stock_data = StockData(
    symbol="AAPL",
    company_info=CompanyInfo(
        symbol="AAPL",
        name="Apple Inc.",
        sector="Technology"
    ),
    metrics=FinancialMetrics(
        revenue=394328000000,
        net_income=96995000000
    ),
    # ... other fields
)

# Converting to dictionary
data_dict = stock_data.to_dict()
```

## Best Practices

1. Always use these models when working with stock data
2. Use the `to_dict()` method when serializing data
3. Handle optional fields appropriately
4. Validate data before creating model instances
5. Use type hints when working with these models 