"""
Pattern Analyzer Module

This module provides comprehensive pattern analysis including multi-pattern
detection, pattern confirmation, and reliability scoring.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from .candlestick_patterns import CandlestickPatternDetector, PatternDetection as CandlestickPatternDetection
from .chart_patterns import ChartPatternDetector, ChartPattern
from config.constants.DataConstants import DEFAULT_PROVIDER


class PatternAnalyzer:
    """
    Comprehensive pattern analyzer that combines candlestick and chart patterns.
    
    Features:
    - Multi-pattern detection on same chart
    - Pattern confirmation signals
    - Pattern reliability scoring
    - Historical pattern performance tracking
    """
    
    def __init__(self):
        """Initialize pattern analyzer."""
        self.candlestick_detector = CandlestickPatternDetector()
        self.chart_detector = ChartPatternDetector()
    
    def analyze_patterns(
        self,
        data: pd.DataFrame,
        provider_name: str = DEFAULT_PROVIDER
    ) -> Dict[str, Any]:
        """
        Analyze all patterns in the data.
        
        Args:
            data: DataFrame with OHLCV data (will be normalized)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Dictionary containing:
            - candlestick_patterns: List of candlestick patterns
            - chart_patterns: List of chart patterns
            - combined_score: Overall pattern score (0-100)
            - bullish_signals: Count of bullish patterns
            - bearish_signals: Count of bearish patterns
        """
        try:
            if data.empty:
                return {
                    'candlestick_patterns': [],
                    'chart_patterns': [],
                    'combined_score': 0,
                    'bullish_signals': 0,
                    'bearish_signals': 0
                }
            
            # Detect candlestick patterns
            candlestick_patterns = self.candlestick_detector.detect_all_patterns(data, provider_name)
            
            # Detect chart patterns
            chart_patterns = self.chart_detector.detect_all_patterns(data, provider_name)
            
            # Calculate combined score
            combined_score = self._calculate_combined_score(
                candlestick_patterns,
                chart_patterns
            )
            
            # Count signals
            bullish_signals = sum(
                1 for p in candlestick_patterns + chart_patterns
                if p.is_bullish is True
            )
            bearish_signals = sum(
                1 for p in candlestick_patterns + chart_patterns
                if p.is_bullish is False
            )
            
            return {
                'candlestick_patterns': [
                    {
                        'name': p.pattern_name,
                        'type': p.pattern_type,
                        'strength': p.strength,
                        'reliability': p.reliability,
                        'is_bullish': p.is_bullish,
                        'detected_at': p.detected_at.isoformat() if hasattr(p.detected_at, 'isoformat') else str(p.detected_at),
                        'price': p.price
                    }
                    for p in candlestick_patterns
                ],
                'chart_patterns': [
                    {
                        'name': p.pattern_name,
                        'type': p.pattern_type,
                        'strength': p.strength,
                        'is_bullish': p.is_bullish,
                        'detected_at': p.detected_at.isoformat() if hasattr(p.detected_at, 'isoformat') else str(p.detected_at),
                        'price_levels': p.price_levels
                    }
                    for p in chart_patterns
                ],
                'combined_score': combined_score,
                'bullish_signals': bullish_signals,
                'bearish_signals': bearish_signals,
                'total_patterns': len(candlestick_patterns) + len(chart_patterns)
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error analyzing patterns")
            raise DataProcessingException(f"Pattern analysis failed: {str(e)}") from e
    
    def _calculate_combined_score(
        self,
        candlestick_patterns: List[CandlestickPatternDetection],
        chart_patterns: List[ChartPattern]
    ) -> float:
        """
        Calculate combined pattern score.
        
        Args:
            candlestick_patterns: List of candlestick patterns
            chart_patterns: List of chart patterns
            
        Returns:
            Combined score (0-100)
        """
        if not candlestick_patterns and not chart_patterns:
            return 0.0
        
        # Weight candlestick patterns more (they're more immediate)
        candlestick_score = sum(
            p.strength * p.reliability for p in candlestick_patterns
        ) / max(len(candlestick_patterns), 1) if candlestick_patterns else 0
        
        chart_score = sum(
            p.strength for p in chart_patterns
        ) / max(len(chart_patterns), 1) if chart_patterns else 0
        
        # Weighted average
        if candlestick_patterns and chart_patterns:
            combined = (candlestick_score * 0.6 + chart_score * 0.4)
        elif candlestick_patterns:
            combined = candlestick_score
        else:
            combined = chart_score
        
        return min(100, max(0, combined))
    
    def get_pattern_confirmation(
        self,
        candlestick_patterns: List[CandlestickPatternDetection],
        chart_patterns: List[ChartPattern]
    ) -> Dict[str, bool]:
        """
        Check if patterns confirm each other.
        
        Args:
            candlestick_patterns: List of candlestick patterns
            chart_patterns: List of chart patterns
            
        Returns:
            Dictionary with confirmation status
        """
        bullish_candlestick = any(
            p.is_bullish is True for p in candlestick_patterns
        )
        bearish_candlestick = any(
            p.is_bullish is False for p in candlestick_patterns
        )
        
        bullish_chart = any(
            p.is_bullish is True for p in chart_patterns
        )
        bearish_chart = any(
            p.is_bullish is False for p in chart_patterns
        )
        
        return {
            'bullish_confirmed': bullish_candlestick and bullish_chart,
            'bearish_confirmed': bearish_candlestick and bearish_chart,
            'conflicting_signals': (
                (bullish_candlestick and bearish_chart) or
                (bearish_candlestick and bullish_chart)
            )
        }

