import yfinance as yf
from typing import List, Dict, Any
from utils.debug_utils import DebugUtils
from services.fetcher.base_fetcher import BaseFetcher

class NewsFetcher(BaseFetcher):
    """Class for fetching company news."""
    
    def __init__(self):
        """Initialize the news fetcher."""
        BaseFetcher.__init__(self)  # Initialize BaseFetcher
        self._debug = DebugUtils()
    
    def fetch_news(self, stock: yf.Ticker, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch company news.
        
        Args:
            stock: Yahoo Finance Ticker object
            symbol: Stock symbol for logging
            limit: Maximum number of news items to fetch
            
        Returns:
            List of news items
        """
        try:
            DebugUtils.info(f"Fetching news for {symbol} (limit={limit})...")
            news_lambda = lambda: stock.get_news()
            news_lambda.__name__ = "stock.news"
            news_df = self.fetch_with_retry(symbol, news_lambda)
            return news_df if news_df else []
                
        except Exception as e:
            DebugUtils.log_error(e, f"Error fetching news for {symbol}")
            return [] 