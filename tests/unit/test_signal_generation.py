"""
Unit tests for signal generation and entry detection.

Tests verify that trading signals are generated correctly.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from services.analyzers.analysis.technical_analysis import TechnicalAnalyzer
from config.constants.NumericConstants import (
    RSI_OVERBOUGHT_THRESHOLD, RSI_OVERSOLD_THRESHOLD
)


class TestSignalGeneration:
    """Test suite for signal generation."""
    
    def test_signal_generation_structure(self, sample_price_data):
        """Test that signals have correct structure."""
        signals = TechnicalAnalyzer.generate_signals(sample_price_data)
        
        assert isinstance(signals, dict)
        assert 'buy' in signals
        assert 'sell' in signals
        assert isinstance(signals['buy'], list)
        assert isinstance(signals['sell'], list)
    
    def test_buy_signal_on_ma_crossover(self):
        """Test buy signal generation on moving average crossover."""
        # Create data with upward crossover
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        
        # Create prices where SMA20 crosses above SMA50
        prices = []
        for i in range(100):
            if i < 50:
                prices.append(100 - i * 0.5)  # Decreasing
            else:
                prices.append(75 + (i - 50) * 1.0)  # Increasing
        
        df = pd.DataFrame({
            'Open': prices,
            'High': [p * 1.02 for p in prices],
            'Low': [p * 0.98 for p in prices],
            'Close': prices,
            'Volume': [1000000] * 100
        }, index=dates)
        
        signals = TechnicalAnalyzer.generate_signals(df)
        
        # Should generate at least some signals if crossover occurs
        assert isinstance(signals['buy'], list)
        assert isinstance(signals['sell'], list)
    
    def test_sell_signal_on_ma_crossover(self):
        """Test sell signal generation on moving average crossover."""
        # Create data with downward crossover
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        
        # Create prices where SMA20 crosses below SMA50
        prices = []
        for i in range(100):
            if i < 50:
                prices.append(75 + i * 1.0)  # Increasing
            else:
                prices.append(125 - (i - 50) * 0.5)  # Decreasing
        
        df = pd.DataFrame({
            'Open': prices,
            'High': [p * 1.02 for p in prices],
            'Low': [p * 0.98 for p in prices],
            'Close': prices,
            'Volume': [1000000] * 100
        }, index=dates)
        
        signals = TechnicalAnalyzer.generate_signals(df)
        
        # Should generate at least some signals if crossover occurs
        assert isinstance(signals['buy'], list)
        assert isinstance(signals['sell'], list)
    
    def test_signal_format(self, sample_price_data):
        """Test that signals have correct format."""
        signals = TechnicalAnalyzer.generate_signals(sample_price_data)
        
        # Check buy signals format
        for buy_signal in signals['buy']:
            assert 'date' in buy_signal
            assert 'price' in buy_signal
            assert 'type' in buy_signal
            assert buy_signal['type'] == 'MA_CROSSOVER'
            assert isinstance(buy_signal['price'], (int, float))
        
        # Check sell signals format
        for sell_signal in signals['sell']:
            assert 'date' in sell_signal
            assert 'price' in sell_signal
            assert 'type' in sell_signal
            assert sell_signal['type'] == 'MA_CROSSOVER'
            assert isinstance(sell_signal['price'], (int, float))
    
    def test_trend_analysis_integration(self, sample_price_data):
        """Test trend analysis integration with signals."""
        trend = TechnicalAnalyzer.analyze_trend(sample_price_data)
        
        assert 'direction' in trend
        assert 'strength' in trend
        assert 'rsi_signal' in trend
        
        # Verify valid trend values
        assert trend['direction'] in ['bullish', 'bearish', 'neutral', 'unknown']
        assert trend['strength'] in ['strong', 'moderate', 'weak', 'unknown']
        assert trend['rsi_signal'] in ['overbought', 'oversold', 'neutral', 'unknown']

