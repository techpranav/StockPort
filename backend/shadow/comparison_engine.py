"""
Comparison Engine

Compares shadow vs live performance.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from utils.debug_utils import DebugUtils
from backend.learning.performance_tracker import PerformanceTracker


@dataclass
class ShadowComparison:
    """Shadow vs live comparison."""
    strategy_id: str
    period_start: datetime
    period_end: datetime
    live_win_rate: float
    live_profit_factor: float
    live_sharpe: float
    live_drawdown: float
    shadow_win_rate: float
    shadow_profit_factor: float
    shadow_sharpe: float
    shadow_drawdown: float
    win_rate_diff: float
    profit_factor_diff: float
    sharpe_diff: float
    drawdown_diff: float
    recommendation: str  # activate, keep_shadow, disable


class ComparisonEngine:
    """
    Compares shadow vs live performance.
    """
    
    def __init__(self, performance_tracker: PerformanceTracker):
        """
        Initialize comparison engine.
        
        Args:
            performance_tracker: Performance tracker instance
        """
        self.performance_tracker = performance_tracker
    
    def compare(
        self,
        strategy_id: str,
        days: int = 30
    ) -> Optional[ShadowComparison]:
        """
        Compare shadow vs live performance.
        
        Args:
            strategy_id: Strategy identifier
            days: Number of days to compare
            
        Returns:
            ShadowComparison or None
        """
        # Get live performance
        live_perf = self.performance_tracker.get_performance(f"live_{strategy_id}", days)
        
        # Get shadow performance
        shadow_perf = self.performance_tracker.get_performance(f"shadow_{strategy_id}", days)
        
        if not live_perf or not shadow_perf:
            return None
        
        # Calculate differences
        win_rate_diff = shadow_perf.win_rate - live_perf.win_rate
        profit_factor_diff = shadow_perf.profit_factor - live_perf.profit_factor
        sharpe_diff = shadow_perf.sharpe_ratio - live_perf.sharpe_ratio
        drawdown_diff = shadow_perf.max_drawdown - live_perf.max_drawdown
        
        # Generate recommendation with more sophisticated logic
        shadow_better_win_rate = shadow_perf.win_rate > live_perf.win_rate + 0.05  # 5% better
        shadow_better_profit = shadow_perf.profit_factor > live_perf.profit_factor + 0.2  # 20% better
        shadow_good_sharpe = shadow_perf.sharpe_ratio > 0.5
        shadow_low_drawdown = shadow_perf.max_drawdown < 0.15  # Less than 15%
        
        if (shadow_better_win_rate and shadow_better_profit and 
            shadow_good_sharpe and shadow_low_drawdown and
            shadow_perf.profit_factor > 1.5):
            recommendation = "activate"
        elif shadow_perf.profit_factor < 0.8 or shadow_perf.win_rate < 0.4:
            recommendation = "disable"
        elif shadow_perf.profit_factor < 1.0:
            recommendation = "keep_shadow"  # Keep testing
        else:
            recommendation = "keep_shadow"  # Continue monitoring
        
        return ShadowComparison(
            strategy_id=strategy_id,
            period_start=shadow_perf.period_start,
            period_end=shadow_perf.period_end,
            live_win_rate=live_perf.win_rate,
            live_profit_factor=live_perf.profit_factor,
            live_sharpe=live_perf.sharpe_ratio,
            live_drawdown=live_perf.max_drawdown,
            shadow_win_rate=shadow_perf.win_rate,
            shadow_profit_factor=shadow_perf.profit_factor,
            shadow_sharpe=shadow_perf.sharpe_ratio,
            shadow_drawdown=shadow_perf.max_drawdown,
            win_rate_diff=win_rate_diff,
            profit_factor_diff=profit_factor_diff,
            sharpe_diff=sharpe_diff,
            drawdown_diff=drawdown_diff,
            recommendation=recommendation
        )

