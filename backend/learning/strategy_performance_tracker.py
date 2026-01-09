"""
Strategy Performance Tracker

Tracks real-time strategy performance and ranking.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from utils.debug_utils import DebugUtils
from models.strategy_signal import StrategySignal


class StrategyPerformanceTracker:
    """
    Strategy performance tracker.
    
    Features:
    - Real-time strategy performance
    - Win rate tracking
    - Average profit/loss
    - Strategy ranking
    - Performance attribution
    """
    
    def __init__(self):
        """Initialize performance tracker."""
        # Strategy performance data
        self.strategy_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_signals': 0,
            'profitable_signals': 0,
            'losing_signals': 0,
            'breakeven_signals': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'avg_profit': 0.0,
            'avg_loss': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'avg_confidence': 0.0,
            'avg_score': 0.0,
            'last_signal_time': None,
            'signals': []  # Recent signals
        })
        
        # Track signal outcomes
        self.signal_outcomes: Dict[str, Dict[str, Any]] = {}  # signal_id -> outcome
        
        DebugUtils.info("Initialized StrategyPerformanceTracker")
    
    def track_signal(
        self,
        signal: StrategySignal
    ):
        """
        Track a new signal.
        
        Args:
            signal: Strategy signal to track
        """
        strategy_id = signal.strategy_id
        
        stats = self.strategy_stats[strategy_id]
        stats['total_signals'] += 1
        stats['avg_score'] = ((stats['avg_score'] * (stats['total_signals'] - 1)) + signal.score) / stats['total_signals']
        stats['avg_confidence'] = ((stats['avg_confidence'] * (stats['total_signals'] - 1)) + signal.confidence) / stats['total_signals']
        stats['last_signal_time'] = signal.timestamp
        
        # Store recent signal
        stats['signals'].append({
            'signal_id': signal.signal_id,
            'symbol': signal.opportunity.symbol,
            'score': signal.score,
            'confidence': signal.confidence,
            'entry_price': signal.entry_price,
            'timestamp': signal.timestamp.isoformat()
        })
        
        # Keep only last 100 signals
        if len(stats['signals']) > 100:
            stats['signals'] = stats['signals'][-100:]
        
        # Initialize outcome tracking
        self.signal_outcomes[signal.signal_id] = {
            'strategy_id': strategy_id,
            'symbol': signal.opportunity.symbol,
            'entry_price': signal.entry_price,
            'entry_time': signal.timestamp,
            'outcome': None,
            'exit_price': None,
            'exit_time': None,
            'profit_loss': None,
            'profit_loss_pct': None
        }
    
    def track_outcome(
        self,
        signal_id: str,
        outcome: str,  # 'profit', 'loss', 'breakeven'
        exit_price: float,
        exit_time: Optional[datetime] = None,
        profit_loss: Optional[float] = None,
        profit_loss_pct: Optional[float] = None
    ):
        """
        Track signal outcome.
        
        Args:
            signal_id: Signal identifier
            outcome: Outcome type
            exit_price: Exit price
            exit_time: Exit time (default: now)
            profit_loss: Profit/loss amount
            profit_loss_pct: Profit/loss percentage
        """
        if signal_id not in self.signal_outcomes:
            DebugUtils.warning(f"Signal {signal_id} not found in outcomes")
            return
        
        outcome_data = self.signal_outcomes[signal_id]
        outcome_data['outcome'] = outcome
        outcome_data['exit_price'] = exit_price
        outcome_data['exit_time'] = exit_time or datetime.now()
        outcome_data['profit_loss'] = profit_loss
        outcome_data['profit_loss_pct'] = profit_loss_pct
        
        # Update strategy stats
        strategy_id = outcome_data['strategy_id']
        stats = self.strategy_stats[strategy_id]
        
        if outcome == 'profit':
            stats['profitable_signals'] += 1
            if profit_loss:
                stats['total_profit'] += profit_loss
                stats['avg_profit'] = stats['total_profit'] / stats['profitable_signals']
        elif outcome == 'loss':
            stats['losing_signals'] += 1
            if profit_loss:
                stats['total_loss'] += abs(profit_loss)
                stats['avg_loss'] = stats['total_loss'] / stats['losing_signals']
        elif outcome == 'breakeven':
            stats['breakeven_signals'] += 1
        
        # Update win rate
        closed_signals = stats['profitable_signals'] + stats['losing_signals'] + stats['breakeven_signals']
        if closed_signals > 0:
            stats['win_rate'] = stats['profitable_signals'] / closed_signals
        
        # Update profit factor
        if stats['total_loss'] > 0:
            stats['profit_factor'] = stats['total_profit'] / stats['total_loss']
        elif stats['total_profit'] > 0:
            stats['profit_factor'] = float('inf')
        else:
            stats['profit_factor'] = 0.0
    
    def get_strategy_performance(
        self,
        strategy_id: str
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Performance metrics dictionary
        """
        return self.strategy_stats.get(strategy_id, {}).copy()
    
    def get_all_strategy_performance(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance metrics for all strategies.
        
        Returns:
            Dictionary mapping strategy_id to performance metrics
        """
        return dict(self.strategy_stats)
    
    def get_strategy_ranking(
        self,
        metric: str = 'win_rate'  # 'win_rate', 'profit_factor', 'avg_score', 'total_profit'
    ) -> List[Dict[str, Any]]:
        """
        Get strategy ranking by performance metric.
        
        Args:
            metric: Metric to rank by
            
        Returns:
            List of strategies sorted by metric (descending)
        """
        rankings = []
        
        for strategy_id, stats in self.strategy_stats.items():
            if stats['total_signals'] == 0:
                continue
            
            value = stats.get(metric, 0)
            
            rankings.append({
                'strategy_id': strategy_id,
                'metric_value': value,
                'total_signals': stats['total_signals'],
                'win_rate': stats['win_rate'],
                'profit_factor': stats['profit_factor'],
                'avg_score': stats['avg_score'],
                'avg_confidence': stats['avg_confidence']
            })
        
        # Sort by metric value (descending)
        rankings.sort(key=lambda x: x['metric_value'], reverse=True)
        
        # Add rank
        for i, ranking in enumerate(rankings):
            ranking['rank'] = i + 1
        
        return rankings
    
    def get_performance_attribution(
        self,
        strategy_id: str,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance attribution for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            lookback_days: Days to look back
            
        Returns:
            Attribution analysis
        """
        stats = self.strategy_stats.get(strategy_id, {})
        
        if not stats or stats['total_signals'] == 0:
            return {
                'strategy_id': strategy_id,
                'period': lookback_days,
                'attribution': {}
            }
        
        # Analyze recent signals
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        recent_signals = [
            s for s in stats['signals']
            if datetime.fromisoformat(s['timestamp']) >= cutoff_date
        ]
        
        # Group by symbol
        symbol_performance = defaultdict(lambda: {'count': 0, 'total_profit': 0.0})
        
        for signal in recent_signals:
            signal_id = signal['signal_id']
            if signal_id in self.signal_outcomes:
                outcome = self.signal_outcomes[signal_id]
                if outcome['outcome'] and outcome['profit_loss']:
                    symbol = outcome['symbol']
                    symbol_performance[symbol]['count'] += 1
                    symbol_performance[symbol]['total_profit'] += outcome['profit_loss']
        
        # Top performing symbols
        top_symbols = sorted(
            symbol_performance.items(),
            key=lambda x: x[1]['total_profit'],
            reverse=True
        )[:10]
        
        return {
            'strategy_id': strategy_id,
            'period': lookback_days,
            'total_signals': len(recent_signals),
            'top_symbols': [
                {
                    'symbol': symbol,
                    'signals': perf['count'],
                    'total_profit': perf['total_profit']
                }
                for symbol, perf in top_symbols
            ],
            'overall_performance': {
                'win_rate': stats['win_rate'],
                'profit_factor': stats['profit_factor'],
                'avg_score': stats['avg_score']
            }
        }

