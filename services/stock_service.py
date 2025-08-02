from typing import Dict, Any, List, Optional
import pandas as pd

from models.stock_data import StockData, CompanyInfo, NewsItem
from services.stock_data_provider import StockDataProvider
from services.stock_data_factory import StockDataFactory
from services.yahoo_finance.yahoo_finance_service import YahooFinanceService
from exceptions.stock_data_exceptions import DataFetchException
from utils.debug_utils import DebugUtils
from services.fetcher.base_fetcher import BaseFetcher

class StockService(BaseFetcher):
    """Service for fetching stock data from various providers."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StockService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the stock service."""
        if not self._initialized:
            BaseFetcher.__init__(self)  # Initialize BaseFetcher
            self._provider = StockDataFactory.get_default_provider()
            self._debug = DebugUtils()
            self._initialized = True
    
    def _debug_print(self, *args, **kwargs):
        """Debug print method."""
        self._debug.debug(*args, **kwargs)
    
    def fetch_stock_data(self, symbol: str) -> StockData:
        """Fetch comprehensive stock data.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            StockData object containing all stock information
        """
        self._debug.info(f"Fetching comprehensive stock data for {symbol}")
        stock_data = self._provider.fetch_stock_data(symbol)
        return stock_data
    
    def fetch_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical price data.
        
        Args:
            symbol: Stock symbol to fetch data for
            period: Time period (e.g., "1y", "6mo", "1d")
            interval: Data interval (e.g., "1d", "1h", "5m")
            
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