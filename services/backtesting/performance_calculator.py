"""
Performance Calculator

Calculates performance metrics for backtest results.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

from models.backtest_result import BacktestTrade
from utils.debug_utils import DebugUtils


class PerformanceCalculator:
    """
    Calculates performance metrics for backtests.
    
    Features:
    - Return calculations
    - Win rate and profit factor
    - Drawdown analysis
    - Sharpe ratio
    """
    
    def __init__(self):
        """Initialize performance calculator."""
        DebugUtils.info("Initialized PerformanceCalculator")
    
    def calculate_performance(
        self,
        initial_capital: float,
        final_capital: float,
        trades: List[BacktestTrade],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            initial_capital: Starting capital
            final_capital: Ending capital
            trades: List of trades
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary of performance metrics
        """
        # Basic returns
        total_return = final_capital - initial_capital
        total_return_pct = (total_return / initial_capital) * 100 if initial_capital > 0 else 0
        
        # Trade statistics
        closed_trades = [t for t in trades if t.status.value == 'closed' and t.profit_loss is not None]
        total_trades = len(closed_trades)
        
        winning_trades = [t for t in closed_trades if t.profit_loss and t.profit_loss > 0]
        losing_trades = [t for t in closed_trades if t.profit_loss and t.profit_loss <= 0]
        
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        # Average profit/loss
        avg_profit = np.mean([t.profit_loss for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.profit_loss for t in losing_trades]) if losing_trades else 0
        
        # Profit factor
        total_profit = sum(t.profit_loss for t in winning_trades) if winning_trades else 0
        total_loss = abs(sum(t.profit_loss for t in losing_trades)) if losing_trades else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf') if total_profit > 0 else 0
        
        # Drawdown
        max_drawdown, max_drawdown_pct = self._calculate_drawdown(trades, initial_capital)
        
        # Sharpe ratio
        sharpe_ratio = self._calculate_sharpe_ratio(trades, start_date, end_date)
        
        return {
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'sharpe_ratio': sharpe_ratio
        }
    
    def _calculate_drawdown(
        self,
        trades: List[BacktestTrade],
        initial_capital: float
    ) -> tuple[float, float]:
        """
        Calculate maximum drawdown.
        
        Args:
            trades: List of trades
            initial_capital: Starting capital
            
        Returns:
            Tuple of (max_drawdown, max_drawdown_pct)
        """
        if not trades:
            return 0.0, 0.0
        
        # Calculate equity curve
        equity_curve = [initial_capital]
        current_capital = initial_capital
        
        for trade in trades:
            if trade.status.value == 'closed' and trade.profit_loss:
                current_capital += trade.profit_loss
                equity_curve.append(current_capital)
        
        if len(equity_curve) < 2:
            return 0.0, 0.0
        
        # Calculate drawdown
        peak = equity_curve[0]
        max_drawdown = 0.0
        max_drawdown_pct = 0.0
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            
            drawdown = peak - equity
            drawdown_pct = (drawdown / peak * 100) if peak > 0 else 0
            
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_pct = drawdown_pct
        
        return max_drawdown, max_drawdown_pct
    
    def _calculate_sharpe_ratio(
        self,
        trades: List[BacktestTrade],
        start_date: datetime,
        end_date: datetime
    ) -> Optional[float]:
        """
        Calculate Sharpe ratio.
        
        Args:
            trades: List of trades
            start_date: Start date
            end_date: End date
            
        Returns:
            Sharpe ratio or None if insufficient data
        """
        closed_trades = [t for t in trades if t.status.value == 'closed' and t.profit_loss_pct is not None]
        
        if len(closed_trades) < 2:
            return None
        
        returns = [t.profit_loss_pct for t in closed_trades]
        
        if not returns:
            return None
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return None
        
        # Annualized Sharpe ratio (assuming daily returns)
        days = (end_date - start_date).days
        if days == 0:
            return None
        
        annualized_return = mean_return * (365 / days)
        annualized_std = std_return * np.sqrt(365 / days)
        
        sharpe_ratio = annualized_return / annualized_std if annualized_std > 0 else None
        
        return sharpe_ratio

