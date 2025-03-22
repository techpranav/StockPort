import yfinance as yf
import pandas as pd
from typing import Dict, Any, List
from core.config import (
    INCOME_STATEMENT_KEYS,
    BALANCE_SHEET_KEYS,
    CASH_FLOW_KEYS
)
import json
from datetime import datetime
import plotly.subplots as sp
import plotly.graph_objects as go

class YahooFinanceService:
    def __init__(self):
        self.income_statement_keys = INCOME_STATEMENT_KEYS
        self.balance_sheet_keys = BALANCE_SHEET_KEYS
        self.cash_flow_keys = CASH_FLOW_KEYS

    def fetch_stock_data(self, symbol: str, exportFinacials=False, exportFilteredFinancials=False) -> Dict[str, Any]:
        """Fetch stock data from Yahoo Finance."""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1y", interval="1d")
            info = stock.info  # Fetch stock data

            stats = {
                "Market Cap": info.get("marketCap"),
                "PE Ratio": info.get("trailingPE"),
                "EPS": info.get("trailingEps"),
                "52 Week High": info.get("fiftyTwoWeekHigh"),
                "52 Week Low": info.get("fiftyTwoWeekLow"),
                "Dividend Yield": info.get("dividendYield"),
                "Recommendation": info.get("recommendationKey"),
            }

            news = stock.get_news()[:5]  # Fetch latest 5 news articles

            financials = self.fetch_financials(stock)
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
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")

    def fetch_financials(self, ticker):
        yearly_income_statement = ticker.financials
        yearly_balance_sheet = ticker.balance_sheet
        yearly_cashflow = ticker.cashflow

        quarterly_income_statement = ticker.quarterly_financials
        quarterly_balance_sheet = ticker.quarterly_balance_sheet
        quarterly_cashflow = ticker.quarterly_cashflow

        return {
            "yearly_income_statement": yearly_income_statement,
            "yearly_balance_sheet": yearly_balance_sheet,
            "yearly_cashflow": yearly_cashflow,
            "quarterly_income_statement": quarterly_income_statement,
            "quarterly_balance_sheet": quarterly_balance_sheet,
            "quarterly_cashflow": quarterly_cashflow,
        }

    def export_to_excel(self, stock_symbol, financials):
        """Exports financial data to an Excel file."""
        with pd.ExcelWriter(f"{stock_symbol}_financials.xlsx") as writer:
            financials["yearly_income_statement"].to_excel(writer, sheet_name="Yearly Income Statement")
            financials["yearly_balance_sheet"].to_excel(writer, sheet_name="Yearly Balance Sheet")
            financials["yearly_cashflow"].to_excel(writer, sheet_name="Yearly Cash Flow")
            financials["quarterly_income_statement"].to_excel(writer, sheet_name="Quarterly Income Statement")
            financials["quarterly_balance_sheet"].to_excel(writer, sheet_name="Quarterly Balance Sheet")
            financials["quarterly_cashflow"].to_excel(writer, sheet_name="Quarterly Cash Flow")
        print(f"Financial data exported to {stock_symbol}_financials.xlsx")

    def export_filtered_financials(self, stock_symbol, financials, exportFilteredFinancials=False):
        """Filter each of the six statements (yearly/quarterly for income, balance, cashflow)
        to keep only the desired keys, then export them to 'updated_financials.xlsx'."""
        # Extract each DataFrame from the financials dictionary
        yearly_income = financials["yearly_income_statement"]
        yearly_balance = financials["yearly_balance_sheet"]
        yearly_cashflow = financials["yearly_cashflow"]
        quarterly_income = financials["quarterly_income_statement"]
        quarterly_balance = financials["quarterly_balance_sheet"]
        quarterly_cashflow = financials["quarterly_cashflow"]

        # Filter them according to the keys we want
        yis_filtered = self.filter_financial_df(yearly_income, self.income_statement_keys)
        ybs_filtered = self.filter_financial_df(yearly_balance, self.balance_sheet_keys)
        ycf_filtered = self.filter_financial_df(yearly_cashflow, self.cash_flow_keys)

        qis_filtered = self.filter_financial_df(quarterly_income, self.income_statement_keys)
        qbs_filtered = self.filter_financial_df(quarterly_balance, self.balance_sheet_keys)
        qcf_filtered = self.filter_financial_df(quarterly_cashflow, self.cash_flow_keys)

        if exportFilteredFinancials:
            # Write to a new Excel file named "<symbol>_updated_financials.xlsx"
            output_file = f"{stock_symbol}_updated_financials.xlsx"
            with pd.ExcelWriter(output_file) as writer:
                yis_filtered.to_excel(writer, sheet_name="Yearly Income Statement")
                ybs_filtered.to_excel(writer, sheet_name="Yearly Balance Sheet")
                ycf_filtered.to_excel(writer, sheet_name="Yearly Cash Flow")

                qis_filtered.to_excel(writer, sheet_name="Quarterly Income Statement")
                qbs_filtered.to_excel(writer, sheet_name="Quarterly Balance Sheet")
                qcf_filtered.to_excel(writer, sheet_name="Quarterly Cash Flow")
            print(f"Filtered financial data exported to {output_file}")

        return {
            "yearly_income_statement": yis_filtered,
            "yearly_balance_sheet": ybs_filtered,
            "yearly_cashflow": ycf_filtered,
            "quarterly_income_statement": qis_filtered,
            "quarterly_balance_sheet": qbs_filtered,
            "quarterly_cashflow": qcf_filtered,
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

    def get_financials_text(self, data: Dict[str, Any]) -> str:
        """Format financial data as text."""
        text = []
        
        # Add income statement
        if not data["income_stmt"].empty:
            text.append(self._format_financials("Income Statement", data["income_stmt"]))
        
        # Add balance sheet
        if not data["balance_sheet"].empty:
            text.append(self._format_financials("Balance Sheet", data["balance_sheet"]))
        
        # Add cash flow
        if not data["cash_flow"].empty:
            text.append(self._format_financials("Cash Flow", data["cash_flow"]))
        
        return "\n\n".join(text)

    def _format_financials(self, title: str, df: pd.DataFrame) -> str:
        """Format financial data with title."""
        if df.empty:
            return f"{title}:\nNo data available"
        
        return f"{title}:\n{df.to_string()}" 