import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
from utils.debug_utils import DebugUtils
from services.data_providers.fetcher.base_fetcher import BaseFetcher

class HistoricalDataFetcher(BaseFetcher):
    """Class for fetching historical stock data."""
    
    def __init__(self):
        """Initialize the historical data fetcher."""
        BaseFetcher.__init__(self)  # Initialize BaseFetcher
        self._debug = DebugUtils()
    
    def fetch_historical_data(self, stock: yf.Ticker, symbol: str, days_back: int = 365, interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical price data.
        
        Args:
            stock: Yahoo Finance Ticker object
            symbol: Stock symbol for logging
            days_back: Number of days of historical data to fetch
            interval: Data interval (e.g., "1d", "1h", "5m")
            
        Returns:
            DataFrame containing historical price data
        """
        try:
            # Convert days_back to Yahoo Finance period format
            period = self._convert_days_to_period(days_back)
            
            DebugUtils.info(f"Fetching historical data for {symbol} (days_back={days_back}, period={period}, interval={interval})")
            
            def fetch_data():
                return stock.history(period=period, interval=interval)
            
            # Use retry mechanism
            history_data = self.fetch_with_retry(
                symbol,
                fetch_data
            )
            
            if history_data is not None and not history_data.empty:
                DebugUtils.info(f"Successfully fetched {len(history_data)} rows of historical data for {symbol}")
                return history_data
            else:
                DebugUtils.warning(f"No historical data available for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching historical data for {symbol}")
            return pd.DataFrame()
    
    def _convert_days_to_period(self, days_back: int) -> str:
        """
        Convert days_back to Yahoo Finance period format.
        
        Args:
            days_back: Number of days
            
        Returns:
            Yahoo Finance period string
        """
        if days_back <= 5:
            return "5d"
        elif days_back <= 30:
            return "1mo"
        elif days_back <= 90:
            return "3mo"
        elif days_back <= 180:
            return "6mo"
        elif days_back <= 365:
            return "1y"
        elif days_back <= 730:
            return "2y"
        elif days_back <= 1825:
            return "5y"
        else:
            return "max" 