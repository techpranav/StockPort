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
            DebugUtils.info(f"Fetching company info for {symbol}...")
            info_lambda = lambda: stock.info
            info_lambda.__name__ = "stock.info"
            return self.fetch_with_retry(symbol, info_lambda)
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching company info for {symbol}")
            return {} 