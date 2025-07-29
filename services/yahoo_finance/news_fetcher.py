from typing import List, Dict, Any
import yfinance as yf
from utils.debug_utils import DebugUtils
from .base_fetcher import BaseFetcher

class NewsFetcher(BaseFetcher):
    """Class for fetching company news."""
    
    def fetch_news(self, stock: yf.Ticker,symbol: str) -> List[Dict[str, Any]]:
        """
        Fetch company news.
        
        Args:
            stock: Yahoo Finance Ticker object
            
        Returns:
            List of dictionaries containing news items
        """
        DebugUtils.info("\nFetching news...")
        try:
            news_df = self.fetch_with_retry(symbol, stock.get_news)
            return news_df if news_df else []
        except Exception as e:
            DebugUtils.error(f"Error fetching news: {str(e)}")
            return [] 