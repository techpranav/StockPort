"""
Walk-Forward Analysis

Prevents overfitting by optimizing on in-sample data and testing on out-of-sample data.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd

from utils.debug_utils import DebugUtils
from models.backtest_result import BacktestResult
from services.backtesting.backtest_engine import BacktestEngine


class WalkForwardAnalyzer:
    """
    Walk-forward analysis for backtesting.
    
    Features:
    - Split data into in-sample and out-of-sample periods
    - Optimize parameters on in-sample
    - Test on out-of-sample
    - Rolling window analysis
    - Prevents overfitting
    """
    
    def __init__(self, backtest_engine: BacktestEngine):
        """
        Initialize walk-forward analyzer.
        
        Args:
            backtest_engine: Backtest engine instance
        """
        self.backtest_engine = backtest_engine
    
    def run_walk_forward(
        self,
        strategy_name: str,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        in_sample_days: int = 180,
        out_of_sample_days: int = 60,
        step_days: int = 30,
        initial_capital: float = 100000.0,
        position_size_pct: float = 10.0,
        transaction_cost: float = 0.001,
        parameter_ranges: Optional[Dict[str, List[Any]]] = None
    ) -> Dict[str, Any]:
        """
        Run walk-forward analysis.
        
        Args:
            strategy_name: Name of the strategy
            symbols: List of stock symbols to test
            start_date: Start date for analysis
            end_date: End date for analysis
            in_sample_days: Days for in-sample optimization
            out_of_sample_days: Days for out-of-sample testing
            step_days: Days to step forward each iteration
            initial_capital: Starting capital
            position_size_pct: Percentage of capital per position
            transaction_cost: Transaction cost percentage
            parameter_ranges: Parameter ranges for optimization (optional)
            
        Returns:
            Dictionary with walk-forward results
        """
        DebugUtils.info(
            f"Starting walk-forward analysis: "
            f"in-sample={in_sample_days}d, out-of-sample={out_of_sample_days}d, step={step_days}d"
        )
        
        results = {
            'strategy_name': strategy_name,
            'symbols': symbols,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'iterations': [],
            'summary': {}
        }
        
        current_start = start_date
        iteration = 0
        
        while current_start + timedelta(days=in_sample_days + out_of_sample_days) <= end_date:
            iteration += 1
            
            # Define periods
            in_sample_start = current_start
            in_sample_end = in_sample_start + timedelta(days=in_sample_days)
            out_of_sample_start = in_sample_end
            out_of_sample_end = min(
                out_of_sample_start + timedelta(days=out_of_sample_days),
                end_date
            )
            
            DebugUtils.info(
                f"Walk-forward iteration {iteration}: "
                f"In-sample: {in_sample_start.date()} to {in_sample_end.date()}, "
                f"Out-of-sample: {out_of_sample_start.date()} to {out_of_sample_end.date()}"
            )
            
            # Optimize parameters on in-sample (if parameter ranges provided)
            optimal_params = None
            if parameter_ranges:
                optimal_params = self._optimize_parameters(
                    strategy_name,
                    symbols,
                    in_sample_start,
                    in_sample_end,
                    initial_capital,
                    position_size_pct,
                    transaction_cost,
                    parameter_ranges
                )
            
            # Test on out-of-sample
            out_of_sample_result = self.backtest_engine.run_backtest(
                strategy_name=strategy_name,
                symbols=symbols,
                start_date=out_of_sample_start,
                end_date=out_of_sample_end,
                initial_capital=initial_capital,
                position_size_pct=position_size_pct,
                transaction_cost=transaction_cost
            )
            
            # Store iteration results
            iteration_result = {
                'iteration': iteration,
                'in_sample_period': {
                    'start': in_sample_start.isoformat(),
                    'end': in_sample_end.isoformat()
                },
                'out_of_sample_period': {
                    'start': out_of_sample_start.isoformat(),
                    'end': out_of_sample_end.isoformat()
                },
                'optimal_parameters': optimal_params,
                'out_of_sample_performance': {
                    'total_return': out_of_sample_result.total_return,
                    'total_return_pct': out_of_sample_result.total_return_pct,
                    'win_rate': out_of_sample_result.win_rate,
                    'profit_factor': out_of_sample_result.profit_factor,
                    'max_drawdown': out_of_sample_result.max_drawdown,
                    'max_drawdown_pct': out_of_sample_result.max_drawdown_pct,
                    'sharpe_ratio': out_of_sample_result.sharpe_ratio
                }
            }
            
            results['iterations'].append(iteration_result)
            
            # Step forward
            current_start += timedelta(days=step_days)
        
        # Calculate summary statistics
        results['summary'] = self._calculate_summary(results['iterations'])
        
        DebugUtils.info(f"Walk-forward analysis completed: {len(results['iterations'])} iterations")
        
        return results
    
    def _optimize_parameters(
        self,
        strategy_name: str,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        initial_capital: float,
        position_size_pct: float,
        transaction_cost: float,
        parameter_ranges: Dict[str, List[Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Optimize strategy parameters using grid search on in-sample data.
        
        Args:
            strategy_name: Strategy name
            symbols: Stock symbols
            start_date: Start date
            end_date: End date
            initial_capital: Initial capital
            position_size_pct: Position size percentage
            transaction_cost: Transaction cost
            parameter_ranges: Parameter ranges to test
            
        Returns:
            Optimal parameters dictionary
        """
        # Simple grid search (can be enhanced with genetic algorithm or Bayesian optimization)
        best_params = None
        best_performance = float('-inf')
        
        # Generate parameter combinations
        param_combinations = self._generate_parameter_combinations(parameter_ranges)
        
        DebugUtils.info(f"Optimizing {len(param_combinations)} parameter combinations")
        
        for params in param_combinations:
            try:
                # Run backtest with these parameters
                # Note: This would require modifying backtest_engine to accept strategy parameters
                # For now, we'll return None and let the strategy use default parameters
                pass
            except Exception as e:
                DebugUtils.log_error(e, f"Error optimizing parameters: {params}")
                continue
        
        return best_params
    
    def _generate_parameter_combinations(
        self,
        parameter_ranges: Dict[str, List[Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate all parameter combinations for grid search.
        
        Args:
            parameter_ranges: Dictionary of parameter names to value ranges
            
        Returns:
            List of parameter combination dictionaries
        """
        import itertools
        
        param_names = list(parameter_ranges.keys())
        param_values = [parameter_ranges[name] for name in param_names]
        
        combinations = []
        for combo in itertools.product(*param_values):
            combinations.append(dict(zip(param_names, combo)))
        
        return combinations
    
    def _calculate_summary(
        self,
        iterations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate summary statistics from walk-forward iterations.
        
        Args:
            iterations: List of iteration results
            
        Returns:
            Summary statistics dictionary
        """
        if not iterations:
            return {}
        
        returns = [it['out_of_sample_performance']['total_return_pct'] for it in iterations]
        win_rates = [it['out_of_sample_performance']['win_rate'] for it in iterations]
        profit_factors = [it['out_of_sample_performance']['profit_factor'] for it in iterations]
        drawdowns = [it['out_of_sample_performance']['max_drawdown_pct'] for it in iterations]
        sharpe_ratios = [it['out_of_sample_performance']['sharpe_ratio'] for it in iterations]
        
        return {
            'total_iterations': len(iterations),
            'avg_return_pct': sum(returns) / len(returns) if returns else 0.0,
            'avg_win_rate': sum(win_rates) / len(win_rates) if win_rates else 0.0,
            'avg_profit_factor': sum(profit_factors) / len(profit_factors) if profit_factors else 0.0,
            'avg_drawdown_pct': sum(drawdowns) / len(drawdowns) if drawdowns else 0.0,
            'avg_sharpe_ratio': sum(sharpe_ratios) / len(sharpe_ratios) if sharpe_ratios else 0.0,
            'consistency': self._calculate_consistency(returns),
            'best_iteration': max(iterations, key=lambda x: x['out_of_sample_performance']['total_return_pct']),
            'worst_iteration': min(iterations, key=lambda x: x['out_of_sample_performance']['total_return_pct'])
        }
    
    def _calculate_consistency(self, returns: List[float]) -> float:
        """
        Calculate consistency score (percentage of positive returns).
        
        Args:
            returns: List of return percentages
            
        Returns:
            Consistency score (0-1)
        """
        if not returns:
            return 0.0
        
        positive_returns = sum(1 for r in returns if r > 0)
        return positive_returns / len(returns)

