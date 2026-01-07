"""
NSE (National Stock Exchange) Data Provider

Provides data for Indian stocks listed on NSE using yfinance with .NS suffix.
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from services.data_providers.stock_data_provider import StockDataProvider
from services.data_providers.fetcher.base_fetcher import BaseFetcher
from exceptions.stock_data_exceptions import DataFetchException, InvalidSymbolException
from utils.debug_utils import DebugUtils
from config.constants.DataConstants import NSE_SUFFIX


class NSEProvider(StockDataProvider, BaseFetcher):
    """
    NSE data provider using yfinance.
    
    NSE symbols should be provided without .NS suffix (e.g., 'RELIANCE' not 'RELIANCE.NS').
    The provider will automatically append .NS for yfinance.
    """
    
    def __init__(self):
        """Initialize NSE provider."""
        BaseFetcher.__init__(self)
        DebugUtils.info("Initialized NSE Provider")
    
    def get_provider_name(self) -> str:
        """
        Get the provider name.
        
        Returns:
            Provider name string
        """
        return "nse"
    
    def _add_nse_suffix(self, symbol: str) -> str:
        """
        Add .NS suffix to symbol if not present.
        
        Args:
            symbol: Stock symbol (with or without .NS)
            
        Returns:
            Symbol with .NS suffix
        """
        if symbol.endswith(NSE_SUFFIX):
            return symbol
        return f"{symbol}{NSE_SUFFIX}"
    
    def fetch_historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical price data for NSE stock.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS')
            period: Period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with historical OHLCV data
            
        Raises:
            DataFetchException: If data fetch fails
        """
        try:
            # Add .NS suffix if needed
            yf_symbol = self._add_nse_suffix(symbol)
            
            DebugUtils.info(f"Fetching NSE historical data for {yf_symbol} (period={period}, interval={interval})")
            
            ticker = self.fetch_with_retry(yf_symbol, yf.Ticker, yf_symbol)
            hist = self.fetch_with_retry(yf_symbol, ticker.history, period=period, interval=interval)
            
            if hist.empty:
                DebugUtils.warning(f"No historical data returned for {yf_symbol}")
                return pd.DataFrame()
            
            DebugUtils.info(f"Fetched {len(hist)} rows of historical data for {yf_symbol}")
            return hist
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching NSE historical data for {symbol}")
            raise DataFetchException(f"Failed to fetch NSE historical data for {symbol}: {str(e)}") from e
    
    def fetch_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch company information for NSE stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company information
        """
        try:
            yf_symbol = self._add_nse_suffix(symbol)
            ticker = self.fetch_with_retry(yf_symbol, yf.Ticker, yf_symbol)
            info = self.fetch_with_retry(yf_symbol, lambda: ticker.info)
            
            return info if info else {}
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching NSE company info for {symbol}")
            return {}
    
    def fetch_current_price(self, symbol: str) -> Optional[float]:
        """
        Fetch current/live price for NSE stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price or None if unavailable
        """
        try:
            yf_symbol = self._add_nse_suffix(symbol)
            ticker = self.fetch_with_retry(yf_symbol, yf.Ticker, yf_symbol)
            info = self.fetch_with_retry(yf_symbol, lambda: ticker.info)
            
            # Try different price fields
            price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            
            if price:
                return float(price)
            return None
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching NSE current price for {symbol}")
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if symbol exists on NSE.
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            True if symbol is valid, False otherwise
        """
        try:
            yf_symbol = self._add_nse_suffix(symbol)
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            # Check if we got valid info
            if info and 'symbol' in info:
                return True
            return False
            
        except Exception:
            return False

