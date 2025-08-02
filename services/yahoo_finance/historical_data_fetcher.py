import yfinance as yf
import pandas as pd
from typing import Dict, Any
from utils.debug_utils import DebugUtils
from services.fetcher.base_fetcher import BaseFetcher

class HistoricalDataFetcher(BaseFetcher):
    """Class for fetching historical stock data."""
    
    def __init__(self):
        """Initialize the historical data fetcher."""
        BaseFetcher.__init__(self)  # Initialize BaseFetcher
        self._debug = DebugUtils()
    
    def fetch_historical_data(self, stock: yf.Ticker, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical price data.
        
        Args:
            stock: Yahoo Finance Ticker object
            symbol: Stock symbol for logging
            period: Time period (e.g., "1y", "6mo", "1d")
            interval: Data interval (e.g., "1d", "1h", "5m")
            
        Returns:
            DataFrame containing historical price data
        """
        try:
            DebugUtils.info(f"Fetching historical data for {symbol} (period={period}, interval={interval})")
            
            # Fetch historical data with retry logic
            hist_data = self.fetch_with_retry(symbol, stock.history, period=period, interval=interval)
            
            if hist_data.empty:
                DebugUtils.warning(f"No historical data found for {symbol}")
                return pd.DataFrame()
            
            return hist_data
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching historical data for {symbol}")
            return pd.DataFrame() 