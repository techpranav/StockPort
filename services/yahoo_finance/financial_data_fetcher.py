import traceback
from typing import Dict
import yfinance as yf
import pandas as pd
from utils.debug_utils import DebugUtils
from services.fetcher.base_fetcher import BaseFetcher


class FinancialDataFetcher(BaseFetcher):
    """Class for fetching financial statements."""

    def __init__(self):
        """Initialize the financial data fetcher."""
        BaseFetcher.__init__(self)  # Initialize BaseFetcher
        self._debug = DebugUtils()

    def fetch_financial_data(self, stock: yf.Ticker, symbol: str) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Fetch financial statements.
        
        Args:
            stock: Yahoo Finance Ticker object
            symbol: Stock symbol for logging
            
        Returns:
            Dictionary containing financial statements
        """
        financials = {
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
        }

        try:
            # Fetch yearly financials
            DebugUtils.info(f"Fetching yearly financials for {symbol}...")
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

            financials['yearly']['income_statement'] = self.fetch_with_retry(symbol, lambda_stock_financials)
            financials['yearly']['balance_sheet'] = self.fetch_with_retry(symbol, lambda_stock_balancesheet)
            financials['yearly']['cashflow'] = self.fetch_with_retry(symbol, lambda_cashflow)

            # Fetch quarterly financials
            DebugUtils.info(f"Fetching quarterly financials for {symbol}...")

            financials['quarterly']['income_statement'] = self.fetch_with_retry(symbol, lambda_quarterly_financials)
            financials['quarterly']['balance_sheet'] = self.fetch_with_retry(symbol, lambda_quarterly_balance_sheet)
            financials['quarterly']['cashflow'] = self.fetch_with_retry(symbol, lambda_quarterly_cashflow)


        except Exception as e:
            print(traceback.format_exc())
            DebugUtils.log_error(e, f"Error fetching financial data for {symbol}")

        return financials
