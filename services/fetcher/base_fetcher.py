import random
import time
import traceback
from typing import TypeVar, Callable, Any, Optional
import pandas as pd
import yfinance as yf
from config.settings import Settings
from exceptions.stock_data_exceptions import (
    RateLimitException, InvalidSymbolException, DataFetchException
)
from utils.debug_utils import DebugUtils

T = TypeVar('T')

class BaseFetcher:
    """Base class for fetching data with retry logic and rate limiting."""
    
    def __init__(self):
        """Initialize the base fetcher."""
        self.rate_limit_delay = Settings.API_RATE_LIMIT_DELAY
        self.max_retries = Settings.API_MAX_RETRIES
        self.last_request_time = 0
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.api_call_count = 0
        self._min_request_interval = 1.0
        self._debug = DebugUtils()
    
    def fetch_with_retry(self, symbol: str, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a function with retry logic and exponential backoff.
        
        Args:
            symbol: Stock symbol for logging
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            RateLimitException: When rate limit is exceeded
            InvalidSymbolException: When symbol is invalid
            DataFetchException: When data fetch fails
        """
        last_error: Optional[Exception] = None
        api_name: str = func.__name__ if hasattr(func, '__name__') else str(func)
        
        # Validate symbol
        if not symbol or symbol.strip() == '':
            raise InvalidSymbolException("Invalid symbol: Empty string")
        
        for attempt in range(self.max_retries):
            try:
                self._log_api_call(api_name, symbol)
                self._wait_for_rate_limit()
                
                # Add jitter to avoid thundering herd
                jitter: float = random.uniform(0, 1)
                time.sleep(jitter)
                
                # Handle DataFrame objects specially
                if isinstance(func, pd.DataFrame):
                    return func
                
                result: T = func(*args, **kwargs)
                self.consecutive_failures = 0  # Reset consecutive failures on success
                
                # Validate result for ticker initialization
                if func == yf.Ticker:
                    if result is None or not hasattr(result, 'info'):
                        raise InvalidSymbolException(f"Invalid or unknown symbol: {symbol}")
                    # Check if we can get basic info
                    try:
                        result.info.get('symbol', '')
                    except Exception:
                        raise InvalidSymbolException(f"Invalid or unknown symbol: {symbol}")
                
                return result
                
            except InvalidSymbolException as e:
                # Don't retry for invalid symbols
                self._debug.log_error(e)
                raise
            except Exception as e:
                last_error = e
                error_msg: str = str(e)
                
                if "Too Many Requests" in error_msg:
                    self.consecutive_failures += 1
                    if attempt < self.max_retries - 1:
                        wait_time: float = min(
                            self.rate_limit_delay * (2 ** attempt) + random.uniform(0, 1),
                            Settings.API_RATE_LIMIT_COOLDOWN
                        )
                        self._debug.log_warning(f"Rate limit hit for {symbol}. Retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                        continue
                        
                elif "symbol may be delisted" in error_msg.lower():
                    raise InvalidSymbolException(f"Symbol may be delisted: {symbol}")
                    
                elif "Invalid symbol" in error_msg:
                    raise InvalidSymbolException(f"Invalid symbol: {symbol}")
                    
                elif attempt < self.max_retries - 1:
                    wait_time = self.rate_limit_delay * (2 ** attempt) + random.uniform(0, 1)
                    self._debug.log_warning(f"Error occurred for {symbol}. Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    continue
                
                self._debug.log_error(f"Max retries ({self.max_retries}) reached for {api_name}")
                raise DataFetchException(f"Error fetching data: {str(e)}")
        
        if last_error:
            raise last_error
    
    def _log_api_call(self, api_name: str, symbol: str) -> None:
        """
        Log API call details.
        
        Args:
            api_name: Name of the API being called
            symbol: Stock symbol
        """
        self.api_call_count += 1
        self._debug.log_api_call(api_name, symbol, self.api_call_count, self.max_retries)
        self._debug.debug(f"Consecutive Failures: {self.consecutive_failures}")
    
    def _wait_for_rate_limit(self) -> None:
        """Wait to respect rate limits."""
        current_time: float = time.time()
        time_since_last_request: float = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            sleep_time: float = self.rate_limit_delay - time_since_last_request
            self._debug.debug(f"Rate limit: Waiting {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time() 