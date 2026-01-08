"""
NSEPython Data Provider for Indian Stocks

Provides comprehensive Indian stock market data using the nsepython library.
Supports NSE exchange with real-time and historical data.
"""

import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, date

from services.data_providers.stock_data_provider import StockDataProvider
from services.data_providers.fetcher.base_fetcher import BaseFetcher
from exceptions.stock_data_exceptions import DataFetchException, InvalidSymbolException
from utils.debug_utils import DebugUtils
from models.stock_data import (
    StockData, CompanyInfo, FinancialMetrics, TechnicalIndicators,
    TechnicalSignals, FinancialStatements, NewsItem
)


class NSEPythonProvider(StockDataProvider, BaseFetcher):
    """
    NSEPython data provider for Indian stock markets.
    
    Uses nsepython library to fetch data directly from NSE APIs.
    Supports:
    - Historical price data
    - Real-time/live prices
    - Company information
    - Quote data
    """
    
    def __init__(self):
        """Initialize NSEPython provider."""
        BaseFetcher.__init__(self)
        DebugUtils.info("Initialized NSEPython Provider")
    
    def get_provider_name(self) -> str:
        """
        Get the provider name.
        
        Returns:
            Provider name string
        """
        return "nsepython"
    
    def _normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol by removing exchange suffix if present.
        
        Args:
            symbol: Stock symbol (with or without .NS suffix)
            
        Returns:
            Normalized symbol without suffix
        """
        # Remove .NS or .BO suffix if present
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            return symbol[:-3]
        return symbol.upper()
    
    def _calculate_start_date(self, end_date: datetime, period: str) -> datetime:
        """Calculate start date from period string."""
        period_map = {
            '1d': timedelta(days=1),
            '5d': timedelta(days=5),
            '1mo': timedelta(days=30),
            '3mo': timedelta(days=90),
            '6mo': timedelta(days=180),
            '1y': timedelta(days=365),
            '2y': timedelta(days=730),
            '5y': timedelta(days=1825),
            '10y': timedelta(days=3650),
            'ytd': timedelta(days=(end_date - datetime(end_date.year, 1, 1)).days),
            'max': timedelta(days=3650)  # Max 10 years
        }
        delta = period_map.get(period, timedelta(days=365))
        return end_date - delta
    
    def fetch_historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical price data for Indian stock.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            period: Period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1d, 1wk, 1mo) - nsepython primarily supports daily
            
        Returns:
            DataFrame with historical OHLCV data
            
        Raises:
            DataFetchException: If data fetch fails
        """
        try:
            from nsepython import nsefetch, equity_history
            
            normalized_symbol = self._normalize_symbol(symbol)
            DebugUtils.info(f"Fetching NSEPython historical data for {normalized_symbol} (period={period})")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = self._calculate_start_date(end_date, period)
            
            # Convert to date strings in DD-MM-YYYY format
            start_str = start_date.strftime('%d-%m-%Y')
            end_str = end_date.strftime('%d-%m-%Y')
            
            # Fetch historical data using nsepython
            # equity_history requires: symbol, series, start_date, end_date
            hist_data = None
            try:
                # Use 'EQ' series for equity stocks
                hist_data = equity_history(normalized_symbol, 'EQ', start_str, end_str)
                DebugUtils.debug(f"equity_history returned type: {type(hist_data)}")
                
                # Convert to DataFrame if needed
                if hist_data is not None:
                    if isinstance(hist_data, pd.DataFrame):
                        pass  # Already DataFrame
                    elif isinstance(hist_data, list):
                        if len(hist_data) > 0:
                            hist_data = pd.DataFrame(hist_data)
                        else:
                            hist_data = pd.DataFrame()
                    elif isinstance(hist_data, dict):
                        # Try to extract data array
                        if 'data' in hist_data:
                            hist_data = pd.DataFrame(hist_data['data']) if hist_data['data'] else pd.DataFrame()
                        elif 'history' in hist_data:
                            hist_data = pd.DataFrame(hist_data['history']) if hist_data['history'] else pd.DataFrame()
                        else:
                            hist_data = pd.DataFrame()
                    else:
                        hist_data = pd.DataFrame()
                else:
                    hist_data = pd.DataFrame()
            except Exception as e:
                DebugUtils.warning(f"equity_history failed: {e}")
                hist_data = None
            
            # If equity_history didn't work, try nsefetch
            if hist_data is None or (isinstance(hist_data, pd.DataFrame) and hist_data.empty):
                try:
                    # Alternative: use nsefetch with historical API endpoint
                    hist_url = f'https://www.nseindia.com/api/historical/cm/equity?symbol={normalized_symbol}&series=["EQ"]&from={start_str}&to={end_str}'
                    hist_data = nsefetch(hist_url)
                    DebugUtils.debug(f"nsefetch returned type: {type(hist_data)}")
                    
                    # Process nsefetch response
                    if isinstance(hist_data, dict):
                        if 'data' in hist_data:
                            hist_data = pd.DataFrame(hist_data['data']) if hist_data['data'] else pd.DataFrame()
                        else:
                            hist_data = pd.DataFrame()
                    elif isinstance(hist_data, list):
                        hist_data = pd.DataFrame(hist_data) if hist_data else pd.DataFrame()
                    else:
                        hist_data = pd.DataFrame()
                except Exception as e2:
                    DebugUtils.warning(f"nsefetch also failed: {e2}")
                    hist_data = pd.DataFrame()
            
            if hist_data is None:
                DebugUtils.warning(f"No historical data returned for {normalized_symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame if needed
            if isinstance(hist_data, dict):
                # Try to extract data array
                if 'data' in hist_data:
                    hist_data = hist_data['data']
                elif 'history' in hist_data:
                    hist_data = hist_data['history']
                else:
                    # Try to convert dict to DataFrame
                    hist_data = pd.DataFrame([hist_data])
            
            if isinstance(hist_data, list):
                hist_data = pd.DataFrame(hist_data)
            
            if not isinstance(hist_data, pd.DataFrame):
                hist_data = pd.DataFrame()
            
            if hist_data.empty:
                DebugUtils.warning(f"Historical data is empty for {normalized_symbol}")
                return pd.DataFrame()
            
            # Normalize column names
            hist_data = self._normalize_dataframe_columns(hist_data)
            
            # Ensure date index
            if not isinstance(hist_data.index, pd.DatetimeIndex):
                # Try to find date column
                date_cols = [col for col in hist_data.columns if 'date' in col.lower() or 'time' in col.lower()]
                if date_cols:
                    hist_data[date_cols[0]] = pd.to_datetime(hist_data[date_cols[0]], errors='coerce')
                    hist_data.set_index(date_cols[0], inplace=True)
            
            DebugUtils.info(f"Fetched {len(hist_data)} rows of historical data for {normalized_symbol}")
            return hist_data
            
        except ImportError:
            raise DataFetchException("NSEPython library not installed. Install with: pip install nsepython")
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching NSEPython historical data for {symbol}")
            raise DataFetchException(f"Failed to fetch NSEPython historical data for {symbol}: {str(e)}") from e
    
    def _normalize_dataframe_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize DataFrame columns to standard format."""
        if df.empty:
            return df
        
        # Map common column name variations to standard names
        column_mapping = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'lastprice': 'Close',
            'ltp': 'Close',
            'volume': 'Volume',
            'tradedquantity': 'Volume',
            'adj close': 'Adj Close',
            'adj_close': 'Adj Close',
            'date': 'Date',
            'timestamp': 'Date',
            'tradeddate': 'Date'
        }
        
        # Rename columns if needed
        df.columns = [column_mapping.get(col.lower(), col) for col in df.columns]
        
        # Ensure we have Close column (use lastPrice or LTP if available)
        if 'Close' not in df.columns:
            for alt in ['lastPrice', 'ltp', 'last_price']:
                if alt in df.columns:
                    df['Close'] = df[alt]
                    break
        
        return df
    
    def fetch_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch company information for Indian stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company information
        """
        try:
            from nsepython import nsefetch
            
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Fetch equity quote data from NSE API
            try:
                quote_url = f'https://www.nseindia.com/api/quote-equity?symbol={normalized_symbol}'
                quote_data = nsefetch(quote_url)
                
                if quote_data and isinstance(quote_data, dict):
                    # Extract relevant company info
                    info = quote_data.get('info', {})
                    price_info = quote_data.get('priceInfo', {})
                    
                    company_info = {
                        'symbol': normalized_symbol,
                        'companyName': info.get('companyName'),
                        'industry': info.get('industry'),
                        'sector': info.get('industry'),  # NSE uses industry for sector
                        'marketCap': price_info.get('marketCap'),
                        'lastPrice': price_info.get('lastPrice'),
                        'previousClose': price_info.get('previousClose'),
                        'open': price_info.get('open'),
                        'high': price_info.get('intraDayHighLow', {}).get('max'),
                        'low': price_info.get('intraDayHighLow', {}).get('min'),
                        'volume': price_info.get('totalTradedVolume')
                    }
                    
                    # Add full quote data
                    company_info['raw_data'] = quote_data
                    
                    return company_info
            except Exception as e:
                DebugUtils.warning(f"Failed to fetch company info for {normalized_symbol}: {e}")
            
            return {}
            
        except ImportError:
            DebugUtils.warning("NSEPython library not installed")
            return {}
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching NSEPython company info for {symbol}")
            return {}
    
    def fetch_current_price(self, symbol: str) -> Optional[float]:
        """
        Fetch current/live price for Indian stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price or None if unavailable
        """
        try:
            from nsepython import nsefetch
            
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Fetch quote data from NSE API
            try:
                quote_url = f'https://www.nseindia.com/api/quote-equity?symbol={normalized_symbol}'
                quote_data = nsefetch(quote_url)
                
                if quote_data and isinstance(quote_data, dict):
                    price_info = quote_data.get('priceInfo', {})
                    # Try different price fields
                    price = (price_info.get('lastPrice') or 
                            price_info.get('previousClose') or
                            price_info.get('open'))
                    if price is not None:
                        return float(price)
            except Exception as e:
                DebugUtils.debug(f"Failed to fetch current price for {normalized_symbol}: {e}")
            
            return None
            
        except ImportError:
            DebugUtils.warning("NSEPython library not installed")
            return None
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching NSEPython current price for {symbol}")
            return None
    
    def fetch_stock_data(self, symbol: str) -> StockData:
        """
        Fetch comprehensive stock data for Indian stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            StockData object with all stock information
        """
        try:
            from nsepython import nse_eq
            
            normalized_symbol = self._normalize_symbol(symbol)
            DebugUtils.info(f"Fetching comprehensive NSEPython data for {normalized_symbol}")
            
            # Fetch historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            history = self.fetch_historical_data(
                normalized_symbol,
                period='1y',
                interval='1d'
            )
            
            # Fetch company info
            company_info_dict = self.fetch_company_info(normalized_symbol)
            
            # Company info already fetched via fetch_company_info
            
            # Build CompanyInfo
            company_info = CompanyInfo(
                symbol=normalized_symbol,
                name=company_info_dict.get('info', {}).get('companyName') or 
                     company_info_dict.get('companyName') or 
                     company_info_dict.get('name') or 
                     normalized_symbol,
                sector=company_info_dict.get('info', {}).get('industry') or 
                       company_info_dict.get('industry'),
                industry=company_info_dict.get('info', {}).get('industry') or 
                         company_info_dict.get('industry'),
                market_cap=company_info_dict.get('marketCap') or 
                          company_info_dict.get('info', {}).get('marketCap'),
                exchange='NSE'
            )
            
            # Get current price
            current_price = self.fetch_current_price(normalized_symbol)
            if current_price is None and not history.empty:
                current_price = float(history['Close'].iloc[-1]) if 'Close' in history.columns else None
            
            # Build TechnicalIndicators
            technical_indicators = TechnicalIndicators(
                current_price=current_price
            )
            
            # Build other components
            technical_signals = TechnicalSignals()
            financial_metrics = FinancialMetrics()
            financial_statements = FinancialStatements()
            
            # Build StockData
            stock_data = StockData(
                symbol=normalized_symbol,
                company_info=company_info,
                info=company_info_dict,
                metrics=financial_metrics,
                technical_analysis=technical_indicators,
                technical_signals=technical_signals,
                financials=financial_statements,
                news=[],
                raw_data={'history': history, 'provider': 'nsepython', 'exchange': 'NSE'}
            )
            
            DebugUtils.info(f"Successfully fetched NSEPython data for {normalized_symbol}")
            return stock_data
            
        except ImportError:
            raise DataFetchException("NSEPython library not installed. Install with: pip install nsepython")
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching NSEPython stock data for {symbol}")
            raise DataFetchException(f"Failed to fetch NSEPython stock data for {symbol}: {str(e)}") from e
    
    def fetch_financials(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch financial statements for Indian stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary containing financial statements
        """
        try:
            from nsepython import nsefetch
            
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Try to fetch financials from NSE API
            try:
                financials_url = f'https://www.nseindia.com/api/company-financial-results?symbol={normalized_symbol}'
                financials = nsefetch(financials_url)
                return financials if isinstance(financials, dict) else {}
            except Exception as e:
                DebugUtils.warning(f"Failed to fetch financials for {normalized_symbol}: {e}")
                return {}
            
        except ImportError:
            DebugUtils.warning("NSEPython library not installed")
            return {}
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching NSEPython financials for {symbol}")
            return {}
    
    def fetch_news(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch company news for Indian stock.
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of news items
            
        Returns:
            List of news items
        """
        try:
            from nsepython import nsefetch
            
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Try to fetch news from NSE API
            try:
                news_url = f'https://www.nseindia.com/api/company-announcements?symbol={normalized_symbol}'
                news_data = nsefetch(news_url)
                
                if isinstance(news_data, dict) and 'data' in news_data:
                    news_list = news_data['data']
                    if isinstance(news_list, list):
                        return news_list[:limit]
                
                return []
            except Exception as e:
                DebugUtils.warning(f"Failed to fetch news for {normalized_symbol}: {e}")
                return []
            
        except ImportError:
            DebugUtils.warning("NSEPython library not installed")
            return []
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching NSEPython news for {symbol}")
            return []
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if symbol exists on NSE.
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            True if symbol is valid, False otherwise
        """
        try:
            from nsepython import nsefetch
            
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Try to fetch quote - if it works, symbol is valid
            quote_url = f'https://www.nseindia.com/api/quote-equity?symbol={normalized_symbol}'
            quote_data = nsefetch(quote_url)
            
            if quote_data and isinstance(quote_data, dict):
                # Check if we got valid data
                info = quote_data.get('info', {})
                if info.get('symbol') or info.get('companyName'):
                    return True
            
            return False
            
        except Exception:
            return False

