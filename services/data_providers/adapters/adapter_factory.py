"""
Data Adapter Factory

Factory for creating and managing data adapters for different providers.
"""

from typing import Dict, Optional
from services.data_providers.adapters.data_adapter import DataAdapter
from services.data_providers.adapters.yahoo_finance_adapter import YahooFinanceAdapter
from services.data_providers.adapters.alpha_vantage_adapter import AlphaVantageAdapter
from services.data_providers.adapters.nse_adapter import NSEAdapter
from services.data_providers.adapters.bse_adapter import BSEAdapter
from utils.debug_utils import DebugUtils


class AdapterFactory:
    """
    Factory for creating data adapters.
    
    Manages registration and instantiation of adapters for different
    data providers.
    """
    
    _adapters: Dict[str, type] = {}
    _instances: Dict[str, DataAdapter] = {}
    
    @classmethod
    def _register_default_adapters(cls):
        """Register default adapters."""
        try:
            cls._adapters['yahoo_finance'] = YahooFinanceAdapter
            cls._adapters['yahoo'] = YahooFinanceAdapter  # Alias
            cls._adapters['yfinance'] = YahooFinanceAdapter  # Alias
            DebugUtils.info("Registered Yahoo Finance adapter")
        except Exception as e:
            DebugUtils.warning(f"Could not register Yahoo Finance adapter: {e}")
        
        try:
            cls._adapters['alpha_vantage'] = AlphaVantageAdapter
            cls._adapters['av'] = AlphaVantageAdapter  # Alias
            cls._adapters['alphavantage'] = AlphaVantageAdapter  # Alias
            DebugUtils.info("Registered Alpha Vantage adapter")
        except Exception as e:
            DebugUtils.warning(f"Could not register Alpha Vantage adapter: {e}")
        
        try:
            cls._adapters['nse'] = NSEAdapter
            cls._adapters['nse_india'] = NSEAdapter  # Alias
            DebugUtils.info("Registered NSE adapter")
        except Exception as e:
            DebugUtils.warning(f"Could not register NSE adapter: {e}")
        
        try:
            cls._adapters['bse'] = BSEAdapter
            cls._adapters['bse_india'] = BSEAdapter  # Alias
            DebugUtils.info("Registered BSE adapter")
        except Exception as e:
            DebugUtils.warning(f"Could not register BSE adapter: {e}")
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: type) -> None:
        """
        Register a new data adapter.
        
        Args:
            name: Name of the adapter/provider
            adapter_class: Adapter class that inherits from DataAdapter
            
        Raises:
            ValueError: If adapter_class doesn't inherit from DataAdapter
        """
        if not issubclass(adapter_class, DataAdapter):
            raise ValueError(
                f"Adapter class must inherit from DataAdapter, "
                f"got {adapter_class.__name__}"
            )
        
        cls._adapters[name] = adapter_class
        DebugUtils.info(f"Registered data adapter: {name}")
    
    @classmethod
    def get_adapter(cls, provider_name: str) -> DataAdapter:
        """
        Get a data adapter instance for the specified provider.
        
        Uses singleton pattern - returns same instance for same provider.
        
        Args:
            provider_name: Name of the provider (e.g., 'yahoo_finance')
            
        Returns:
            DataAdapter instance for the provider
            
        Raises:
            ValueError: If provider is not registered
        """
        # Ensure default adapters are registered
        if not cls._adapters:
            cls._register_default_adapters()
        
        # Normalize provider name
        provider_name = provider_name.lower().strip()
        
        # Check if adapter is registered
        if provider_name not in cls._adapters:
            available = ', '.join(cls._adapters.keys())
            raise ValueError(
                f"Adapter for provider '{provider_name}' is not registered. "
                f"Available providers: {available}"
            )
        
        # Return singleton instance if exists
        if provider_name in cls._instances:
            return cls._instances[provider_name]
        
        # Create new instance
        adapter_class = cls._adapters[provider_name]
        adapter = adapter_class()
        cls._instances[provider_name] = adapter
        
        DebugUtils.debug(f"Created adapter instance for: {provider_name}")
        return adapter
    
    @classmethod
    def get_default_adapter(cls) -> DataAdapter:
        """
        Get the default data adapter (Yahoo Finance).
        
        Returns:
            Default DataAdapter instance
        """
        return cls.get_adapter('yahoo_finance')
    
    @classmethod
    def list_adapters(cls) -> list:
        """
        List all registered adapters.
        
        Returns:
            List of adapter names
        """
        # Ensure default adapters are registered
        if not cls._adapters:
            cls._register_default_adapters()
        
        return list(cls._adapters.keys())
    
    @classmethod
    def is_adapter_registered(cls, provider_name: str) -> bool:
        """
        Check if an adapter is registered for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            True if adapter is registered, False otherwise
        """
        # Ensure default adapters are registered
        if not cls._adapters:
            cls._register_default_adapters()
        
        provider_name = provider_name.lower().strip()
        return provider_name in cls._adapters
    
    @classmethod
    def clear_instances(cls):
        """
        Clear all adapter instances (useful for testing).
        """
        cls._instances.clear()
        DebugUtils.debug("Cleared all adapter instances")

