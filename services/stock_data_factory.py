from typing import Dict, Type
from .stock_data_provider import StockDataProvider
from .yahoo_finance.yahoo_finance_service import YahooFinanceService
from .providers.alpha_vantage_provider import AlphaVantageProvider

class StockDataFactory:
    """Factory class for creating and managing stock data providers."""
    
    _providers: Dict[str, Type[StockDataProvider]] = {}
    _default_provider: str = 'yahoo_finance'  # Default to Yahoo Finance
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[StockDataProvider]) -> None:
        """Register a new stock data provider.
        
        Args:
            name: Unique identifier for the provider
            provider_class: Provider class that implements StockDataProvider
        """
        cls._providers[name] = provider_class
    
    @classmethod
    def get_provider(cls, name: str, **kwargs) -> StockDataProvider:
        """Get an instance of a stock data provider.
        
        Args:
            name: Name of the provider to get
            **kwargs: Additional arguments to pass to the provider constructor
            
        Returns:
            An instance of the requested provider
            
        Raises:
            ValueError: If the provider is not registered
        """
        if name not in cls._providers:
            raise ValueError(f"Provider '{name}' is not registered")
        
        provider_class = cls._providers[name]
        return provider_class(**kwargs)
    
    @classmethod
    def get_default_provider(cls, **kwargs) -> StockDataProvider:
        """Get an instance of the default stock data provider.
        
        Args:
            **kwargs: Additional arguments to pass to the provider constructor
            
        Returns:
            An instance of the default provider
        """
        return cls.get_provider(cls._default_provider, **kwargs)
    
    @classmethod
    def set_default_provider(cls, name: str) -> None:
        """Set the default stock data provider.
        
        Args:
            name: Name of the provider to set as default
            
        Raises:
            ValueError: If the provider is not registered
        """
        if name not in cls._providers:
            raise ValueError(f"Provider '{name}' is not registered")
        cls._default_provider = name
    
    @classmethod
    def list_providers(cls) -> Dict[str, Type[StockDataProvider]]:
        """Get a list of all registered providers.
        
        Returns:
            Dictionary mapping provider names to their classes
        """
        return cls._providers.copy()

# Register the providers
StockDataFactory.register_provider('yahoo_finance', YahooFinanceService)
StockDataFactory.register_provider('alpha_vantage', AlphaVantageProvider) 