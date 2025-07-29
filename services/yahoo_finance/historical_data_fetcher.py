from typing import Optional
import yfinance as yf
import pandas as pd
from utils.debug_utils import DebugUtils
from .base_fetcher import BaseFetcher

class HistoricalDataFetcher(BaseFetcher):
    """Class for fetching historical stock data."""
    
    def fetch_historical_data(self, stock: yf.Ticker, symbol : str) -> pd.DataFrame:
        """
        Fetch historical price data.
        
        Args:
            stock: Yahoo Finance Ticker object
            
        Returns:
            DataFrame containing historical price data
        """
        DebugUtils.info("\nFetching historical data...")
        try:
            # Try with a shorter period first
            hist_data = self.fetch_with_retry(
                symbol,
                stock.history,
                period="6mo",
                interval="1d"
            )
            
            if hist_data.empty:
                DebugUtils.warning("Historical data is empty, trying with a shorter period...")
                hist_data = self.fetch_with_retry(
                    symbol,
                    stock.history,
                    period="1mo",
                    interval="1d"
                )
            return hist_data
        except Exception as e:
            error_msg = f"Error fetching historical data: {str(e)}"
            DebugUtils.error(error_msg)
            return pd.DataFrame() 