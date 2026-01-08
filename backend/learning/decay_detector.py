"""
Decay Detector

Detects strategy decay.
"""

from typing import Optional
from datetime import datetime, timedelta

from utils.debug_utils import DebugUtils
from backend.learning.performance_tracker import PerformanceTracker, StrategyPerformance


class DecayDetector:
    """
    Detects strategy decay.
    
    Decay indicators:
    - Win rate decline > 10%
    - Profit factor < 1.0
    - Sharpe < 0.3
    - Drawdown > 20%
    """
    
    def __init__(self, performance_tracker: PerformanceTracker):
        """
        Initialize decay detector.
        
        Args:
            performance_tracker: Performance tracker instance
        """
        self.performance_tracker = performance_tracker
    
    def detect_decay(self, strategy_id: str) -> bool:
        """
        Detect if strategy is decaying.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            True if decay detected, False otherwise
        """
        # Get recent performance (30 days)
        recent = self.performance_tracker.get_performance(strategy_id, days=30)
        if not recent:
            return False  # No data = no decay
        
        # Get baseline performance (90 days)
        baseline = self.performance_tracker.get_performance(strategy_id, days=90)
        if not baseline:
            return False  # No baseline = can't detect decay
        
        from backend.settings import get_settings
        settings = get_settings()
        
        # Get thresholds from settings
        win_rate_threshold = settings.get_decay_win_rate_threshold()
        profit_factor_threshold = settings.get_decay_profit_factor_threshold()
        sharpe_threshold = settings.get_decay_sharpe_threshold()
        drawdown_threshold = settings.get_decay_drawdown_threshold()
        
        # Check win rate decline
        if recent.win_rate < baseline.win_rate - win_rate_threshold:
            DebugUtils.warning(
                f"Strategy {strategy_id} decay detected: win rate dropped "
                f"from {baseline.win_rate:.1%} to {recent.win_rate:.1%}"
            )
            return True
        
        # Check profit factor
        if recent.profit_factor < profit_factor_threshold:
            DebugUtils.warning(
                f"Strategy {strategy_id} decay detected: profit factor {recent.profit_factor:.2f} < {profit_factor_threshold:.2f}"
            )
            return True
        
        # Check Sharpe ratio
        if recent.sharpe_ratio < sharpe_threshold:
            DebugUtils.warning(
                f"Strategy {strategy_id} decay detected: Sharpe ratio {recent.sharpe_ratio:.2f} < {sharpe_threshold:.2f}"
            )
            return True
        
        # Check drawdown
        if recent.max_drawdown > drawdown_threshold:
            DebugUtils.warning(
                f"Strategy {strategy_id} decay detected: drawdown {recent.max_drawdown:.1%} > {drawdown_threshold:.1%}"
            )
            return True
        
        return False

