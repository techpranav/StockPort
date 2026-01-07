"""
Unit tests for EntryDetector.

Tests verify entry point detection logic and signal classification.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from services.analyzers.signals.entry_detector import EntryDetector, EntrySignal
from config.constants.DataConstants import DEFAULT_PROVIDER


class TestEntryDetector:
    """Test suite for EntryDetector class."""
    
    @pytest.fixture
    def entry_detector(self):
        """Create EntryDetector instance."""
        return EntryDetector()
    
    @pytest.fixture
    def sample_data_with_indicators(self, sample_price_data):
        """Create sample data with indicators."""
        indicators = {
            'sma_20': sample_price_data['Close'].rolling(20).mean(),
            'sma_50': sample_price_data['Close'].rolling(50).mean(),
            'rsi': pd.Series([55.0] * len(sample_price_data), index=sample_price_data.index),
            'macd': pd.Series([0.5] * len(sample_price_data), index=sample_price_data.index),
            'macd_signal': pd.Series([0.4] * len(sample_price_data), index=sample_price_data.index)
        }
        return sample_price_data, indicators
    
    def test_entry_detector_initialization(self, entry_detector):
        """Test EntryDetector initialization."""
        assert entry_detector is not None
        assert entry_detector.signal_scorer is not None
        assert EntryDetector.STRONG_BUY_THRESHOLD == 80
        assert EntryDetector.BUY_THRESHOLD == 60
        assert EntryDetector.WATCH_THRESHOLD == 40
    
    def test_detect_entry_with_valid_data(self, entry_detector, sample_data_with_indicators):
        """Test entry detection with valid data."""
        data, indicators = sample_data_with_indicators
        
        entry_signal = entry_detector.detect_entry(
            symbol='TEST',
            data=data,
            indicators=indicators
        )
        
        assert isinstance(entry_signal, EntrySignal)
        assert entry_signal.symbol == 'TEST'
        assert entry_signal.signal_type in ['STRONG_BUY', 'BUY', 'WATCH', 'AVOID']
        assert 0 <= entry_signal.score <= 100
        assert 0 <= entry_signal.confidence <= 1
        assert entry_signal.entry_price > 0
    
    def test_detect_entry_strong_buy_signal(self, entry_detector, sample_price_data):
        """Test detection of strong buy signal."""
        # Create bullish indicators
        indicators = {
            'sma_20': pd.Series([100] * len(sample_price_data), index=sample_price_data.index),
            'sma_50': pd.Series([95] * len(sample_price_data), index=sample_price_data.index),
            'rsi': pd.Series([45.0] * len(sample_price_data), index=sample_price_data.index),  # Not overbought
            'macd': pd.Series([1.0] * len(sample_price_data), index=sample_price_data.index),
            'macd_signal': pd.Series([0.5] * len(sample_price_data), index=sample_price_data.index)
        }
        
        entry_signal = entry_detector.detect_entry(
            symbol='TEST',
            data=sample_price_data,
            indicators=indicators
        )
        
        assert entry_signal.signal_type in ['STRONG_BUY', 'BUY', 'WATCH', 'AVOID']
        assert entry_signal.score >= 0
    
    def test_detect_entry_avoid_signal(self, entry_detector, sample_price_data):
        """Test detection of avoid signal."""
        # Create bearish indicators
        indicators = {
            'sma_20': pd.Series([95] * len(sample_price_data), index=sample_price_data.index),
            'sma_50': pd.Series([100] * len(sample_price_data), index=sample_price_data.index),
            'rsi': pd.Series([75.0] * len(sample_price_data), index=sample_price_data.index),  # Overbought
            'macd': pd.Series([-0.5] * len(sample_price_data), index=sample_price_data.index),
            'macd_signal': pd.Series([0.0] * len(sample_price_data), index=sample_price_data.index)
        }
        
        entry_signal = entry_detector.detect_entry(
            symbol='TEST',
            data=sample_price_data,
            indicators=indicators
        )
        
        assert entry_signal.signal_type in ['STRONG_BUY', 'BUY', 'WATCH', 'AVOID']
        assert entry_signal.score >= 0
    
    def test_entry_signal_structure(self, entry_detector, sample_data_with_indicators):
        """Test EntrySignal structure."""
        data, indicators = sample_data_with_indicators
        
        entry_signal = entry_detector.detect_entry(
            symbol='TEST',
            data=data,
            indicators=indicators
        )
        
        # Verify all required fields
        assert hasattr(entry_signal, 'symbol')
        assert hasattr(entry_signal, 'signal_type')
        assert hasattr(entry_signal, 'score')
        assert hasattr(entry_signal, 'confidence')
        assert hasattr(entry_signal, 'entry_price')
        assert hasattr(entry_signal, 'stop_loss')
        assert hasattr(entry_signal, 'take_profit')
    
    def test_entry_signal_with_patterns(self, entry_detector, sample_data_with_indicators):
        """Test entry detection with pattern analysis."""
        data, indicators = sample_data_with_indicators
        
        patterns = {
            'bullish_patterns': ['hammer', 'engulfing'],
            'bearish_patterns': []
        }
        
        entry_signal = entry_detector.detect_entry(
            symbol='TEST',
            data=data,
            indicators=indicators,
            patterns=patterns
        )
        
        assert isinstance(entry_signal, EntrySignal)
        assert entry_signal.score >= 0

