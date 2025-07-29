from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from services.stock_data_factory import StockDataFactory
from models.stock_data import StockData, CompanyInfo, FinancialMetrics, TechnicalIndicators, TechnicalSignals, FinancialStatements, NewsItem
from utils.debug_utils import DebugUtils
import random
import time
from services.yahoo_finance.yahoo_finance_service import YahooFinanceService

class StockService:
    """Service for fetching stock data from various providers."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StockService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the stock service."""
        # Only initialize once
        if StockService._initialized:
            return
            
        self._debug = DebugUtils()
        self._provider = StockDataFactory.get_provider('yahoo_finance')
        self._debug.log_info(f"Initialized StockService with provider: {self._provider.get_provider_name()}")
        StockService._initialized = True
    
    def _debug_print(self, *args, **kwargs):
        """Print debug messages only if debug mode is enabled."""
        self._debug.debug(*args, **kwargs)

    def fetch_stock_data(self, symbol: str) -> StockData:
        """Fetch stock data for a symbol.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            StockData object containing the fetched data
        """
        self._debug.info(f"Fetching stock data for {symbol}")
        return self._provider.fetch_stock_data(symbol)

    def fetch_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical price data.
        
        Args:
            symbol: Stock symbol to fetch data for
            period: Time period to fetch (default: "1y")
            interval: Data interval (default: "1d")
            
        Returns:
            DataFrame containing historical price data
        """
        self._debug.info(f"Fetching historical data for {symbol} (period={period}, interval={interval})")
        return self._provider.fetch_historical_data(symbol, period, interval)
    
    def fetch_financials(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial statements.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dictionary containing financial statements
        """
        self._debug.info(f"Fetching financials for {symbol}")
        return self._provider.fetch_financials(symbol)
    
    def fetch_company_info(self, symbol: str) -> CompanyInfo:
        """Fetch company information.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            CompanyInfo object containing company details
        """
        self._debug.info(f"Fetching company info for {symbol}")
        return self._provider.fetch_company_info(symbol)
    
    def fetch_news(self, symbol: str, limit: int = 5) -> List[NewsItem]:
        """Fetch company news.
        
        Args:
            symbol: Stock symbol to fetch data for
            limit: Maximum number of news items to fetch (default: 5)
            
        Returns:
            List of NewsItem objects
        """
        self._debug.info(f"Fetching news for {symbol} (limit={limit})")
        return self._provider.fetch_news(symbol, limit)
    
    def get_provider_name(self) -> str:
        """Get the name of the current data provider."""
        return self._provider.get_provider_name()

    def _fetch_with_retry(self,symbol, api_call, *args, **kwargs):
        """Execute an API call with retry logic.
        
        Args:
            api_call: The API function to call
            *args: Arguments for the API call
            **kwargs: Keyword arguments for the API call
            
        Returns:
            The result of the API call
            
        Raises:
            Exception: If max retries are reached or if the symbol is invalid
        """
        max_retries = 3  # Maximum number of retries
        base_delay = 2  # Base delay in seconds
        
        # Validate symbol if present in args
        if args and isinstance(args[0], str):
            if not symbol:
                raise ValueError("Invalid symbol: Empty string")
            # Update args with validated symbol
            args = (symbol,) + args[1:]
        
        for attempt in range(1, max_retries + 1):
            try:
                self._debug.log_api_call(
                    api_call.__name__,
                    symbol=symbol,
                    attempt=attempt,
                    total_attempts=max_retries
                )
                return api_call(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    self._debug.error(f"Max retries ({max_retries}) reached for {api_call.__name__}")
                    raise
                    
                if "Too Many Requests" in str(e):
                    wait_time = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                    self._debug.warning(f"Rate limit hit. Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                else:
                    self._debug.error(f"Error in {api_call.__name__}: {str(e)}")
                    # Don't retry for invalid symbols or other non-retryable errors
                    if "Invalid symbol" in str(e) or "Unknown symbol" in str(e):
                        raise
                    wait_time = base_delay * (2 ** (attempt - 1))
                    self._debug.warning(f"Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
        
        raise Exception(f"Max retries ({max_retries}) reached for {api_call.__name__}") 