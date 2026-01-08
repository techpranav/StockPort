"""
Timing Awareness Module

Provides timing awareness for signals and opportunities:
- Signal expiry management
- Latency tracking
- Stale detection
"""

from backend.timing.signal_expiry import SignalExpiryManager, SignalExpiry
from backend.timing.latency_tracker import LatencyTracker, LatencyBudget
from backend.timing.stale_detector import StaleDetector

__all__ = [
    'SignalExpiryManager',
    'SignalExpiry',
    'LatencyTracker',
    'LatencyBudget',
    'StaleDetector'
]
