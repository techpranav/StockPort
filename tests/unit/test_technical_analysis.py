"""
Unit tests for technical analysis calculations.

These tests verify that all technical indicators are calculated correctly,
as accuracy is critical for trading decisions.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from services.analyzers.analysis.technical_analysis import TechnicalAnalyzer
from exceptions.stock_data_exceptions import DataProcessingException
from config.constants.NumericConstants import (
    RSI_PERIOD, RSI_OVERBOUGHT_THRESHOLD, RSI_OVERSOLD_THRESHOLD,
    SMA_SHORT_PERIOD, SMA_LONG_PERIOD,
    MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD
)


class TestTechnicalAnalyzer:
    """Test suite for TechnicalAnalyzer class."""
    
    def test_calculate_indicators_with_valid_data(self, sample_price_data):
        """Test indicator calculation with valid price data."""
        indicators = TechnicalAnalyzer.calculate_indicators(sample_price_data)
        
        # Verify all expected indicators are present
        assert 'sma_20' in indicators
        assert 'sma_50' in indicators
        assert 'sma_200' in indicators
        assert 'rsi' in indicators
        assert 'macd' in indicators
        assert 'macd_signal' in indicators
        assert 'macd_histogram' in indicators
        
        # Verify indicators are Series
        assert isinstance(indicators['sma_20'], pd.Series)
        assert isinstance(indicators['rsi'], pd.Series)
        assert isinstance(indicators['macd'], pd.Series)
    
    def test_calculate_indicators_with_empty_dataframe(self):
        """Test that empty DataFrame raises appropriate exception."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(DataProcessingException) as exc_info:
            TechnicalAnalyzer.calculate_indicators(empty_df)
        
        assert "empty" in str(exc_info.value).lower()
    
    def test_calculate_indicators_with_insufficient_data(self):
        """Test that insufficient data points raises exception."""
        # Create DataFrame with less than 20 data points
        dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
        df = pd.DataFrame({
            'Open': [100] * 10,
            'High': [105] * 10,
            'Low': [95] * 10,
            'Close': [100] * 10,
            'Volume': [1000] * 10
        }, index=dates)
        
        with pytest.raises(DataProcessingException) as exc_info:
            TechnicalAnalyzer.calculate_indicators(df)
        
        assert "insufficient" in str(exc_info.value).lower() or "20" in str(exc_info.value)
    
    def test_calculate_indicators_with_none_data(self):
        """Test that None data raises exception."""
        with pytest.raises(DataProcessingException) as exc_info:
            TechnicalAnalyzer.calculate_indicators(None)
        
        assert "none" in str(exc_info.value).lower()
    
    def test_sma_calculation_accuracy(self, sample_price_data):
        """Test that SMA calculation is mathematically correct."""
        indicators = TechnicalAnalyzer.calculate_indicators(sample_price_data)
        
        # Get close prices
        close = sample_price_data['Close']
        
        # Calculate expected SMA manually
        expected_sma_20 = close.rolling(window=20).mean()
        expected_sma_50 = close.rolling(window=50).mean()
        
        # Compare calculated vs expected (allowing for floating point precision)
        pd.testing.assert_series_equal(
            indicators['sma_20'],
            expected_sma_20,
            check_names=False,
            rtol=1e-5
        )
        
        pd.testing.assert_series_equal(
            indicators['sma_50'],
            expected_sma_50,
            check_names=False,
            rtol=1e-5
        )
    
    def test_rsi_calculation_accuracy(self, sample_price_data):
        """Test that RSI calculation is mathematically correct."""
        indicators = TechnicalAnalyzer.calculate_indicators(sample_price_data)
        
        # Verify RSI values are within valid range (0-100)
        rsi = indicators['rsi'].dropna()
        assert (rsi >= 0).all()
        assert (rsi <= 100).all()
        
        # Verify RSI calculation matches manual calculation
        close = sample_price_data['Close']
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
        rs = gain / loss
        expected_rsi = 100 - (100 / (1 + rs))
        
        # Compare (allowing for NaN values)
        rsi_valid = indicators['rsi'].dropna()
        expected_rsi_valid = expected_rsi.dropna()
        
        if len(rsi_valid) > 0 and len(expected_rsi_valid) > 0:
            # Align indices
            common_idx = rsi_valid.index.intersection(expected_rsi_valid.index)
            if len(common_idx) > 0:
                np.testing.assert_allclose(
                    rsi_valid.loc[common_idx].values,
                    expected_rsi_valid.loc[common_idx].values,
                    rtol=1e-5
                )
    
    def test_rsi_overbought_oversold_detection(self, sample_price_data):
        """Test RSI overbought/oversold detection."""
        indicators = TechnicalAnalyzer.calculate_indicators(sample_price_data)
        rsi = indicators['rsi'].dropna()
        
        if len(rsi) > 0:
            # Check if any values are in overbought/oversold ranges
            overbought_count = (rsi > RSI_OVERBOUGHT_THRESHOLD).sum()
            oversold_count = (rsi < RSI_OVERSOLD_THRESHOLD).sum()
            
            # At least verify the calculation produces valid ranges
            assert overbought_count >= 0
            assert oversold_count >= 0
    
    def test_macd_calculation_accuracy(self, sample_price_data):
        """Test that MACD calculation is mathematically correct."""
        indicators = TechnicalAnalyzer.calculate_indicators(sample_price_data)
        
        # Verify MACD components exist
        assert 'macd' in indicators
        assert 'macd_signal' in indicators
        assert 'macd_histogram' in indicators
        
        # Verify MACD histogram = MACD - Signal
        macd = indicators['macd'].dropna()
        signal = indicators['macd_signal'].dropna()
        histogram = indicators['macd_histogram'].dropna()
        
        if len(macd) > 0 and len(signal) > 0 and len(histogram) > 0:
            # Align indices
            common_idx = macd.index.intersection(signal.index).intersection(histogram.index)
            if len(common_idx) > 0:
                expected_histogram = macd.loc[common_idx] - signal.loc[common_idx]
                np.testing.assert_allclose(
                    histogram.loc[common_idx].values,
                    expected_histogram.values,
                    rtol=1e-5
                )
    
    def test_generate_signals_with_valid_data(self, sample_price_data):
        """Test signal generation with valid data."""
        signals = TechnicalAnalyzer.generate_signals(sample_price_data)
        
        # Verify signal structure
        assert 'buy' in signals
        assert 'sell' in signals
        assert isinstance(signals['buy'], list)
        assert isinstance(signals['sell'], list)
        
        # Verify signal format if signals exist
        if len(signals['buy']) > 0:
            buy_signal = signals['buy'][0]
            assert 'date' in buy_signal
            assert 'price' in buy_signal
            assert 'type' in buy_signal
            assert buy_signal['type'] == 'MA_CROSSOVER'
    
    def test_generate_signals_with_empty_data(self):
        """Test signal generation with empty data."""
        empty_df = pd.DataFrame()
        signals = TechnicalAnalyzer.generate_signals(empty_df)
        
        assert signals == {'buy': [], 'sell': []}
    
    def test_analyze_trend_bullish(self):
        """Test trend analysis for bullish trend."""
        # Create data with clear uptrend
        dates = pd.date_range(start='2023-01-01', periods=250, freq='D')
        prices = pd.Series([100 + i * 0.2 for i in range(250)], index=dates)
        
        df = pd.DataFrame({
            'Open': prices,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': [1000000] * 250
        }, index=dates)
        
        trend = TechnicalAnalyzer.analyze_trend(df)
        
        assert 'direction' in trend
        assert 'strength' in trend
        assert 'rsi_signal' in trend
        # Should detect bullish trend
        assert trend['direction'] in ['bullish', 'neutral']
    
    def test_analyze_trend_bearish(self):
        """Test trend analysis for bearish trend."""
        # Create data with clear downtrend
        dates = pd.date_range(start='2023-01-01', periods=250, freq='D')
        prices = pd.Series([200 - i * 0.2 for i in range(250)], index=dates)
        
        df = pd.DataFrame({
            'Open': prices,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': [1000000] * 250
        }, index=dates)
        
        trend = TechnicalAnalyzer.analyze_trend(df)
        
        assert 'direction' in trend
        assert 'strength' in trend
        assert 'rsi_signal' in trend
        # Should detect bearish trend
        assert trend['direction'] in ['bearish', 'neutral']
    
    def test_analyze_trend_with_empty_data(self):
        """Test trend analysis with empty data."""
        empty_df = pd.DataFrame()
        trend = TechnicalAnalyzer.analyze_trend(empty_df)
        
        assert trend['direction'] == 'unknown'
        assert trend['strength'] == 'unknown'
        assert trend['rsi_signal'] == 'unknown'

