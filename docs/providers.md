# Data Providers

This document describes the data provider system used in the Stock Analysis Tool.

## Overview

The application uses a provider-based architecture to fetch stock data from multiple sources. This design allows for easy integration of new data providers while maintaining a consistent interface.

## Provider Interface

The `StockDataProvider` abstract base class defines the interface that all providers must implement:

```python
class StockDataProvider(ABC):
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        pass
    
    @abstractmethod
    def fetch_stock_data(self, symbol: str) -> StockData:
        """Fetch all stock data and return in standardized format."""
        pass
    
    @abstractmethod
    def fetch_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical price data."""
        pass
    
    @abstractmethod
    def fetch_financials(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial statements."""
        pass
    
    @abstractmethod
    def fetch_company_info(self, symbol: str) -> Dict[str, Any]:
        """Fetch company information."""
        pass
    
    @abstractmethod
    def fetch_news(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch company news."""
        pass
```

## Provider Factory

The `StockDataFactory` class manages the registration and instantiation of providers:

```python
class StockDataFactory:
    _providers = {}
    
    @classmethod
    def get_provider(cls, provider_name: str) -> StockDataProvider:
        """Get a provider instance by name."""
        pass
    
    @classmethod
    def get_default_provider(cls) -> StockDataProvider:
        """Get the default provider instance."""
        pass
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[StockDataProvider]):
        """Register a new provider."""
        pass
```

## Available Providers

### Yahoo Finance Provider

The `YahooFinanceProvider` implements the provider interface using the Yahoo Finance API:

```python
class YahooFinanceProvider(StockDataProvider):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._last_api_call = 0
        self._cooldown_period = 2
        self._max_retries = 3
        self._retry_delay = 5
```

Features:
- Rate limiting
- Retry logic
- Error handling
- Data normalization

### Alpha Vantage Provider

The `AlphaVantageProvider` implements the provider interface using the Alpha Vantage API:

```python
class AlphaVantageProvider(StockDataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
```

Features:
- API key authentication
- Data normalization
- Error handling

## Adding a New Provider

To add a new provider:

1. Create a new class that inherits from `StockDataProvider`
2. Implement all required methods
3. Register the provider with the factory

Example:
```python
class NewProvider(StockDataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_provider_name(self) -> str:
        return "new_provider"
    
    def fetch_stock_data(self, symbol: str) -> StockData:
        # Implementation
        pass
    
    # Implement other methods...

# Register the provider
StockDataFactory.register_provider('new_provider', NewProvider)
```

## Using Providers

```python
# Get a specific provider
provider = StockDataFactory.get_provider('yahoo')

# Get the default provider
provider = StockDataFactory.get_default_provider()

# Fetch stock data
stock_data = provider.fetch_stock_data('AAPL')
```

## Google Drive

The app can upload generated reports to Google Drive.

See: [Google Drive Setup](./GOOGLE_DRIVE_SETUP.md)

Supported auth modes:

- User OAuth (Desktop) – interactive sign-in on first run
- Service Account – headless, for servers/CI

Environment variables:

```
GOOGLE_DRIVE_USE_SERVICE_ACCOUNT=false  # or true
GOOGLE_DRIVE_CREDENTIALS_FILE=config/credentials/client_secret.json
GOOGLE_APPLICATION_CREDENTIALS=config/credentials/service_account.json
GOOGLE_DRIVE_FOLDER_ID=<folder_id>
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.file
```

## Best Practices

1. Always implement rate limiting
2. Handle API errors gracefully
3. Normalize data to the standard format
4. Use logging for debugging
5. Implement retry logic for failed requests
6. Cache responses when appropriate
7. Validate input parameters
8. Document API-specific requirements

## Error Handling

Providers should handle the following types of errors:

1. API rate limits
2. Network errors
3. Invalid symbols
4. Missing data
5. Authentication errors

Example error handling:
```python
try:
    data = self._fetch_with_retry(symbol)
except RateLimitError:
    self._handle_rate_limit()
except NetworkError:
    self._handle_network_error()
except InvalidSymbolError:
    raise ValueError(f"Invalid symbol: {symbol}")
```

## Rate Limiting

Each provider should implement rate limiting to avoid API restrictions:

```python
def _wait_for_rate_limit(self):
    current_time = time.time()
    time_since_last_request = current_time - self.last_request_time
    
    if time_since_last_request < self.rate_limit_delay:
        sleep_time = self.rate_limit_delay - time_since_last_request
        time.sleep(sleep_time)
    
    self.last_request_time = time.time()
```

## Data Normalization

Providers must normalize their data to match the standard models:

```python
def _normalize_company_info(self, raw_data: Dict[str, Any]) -> CompanyInfo:
    return CompanyInfo(
        symbol=raw_data.get('symbol', ''),
        name=raw_data.get('longName', ''),
        # ... other fields
    )
``` 