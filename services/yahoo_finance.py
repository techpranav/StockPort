import yfinance as yf
import pandas as pd
from typing import Dict, Any, List
from constants.Constants import (
    INCOME_STATEMENT_KEYS,
    BALANCE_SHEET_KEYS,
    CASHFLOW_KEYS,
    FINANCIAL_STATEMENT_TYPES,
    FINANCIAL_SHEET_NAMES,
    FINANCIAL_STATEMENT_FILTER_KEYS,
    FINANCIAL_METRICS_KEYS
)
import json
from datetime import datetime
import plotly.subplots as sp
import plotly.graph_objects as go
import time
from requests.exceptions import RequestException
import random

class YahooFinanceService:
    def __init__(self):
        self.income_statement_keys = INCOME_STATEMENT_KEYS
        self.balance_sheet_keys = BALANCE_SHEET_KEYS
        self.cashflow_keys = CASHFLOW_KEYS
        self.max_retries = 3
        self.retry_delay = 10  # Increased delay between retries
        self.request_delay = 3  # Delay between API calls
        self.last_request_time = 0

    def _wait_between_requests(self):
        """Ensure minimum delay between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.request_delay:
            time.sleep(self.request_delay - time_since_last_request)
        self.last_request_time = time.time()

    def fetch_stock_data(self, symbol: str, exportFinacials=False, exportFilteredFinancials=False) -> Dict[str, Any]:
        """Fetch stock data from Yahoo Finance with retry logic."""
        for attempt in range(self.max_retries):
            try:
                print(f"Fetching stock data for {symbol} (Attempt {attempt + 1}/{self.max_retries})")
                
                # Add random delay between attempts
                if attempt > 0:
                    delay = self.retry_delay + random.uniform(5, 10)  # Increased random delay
                    print(f"Waiting {delay:.1f} seconds before retry...")
                    time.sleep(delay)
                
                # Initialize the ticker with a delay
                self._wait_between_requests()
                time.sleep(2)  # Additional delay before creating ticker
                stock = yf.Ticker(symbol)
                
                # Fetch basic info with delay
                self._wait_between_requests()
                time.sleep(3)  # Additional delay before fetching info
                info = stock.info
                if not info:
                    raise Exception(f"No data found for symbol {symbol}")
                
                # Fetch historical data with delay
                self._wait_between_requests()
                time.sleep(3)  # Additional delay before fetching history
                data = stock.history(period="1y", interval="1d")
                if data.empty:
                    raise Exception(f"No price data found for {symbol}")
                
                # Fetch news with delay
                self._wait_between_requests()
                time.sleep(3)  # Additional delay before fetching news
                news = stock.get_news()[:5]
                
                # Fetch financials with delay
                self._wait_between_requests()
                time.sleep(3)  # Additional delay before fetching financials
                financials = self.fetch_financials(stock)
                
                stats = {
                    "Market Cap": info.get("marketCap"),
                    "PE Ratio": info.get("trailingPE"),
                    "EPS": info.get("trailingEps"),
                    "52 Week High": info.get("fiftyTwoWeekHigh"),
                    "52 Week Low": info.get("fiftyTwoWeekLow"),
                    "Dividend Yield": info.get("dividendYield"),
                    "Recommendation": info.get("recommendationKey"),
                }

                if exportFinacials:
                    self.export_to_excel(symbol, financials)
                filtered_financials = self.export_filtered_financials(symbol, financials, exportFilteredFinancials)
                
                return {
                    "info": info,
                    "financials": financials,
                    "filtered_financials": filtered_financials,
                    "stats": stats,
                    "news": news,
                    "history": data,
                    "minInfo": {
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
                
            except RequestException as e:
                if "429" in str(e):  # Rate limit error
                    if attempt < self.max_retries - 1:
                        delay = 30 + random.uniform(5, 15)  # Longer delay for rate limit errors
                        print(f"Rate limit hit for {symbol}. Waiting {delay:.1f} seconds before retry...")
                        time.sleep(delay)
                        continue
                elif attempt < self.max_retries - 1:
                    print(f"Request failed for {symbol}. Retrying in {self.retry_delay} seconds...")
                    continue
                raise Exception(f"Failed to fetch data for {symbol} after {self.max_retries} attempts: {str(e)}")
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Error occurred for {symbol}. Retrying in {self.retry_delay} seconds...")
                    continue
                raise Exception(f"Error fetching data for {symbol}: {str(e)}")
        
        raise Exception(f"Failed to fetch data for {symbol} after {self.max_retries} attempts")

    def fetch_financials(self, ticker):
        yearly_income_statement = ticker.financials
        yearly_balance_sheet = ticker.balance_sheet
        yearly_cashflow = ticker.cashflow

        quarterly_income_statement = ticker.quarterly_financials
        quarterly_balance_sheet = ticker.quarterly_balance_sheet
        quarterly_cashflow = ticker.quarterly_cashflow

        return {
            FINANCIAL_STATEMENT_TYPES["yearly"]["income_statement"]: yearly_income_statement,
            FINANCIAL_STATEMENT_TYPES["yearly"]["balance_sheet"]: yearly_balance_sheet,
            FINANCIAL_STATEMENT_TYPES["yearly"]["cashflow"]: yearly_cashflow,
            FINANCIAL_STATEMENT_TYPES["quarterly"]["income_statement"]: quarterly_income_statement,
            FINANCIAL_STATEMENT_TYPES["quarterly"]["balance_sheet"]: quarterly_balance_sheet,
            FINANCIAL_STATEMENT_TYPES["quarterly"]["cashflow"]: quarterly_cashflow,
        }

    def export_to_excel(self, stock_symbol, financials):
        """Exports financial data to an Excel file."""
        with pd.ExcelWriter(f"{stock_symbol}_financials.xlsx") as writer:
            # Export yearly statements
            financials[FINANCIAL_STATEMENT_TYPES["yearly"]["income_statement"]].to_excel(
                writer, sheet_name=FINANCIAL_SHEET_NAMES["yearly"]["income_statement"])
            financials[FINANCIAL_STATEMENT_TYPES["yearly"]["balance_sheet"]].to_excel(
                writer, sheet_name=FINANCIAL_SHEET_NAMES["yearly"]["balance_sheet"])
            financials[FINANCIAL_STATEMENT_TYPES["yearly"]["cashflow"]].to_excel(
                writer, sheet_name=FINANCIAL_SHEET_NAMES["yearly"]["cashflow"])
            
            # Export quarterly statements
            financials[FINANCIAL_STATEMENT_TYPES["quarterly"]["income_statement"]].to_excel(
                writer, sheet_name=FINANCIAL_SHEET_NAMES["quarterly"]["income_statement"])
            financials[FINANCIAL_STATEMENT_TYPES["quarterly"]["balance_sheet"]].to_excel(
                writer, sheet_name=FINANCIAL_SHEET_NAMES["quarterly"]["balance_sheet"])
            financials[FINANCIAL_STATEMENT_TYPES["quarterly"]["cashflow"]].to_excel(
                writer, sheet_name=FINANCIAL_SHEET_NAMES["quarterly"]["cashflow"])
        print(f"Financial data exported to {stock_symbol}_financials.xlsx")

    def export_filtered_financials(self, stock_symbol, financials, exportFilteredFinancials=False):
        """Filter each of the six statements (yearly/quarterly for income, balance, cashflow)
        to keep only the desired keys, then export them to 'updated_financials.xlsx'."""
        # Extract each DataFrame from the financials dictionary
        yearly_income = financials[FINANCIAL_STATEMENT_TYPES["yearly"]["income_statement"]]
        yearly_balance = financials[FINANCIAL_STATEMENT_TYPES["yearly"]["balance_sheet"]]
        yearly_cashflow = financials[FINANCIAL_STATEMENT_TYPES["yearly"]["cashflow"]]
        quarterly_income = financials[FINANCIAL_STATEMENT_TYPES["quarterly"]["income_statement"]]
        quarterly_balance = financials[FINANCIAL_STATEMENT_TYPES["quarterly"]["balance_sheet"]]
        quarterly_cashflow = financials[FINANCIAL_STATEMENT_TYPES["quarterly"]["cashflow"]]

        # Filter them according to the keys we want
        yis_filtered = self.filter_financial_df(yearly_income, self.income_statement_keys)
        ybs_filtered = self.filter_financial_df(yearly_balance, self.balance_sheet_keys)
        ycf_filtered = self.filter_financial_df(yearly_cashflow, self.cashflow_keys)

        qis_filtered = self.filter_financial_df(quarterly_income, self.income_statement_keys)
        qbs_filtered = self.filter_financial_df(quarterly_balance, self.balance_sheet_keys)
        qcf_filtered = self.filter_financial_df(quarterly_cashflow, self.cashflow_keys)

        if exportFilteredFinancials:
            # Write to a new Excel file named "<symbol>_updated_financials.xlsx"
            output_file = f"{stock_symbol}_updated_financials.xlsx"
            with pd.ExcelWriter(output_file) as writer:
                yis_filtered.to_excel(writer, sheet_name=FINANCIAL_SHEET_NAMES["yearly"]["income_statement"])
                ybs_filtered.to_excel(writer, sheet_name=FINANCIAL_SHEET_NAMES["yearly"]["balance_sheet"])
                ycf_filtered.to_excel(writer, sheet_name=FINANCIAL_SHEET_NAMES["yearly"]["cashflow"])

                qis_filtered.to_excel(writer, sheet_name=FINANCIAL_SHEET_NAMES["quarterly"]["income_statement"])
                qbs_filtered.to_excel(writer, sheet_name=FINANCIAL_SHEET_NAMES["quarterly"]["balance_sheet"])
                qcf_filtered.to_excel(writer, sheet_name=FINANCIAL_SHEET_NAMES["quarterly"]["cashflow"])
            print(f"Filtered financial data exported to {output_file}")

        return {
            FINANCIAL_STATEMENT_TYPES["yearly"]["income_statement"]: yis_filtered,
            FINANCIAL_STATEMENT_TYPES["yearly"]["balance_sheet"]: ybs_filtered,
            FINANCIAL_STATEMENT_TYPES["yearly"]["cashflow"]: ycf_filtered,
            FINANCIAL_STATEMENT_TYPES["quarterly"]["income_statement"]: qis_filtered,
            FINANCIAL_STATEMENT_TYPES["quarterly"]["balance_sheet"]: qbs_filtered,
            FINANCIAL_STATEMENT_TYPES["quarterly"]["cashflow"]: qcf_filtered,
        }

    def filter_financial_df(self, df, keys):
        """Filter a DataFrame so that only the specified row labels (keys) remain.
        We assume df.index contains the row labels (e.g., 'EBITDA', 'Net Income')."""
        if df is None or df.empty:
            return df  # Return as-is if empty or None

        # Keep only rows that match the keys, preserving the order of 'keys'
        filtered = df.loc[df.index.intersection(keys)]
        # Reindex to maintain the same order as in 'keys'
        filtered = filtered.reindex(keys)
        return filtered

    def calculate_macd(self, df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
        """Calculate MACD indicator."""
        # Calculate fast and slow EMAs
        exp1 = df['Close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = df['Close'].ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2  # MACD line
        
        # Calculate signal line
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        
        # Calculate histogram
        hist = macd - signal
        
        # Add to DataFrame
        df['MACD'] = macd
        df['Signal'] = signal
        df['Histogram'] = hist
        
        print(f"MACD data for {df.index.name}: {df[['MACD', 'Signal', 'Histogram']].head()}")  # Log MACD data
        return df

    def create_price_chart(self, df: pd.DataFrame, symbol: str) -> go.Figure:
        """Create a price chart with technical indicators."""
        # Create subplots
        fig = sp.make_subplots(rows=4, cols=1, shared_xaxes=True,
                                vertical_spacing=0.02,
                                subplot_titles=(f"{symbol} Price", "MACD", "Signal", "Histogram"))

        # Add price trace
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close', line=dict(color='black')), row=1, col=1)

        # Check if MACD data exists
        if 'MACD' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')), row=2, col=1)
        
        # Check if Signal data exists
        if 'Signal' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], name='Signal', line=dict(color='orange')), row=3, col=1)

        # Check if Histogram data exists
        if 'Histogram' in df.columns:
            fig.add_trace(go.Bar(x=df.index, y=df['Histogram'], name='Histogram', marker_color='red'), row=4, col=1)

        # Update layout
        fig.update_layout(title_text=f"{symbol} Technical Analysis", height=800)
        return fig

    def filter_stock_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and clean stock data."""
        filtered_data = {}
        
        # Filter info section
        if 'info' in data:
            filtered_data['info'] = data['info']
       
         # Filter financial statements
        if 'financials' in data:
            financials = data['financials']
            
            # Process yearly statements
            for statement_type in ['income_statement', 'balance_sheet', 'cashflow']:
                key = FINANCIAL_STATEMENT_FILTER_KEYS['yearly'][statement_type]
                if key in financials:
                    filtered_data[key] = self._filter_dataframe(financials[key])
            
            # Process quarterly statements
            for statement_type in ['income_statement', 'balance_sheet', 'cashflow']:
                key = FINANCIAL_STATEMENT_FILTER_KEYS['quarterly'][statement_type]
                if key in financials:
                    filtered_data[key] = self._filter_dataframe(financials[key])
        
        # Add metrics
        filtered_data['metrics'] = self._calculate_metrics(filtered_data)
        
        return filtered_data
    
    def _filter_financial_statements(self, data: Dict[str, pd.DataFrame], statement_type: str = 'financials') -> Dict[str, pd.DataFrame]:
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
            keys = self.income_statement_keys + self.balance_sheet_keys + self.cashflow_keys
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
        
        # Income Statement Metrics
        metrics["Revenue"] = info.get(FINANCIAL_METRICS_KEYS["income_statement"]["revenue"], 0)
        metrics["Gross Profit"] = info.get(FINANCIAL_METRICS_KEYS["income_statement"]["gross_profit"], 0)
        
        # Get Operating Income from income statement
        yearly_income_key = FINANCIAL_STATEMENT_FILTER_KEYS['yearly']['income_statement']
        if yearly_income_key in data and not data[yearly_income_key].empty:
            income_stmt = data[yearly_income_key]
            if  FINANCIAL_METRICS_KEYS["income_statement"]["operating_income"] in income_stmt.index:
                metrics["Operating Income"] = income_stmt.loc[FINANCIAL_METRICS_KEYS["income_statement"]["operating_income"]].iloc[0]
            else:
                metrics["Operating Income"] = info.get(FINANCIAL_METRICS_KEYS["income_statement"]["operating_income"], 0)
            
            # Get Net Income from income statement
            if FINANCIAL_METRICS_KEYS["income_statement"]["net_income"] in income_stmt.index:
                metrics["Net Income"] = income_stmt.loc[FINANCIAL_METRICS_KEYS["income_statement"]["net_income"]].iloc[0]
            else:
                metrics["Net Income"] = info.get(FINANCIAL_METRICS_KEYS["income_statement"]["net_income"], 0)
        else:
            metrics["Operating Income"] = info.get(FINANCIAL_METRICS_KEYS["income_statement"]["operating_income"], 0)
            metrics["Net Income"] = info.get(FINANCIAL_METRICS_KEYS["income_statement"]["net_income"], 0)
        
        # Get Total Liabilities from balance sheet
        yearly_balance_key = FINANCIAL_STATEMENT_FILTER_KEYS['yearly']['balance_sheet']
        if yearly_balance_key in data and not data[yearly_balance_key].empty:
            balance_sheet = data[yearly_balance_key]
            if 'Total Liabilities' in balance_sheet.index:
                metrics["Total Liabilities"] = balance_sheet.loc[FINANCIAL_METRICS_KEYS["balance_sheet"]["total_liabilities"]].iloc[0]
            else:
                metrics["Total Liabilities"] = info.get(FINANCIAL_METRICS_KEYS["balance_sheet"]["total_liabilities"], 0)
        else:
            metrics["Total Liabilities"] = info.get(FINANCIAL_METRICS_KEYS["balance_sheet"]["total_liabilities"], 0)
        
        # Balance Sheet Metrics
        metrics["Total Assets"] = info.get(FINANCIAL_METRICS_KEYS["balance_sheet"]["total_assets"], 0)
        metrics["Total Equity"] = info.get(FINANCIAL_METRICS_KEYS["balance_sheet"]["total_equity"], 0)
        
        # Get Cash Flow metrics from cash flow statement
        yearly_cashflow_key = FINANCIAL_STATEMENT_FILTER_KEYS['yearly']['cashflow']
        if yearly_cashflow_key in data and not data[yearly_cashflow_key].empty:
            cashflow_stmt = data[yearly_cashflow_key]
            
            # Get Operating Cash Flow
            if  FINANCIAL_METRICS_KEYS["cashflow"]["operating_cashflow"] in cashflow_stmt.index:
                metrics["Operating Cash Flow"] = cashflow_stmt.loc[FINANCIAL_METRICS_KEYS["cashflow"]["operating_cashflow"]].iloc[0]
            else:
                metrics["Operating Cash Flow"] = info.get(FINANCIAL_METRICS_KEYS["cashflow"]["operating_cashflow"], 0)
            
            # Get Investing Cash Flow
            if FINANCIAL_METRICS_KEYS["cashflow"]["investing_cashflow"] in cashflow_stmt.index:
                metrics["Investing Cash Flow"] = cashflow_stmt.loc[FINANCIAL_METRICS_KEYS["cashflow"]["investing_cashflow"]].iloc[0]
            else:
                metrics["Investing Cash Flow"] = info.get(FINANCIAL_METRICS_KEYS["cashflow"]["investing_cashflow"], 0)
            
            # Get Financing Cash Flow
            if FINANCIAL_METRICS_KEYS["cashflow"]["financing_cashflow"] in cashflow_stmt.index:
                metrics["Financing Cash Flow"] = cashflow_stmt.loc[FINANCIAL_METRICS_KEYS["cashflow"]["financing_cashflow"]].iloc[0]
            else:
                metrics["Financing Cash Flow"] = info.get(FINANCIAL_METRICS_KEYS["cashflow"]["financing_cashflow"], 0)
        else:
            metrics["Operating Cash Flow"] = info.get(FINANCIAL_METRICS_KEYS["cashflow"]["operating_cashflow"], 0)
            metrics["Investing Cash Flow"] = info.get(FINANCIAL_METRICS_KEYS["cashflow"]["investing_cashflow"], 0)
            metrics["Financing Cash Flow"] = info.get(FINANCIAL_METRICS_KEYS["cashflow"]["financing_cashflow"], 0)
        
        return metrics

    def get_financials_text(self, data: Dict[str, Any]) -> str:
        """Format financial data as text."""
        text = []
        
        # Add income statement
        if not data["income_statement"].empty:
            text.append(self._format_financials("Income Statement", data["income_statement"]))
        
        # Add balance sheet
        if not data["balance_sheet"].empty:
            text.append(self._format_financials("Balance Sheet", data["balance_sheet"]))
        
        # Add cash flow
        if not data["cashflow"].empty:
            text.append(self._format_financials("Cash Flow", data["cashflow"]))
        
        return "\n\n".join(text)

    def _format_financials(self, title: str, df: pd.DataFrame) -> str:
        """Format financial data with title."""
        if df.empty:
            return f"{title}:\nNo data available"
        
        return f"{title}:\n{df.to_string()}" 