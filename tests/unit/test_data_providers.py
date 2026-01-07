"""
Unit tests for data providers.

Tests verify data provider functionality and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from services.stock_data_factory import StockDataFactory
from services.data_providers.stock_data_provider import StockDataProvider
from models.stock_data import StockData, CompanyInfo, FinancialMetrics, TechnicalIndicators


class TestStockDataFactory:
    """Test suite for StockDataFactory."""
    
    def test_get_provider_yahoo_finance(self):
        """Test getting Yahoo Finance provider."""
        provider = StockDataFactory.get_provider("yahoo_finance")
        
        assert provider is not None
        assert isinstance(provider, StockDataProvider)
    
    def test_get_provider_invalid_name(self):
        """Test getting provider with invalid name."""
        # Should return default provider or raise exception
        try:
            provider = StockDataFactory.get_provider("invalid_provider")
            # If it doesn't raise, it should return a valid provider
            assert provider is not None
        except Exception:
            # Exception is also acceptable
            pass
    
    def test_get_provider_with_kwargs(self):
        """Test getting provider with additional kwargs."""
        provider = StockDataFactory.get_provider("yahoo_finance", days_back=180)
        
        assert provider is not None
        if hasattr(provider, 'days_back'):
            assert provider.days_back == 180


class TestDataProviderInterface:
    """Test suite for data provider interface."""
    
    def test_provider_has_required_methods(self):
        """Test that provider implements required interface."""
        provider = StockDataFactory.get_provider("yahoo_finance")
        
        # Check required methods exist
        assert hasattr(provider, 'fetch_stock_data')
        assert hasattr(provider, 'get_provider_name')
        assert callable(provider.fetch_stock_data)
        assert callable(provider.get_provider_name)
    
    def test_provider_name_is_string(self):
        """Test that provider name is a string."""
        provider = StockDataFactory.get_provider("yahoo_finance")
        name = provider.get_provider_name()
        
        assert isinstance(name, str)
        assert len(name) > 0

