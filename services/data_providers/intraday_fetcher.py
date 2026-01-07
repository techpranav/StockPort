"""
Intraday Data Fetcher Module

This module provides intraday data fetching capabilities with support for
multiple timeframes (1m, 5m, 15m, 30m, 1h) and market hours awareness.
"""

from typing import Dict, Optional, List
import pandas as pd
from datetime import datetime, time

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataFetchException
from services.data_providers.stock_data_provider import StockDataProvider
from config.constants.IntradayConstants import (
    INTRADAY_TIMEFRAMES,
    MARKET_OPEN_HOUR,
    MARKET_OPEN_MINUTE,
    MARKET_CLOSE_HOUR,
    MARKET_CLOSE_MINUTE
)


class IntradayFetcher:
    """
    Fetcher for intraday stock data.
    
    Features:
    - Support for 1m, 5m, 15m, 30m, 1h intervals
    - Market hours detection
    - Pre-market and after-hours handling
    """
    
    def __init__(self, provider: StockDataProvider):
        """
        Initialize intraday fetcher.
        
        Args:
            provider: Stock data provider instance
        """
        self.provider = provider
    
    def fetch_intraday_data(
        self,
        symbol: str,
        interval: str = "5m",
        period: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch intraday data for a symbol.
        
        Args:
            symbol: Stock symbol
            interval: Data interval (1m, 5m, 15m, 30m, 1h)
            period: Period to fetch (1d, 5d, 1mo, etc.)
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            DataFetchException: If fetch fails
        """
        try:
            if interval not in INTRADAY_TIMEFRAMES:
                raise DataFetchException(
                    f"Unsupported interval: {interval}. Supported: {INTRADAY_TIMEFRAMES}"
                )
            
            # Use provider's fetch_historical_data with interval
            data = self.provider.fetch_historical_data(
                symbol=symbol,
                period=period,
                interval=interval
            )
            
            if data.empty:
                raise DataFetchException(f"No intraday data available for {symbol}")
            
            DebugUtils.info(f"Fetched {len(data)} intraday data points for {symbol} ({interval})")
            return data
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching intraday data for {symbol}")
            raise DataFetchException(f"Intraday fetch failed: {str(e)}") from e
    
    def fetch_multiple_timeframes(
        self,
        symbol: str,
        timeframes: Optional[List[str]] = None,
        period: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple timeframes.
        
        Args:
            symbol: Stock symbol
            timeframes: List of timeframes to fetch (default: all intraday)
            period: Period to fetch
            
        Returns:
            Dictionary mapping timeframe to DataFrame
        """
        if timeframes is None:
            timeframes = INTRADAY_TIMEFRAMES
        
        results = {}
        
        for timeframe in timeframes:
            try:
                data = self.fetch_intraday_data(symbol, timeframe, period)
                results[timeframe] = data
            except Exception as e:
                DebugUtils.warning(f"Failed to fetch {timeframe} data for {symbol}: {str(e)}")
                results[timeframe] = pd.DataFrame()
        
        return results
    
    def is_market_open(self, check_time: Optional[datetime] = None) -> bool:
        """
        Check if market is currently open.
        
        Args:
            check_time: Time to check (default: now)
            
        Returns:
            True if market is open
        """
        if check_time is None:
            check_time = datetime.now()
        
        market_open = time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE)
        market_close = time(MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE)
        current_time = check_time.time()
        
        # Check if weekday (Monday=0, Sunday=6)
        is_weekday = check_time.weekday() < 5
        
        return is_weekday and market_open <= current_time <= market_close

