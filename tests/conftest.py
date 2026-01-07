"""
Pytest configuration and fixtures for test suite.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.stock_data import StockData, CompanyInfo, FinancialMetrics, TechnicalIndicators
from services.stock_service import StockService
from services.analyzers.analysis.technical_analysis import TechnicalAnalyzer


@pytest.fixture
def sample_price_data():
    """Generate sample OHLCV price data for testing."""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    # Generate realistic price data with trend
    np.random.seed(42)
    base_price = 100.0
    prices = []
    for i in range(100):
        # Add trend and random walk
        trend = i * 0.1
        noise = np.random.normal(0, 2)
        price = base_price + trend + noise
        prices.append(price)
    
    df = pd.DataFrame({
        'Open': prices,
        'High': [p * 1.02 for p in prices],
        'Low': [p * 0.98 for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 5000000, 100),
        'Adj Close': prices
    }, index=dates)
    
    return df


@pytest.fixture
def sample_stock_data(sample_price_data):
    """Create a sample StockData object for testing."""
    from models.stock_data import TechnicalSignals, FinancialStatements, NewsItem
    
    company_info = CompanyInfo(
        symbol="TEST",
        name="Test Company",
        sector="Technology",
        industry="Software",
        market_cap=1000000000.0
    )
    
    financial_metrics = FinancialMetrics(
        revenue=100000000.0,
        net_income=10000000.0,
        eps=2.5,
        pe_ratio=25.0
    )
    
    technical_indicators = TechnicalIndicators(
        current_price=sample_price_data['Close'].iloc[-1],
        sma_20=sample_price_data['Close'].rolling(20).mean().iloc[-1],
        sma_50=sample_price_data['Close'].rolling(50).mean().iloc[-1]
    )
    
    technical_signals = TechnicalSignals(
        trend="bullish",
        momentum="neutral",
        volatility="normal",
        volume="normal"
    )
    
    financial_statements = FinancialStatements()
    
    stock_data = StockData(
        symbol="TEST",
        company_info=company_info,
        info={},
        metrics=financial_metrics,
        technical_analysis=technical_indicators,
        technical_signals=technical_signals,
        financials=financial_statements,
        news=[],
        raw_data={'history': sample_price_data}
    )
    
    return stock_data


@pytest.fixture
def mock_stock_service():
    """Create a mock StockService for testing."""
    service = Mock(spec=StockService)
    return service


@pytest.fixture
def mock_webhook_payload():
    """Sample webhook payload for testing."""
    return {
        'event': 'payment.captured',
        'payload': {
            'payment': {
                'id': 'pay_test123',
                'amount': 10000,
                'currency': 'USD',
                'status': 'captured'
            }
        }
    }


@pytest.fixture
def sample_indicators_data():
    """Sample technical indicators data for testing."""
    dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
    prices = pd.Series([100 + i * 0.5 + np.random.normal(0, 1) for i in range(50)], index=dates)
    
    return {
        'close': prices,
        'sma_20': prices.rolling(20).mean(),
        'sma_50': prices.rolling(50).mean(),
        'rsi': pd.Series([50 + np.random.normal(0, 10) for _ in range(50)], index=dates),
        'macd': pd.Series([0.5 + np.random.normal(0, 0.1) for _ in range(50)], index=dates),
        'macd_signal': pd.Series([0.4 + np.random.normal(0, 0.1) for _ in range(50)], index=dates)
    }

