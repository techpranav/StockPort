"""
Learning Module

Provides performance tracking, decay detection, and strategy optimization:
- Performance tracking with comprehensive metrics
- Decay detection for strategy monitoring
- Performance analysis and reporting
"""

from backend.learning.performance_tracker import PerformanceTracker, StrategyPerformance
from backend.learning.decay_detector import DecayDetector

__all__ = [
    'PerformanceTracker',
    'StrategyPerformance',
    'DecayDetector'
]
