import yfinance as yf
from typing import Dict, Any
from utils.debug_utils import DebugUtils
from services.fetcher.base_fetcher import BaseFetcher

class CompanyInfoFetcher(BaseFetcher):
    """Class for fetching company information."""
    
    def __init__(self):
        """Initialize the company info fetcher."""
        BaseFetcher.__init__(self)  # Initialize BaseFetcher
        self._debug = DebugUtils()
    
    def fetch_company_info(self, stock: yf.Ticker, symbol: str) -> Dict[str, Any]:
        """
        Fetch company information.
        
        Args:
            stock: Yahoo Finance Ticker object
            symbol: Stock symbol for logging
            
        Returns:
            Dictionary containing company information
        """
        try:
            self._debug.info(f"Fetching company info for {symbol}...")
            return self.fetch_with_retry(symbol, lambda: stock.info)
        except Exception as e:
            self._debug.log_error(e, f"Error fetching company info for {symbol}")
            return {} 