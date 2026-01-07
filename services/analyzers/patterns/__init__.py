"""
Pattern Recognition Module

This module provides pattern recognition capabilities for candlestick patterns
and chart patterns with scoring and reliability metrics.
"""

from .candlestick_patterns import CandlestickPatternDetector, PatternDetection as CandlestickPatternDetection
from .chart_patterns import ChartPatternDetector, ChartPattern
from .pattern_analyzer import PatternAnalyzer

__all__ = [
    'CandlestickPatternDetector',
    'CandlestickPatternDetection',
    'ChartPatternDetector',
    'ChartPattern',
    'PatternAnalyzer'
]
