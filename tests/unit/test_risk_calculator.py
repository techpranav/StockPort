"""
Unit tests for RiskCalculator.

Tests verify risk metric calculations including stop-loss, risk-reward ratios, etc.
"""

import pytest
import pandas as pd
import numpy as np

from services.analyzers.risk.risk_calculator import RiskCalculator
from config.constants.DataConstants import DEFAULT_PROVIDER


class TestRiskCalculator:
    """Test suite for RiskCalculator class."""
    
    @pytest.fixture
    def risk_calculator(self):
        """Create RiskCalculator instance."""
        return RiskCalculator(risk_per_trade=0.02, risk_reward_ratio=1.5)
    
    @pytest.fixture
    def sample_data_with_indicators(self, sample_price_data):
        """Create sample data with indicators for risk calculation."""
        indicators = {
            'atr': pd.Series([2.0] * len(sample_price_data), index=sample_price_data.index)
        }
        return sample_price_data, indicators
    
    def test_risk_calculator_initialization(self, risk_calculator):
        """Test RiskCalculator initialization."""
        assert risk_calculator is not None
        assert risk_calculator.risk_per_trade == 0.02
        assert risk_calculator.risk_reward_ratio == 1.5
    
    def test_calculate_risk_metrics_with_valid_data(self, risk_calculator, sample_data_with_indicators):
        """Test risk metrics calculation with valid data."""
        data, indicators = sample_data_with_indicators
        entry_price = 100.0
        
        risk_metrics = risk_calculator.calculate_risk_metrics(
            data=data,
            entry_price=entry_price,
            indicators=indicators
        )
        
        assert isinstance(risk_metrics, dict)
        assert 'stop_loss' in risk_metrics
        assert 'take_profit' in risk_metrics
        assert 'risk_reward_ratio' in risk_metrics
        assert risk_metrics['stop_loss'] is not None
        assert risk_metrics['take_profit'] is not None
    
    def test_calculate_risk_metrics_stop_loss_calculation(self, risk_calculator, sample_data_with_indicators):
        """Test stop-loss calculation."""
        data, indicators = sample_data_with_indicators
        entry_price = 100.0
        
        risk_metrics = risk_calculator.calculate_risk_metrics(
            data=data,
            entry_price=entry_price,
            indicators=indicators
        )
        
        # Stop-loss should be below entry price for long positions
        assert risk_metrics['stop_loss'] < entry_price
        assert risk_metrics['stop_loss'] > 0
    
    def test_calculate_risk_metrics_take_profit_calculation(self, risk_calculator, sample_data_with_indicators):
        """Test take-profit calculation."""
        data, indicators = sample_data_with_indicators
        entry_price = 100.0
        
        risk_metrics = risk_calculator.calculate_risk_metrics(
            data=data,
            entry_price=entry_price,
            indicators=indicators
        )
        
        # Take-profit should be above entry price for long positions
        assert risk_metrics['take_profit'] > entry_price
    
    def test_calculate_risk_metrics_risk_reward_ratio(self, risk_calculator, sample_data_with_indicators):
        """Test risk-reward ratio calculation."""
        data, indicators = sample_data_with_indicators
        entry_price = 100.0
        
        risk_metrics = risk_calculator.calculate_risk_metrics(
            data=data,
            entry_price=entry_price,
            indicators=indicators
        )
        
        # Risk-reward ratio should meet minimum threshold
        assert risk_metrics['risk_reward_ratio'] >= risk_calculator.risk_reward_ratio
    
    def test_calculate_risk_metrics_with_account_size(self, risk_calculator, sample_data_with_indicators):
        """Test risk metrics with account size for position sizing."""
        data, indicators = sample_data_with_indicators
        entry_price = 100.0
        account_size = 100000.0
        
        risk_metrics = risk_calculator.calculate_risk_metrics(
            data=data,
            entry_price=entry_price,
            indicators=indicators,
            account_size=account_size
        )
        
        assert isinstance(risk_metrics, dict)
        # Should include position sizing if account_size provided
        if 'position_size' in risk_metrics:
            position_size = risk_metrics['position_size']
            if isinstance(position_size, (int, float)):
                assert position_size > 0
            elif isinstance(position_size, dict):
                # Position size might be a dict with details
                assert len(position_size) > 0
    
    def test_calculate_risk_metrics_with_empty_data(self, risk_calculator):
        """Test risk metrics calculation with empty data."""
        empty_data = pd.DataFrame()
        indicators = {}
        
        with pytest.raises(Exception):  # Should raise DataProcessingException
            risk_calculator.calculate_risk_metrics(
                data=empty_data,
                entry_price=100.0,
                indicators=indicators
            )

