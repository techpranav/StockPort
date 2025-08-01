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
    
    def __init__(self, skip_history: bool = False):  # Default to False to fetch history
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
    
    def fetch_stock_data(self, symbol: str, export_financials: bool = False, export_filtered_financials: bool = False) -> StockData:
        """Fetch stock data for a given symbol.
        
        Args:
            symbol: Stock symbol to fetch data for
            
        Returns:
            StockData object containing standardized stock data
            
        Raises:
            DataFetchError: If there's an error fetching the data
        """
        try:
            # Validate symbol
            if not symbol or not symbol.strip():
                raise InvalidSymbolException("Symbol cannot be empty")
            
            symbol = symbol.strip().upper()
            DebugUtils.info(f"Fetching stock data for {symbol}")
            
            # Create ticker object
            ticker = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            
            data = {}
            print("\n\n ticker ########## ",ticker)
            # Fetch historical data (skip if flag is set)
            if not self.skip_history:
                try:
                    data['history'] = self._historical_fetcher.fetch_historical_data(ticker, symbol)
                    if data['history'].empty:
                        DebugUtils.warning(f"Historical data fetch returned empty DataFrame for {symbol}")
                except Exception as e:
                    DebugUtils.log_error(e, f"Error fetching historical data for {symbol}")
                    data['history'] = pd.DataFrame()
            else:
                data['history'] = pd.DataFrame()
                DebugUtils.info("Skipping historical data fetch (skip_history=True)")
            
            # Fetch financial data
            data['financials'] = self._financial_fetcher.fetch_financial_data(ticker, symbol)
            
            print(f"{'='*60}\n")
            
            # Fetch company info
            data['info'] = self._company_info_fetcher.fetch_company_info(ticker, symbol)
            
            # Fetch news
            data['news'] = self._news_fetcher.fetch_news(ticker, symbol)
            print("\n\n data['info']  ########## ",data['info'] )

            # Convert raw data to StockData object
            return self._normalize_to_stock_data(symbol, data)
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching stock data for {symbol}")
            raise DataFetchException(f"Failed to fetch stock data for {symbol}: {str(e)}")
    
    def _normalize_to_stock_data(self, symbol: str, raw_data: Dict[str, Any]) -> StockData:
        """Convert raw Yahoo Finance data to standardized StockData object."""
        try:
            # Normalize company info
            company_info = self._normalize_company_info(symbol, raw_data.get('info', {}))
            
            # Normalize financial metrics
            metrics = self._normalize_financial_metrics(raw_data)
            
            # Normalize technical indicators
            technical_analysis = self._normalize_technical_indicators(raw_data.get('history', pd.DataFrame()))
            
            # Generate technical signals
            technical_signals = self._normalize_technical_signals(raw_data.get('history', pd.DataFrame()))
            
            # Normalize financial statements
            financials = self._normalize_financial_statements(raw_data.get('financials', {}))
            
            # Normalize news
            news = self._normalize_news(raw_data.get('news', []))
            
            return StockData(
                symbol=symbol,
                company_info=company_info,
                metrics=metrics,
                technical_analysis=technical_analysis,
                technical_signals=technical_signals,
                financials=financials,
                news=news,
                raw_data=raw_data
            )
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error normalizing data for {symbol}")
            # Return a minimal StockData object with available data
            return StockData(
                symbol=symbol,
                company_info=CompanyInfo(symbol=symbol, name=symbol),
                metrics=FinancialMetrics(),
                technical_analysis=TechnicalIndicators(),
                technical_signals=TechnicalSignals(),
                financials=FinancialStatements(),
                news=[],
                raw_data=raw_data
            )
    
    def fetch_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical price data."""
        try:
            ticker = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            return self._historical_fetcher.fetch_historical_data(ticker, symbol, period, interval)
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching historical data for {symbol}")
            return pd.DataFrame()
    
    def fetch_financials(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial statements."""
        try:
            ticker = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            return self._financial_fetcher.fetch_financial_data(ticker, symbol)
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching financials for {symbol}")
            return {}
    
    def fetch_company_info(self, symbol: str) -> CompanyInfo:
        """Fetch company information."""
        try:
            ticker = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            info_dict = self._company_info_fetcher.fetch_company_info(ticker, symbol)
            return CompanyInfo(**info_dict)
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching company info for {symbol}")
            return CompanyInfo()
    
    def fetch_news(self, symbol: str, limit: int = 5) -> List[NewsItem]:
        """Fetch company news."""
        try:
            ticker = self.fetch_with_retry(symbol, yf.Ticker, symbol)
            news_data = self._news_fetcher.fetch_news(ticker, symbol, limit)
            return [NewsItem(**item) for item in news_data]
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching news for {symbol}")
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
            
            # Calculate and add metrics
            filtered_data['metrics'] = self._calculate_metrics(data)
            
            return filtered_data
            
        except Exception as e:
            DebugUtils.log_error(e, "Error filtering stock data")
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
            DebugUtils.log_error(e, f"Error filtering {statement_type}")
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
            DebugUtils.log_error(e, "Error filtering DataFrame")
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

            # # Income Statement Metrics
            metrics["Revenue"] = info.get("totalRevenue", 0)
            metrics["Gross Profit"] = info.get("grossProfits", 0)
            metrics["Operating Income"] = info.get("operatingIncome", 0)
            metrics["Net Income"] = info.get("netIncome", 0)

            # # Balance Sheet Metrics
            metrics["Total Assets"] = info.get("totalAssets", 0)
            metrics["Total Liabilities"] = info.get("totalLiab", 0)
            metrics["Total Equity"] = info.get("totalStockholderEquity", 0)
            #
            # # Cash Flow Metrics
            metrics["Operating Cash Flow"] = info.get("operatingCashflow", 0)
            metrics["Investing Cash Flow"] = info.get("totalCashFromInvestingActivities", 0)
            metrics["Financing Cash Flow"] = info.get("totalCashFromFinancingActivities", 0)
            return metrics
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating metrics")
            return {}
    
    def _normalize_company_info(self, symbol: str, info_dict: Dict[str, Any]) -> CompanyInfo:
        """Normalize company info to CompanyInfo dataclass."""
        try:
            return CompanyInfo(
                symbol=symbol,
                name=info_dict.get('longName', symbol),
                sector=info_dict.get('sector'),
                industry=info_dict.get('industry'),
                website=info_dict.get('website'),
                description=info_dict.get('longBusinessSummary'),
                country=info_dict.get('country'),
                currency=info_dict.get('currency'),
                exchange=info_dict.get('exchange'),
                market_cap=info_dict.get('marketCap'),
                employees=info_dict.get('fullTimeEmployees'),
                phone=info_dict.get('phone'),
                address=info_dict.get('address1'),
                city=info_dict.get('city'),
                state=info_dict.get('state'),
                zip_code=info_dict.get('zip')
            )
        except Exception as e:
            DebugUtils.log_error(e, f"Error normalizing company info for {symbol}")
            return CompanyInfo(symbol=symbol, name=symbol)
    
    def _normalize_financial_metrics(self, raw_data: Dict[str, Any]) -> FinancialMetrics:
        """Normalize financial metrics to FinancialMetrics dataclass."""
        try:
            info = raw_data.get('info', {})
            history = raw_data.get('history', pd.DataFrame())
            
            # Calculate current price from history if available
            current_price = None
            if not history.empty and 'Close' in history.columns:
                current_price = float(history['Close'].iloc[-1])
            
            return FinancialMetrics(
                revenue=info.get('totalRevenue'),
                gross_profit=info.get('grossProfits'),
                operating_income=info.get('operatingIncome'),
                net_income=info.get('netIncome'),
                total_assets=info.get('totalAssets'),
                total_liabilities=info.get('totalLiab'),
                total_equity=info.get('totalStockholderEquity'),
                operating_cash_flow=info.get('operatingCashflow'),
                investing_cash_flow=info.get('totalCashFromInvestingActivities'),
                financing_cash_flow=info.get('totalCashFromFinancingActivities'),
                free_cash_flow=info.get('freeCashflow'),
                eps=info.get('trailingEps'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                beta=info.get('beta')
            )
        except Exception as e:
            DebugUtils.log_error(e, "Error normalizing financial metrics")
            return FinancialMetrics()
    
    def _normalize_technical_indicators(self, history: pd.DataFrame) -> TechnicalIndicators:
        """Normalize technical indicators to TechnicalIndicators dataclass."""
        try:
            if history.empty or 'Close' not in history.columns:
                return TechnicalIndicators()
            
            # Calculate basic indicators
            current_price = float(history['Close'].iloc[-1]) if len(history) > 0 else None
            volume = float(history['Volume'].iloc[-1]) if 'Volume' in history.columns and len(history) > 0 else None
            
            # Calculate SMAs if we have enough data
            sma_20 = float(history['Close'].rolling(20).mean().iloc[-1]) if len(history) >= 20 else None
            sma_50 = float(history['Close'].rolling(50).mean().iloc[-1]) if len(history) >= 50 else None
            sma_200 = float(history['Close'].rolling(200).mean().iloc[-1]) if len(history) >= 200 else None
            
            # Calculate RSI if we have enough data
            rsi = None
            if len(history) >= 14:
                delta = history['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = float(100 - (100 / (1 + rs.iloc[-1]))) if not rs.iloc[-1] == 0 else None
            
            return TechnicalIndicators(
                current_price=current_price,
                sma_20=sma_20,
                sma_50=sma_50,
                sma_200=sma_200,
                rsi=rsi,
                volume=volume,
                volume_sma=float(history['Volume'].rolling(20).mean().iloc[-1]) if 'Volume' in history.columns and len(history) >= 20 else None
            )
        except Exception as e:
            DebugUtils.log_error(e, "Error normalizing technical indicators")
            return TechnicalIndicators()
    
    def _normalize_technical_signals(self, history: pd.DataFrame) -> TechnicalSignals:
        """Generate technical signals from historical data."""
        try:
            if history.empty or 'Close' not in history.columns or len(history) < 20:
                return TechnicalSignals()
            
            # Simple trend analysis
            sma_20 = history['Close'].rolling(20).mean()
            sma_50 = history['Close'].rolling(50).mean() if len(history) >= 50 else None
            current_price = history['Close'].iloc[-1]
            
            # Determine trend
            trend = "Sideways"
            if sma_50 is not None and len(sma_50.dropna()) > 0:
                if current_price > sma_20.iloc[-1] > sma_50.iloc[-1]:
                    trend = "Uptrend"
                elif current_price < sma_20.iloc[-1] < sma_50.iloc[-1]:
                    trend = "Downtrend"
            
            # Simple momentum analysis using RSI
            momentum = "Neutral"
            if len(history) >= 14:
                delta = history['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs.iloc[-1])) if not rs.iloc[-1] == 0 else 50
                
                if rsi > 70:
                    momentum = "Overbought"
                elif rsi < 30:
                    momentum = "Oversold"
            
            # Simple volatility analysis
            volatility = "Normal"
            if len(history) >= 20:
                returns = history['Close'].pct_change()
                vol = returns.rolling(20).std().iloc[-1] * 100
                if vol > 3:
                    volatility = "High"
                elif vol < 1:
                    volatility = "Low"
            
            # Volume analysis
            volume_signal = "Normal Volume"
            if 'Volume' in history.columns and len(history) >= 20:
                avg_volume = history['Volume'].rolling(20).mean().iloc[-1]
                current_volume = history['Volume'].iloc[-1]
                if current_volume > avg_volume * 1.5:
                    volume_signal = "High Volume"
                elif current_volume < avg_volume * 0.5:
                    volume_signal = "Low Volume"
            
            return TechnicalSignals(
                trend=trend,
                momentum=momentum,
                volatility=volatility,
                volume=volume_signal
            )
        except Exception as e:
            DebugUtils.log_error(e, "Error generating technical signals")
            return TechnicalSignals()
    
    def _normalize_financial_statements(self, financials_dict: Dict[str, Any]) -> FinancialStatements:
        """Normalize financial statements to FinancialStatements dataclass."""
        try:
            return FinancialStatements(
                yearly_income_statement=financials_dict.get('yearly', {}).get('income_statement', pd.DataFrame()),
                quarterly_income_statement=financials_dict.get('quarterly', {}).get('income_statement', pd.DataFrame()),
                yearly_balance_sheet=financials_dict.get('yearly', {}).get('balance_sheet', pd.DataFrame()),
                quarterly_balance_sheet=financials_dict.get('quarterly', {}).get('balance_sheet', pd.DataFrame()),
                yearly_cash_flow=financials_dict.get('yearly', {}).get('cashflow', pd.DataFrame()),
                quarterly_cash_flow=financials_dict.get('quarterly', {}).get('cashflow', pd.DataFrame())
            )
        except Exception as e:
            DebugUtils.log_error(e, "Error normalizing financial statements")
            return FinancialStatements()
    
    def _normalize_news(self, news_list: List[Dict[str, Any]]) -> List[NewsItem]:
        """Normalize news data to NewsItem dataclass."""
        try:
            normalized_news = []
            for item in news_list:
                try:
                    news_item = NewsItem(
                        title=item.get('title', ''),
                        summary=item.get('summary'),
                        url=item.get('link'),
                        published_date=item.get('providerPublishTime'),
                        source=item.get('publisher')
                    )
                    normalized_news.append(news_item)
                except Exception as e:
                    DebugUtils.log_error(e, f"Error normalizing news item: {item}")
                    continue
            return normalized_news
        except Exception as e:
            DebugUtils.log_error(e, "Error normalizing news")
            return []
