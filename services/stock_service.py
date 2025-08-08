from typing import Dict, Any, Optional
import pandas as pd

from models.stock_data import StockData, CompanyInfo, NewsItem
from services.data_providers.stock_data_provider import StockDataProvider
from services.stock_data_factory import StockDataFactory
from services.data_providers.yahoo_finance.yahoo_finance_service import YahooFinanceService
from exceptions.stock_data_exceptions import DataFetchException
from utils.debug_utils import DebugUtils
from services.data_providers.fetcher.base_fetcher import BaseFetcher

class StockService:
    """
    High-level service for stock data operations.
    
    This service acts as a facade that coordinates between different
    data providers and provides a unified interface for stock data operations.
    """
    
    def __init__(self, provider_name: str = "yahoo_finance", days_back: int = 365, **provider_kwargs):
        """
        Initialize the stock service.
        
        Args:
            provider_name: Name of the data provider to use
            days_back: Number of days of historical data to fetch
            **provider_kwargs: Additional arguments for the provider
        """
        self.days_back = days_back
        
        # Add days_back to provider kwargs
        provider_kwargs['days_back'] = days_back
        
        # Get the provider from factory
        self._provider = StockDataFactory.get_provider(provider_name, **provider_kwargs)
        
        DebugUtils.info(f"Initialized StockService with provider: {provider_name}, days_back: {days_back}")
    
    def fetch_stock_data(self, symbol: str) -> StockData:
        """
        Fetch comprehensive stock data for a symbol.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            StockData object containing all stock information
            
        Raises:
            Exception: If data fetching fails
        """
        try:
            DebugUtils.info(f"Fetching stock data for {symbol} with {self.days_back} days of history")
            
            # Use the provider to fetch data
            stock_data = self._provider.fetch_stock_data(symbol)
            
            DebugUtils.info(f"Successfully fetched stock data for {symbol}")
            return stock_data
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching stock data for {symbol}")
            raise
    
    def get_provider_name(self) -> str:
        """Get the name of the current data provider."""
        return self._provider.get_provider_name()
    
    def set_days_back(self, days_back: int):
        """
        Update the days_back setting.
        
        Args:
            days_back: Number of days of historical data to fetch
        """
        self.days_back = days_back
        
        # Update provider if it supports days_back
        if hasattr(self._provider, 'days_back'):
            self._provider.days_back = days_back
            DebugUtils.info(f"Updated days_back to {days_back}")
    
    def get_days_back(self) -> int:
        """Get the current days_back setting."""
        return self.days_back