"""
Unit tests for StockService.

Tests verify that stock data fetching and service methods work correctly.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from services.stock_service import StockService
from models.stock_data import StockData, CompanyInfo, FinancialMetrics
from exceptions.stock_data_exceptions import DataFetchException
import pandas as pd


class TestStockService:
    """Test suite for StockService class."""
    
    def test_stock_service_initialization(self):
        """Test StockService initialization with default parameters."""
        service = StockService()
        
        assert service.days_back == 365
        # Provider name can be "yahoo_finance" or "Yahoo Finance" depending on implementation
        provider_name = service.get_provider_name()
        assert provider_name in ["yahoo_finance", "Yahoo Finance", "yahoo"]
    
    def test_stock_service_initialization_custom_days(self):
        """Test StockService initialization with custom days_back."""
        service = StockService(days_back=180)
        
        assert service.days_back == 180
    
    def test_fetch_stock_data_success(self, sample_stock_data):
        """Test successful stock data fetching."""
        with patch('services.stock_service.StockDataFactory') as mock_factory:
            mock_provider = Mock()
            mock_provider.fetch_stock_data.return_value = sample_stock_data
            mock_provider.get_provider_name.return_value = "yahoo_finance"
            mock_factory.get_provider.return_value = mock_provider
            
            service = StockService()
            result = service.fetch_stock_data("TEST")
            
            assert result.symbol == "TEST"
            assert result.company_info.name == "Test Company"
            mock_provider.fetch_stock_data.assert_called_once_with("TEST")
    
    def test_fetch_stock_data_failure(self):
        """Test stock data fetching failure handling."""
        with patch('services.stock_service.StockDataFactory') as mock_factory:
            mock_provider = Mock()
            mock_provider.fetch_stock_data.side_effect = Exception("API Error")
            mock_provider.get_provider_name.return_value = "yahoo_finance"
            mock_factory.get_provider.return_value = mock_provider
            
            service = StockService()
            
            with pytest.raises(Exception) as exc_info:
                service.fetch_stock_data("INVALID")
            
            assert "API Error" in str(exc_info.value)
    
    def test_get_provider_name(self):
        """Test getting provider name."""
        with patch('services.stock_service.StockDataFactory') as mock_factory:
            mock_provider = Mock()
            mock_provider.get_provider_name.return_value = "test_provider"
            mock_factory.get_provider.return_value = mock_provider
            
            service = StockService(provider_name="test_provider")
            assert service.get_provider_name() == "test_provider"
    
    def test_set_days_back(self):
        """Test updating days_back setting."""
        with patch('services.stock_service.StockDataFactory') as mock_factory:
            mock_provider = Mock()
            mock_provider.get_provider_name.return_value = "yahoo_finance"
            mock_provider.days_back = 365
            mock_factory.get_provider.return_value = mock_provider
            
            service = StockService(days_back=365)
            service.set_days_back(180)
            
            assert service.days_back == 180
            assert mock_provider.days_back == 180
    
    def test_get_days_back(self):
        """Test getting days_back setting."""
        service = StockService(days_back=180)
        assert service.get_days_back() == 180

