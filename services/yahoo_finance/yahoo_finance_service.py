import traceback
from typing import Dict, Any, List, Optional, Union, Callable, TypeVar, Tuple
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
from models.stock_data import StockData, CompanyInfo, FinancialMetrics, TechnicalIndicators, TechnicalSignals, FinancialStatements, NewsItem
from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import RateLimitException, InvalidSymbolException, DataFetchException
from services.analysis.financial_analysis import FinancialAnalyzer
from services.analysis.technical_analysis import TechnicalAnalyzer
from services.yahoo_finance.data_exporter import DataExporter
from config.settings import Settings
from core.config import INCOME_STATEMENT_KEYS, BALANCE_SHEET_KEYS, CASHFLOW_KEYS
from .historical_data_fetcher import HistoricalDataFetcher
from .financial_data_fetcher import FinancialDataFetcher
from .company_info_fetcher import CompanyInfoFetcher
from .news_fetcher import NewsFetcher
import random

# Type aliases for commonly used types
T = TypeVar('T')
YahooTicker = yf.Ticker
FinancialData = Dict[str, Dict[str, pd.DataFrame]]
StockDataDict = Dict[str, Any]
NewsData = List[Dict[str, Any]]

class YahooFinanceService:
    """Service for fetching stock data from Yahoo Finance."""
    
    def __init__(self, skip_history: bool = True):  # Default to True to skip history for now
        """Initialize the service.
        
        Args:
            skip_history: If True, skip fetching historical data
        """
        self._skip_history = skip_history
        self._debug = DebugUtils()
        self._historical_fetcher = HistoricalDataFetcher()
        self._financial_fetcher = FinancialDataFetcher()
        self._company_info_fetcher = CompanyInfoFetcher()
        self._news_fetcher = NewsFetcher()
        self._last_request_time = 0
        self._request_count = 0
        self._max_requests_per_minute = 30  # Yahoo Finance rate limit
        self.debug_mode = False
        self.api_call_count = 0
        self.consecutive_failures = 0
        self.rate_limit_delay = 1  # Assuming a default rate_limit_delay
        self.rate_limit_cooldown = 10  # Assuming a default rate_limit_cooldown

        self.income_statement_keys = INCOME_STATEMENT_KEYS
        self.balance_sheet_keys = BALANCE_SHEET_KEYS
        self.cash_flow_keys = CASHFLOW_KEYS
    def _debug_print(self, *args, **kwargs):
        """Print debug messages only if debug mode is enabled."""
        if self.debug_mode:
            DebugUtils.debug(*args, **kwargs)

    def _log_api_call(self, api_name: str, symbol: str):
        """Log API call details."""
        self.api_call_count += 1
        if self.debug_mode:
            DebugUtils.log_api_call(api_name, symbol, self.api_call_count, self.max_retries)
            self._debug_print(f"Consecutive Failures: {self.consecutive_failures}")

    def _wait_for_rate_limit(self):
        """Wait to respect rate limits."""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            if self.debug_mode:
                self._debug_print(f"Rate limit: Waiting {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()

    def _fetch_with_retry(self,symbol,func: Callable, *args, max_retries: int = Settings.API_MAX_RETRIES, **kwargs) -> Any:
        """Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Arguments for the function
            max_retries: Maximum number of retry attempts
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the function call

        Raises:
            DataFetchException: If all retries fail
            InvalidSymbolException: If the symbol is invalid
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                if args and isinstance(args[0], str):

                    self._log_api_call(func.__name__, args[0] if args else "Unknown")
                    self._wait_for_rate_limit()

                    # Add jitter to avoid thundering herd
                    jitter = random.uniform(0, 1)
                    time.sleep(jitter)

                    # Validate symbol if present in args
                    if not symbol:
                        raise ValueError("Invalid symbol: Empty string")
                    # Update args with validated symbol
                    args = (symbol,) + args[1:]

                # Handle DataFrame objects specially
                if isinstance(func, pd.DataFrame):
                    return func

                result = func(*args, **kwargs)
                self.consecutive_failures = 0  # Reset consecutive failures on success

                # Validate result for ticker initialization
                if func == yf.Ticker:
                    if result is None or not hasattr(result, 'info'):
                        raise InvalidSymbolException(f"Invalid or unknown symbol: {args[0]}")
                    # Check if we can get basic info
                    try:
                        result.info.get('symbol', '')
                    except Exception:
                        raise InvalidSymbolException(f"Invalid or unknown symbol: {args[0]}")

                return result
            except InvalidSymbolException as e:
                # Don't retry for invalid symbols
                self._debug.log_error(e)
                print(traceback.format_exc())
                raise
            except Exception as e:
                # Don't retry for invalid symbols or other non-retryable errors
                if "Invalid symbol" in str(e) or "Unknown symbol" in str(e):
                    raise
                last_error = e
                if isinstance(e, RateLimitException):
                    wait_time = Settings.API_RATE_LIMIT_COOLDOWN
                    self._debug.log_warning(f"Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    wait_time = Settings.API_REQUEST_DELAY * (attempt + 1)
                    self._debug.log_warning(f"Attempt {attempt + 1} failed. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                print(traceback.format_exc())

            if attempt == max_retries:
                self._debug.error(f"Max retries ({max_retries}) reached for {func.__name__}")
                raise

        raise DataFetchException(f"Failed after {max_retries} attempts: {str(last_error)}")

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
            # Validate symbol format
            if not symbol or not isinstance(symbol, str):
                raise InvalidSymbolException("Invalid symbol format")
            
            symbol = symbol.strip().upper()
            if not symbol:
                raise InvalidSymbolException("Empty symbol")
            
            self._debug.log_api_call("YahooFinance", symbol)
            
            # Initialize data dictionary
            data = {
                'symbol': symbol,
                'provider': self.get_provider_name(),
                'timestamp': datetime.now().isoformat(),
                'history': pd.DataFrame(),
                'financials': {
                    'yearly': {
                        'income_statement': pd.DataFrame(),
                        'balance_sheet': pd.DataFrame(),
                        'cashflow': pd.DataFrame()
                    },
                    'quarterly': {
                        'income_statement': pd.DataFrame(),
                        'balance_sheet': pd.DataFrame(),
                        'cashflow': pd.DataFrame()
                    }
                },
                'info': {},
                'news': [],
                'errors': []
            }
            
            # Initialize ticker with retry
            try:
                ticker = self._fetch_with_retry(symbol,yf.Ticker,symbol)
            except InvalidSymbolException as e:
                data['errors'].append(str(e))
                return data
            except Exception as e:
                self._debug.log_error(e, f"Error initializing ticker for {symbol}")
                data['errors'].append(f"Error initializing ticker for {symbol}: {str(e)}")
                return data
            
            # Fetch data with retry logic
            if not self._skip_history:
                try:
                    data['history'] = self._fetch_with_retry(
                        symbol,
                        self._historical_fetcher.fetch_historical_data,
                        ticker,
                        symbol
                    )
                except Exception as e:
                    self._debug.log_error(e, f"Error fetching historical data for {symbol}")
                    data['errors'].append(f"Error fetching historical data for {symbol}: {str(e)}")
            
            try:
                data['financials'] = self._fetch_with_retry(
                    symbol,
                    self._financial_fetcher.fetch_financial_data,
                    ticker,
                    symbol
                )
            except Exception as e:
                print(traceback.format_exc())

                self._debug.log_error(e, f"Error fetching financial data for {symbol}")
                data['errors'].append(f"Error fetching financial data for {symbol}: {str(e)}")
            
            try:
                data['info'] = self._fetch_with_retry(
                    symbol,
                    self._company_info_fetcher.fetch_company_info,
                    ticker,
                    symbol
                )
            except Exception as e:
                self._debug.log_error(e, f"Error fetching company info for {symbol}")
                data['errors'].append(f"Error fetching company info for {symbol}: {str(e)}")
            
            try:
                data['news'] = self._fetch_with_retry(
                    symbol,
                    self._news_fetcher.fetch_news,
                    ticker,
                    symbol
                )
            except Exception as e:
                print(traceback.format_exc())

                self._debug.log_error(e, f"Error fetching news for {symbol}")
                data['errors'].append(f"Error fetching news for {symbol}: {str(e)}")
            
            # Calculate metrics if we have historical data
            if not data['history'].empty:
                data['metrics'] = FinancialAnalyzer.calculate_metrics(data)
                data['indicators'] = TechnicalAnalyzer.calculate_indicators(data['history'])
                data['signals'] = TechnicalAnalyzer.generate_signals(data['history'])
                data['trend'] = TechnicalAnalyzer.analyze_trend(data['history'])
            
            # Export data if requested
            if export_financials:
                DataExporter.export_to_excel(symbol, data['financials']['yearly'])
            
            if export_filtered_financials:
                data['filtered_financials'] = DataExporter.export_filtered_financials(
                    symbol, data['financials']['yearly'], True
                )
            
            self._debug.log_api_call_count(self.api_call_count)
            if data['errors']:
                self._debug.log_warning("\nErrors encountered:")
                for error in data['errors']:
                    self._debug.log_warning(f"- {error}")
            self._debug.log_info("=" * 50)
            
            return data
            
        except Exception as e:
            self._debug.log_error(e, f"Error fetching data for {symbol}")
            raise DataFetchException(f"Failed to fetch data for {symbol}: {str(e)}")
    
    def _fetch_historical_data(self, ticker: yf.Ticker) -> Dict[str, Any]:
        """Fetch historical data for a ticker.
        
        Args:
            ticker: Yahoo Finance ticker object
            
        Returns:
            Dictionary containing historical data
        """
        if self._skip_history:
            return None
            
        try:
            # Fetch historical data
            hist = ticker.history(period="1y")
            if hist.empty:
                return None
            
            # Convert to dictionary
            return {
                'prices': hist['Close'].to_dict(),
                'volumes': hist['Volume'].to_dict(),
                'highs': hist['High'].to_dict(),
                'lows': hist['Low'].to_dict()
            }
        except Exception as e:
            self._debug.log_error(e, "Error in _fetch_historical_data")
            return None

    def filter_stock_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and clean stock data."""
        filtered_data = {}
        print("\n\n filter_stock_data ####### info \n ", data['info'])
        print("\n\n filter_stock_data ####### financials \n ", data['financials'])
        # Filter info section
        if 'info' in data:
            filtered_data['info'] = self._filter_dict_by_keys(data['info'])

        # Filter financial statements
        if 'financials' in data:
            financials = data['financials']

            # Process yearly statements
            if 'yearly_income_stmt' in financials:
                filtered_data['yearly_income_stmt'] = self._filter_dataframe(financials['yearly_income_stmt'])

            if 'yearly_balance_sheet' in financials:
                filtered_data['yearly_balance_sheet'] = self._filter_dataframe(financials['yearly_balance_sheet'])

            if 'yearly_cash_flow' in financials:
                filtered_data['yearly_cash_flow'] = self._filter_dataframe(financials['yearly_cash_flow'])

            # Process quarterly statements
            if 'quarterly_income_stmt' in financials:
                filtered_data['quarterly_income_stmt'] = self._filter_dataframe(financials['quarterly_income_stmt'])

            if 'quarterly_balance_sheet' in financials:
                filtered_data['quarterly_balance_sheet'] = self._filter_dataframe(financials['quarterly_balance_sheet'])

            if 'quarterly_cash_flow' in financials:
                filtered_data['quarterly_cash_flow'] = self._filter_dataframe(financials['quarterly_cash_flow'])

        # Add metrics
        filtered_data['metrics'] = self._calculate_metrics(filtered_data)

        return filtered_data

    def _filter_financial_statements(self, data: Dict[str, pd.DataFrame], statement_type: str = 'financials') -> Dict[
        str, pd.DataFrame]:
        """Filter financial statements and separate yearly and quarterly data."""
        filtered_data = {}

        # Filter yearly data
        if 'yearly' in data:
            yearly_df = self._filter_dataframe(data['yearly'])
            if not yearly_df.empty:
                filtered_data[f'yearly_{statement_type}'] = yearly_df

        # Filter quarterly data
        if 'quarterly' in data:
            quarterly_df = self._filter_dataframe(data['quarterly'])
            if not quarterly_df.empty:
                filtered_data[f'quarterly_{statement_type}'] = quarterly_df

        return filtered_data

    def _filter_dict_by_keys(self, data: Dict[str, Any], keys: List[str] = None) -> Dict[str, Any]:
        """Filter dictionary by specified keys."""
        if keys is None:
            keys = self.income_statement_keys + self.balance_sheet_keys + self.cash_flow_keys
        return {k: v for k, v in data.items() if k in keys}

    def _filter_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and filter DataFrame."""
        if df.empty:
            return df

        # Only convert index to datetime if it's not already and if it contains valid dates
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                # Try to convert only if the index values look like dates
                if df.index.str.match(r'\d{4}-\d{2}-\d{2}').all():
                    df.index = pd.to_datetime(df.index)
            except:
                # If conversion fails, keep the original index
                pass

        # Sort by date in descending order if it's a datetime index
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.sort_index(ascending=False)

        # Remove any columns with all NaN values
        df = df.dropna(axis=1, how='all')

        # Format numbers to 2 decimal places
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        df[numeric_columns] = df[numeric_columns].round(2)

        return df

    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key financial metrics."""
        metrics = {}

        # Get latest values from financial statements
        info = data.get("info", {})
        print("\n\n _calculate_metrics #######  info \n ", info)
        print("\n\n")

        # Income Statement Metrics
        metrics["Revenue"] = info.get("totalRevenue", 0)
        metrics["Gross Profit"] = info.get("grossProfits", 0)
        metrics["Operating Income"] = info.get("operatingIncome", 0)
        metrics["Net Income"] = info.get("netIncome", 0)

        # Balance Sheet Metrics
        metrics["Total Assets"] = info.get("totalAssets", 0)
        metrics["Total Liabilities"] = info.get("totalLiab", 0)
        metrics["Total Equity"] = info.get("totalStockholderEquity", 0)

        # Cash Flow Metrics
        metrics["Operating Cash Flow"] = info.get("totalCashFromOperatingActivities", 0)
        metrics["Investing Cash Flow"] = info.get("totalCashFromInvestingActivities", 0)
        metrics["Financing Cash Flow"] = info.get("totalCashFromFinancingActivities", 0)

        return metrics
