"""
Monte Carlo Simulation

Runs multiple simulations with randomized trade sequences to calculate
risk metrics and confidence intervals.
"""

from typing import Dict, Any, List, Optional
import random
import numpy as np
from datetime import datetime

from utils.debug_utils import DebugUtils
from models.backtest_result import BacktestTrade, TradeType, TradeStatus
from services.backtesting.performance_calculator import PerformanceCalculator

# Note: random and itertools are standard library, no need to add to requirements.txt


class MonteCarloSimulator:
    """
    Monte Carlo simulation for backtesting.
    
    Features:
    - Run 1000+ simulations with randomized trade sequences
    - Calculate probability distributions of returns
    - Risk metrics: VaR, CVaR, maximum drawdown distribution
    - Confidence intervals for performance metrics
    """
    
    def __init__(self, performance_calculator: PerformanceCalculator):
        """
        Initialize Monte Carlo simulator.
        
        Args:
            performance_calculator: Performance calculator instance
        """
        self.performance_calculator = performance_calculator
    
    def run_simulation(
        self,
        trades: List[BacktestTrade],
        initial_capital: float,
        num_simulations: int = 1000,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation.
        
        Args:
            trades: List of trades from backtest
            initial_capital: Initial capital
            num_simulations: Number of simulations to run
            confidence_level: Confidence level for intervals (default 0.95)
            
        Returns:
            Dictionary with simulation results
        """
        DebugUtils.info(f"Running Monte Carlo simulation: {num_simulations} simulations")
        
        if not trades:
            return {
                'num_simulations': num_simulations,
                'final_capitals': [],
                'returns': [],
                'summary': {}
            }
        
        final_capitals = []
        returns = []
        max_drawdowns = []
        win_rates = []
        profit_factors = []
        
        for i in range(num_simulations):
            # Randomize trade sequence
            randomized_trades = self._randomize_trade_sequence(trades)
            
            # Calculate performance for this sequence
            try:
                performance = self.performance_calculator.calculate_performance(
                    initial_capital=initial_capital,
                    final_capital=self._calculate_final_capital(initial_capital, randomized_trades),
                    trades=randomized_trades,
                    start_date=trades[0].entry_date if trades else datetime.now(),
                    end_date=trades[-1].exit_date if trades else datetime.now()
                )
                
                final_capitals.append(performance['final_capital'])
                returns.append(performance['total_return_pct'])
                max_drawdowns.append(performance['max_drawdown_pct'])
                win_rates.append(performance['win_rate'])
                profit_factors.append(performance['profit_factor'])
                
            except Exception as e:
                DebugUtils.log_error(e, f"Error in Monte Carlo simulation {i+1}")
                continue
        
        # Calculate statistics
        summary = self._calculate_statistics(
            final_capitals,
            returns,
            max_drawdowns,
            win_rates,
            profit_factors,
            confidence_level
        )
        
        DebugUtils.info(f"Monte Carlo simulation completed: {len(final_capitals)} successful simulations")
        
        return {
            'num_simulations': num_simulations,
            'successful_simulations': len(final_capitals),
            'final_capitals': final_capitals,
            'returns': returns,
            'max_drawdowns': max_drawdowns,
            'win_rates': win_rates,
            'profit_factors': profit_factors,
            'summary': summary
        }
    
    def _randomize_trade_sequence(
        self,
        trades: List[BacktestTrade]
    ) -> List[BacktestTrade]:
        """
        Randomize trade sequence while preserving trade properties.
        
        Args:
            trades: Original trade list
            
        Returns:
            Randomized trade list
        """
        # Shuffle trades randomly
        randomized = trades.copy()
        random.shuffle(randomized)
        return randomized
    
    def _calculate_final_capital(
        self,
        initial_capital: float,
        trades: List[BacktestTrade]
    ) -> float:
        """
        Calculate final capital from trades.
        
        Args:
            initial_capital: Starting capital
            trades: List of trades
            
        Returns:
            Final capital
        """
        capital = initial_capital
        
        for trade in trades:
            if trade.status == TradeStatus.CLOSED and trade.profit_loss:
                capital += trade.profit_loss
        
        return capital
    
    def _calculate_statistics(
        self,
        final_capitals: List[float],
        returns: List[float],
        max_drawdowns: List[float],
        win_rates: List[float],
        profit_factors: List[float],
        confidence_level: float
    ) -> Dict[str, Any]:
        """
        Calculate statistics from simulation results.
        
        Args:
            final_capitals: List of final capital values
            returns: List of return percentages
            max_drawdowns: List of maximum drawdown percentages
            win_rates: List of win rates
            profit_factors: List of profit factors
            confidence_level: Confidence level
            
        Returns:
            Statistics dictionary
        """
        if not returns:
            return {}
        
        returns_array = np.array(returns)
        drawdowns_array = np.array(max_drawdowns)
        
        # Basic statistics
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        median_return = np.median(returns_array)
        
        # Percentiles
        alpha = 1 - confidence_level
        lower_percentile = alpha / 2 * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        return {
            'mean_return_pct': float(mean_return),
            'std_return_pct': float(std_return),
            'median_return_pct': float(median_return),
            'min_return_pct': float(np.min(returns_array)),
            'max_return_pct': float(np.max(returns_array)),
            'confidence_interval': {
                'level': confidence_level,
                'lower': float(np.percentile(returns_array, lower_percentile)),
                'upper': float(np.percentile(returns_array, upper_percentile))
            },
            'var_95': float(np.percentile(returns_array, 5)),  # Value at Risk (5th percentile)
            'cvar_95': float(np.mean(returns_array[returns_array <= np.percentile(returns_array, 5)])),  # Conditional VaR
            'max_drawdown': {
                'mean': float(np.mean(drawdowns_array)),
                'max': float(np.max(drawdowns_array)),
                'percentile_95': float(np.percentile(drawdowns_array, 95))
            },
            'win_rate': {
                'mean': float(np.mean(win_rates)),
                'std': float(np.std(win_rates))
            },
            'profit_factor': {
                'mean': float(np.mean(profit_factors)),
                'std': float(np.std(profit_factors))
            },
            'probability_of_profit': float(np.sum(returns_array > 0) / len(returns_array)),
            'probability_of_loss': float(np.sum(returns_array < 0) / len(returns_array))
        }

