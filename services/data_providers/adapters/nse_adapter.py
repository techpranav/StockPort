"""
NSE Data Adapter

Adapter for normalizing NSE (National Stock Exchange) data to standard format.
NSE data from yfinance uses the same format as Yahoo Finance, so this adapter
extends YahooFinanceAdapter.
"""

from services.data_providers.adapters.yahoo_finance_adapter import YahooFinanceAdapter
from utils.debug_utils import DebugUtils


class NSEAdapter(YahooFinanceAdapter):
    """
    Adapter for NSE data provider.
    
    NSE data from yfinance uses the same column format as Yahoo Finance,
    so we extend YahooFinanceAdapter.
    """
    
    def __init__(self):
        """Initialize NSE adapter."""
        super().__init__()
        self.provider_name = "nse"
        DebugUtils.debug("Initialized NSE data adapter")
    
    def get_provider_name(self) -> str:
        """
        Get the provider name.
        
        Returns:
            Provider name string
        """
        return "nse"

