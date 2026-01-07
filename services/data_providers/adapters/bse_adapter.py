"""
BSE Data Adapter

Adapter for normalizing BSE (Bombay Stock Exchange) data to standard format.
BSE data from yfinance uses the same format as Yahoo Finance, so this adapter
extends YahooFinanceAdapter.
"""

from services.data_providers.adapters.yahoo_finance_adapter import YahooFinanceAdapter
from utils.debug_utils import DebugUtils


class BSEAdapter(YahooFinanceAdapter):
    """
    Adapter for BSE data provider.
    
    BSE data from yfinance uses the same column format as Yahoo Finance,
    so we extend YahooFinanceAdapter.
    """
    
    def __init__(self):
        """Initialize BSE adapter."""
        super().__init__()
        self.provider_name = "bse"
        DebugUtils.debug("Initialized BSE data adapter")
    
    def get_provider_name(self) -> str:
        """
        Get the provider name.
        
        Returns:
            Provider name string
        """
        return "bse"

