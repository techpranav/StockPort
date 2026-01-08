"""
Performance Tracker

Tracks strategy performance over time.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import statistics

from utils.debug_utils import DebugUtils


@dataclass
class StrategyPerformance:
    """Strategy performance metrics."""
    strategy_id: str
    period_start: datetime
    period_end: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    average_win: float
    average_loss: float
    average_holding_period: int  # days


class PerformanceTracker:
    """
    Tracks strategy performance.
    
    Tracks:
    - Win rate
    - Profit factor
    - Sharpe ratio
    - Drawdown
    - Holding period
    """
    
    def __init__(self):
        """Initialize performance tracker."""
        self.trades: Dict[str, List[Dict[str, Any]]] = defaultdict(list)  # strategy_id -> trades
    
    def record_trade(
        self,
        strategy_id: str,
        trade: Dict[str, Any]
    ):
        """
        Record a trade.
        
        Args:
            strategy_id: Strategy identifier
            trade: Trade dictionary with pnl, entry_date, exit_date, etc.
        """
        self.trades[strategy_id].append(trade)
        DebugUtils.debug(f"Recorded trade for strategy {strategy_id}")
    
    def get_performance(
        self,
        strategy_id: str,
        days: int = 90
    ) -> Optional[StrategyPerformance]:
        """
        Get performance for strategy.
        
        Args:
            strategy_id: Strategy identifier
            days: Number of days to look back
            
        Returns:
            StrategyPerformance or None
        """
        strategy_trades = self.trades.get(strategy_id, [])
        
        if not strategy_trades:
            return None
        
        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_trades = [
            t for t in strategy_trades
            if t.get('exit_date', datetime.now()) > cutoff_date
        ]
        
        if not recent_trades:
            return None
        
        # Calculate metrics
        winning_trades = [t for t in recent_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in recent_trades if t.get('pnl', 0) <= 0]
        
        total_trades = len(recent_trades)
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        win_rate = win_count / total_trades if total_trades > 0 else 0.0
        
        total_profit = sum(t.get('pnl', 0) for t in winning_trades)
        total_loss = abs(sum(t.get('pnl', 0) for t in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0.0
        
        total_return = sum(t.get('pnl', 0) for t in recent_trades)
        
        average_win = total_profit / win_count if win_count > 0 else 0.0
        average_loss = total_loss / loss_count if loss_count > 0 else 0.0
        
        # Calculate holding periods
        holding_periods = []
        for trade in recent_trades:
            entry = trade.get('entry_date')
            exit = trade.get('exit_date')
            if entry and exit:
                if isinstance(entry, str):
                    entry = datetime.fromisoformat(entry)
                if isinstance(exit, str):
                    exit = datetime.fromisoformat(exit)
                holding_periods.append((exit - entry).days)
        
        avg_holding_period = int(sum(holding_periods) / len(holding_periods)) if holding_periods else 0
        
        # Calculate Sharpe ratio (simplified - would need risk-free rate)
        returns = [t.get('pnl_percent', 0) / 100 for t in recent_trades]
        if len(returns) > 1:
            avg_return = statistics.mean(returns)
            std_return = statistics.stdev(returns) if len(returns) > 1 else 0.01
            sharpe_ratio = (avg_return / std_return) * (252 ** 0.5) if std_return > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Calculate max drawdown
        cumulative_returns = []
        cumulative = 0.0
        for trade in recent_trades:
            cumulative += trade.get('pnl_percent', 0) / 100
            cumulative_returns.append(cumulative)
        
        if cumulative_returns:
            peak = cumulative_returns[0]
            max_drawdown = 0.0
            for ret in cumulative_returns:
                if ret > peak:
                    peak = ret
                drawdown = (peak - ret) / (1 + peak) if (1 + peak) > 0 else 0
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        else:
            max_drawdown = 0.0
        
        period_start = min(t.get('entry_date', datetime.now()) for t in recent_trades)
        if isinstance(period_start, str):
            period_start = datetime.fromisoformat(period_start)
        period_end = datetime.now()
        
        return StrategyPerformance(
            strategy_id=strategy_id,
            period_start=period_start,
            period_end=period_end,
            total_trades=total_trades,
            winning_trades=win_count,
            losing_trades=loss_count,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            average_win=average_win,
            average_loss=average_loss,
            average_holding_period=avg_holding_period
        )

