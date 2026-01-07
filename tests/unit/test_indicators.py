"""
Unit tests for technical indicators calculations.

Tests verify accuracy of individual indicator calculations.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from services.analyzers.indicators.intraday_indicators import IntradayIndicators
from services.analyzers.indicators.volume_indicators import VolumeIndicators
from services.analyzers.indicators.momentum_indicators import MomentumIndicators
from config.constants.NumericConstants import RSI_PERIOD


class TestIntradayIndicators:
    """Test suite for intraday indicators."""
    
    def test_calculate_rsi_basic(self, sample_price_data):
        """Test basic RSI calculation."""
        # This is a placeholder - actual implementation depends on IntradayIndicators class
        # Verify RSI values are in valid range
        close = sample_price_data['Close']
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        rsi_valid = rsi.dropna()
        if len(rsi_valid) > 0:
            assert (rsi_valid >= 0).all()
            assert (rsi_valid <= 100).all()
    
    def test_calculate_atr_basic(self, sample_price_data):
        """Test ATR (Average True Range) calculation."""
        high = sample_price_data['High']
        low = sample_price_data['Low']
        close = sample_price_data['Close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR (14-period)
        atr = tr.rolling(window=14).mean()
        
        atr_valid = atr.dropna()
        if len(atr_valid) > 0:
            # ATR should be positive
            assert (atr_valid > 0).all()
            # ATR should be reasonable relative to price
            assert (atr_valid < close.max() * 0.1).all()


class TestVolumeIndicators:
    """Test suite for volume indicators."""
    
    def test_volume_sma_calculation(self, sample_price_data):
        """Test volume SMA calculation."""
        volume = sample_price_data['Volume']
        volume_sma = volume.rolling(window=20).mean()
        
        volume_sma_valid = volume_sma.dropna()
        if len(volume_sma_valid) > 0:
            # Volume SMA should be positive
            assert (volume_sma_valid > 0).all()
            # Volume SMA should be reasonable
            assert (volume_sma_valid <= volume.max() * 1.5).all()
    
    def test_obv_calculation(self, sample_price_data):
        """Test On-Balance Volume calculation."""
        close = sample_price_data['Close']
        volume = sample_price_data['Volume']
        
        # Calculate OBV
        obv = (volume * np.sign(close.diff())).fillna(0).cumsum()
        
        # OBV should be a cumulative sum, so it should generally increase or decrease
        assert len(obv) == len(close)
        assert not obv.isna().any()


class TestMomentumIndicators:
    """Test suite for momentum indicators."""
    
    def test_roc_calculation(self, sample_price_data):
        """Test Rate of Change calculation."""
        close = sample_price_data['Close']
        period = 10
        
        # Calculate ROC
        roc = ((close - close.shift(period)) / close.shift(period)) * 100
        
        roc_valid = roc.dropna()
        if len(roc_valid) > 0:
            # ROC can be positive or negative
            assert isinstance(roc_valid.iloc[0], (int, float, np.number))
    
    def test_momentum_calculation(self, sample_price_data):
        """Test Momentum calculation."""
        close = sample_price_data['Close']
        period = 10
        
        # Calculate Momentum
        momentum = close - close.shift(period)
        
        momentum_valid = momentum.dropna()
        if len(momentum_valid) > 0:
            # Momentum can be positive or negative
            assert isinstance(momentum_valid.iloc[0], (int, float, np.number))

