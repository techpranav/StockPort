# Troubleshooting Guide

This document provides solutions for common issues encountered while using the Stock Analysis Tool.

## Common Issues

### 1. Rate Limit Errors

#### Symptoms
- Error messages about rate limits
- Failed API calls
- Timeout errors

#### Solutions
1. Increase cooldown period:
```python
provider = YahooFinanceProvider()
provider._cooldown_period = 5  # Increase from default 2 seconds
```

2. Implement exponential backoff:
```python
def fetch_with_retry(self, symbol: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return self._fetch_data(symbol)
        except RateLimitError:
            wait_time = (2 ** attempt) * self._cooldown_period
            time.sleep(wait_time)
    raise RateLimitError("Max retries exceeded")
```

3. Use multiple providers:
```python
service = StockService(provider_name='alpha_vantage')  # Switch to different provider
```

### 2. Data Fetching Issues

#### Symptoms
- Missing data
- Incomplete reports
- Invalid symbols

#### Solutions
1. Verify symbol format:
```python
def validate_symbol(symbol: str) -> bool:
    return bool(re.match(r'^[A-Z]{1,5}$', symbol))
```

2. Check data availability:
```python
def check_data_availability(symbol: str) -> bool:
    try:
        data = service.fetch_stock_data(symbol)
        return bool(data.company_info and data.technical_analysis)
    except Exception:
        return False
```

3. Handle missing data:
```python
def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    return data.get(key, default)
```

### 3. Report Generation Issues

#### Symptoms
- Failed report generation
- Corrupted Excel files
- Missing sheets

#### Solutions
1. Check file permissions:
```python
def ensure_directory_writable(path: Path):
    if not path.exists():
        path.mkdir(parents=True)
    if not os.access(path, os.W_OK):
        raise PermissionError(f"Cannot write to {path}")
```

2. Handle large datasets:
```python
def chunk_dataframe(df: pd.DataFrame, chunk_size: int = 1000):
    return [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
```

3. Validate report data:
```python
def validate_report_data(data: Dict[str, Any]) -> bool:
    required_keys = ['company_info', 'technical_analysis', 'financials']
    return all(key in data for key in required_keys)
```

### 4. Performance Issues

#### Symptoms
- Slow data fetching
- High memory usage
- Long report generation times

#### Solutions
1. Implement caching:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def fetch_cached_data(symbol: str) -> Dict[str, Any]:
    return service.fetch_stock_data(symbol)
```

2. Optimize memory usage:
```python
def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].astype('float32')
    return df
```

3. Use batch processing:
```python
def process_symbols_batch(symbols: List[str], batch_size: int = 10):
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        process_batch(batch)
```

### 5. API Connection Issues

#### Symptoms
- Connection timeouts
- Network errors
- SSL certificate issues

#### Solutions
1. Implement retry logic:
```python
def fetch_with_retry(func, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return func()
        except (ConnectionError, TimeoutError):
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

2. Handle SSL issues:
```python
import ssl
import certifi

def create_ssl_context():
    return ssl.create_default_context(cafile=certifi.where())
```

3. Set timeouts:
```python
def fetch_with_timeout(url: str, timeout: int = 30):
    return requests.get(url, timeout=timeout)
```

### 6. Data Validation Issues

#### Symptoms
- Invalid data types
- Missing required fields
- Inconsistent data formats

#### Solutions
1. Implement data validation:
```python
def validate_stock_data(data: StockData) -> bool:
    if not data.symbol or not data.company_info:
        return False
    if not isinstance(data.technical_analysis, TechnicalIndicators):
        return False
    return True
```

2. Handle data conversion:
```python
def safe_convert(value: Any, target_type: Type) -> Any:
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return None
```

3. Normalize data formats:
```python
def normalize_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None
```

## Debugging Tips

1. Enable detailed logging:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

2. Use debug mode:
```python
def debug_mode(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"Result: {result}")
        return result
    return wrapper
```

3. Monitor performance:
```python
import time

def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper
```

## Common Error Messages

1. Rate Limit Error:
```
RateLimitError: Too many requests. Please try again later.
```
Solution: Increase cooldown period or implement exponential backoff.

2. Invalid Symbol Error:
```
ValueError: Invalid symbol format
```
Solution: Verify symbol format and existence.

3. Data Fetching Error:
```
ConnectionError: Failed to fetch data from provider
```
Solution: Check network connection and implement retry logic.

4. Report Generation Error:
```
PermissionError: Cannot write to reports directory
```
Solution: Check file permissions and disk space.

5. Memory Error:
```
MemoryError: Not enough memory to process data
```
Solution: Implement data chunking and memory optimization.

## Getting Help

If you encounter issues not covered in this guide:

1. Check the logs for detailed error messages
2. Review the API documentation
3. Search for similar issues in the issue tracker
4. Contact support with:
   - Error message
   - Steps to reproduce
   - System information
   - Log files 