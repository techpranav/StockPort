import yfinance as yf
import pandas as pd
from typing import Dict, Any
import time
from datetime import datetime
import random
from services.stock_data_provider import StockDataProvider
from config.global_config import GlobalConfig

class YahooFinanceProvider(StockDataProvider):
    """Yahoo Finance implementation of StockDataProvider."""
    
    def __init__(self):
        """Initialize the provider."""
        self.rate_limit_delay = 10
        self.max_retries = 5
        self.last_request_time = 0
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.rate_limit_cooldown = 120
        self.api_call_count = 0
    
    def get_provider_name(self) -> str:
        """Get the name of the data provider."""
        return "Yahoo Finance"
    
    def _wait_for_rate_limit(self):
        """Wait to respect rate limits."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            print(f"Rate limit: Waiting {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _fetch_with_retry(self,symbol, func, *args, **kwargs):
        """Execute a function with retry logic."""
        last_error = None
        api_name = func.__name__ if hasattr(func, '__name__') else str(func)
        symbol = args[0] if args else 'Unknown'
        
        for attempt in range(self.max_retries):
            try:
                self._log_api_call(api_name, symbol)
                self._wait_for_rate_limit()
                result = func(*args, **kwargs)
                self.consecutive_failures = 0
                return result
            except Exception as e:
                last_error = e
                error_msg = str(e)
                print(f"\nError in API call:")
                print(f"Symbol: {symbol}")
                print(f"API: {api_name}")
                print(f"Error: {error_msg}")
                print(f"Attempt: {attempt + 1}/{self.max_retries}")
                
                if "Too Many Requests" in error_msg:
                    self.consecutive_failures += 1
                    if attempt < self.max_retries - 1:
                        base_wait = self.rate_limit_delay * (2 ** attempt)
                        jitter = random.uniform(1, 5)
                        if self.consecutive_failures >= self.max_consecutive_failures:
                            base_wait = self.rate_limit_cooldown
                            print(f"Multiple consecutive failures detected. Using longer cooldown period.")
                        wait_time = min(base_wait + jitter, self.rate_limit_cooldown)
                        print(f"Rate limit hit. Retrying in {wait_time:.1f} seconds... (Attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                elif attempt < self.max_retries - 1:
                    wait_time = self.rate_limit_delay * (2 ** attempt)
                    print(f"Error occurred. Retrying in {wait_time:.1f} seconds... (Attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    continue
                raise
        
        if last_error:
            raise last_error
    
    def _log_api_call(self, api_name: str, symbol: str):
        """Log API call details."""
        self.api_call_count += 1
        print(f"\nAPI Call #{self.api_call_count}:")
        print(f"Symbol: {symbol}")
        print(f"API: {api_name}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Consecutive Failures: {self.consecutive_failures}")
        print("-" * 50)
    
    def fetch_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical price data."""
        try:
            stock = self._fetch_with_retry(symbol,yf.Ticker,symbol)
            return self._fetch_with_retry(symbol, stock.history, period=period, interval=interval)
        except Exception as e:
            print(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame()
    
    def fetch_financials(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial statements."""
        stock = self._fetch_with_retry(symbol, yf.Ticker)

        lambda_stock_financials = lambda: stock.financials
        lambda_stock_balancesheet = lambda: stock.balance_sheet
        lambda_cashflow = lambda: stock.cashflow
        lambda_quarterly_financials = lambda: stock.quarterly_financials
        lambda_quarterly_balance_sheet = lambda: stock.quarterly_cashflow
        lambda_quarterly_cashflow = lambda: stock.quarterly_cashflow

        lambda_stock_financials.__name__ = "stock.financials"
        lambda_stock_balancesheet.__name__ = "stock.balance_sheet"
        lambda_cashflow.__name__ = "stock.cashflow"
        lambda_quarterly_financials.__name__ = "stock.quarterly_financials"
        lambda_quarterly_balance_sheet.__name__ = "stock.quarterly_cashflow"
        lambda_quarterly_cashflow.__name__ = "stock.quarterly_cashflow"

        return {
            'yearly': {
                'income_statement': self._fetch_with_retry(symbol,lambda_stock_financials),
                'balance_sheet': self._fetch_with_retry(symbol,lambda_stock_balancesheet),
                'cashflow': self._fetch_with_retry(symbol,lambda_cashflow)
            },
            'quarterly': {
                'income_statement': self._fetch_with_retry(symbol,lambda_quarterly_financials),
                'balance_sheet': self._fetch_with_retry(symbol,lambda_quarterly_balance_sheet),
                'cashflow': self._fetch_with_retry(symbol,lambda_quarterly_cashflow)
            }
        }
    
    def fetch_company_info(self, symbol: str) -> Dict[str, Any]:
        """Fetch company information."""
        stock = self._fetch_with_retry(symbol,yf.Ticker)
        return self._fetch_with_retry(symbol,stock.info)
    
    def fetch_news(self, symbol: str, limit: int = 5) -> list:
        """Fetch company news."""
        stock = self._fetch_with_retry(symbol,yf.Ticker)
        return self._fetch_with_retry(symbol,stock.get_news)[:limit]
    
    def fetch_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch all stock data for a given symbol."""
        try:
            print(f"\nStarting data fetch for {symbol}")
            print("=" * 50)
            
            # Fetch all data
            hist_data = self.fetch_historical_data(symbol)
            financials = self.fetch_financials(symbol)
            info = self.fetch_company_info(symbol)
            news = self.fetch_news(symbol)
            
            print(f"\nCompleted data fetch for {symbol}")
            print(f"Total API calls made: {self.api_call_count}")
            print("=" * 50)
            
            return {
                'symbol': symbol,
                'history': hist_data,
                'financials': financials,
                'info': info,
                'news': news,
                'minInfo': {
                    "Stock Name": info.get("longName", symbol),
                    "Market Cap": info.get("marketCap"),
                    "PE Ratio": info.get("trailingPE"),
                    "Dividend Yield": info.get("dividendYield"),
                    "52 Week High": info.get("fiftyTwoWeekHigh"),
                    "52 Week Low": info.get("fiftyTwoWeekLow"),
                    "EPS": info.get("trailingEps"),
                    "Sector": info.get("sector"),
                    "Recommendation": info.get("recommendationKey")
                }
            }
            
        except Exception as e:
            print(f"\nError fetching data for {symbol}:")
            print(f"Error: {str(e)}")
            print(f"Total API calls made: {self.api_call_count}")
            print("=" * 50)
            raise 