import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import traceback
import random
import time

from models.stock_data import (
    StockData, CompanyInfo, FinancialMetrics, TechnicalIndicators,
    TechnicalSignals, FinancialStatements, NewsItem
)
from services.stock_data_provider import StockDataProvider
from exceptions.stock_data_exceptions import (
    DataFetchException, InvalidSymbolException, RateLimitException
)
from config.settings import Settings
from utils.debug_utils import DebugUtils
from services.fetcher.base_fetcher import BaseFetcher
from .historical_data_fetcher import HistoricalDataFetcher
from .financial_data_fetcher import FinancialDataFetcher
from .company_info_fetcher import CompanyInfoFetcher
from .news_fetcher import NewsFetcher

class YahooFinanceService(StockDataProvider, BaseFetcher):
    """Yahoo Finance data provider implementation."""
    
    def __init__(self, skip_history: bool = True):  # Default to True to skip history for now
        """Initialize the Yahoo Finance service."""
        BaseFetcher.__init__(self)  # Initialize BaseFetcher
        self.skip_history = skip_history
        self._debug = DebugUtils()
        self._debug_mode = False  # Set to False to disable debug prints
        
        # Initialize specialized fetchers
        self._historical_fetcher = HistoricalDataFetcher()
        self._financial_fetcher = FinancialDataFetcher()
        self._company_info_fetcher = CompanyInfoFetcher()
        self._news_fetcher = NewsFetcher()
    
    def _debug_print(self, *args, **kwargs):
        """Debug print method that respects debug mode."""
        if self._debug_mode:
            print(*args, **kwargs)
    
    def get_provider_name(self) -> str:
        """Get the name of the data provider."""
        return "Yahoo Finance"
    
    def fetch_stock_data(self, symbol: str, export_financials: bool = False, export_filtered_financials: bool = False) -> Dict[str, Any]:
        """Fetch stock data for a given symbol.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            Dictionary containing stock data
            
        Raises:
            DataFetchError: If there's an error fetching the data
        """
        try:
            # Validate symbol
            if not symbol or not symbol.strip():
                raise InvalidSymbolException("Symbol cannot be empty")
            
            symbol = symbol.strip().upper()
            self._debug.info(f"Fetching stock data for {symbol}")
            
            # Create ticker object
            ticker = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            
            data = {}
            
            # Fetch historical data (skip if flag is set)
            if not self.skip_history:
                data['history'] = self._historical_fetcher.fetch_historical_data(ticker, symbol)
            else:
                data['history'] = pd.DataFrame()
                self._debug.info("Skipping historical data fetch (skip_history=True)")
            
            # Fetch financial data
            data['financials'] = self._financial_fetcher.fetch_financial_data(ticker, symbol)
            
            # Fetch company info
            data['info'] = self._company_info_fetcher.fetch_company_info(ticker, symbol)
            
            # Fetch news
            data['news'] = self._news_fetcher.fetch_news(ticker, symbol)
            
            return data
            
        except Exception as e:
            self._debug.log_error(e, f"Error fetching stock data for {symbol}")
            raise DataFetchException(f"Failed to fetch stock data for {symbol}: {str(e)}")
    
    def fetch_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical price data."""
        try:
            ticker = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            return self._historical_fetcher.fetch_historical_data(ticker, symbol, period, interval)
        except Exception as e:
            self._debug.log_error(e, f"Error fetching historical data for {symbol}")
            return pd.DataFrame()
    
    def fetch_financials(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial statements."""
        try:
            ticker = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            return self._financial_fetcher.fetch_financial_data(ticker, symbol)
        except Exception as e:
            self._debug.log_error(e, f"Error fetching financials for {symbol}")
            return {}
    
    def fetch_company_info(self, symbol: str) -> CompanyInfo:
        """Fetch company information."""
        try:
            ticker = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            info_dict = self._company_info_fetcher.fetch_company_info(ticker, symbol)
            return CompanyInfo(**info_dict)
        except Exception as e:
            self._debug.log_error(e, f"Error fetching company info for {symbol}")
            return CompanyInfo()
    
    def fetch_news(self, symbol: str, limit: int = 5) -> List[NewsItem]:
        """Fetch company news."""
        try:
            ticker = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            news_data = self._news_fetcher.fetch_news(ticker, symbol, limit)
            return [NewsItem(**item) for item in news_data]
        except Exception as e:
            self._debug.log_error(e, f"Error fetching news for {symbol}")
            return []
    
    def filter_stock_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and clean stock data."""
        try:
            filtered_data = {}
            
            # Filter company info
            if 'info' in data and data['info']:
                filtered_data['info'] = self._filter_dict_by_keys(data['info'])
            
            # Filter financial statements
            if 'financials' in data and data['financials']:
                filtered_data['financials'] = self._filter_financial_statements(data['financials'])
            
            # Keep other data as is
            for key in ['history', 'news']:
                if key in data:
                    filtered_data[key] = data[key]
            
            return filtered_data
            
        except Exception as e:
            self._debug.log_error(e, "Error filtering stock data")
            return data
    
    def _filter_financial_statements(self, data: Dict[str, pd.DataFrame], statement_type: str = 'financials') -> Dict[
        str, pd.DataFrame]:
        """Filter financial statements to keep only essential columns."""
        try:
            filtered_data = {}
            for period, statements in data.items():
                filtered_data[period] = {}
                for statement_name, df in statements.items():
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        filtered_data[period][statement_name] = self._filter_dataframe(df)
                    else:
                        filtered_data[period][statement_name] = df
            return filtered_data
        except Exception as e:
            self._debug.log_error(e, f"Error filtering {statement_type}")
            return data
    
    def _filter_dict_by_keys(self, data: Dict[str, Any], keys: List[str] = None) -> Dict[str, Any]:
        """Filter dictionary to keep only specified keys."""
        if keys is None:
            # Keep essential company info keys
            keys = ['symbol', 'longName', 'shortName', 'sector', 'industry', 'marketCap', 'enterpriseValue']
        return {k: v for k, v in data.items() if k in keys}
    
    def _filter_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter DataFrame to keep only essential columns."""
        try:
            if df.empty:
                return df
            
            # Keep only numeric columns and essential text columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            text_cols = ['Date', 'date', 'index'] if any(col in df.columns for col in ['Date', 'date', 'index']) else []
            
            essential_cols = numeric_cols + text_cols
            if essential_cols:
                return df[essential_cols]
            return df
            
        except Exception as e:
            self._debug.log_error(e, "Error filtering DataFrame")
            return df
    
    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional metrics from the data."""
        try:
            metrics = {}
            
            # Calculate basic metrics from historical data
            if 'history' in data and isinstance(data['history'], pd.DataFrame) and not data['history'].empty:
                hist_data = data['history']
                if 'Close' in hist_data.columns:
                    metrics['current_price'] = hist_data['Close'].iloc[-1]
                    metrics['price_change'] = hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]
                    metrics['price_change_pct'] = (metrics['price_change'] / hist_data['Close'].iloc[0]) * 100
            
            # Add company info metrics
            if 'info' in data and data['info']:
                info = data['info']
                metrics.update({
                    'market_cap': info.get('marketCap', 0),
                    'enterprise_value': info.get('enterpriseValue', 0),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown')
                })
            
            return metrics
            
        except Exception as e:
            self._debug.log_error(e, "Error calculating metrics")
            return {}
