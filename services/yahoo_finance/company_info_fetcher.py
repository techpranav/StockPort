from typing import Dict, Any
import yfinance as yf
from utils.debug_utils import DebugUtils
from .base_fetcher import BaseFetcher

class CompanyInfoFetcher(BaseFetcher):
    """Class for fetching company information."""
    
    def fetch_company_info(self, stock: yf.Ticker,symbol:str) -> Dict[str, Any]:
        """
        Fetch company information.
        
        Args:
            stock: Yahoo Finance Ticker object
            
        Returns:
            Dictionary containing company information
        """
        DebugUtils.info("\nFetching company info...")
        try:
            lambda_info = lambda: stock.info
            lambda_info.__name__="stock.info"
            return self.fetch_with_retry(symbol, lambda_info)
        except Exception as e:
            DebugUtils.error(f"Error fetching company info: {str(e)}")
            return {} 