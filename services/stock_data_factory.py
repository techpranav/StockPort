"""
Stock Data Factory

Factory class for creating and managing stock data providers.
Supports multiple data sources like Yahoo Finance, Alpha Vantage, etc.
"""

from typing import Dict, Any, Optional
from services.data_providers.stock_data_provider import StockDataProvider
from utils.debug_utils import DebugUtils

class StockDataFactory:
    """Factory for creating stock data providers."""
    
    _providers: Dict[str, type] = {}
    
    @classmethod
    def _register_default_providers(cls):
        """Register default providers."""
        try:
            from services.data_providers.yahoo_finance.yahoo_finance_service import YahooFinanceService
            cls._providers['yahoo_finance'] = YahooFinanceService
            cls._providers['yahoo'] = YahooFinanceService  # Alias
            DebugUtils.info("Registered Yahoo Finance provider")
        except ImportError as e:
            DebugUtils.warning(f"Could not register Yahoo Finance provider: {e}")
        
        try:
            from services.data_providers.providers.alpha_vantage_provider import AlphaVantageProvider
            cls._providers['alpha_vantage'] = AlphaVantageProvider
            cls._providers['av'] = AlphaVantageProvider  # Alias
            DebugUtils.info("Registered Alpha Vantage provider")
        except ImportError as e:
            DebugUtils.warning(f"Could not register Alpha Vantage provider: {e}")
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a new data provider.
        
        Args:
            name: Name of the provider
            provider_class: Provider class that implements StockDataProvider
        """
        if not issubclass(provider_class, StockDataProvider):
            raise ValueError(f"Provider class must inherit from StockDataProvider")
        
        cls._providers[name] = provider_class
        DebugUtils.info(f"Registered data provider: {name}")
    
    @classmethod
    def get_provider(cls, name: str, **kwargs) -> StockDataProvider:
        """
        Get a data provider instance.
        
        Args:
            name: Name of the provider
            **kwargs: Additional arguments for the provider
            
        Returns:
            StockDataProvider: Instance of the requested provider
            
        Raises:
            ValueError: If provider is not registered
        """
        # Ensure default providers are registered
        if not cls._providers:
            cls._register_default_providers()
        
        if name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(f"Provider '{name}' is not registered. Available providers: {available}")
        
        provider_class = cls._providers[name]
        provider = provider_class(**kwargs)
        
        DebugUtils.info(f"Created provider instance: {name}")
        return provider
    
    @classmethod
    def get_default_provider(cls, **kwargs) -> StockDataProvider:
        """
        Get the default data provider (Yahoo Finance).
        
        Args:
            **kwargs: Additional arguments for the provider
            
        Returns:
            StockDataProvider: Default provider instance
        """
        return cls.get_provider('yahoo_finance', **kwargs)
    
    @classmethod
    def list_providers(cls) -> list:
        """
        List all registered providers.
        
        Returns:
            list: List of provider names
        """
        # Ensure default providers are registered
        if not cls._providers:
            cls._register_default_providers()
        
        return list(cls._providers.keys())
    
    @classmethod
    def is_provider_registered(cls, name: str) -> bool:
        """
        Check if a provider is registered.
        
        Args:
            name: Name of the provider
            
        Returns:
            bool: True if provider is registered
        """
        # Ensure default providers are registered
        if not cls._providers:
            cls._register_default_providers()
        
        return name in cls._providers 