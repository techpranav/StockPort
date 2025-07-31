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

class YahooFinanceProvider(StockDataProvider, BaseFetcher):
    """Yahoo Finance data provider implementation."""
    
    def __init__(self):
        """Initialize the Yahoo Finance provider."""
        BaseFetcher.__init__(self)  # Initialize BaseFetcher
        self._debug = DebugUtils()
        self._debug_mode = False  # Set to False to disable debug prints
    
    def get_provider_name(self) -> str:
        """Get the name of the data provider."""
        return "Yahoo Finance"
    
    def fetch_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical price data."""
        try:
            stock = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            return self.fetch_with_retry(symbol, stock.history, period=period, interval=interval)
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching historical data for {symbol}")
            return pd.DataFrame()
    
    def fetch_financials(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial statements."""
        try:
            stock = self.fetch_with_retry(symbol, yf.Ticker, symbol)

            lambda_stock_financials = lambda: stock.financials
            lambda_stock_financials.__name__ = "stock.financials"
            lambda_stock_balancesheet = lambda: stock.balance_sheet
            lambda_stock_balancesheet.__name__ = "stock.balance_sheet"
            lambda_cashflow = lambda: stock.cashflow
            lambda_cashflow.__name__ = "stock.cashflow"
            lambda_quarterly_financials = lambda: stock.quarterly_financials
            lambda_quarterly_financials.__name__ = "stock.quarterly_financials"
            lambda_quarterly_balance_sheet = lambda: stock.quarterly_balance_sheet
            lambda_quarterly_balance_sheet.__name__ = "stock.quarterly_balance_sheet"
            lambda_quarterly_cashflow = lambda: stock.quarterly_cashflow
            lambda_quarterly_cashflow.__name__ = "stock.quarterly_cashflow"

            return {
                'yearly': {
                    'income_statement': self.fetch_with_retry(symbol, lambda_stock_financials),
                    'balance_sheet': self.fetch_with_retry(symbol, lambda_stock_balancesheet),
                    'cashflow': self.fetch_with_retry(symbol, lambda_cashflow)
                },
                'quarterly': {
                    'income_statement': self.fetch_with_retry(symbol, lambda_quarterly_financials),
                    'balance_sheet': self.fetch_with_retry(symbol, lambda_quarterly_balance_sheet),
                    'cashflow': self.fetch_with_retry(symbol, lambda_quarterly_cashflow)
                }
            }
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching financials for {symbol}")
            return {}
    
    def fetch_company_info(self, symbol: str) -> Dict[str, Any]:
        """Fetch company information."""
        try:
            stock = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            info_lambda = lambda: stock.info
            info_lambda.__name__ = "stock.info"
            return self.fetch_with_retry(symbol, info_lambda)
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching company info for {symbol}")
            return {}
    
    def fetch_news(self, symbol: str, limit: int = 5) -> list:
        """Fetch company news."""
        try:
            stock = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            news_lambda = lambda: stock.get_news()
            news_lambda.__name__ = "stock.news"
            news_data = self.fetch_with_retry(symbol, news_lambda)
            return news_data[:limit] if news_data else []
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching news for {symbol}")
            return []
    
    def fetch_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch comprehensive stock data."""
        try:
            # Validate symbol
            if not symbol or not symbol.strip():
                raise InvalidSymbolException("Symbol cannot be empty")
            
            symbol = symbol.strip().upper()
            DebugUtils.info(f"Fetching stock data for {symbol}")
            
            # Create ticker object
            stock = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            
            data = {}
            
            # Fetch historical data
            data['history'] = self.fetch_historical_data(symbol)
            
            # Fetch financial data
            data['financials'] = self.fetch_financials(symbol)
            
            # Fetch company info
            data['info'] = self.fetch_company_info(symbol)
            
            # Fetch news
            data['news'] = self.fetch_news(symbol)
            
            return data
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching stock data for {symbol}")
            raise DataFetchException(f"Failed to fetch stock data for {symbol}: {str(e)}") 