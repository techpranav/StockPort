"""
Unit tests for SignalScorer.

Tests verify signal scoring logic and score calculation accuracy.
"""

import pytest
import pandas as pd
import numpy as np

from services.analyzers.signals.signal_scorer import SignalScorer


class TestSignalScorer:
    """Test suite for SignalScorer class."""
    
    @pytest.fixture
    def signal_scorer(self):
        """Create SignalScorer instance."""
        return SignalScorer()
    
    @pytest.fixture
    def sample_indicators(self):
        """Create sample indicators for scoring."""
        dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
        return {
            'sma_20': pd.Series([100] * 50, index=dates),
            'sma_50': pd.Series([95] * 50, index=dates),
            'rsi': pd.Series([55.0] * 50, index=dates),
            'macd': pd.Series([0.5] * 50, index=dates),
            'macd_signal': pd.Series([0.4] * 50, index=dates)
        }
    
    def test_signal_scorer_initialization(self, signal_scorer):
        """Test SignalScorer initialization."""
        assert signal_scorer is not None
    
    def test_calculate_entry_score_with_valid_indicators(self, signal_scorer, sample_indicators):
        """Test entry score calculation with valid indicators."""
        score_result = signal_scorer.calculate_entry_score(
            indicators=sample_indicators,
            patterns=None,
            timeframe_analysis=None,
            risk_metrics=None
        )
        
        # SignalScorer returns a dict with total_score and breakdown
        assert isinstance(score_result, dict)
        assert 'total_score' in score_result
        score = score_result['total_score']
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100
    
    def test_calculate_entry_score_bullish_indicators(self, signal_scorer):
        """Test score calculation with bullish indicators."""
        dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
        bullish_indicators = {
            'sma_20': pd.Series([105] * 50, index=dates),  # Above SMA50
            'sma_50': pd.Series([100] * 50, index=dates),
            'rsi': pd.Series([45.0] * 50, index=dates),  # Not overbought
            'macd': pd.Series([1.0] * 50, index=dates),  # Positive MACD
            'macd_signal': pd.Series([0.5] * 50, index=dates)
        }
        
        score_result = signal_scorer.calculate_entry_score(
            indicators=bullish_indicators,
            patterns=None,
            timeframe_analysis=None,
            risk_metrics=None
        )
        
        assert isinstance(score_result, dict)
        score = score_result.get('total_score', 0)
        assert score >= 0
        assert score <= 100
    
    def test_calculate_entry_score_bearish_indicators(self, signal_scorer):
        """Test score calculation with bearish indicators."""
        dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
        bearish_indicators = {
            'sma_20': pd.Series([95] * 50, index=dates),  # Below SMA50
            'sma_50': pd.Series([100] * 50, index=dates),
            'rsi': pd.Series([75.0] * 50, index=dates),  # Overbought
            'macd': pd.Series([-0.5] * 50, index=dates),  # Negative MACD
            'macd_signal': pd.Series([0.0] * 50, index=dates)
        }
        
        score_result = signal_scorer.calculate_entry_score(
            indicators=bearish_indicators,
            patterns=None,
            timeframe_analysis=None,
            risk_metrics=None
        )
        
        assert isinstance(score_result, dict)
        score = score_result.get('total_score', 0)
        assert score >= 0
        assert score <= 100
    
    def test_calculate_entry_score_with_patterns(self, signal_scorer, sample_indicators):
        """Test score calculation with pattern analysis."""
        patterns = {
            'bullish_patterns': ['hammer', 'engulfing'],
            'bearish_patterns': []
        }
        
        score_result = signal_scorer.calculate_entry_score(
            indicators=sample_indicators,
            patterns=patterns,
            timeframe_analysis=None,
            risk_metrics=None
        )
        
        assert isinstance(score_result, dict)
        score = score_result.get('total_score', 0)
        assert 0 <= score <= 100
    
    def test_calculate_entry_score_with_timeframe_analysis(self, signal_scorer, sample_indicators):
        """Test score calculation with timeframe analysis."""
        timeframe_analysis = {
            'trend_alignment': 'bullish',
            'timeframe_consensus': 0.8
        }
        
        score_result = signal_scorer.calculate_entry_score(
            indicators=sample_indicators,
            patterns=None,
            timeframe_analysis=timeframe_analysis,
            risk_metrics=None
        )
        
        assert isinstance(score_result, dict)
        score = score_result.get('total_score', 0)
        assert 0 <= score <= 100
    
    def test_calculate_entry_score_with_risk_metrics(self, signal_scorer, sample_indicators):
        """Test score calculation with risk metrics."""
        risk_metrics = {
            'risk_reward_ratio': 2.0,
            'max_drawdown': 0.05
        }
        
        score_result = signal_scorer.calculate_entry_score(
            indicators=sample_indicators,
            patterns=None,
            timeframe_analysis=None,
            risk_metrics=risk_metrics
        )
        
        assert isinstance(score_result, dict)
        score = score_result.get('total_score', 0)
        assert 0 <= score <= 100
    
    def test_calculate_entry_score_all_factors(self, signal_scorer, sample_indicators):
        """Test score calculation with all factors."""
        patterns = {'bullish_patterns': ['hammer'], 'bearish_patterns': []}
        timeframe_analysis = {'trend_alignment': 'bullish', 'timeframe_consensus': 0.8}
        risk_metrics = {'risk_reward_ratio': 2.0, 'max_drawdown': 0.05}
        
        score_result = signal_scorer.calculate_entry_score(
            indicators=sample_indicators,
            patterns=patterns,
            timeframe_analysis=timeframe_analysis,
            risk_metrics=risk_metrics
        )
        
        assert isinstance(score_result, dict)
        score = score_result.get('total_score', 0)
        assert 0 <= score <= 100

