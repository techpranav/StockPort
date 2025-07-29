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
            self._debug.info(f"Fetching news for {symbol} (limit={limit})...")
            news_df = self.fetch_with_retry(symbol, lambda: stock.get_news())
            print("news_df ###### ",news_df)
            if news_df is not None and type(news_df) == list and len(news_df) > 0:
                # Convert DataFrame to list of dictionaries
                news_list = news_df.to_dict('records')
                return news_list[:limit] if news_list else []
            else:
                return []
                
        except Exception as e:
            self._debug.log_error(e, f"Error fetching news for {symbol}")
            return [] 