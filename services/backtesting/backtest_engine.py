"""
Backtest Engine

Core engine for running backtests on trading strategies.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from services.backtesting.strategy_executor import StrategyExecutor
from services.backtesting.performance_calculator import PerformanceCalculator
from models.backtest_result import BacktestResult, BacktestTrade
from core.enhanced_analyzer import EnhancedStockAnalyzer
from utils.debug_utils import DebugUtils
from config.app_config import ENABLE_BACKTESTING


class BacktestEngine:
    """
    Backtesting engine for testing trading strategies.
    
    Features:
    - Run backtests on historical data
    - Simulate trades with entry/exit signals
    - Calculate performance metrics
    - Support multiple strategies
    """
    
    def __init__(self, analyzer: Optional[EnhancedStockAnalyzer] = None):
        """
        Initialize backtest engine.
        
        Args:
            analyzer: Optional enhanced analyzer instance
        """
        self.analyzer = analyzer or EnhancedStockAnalyzer()
        self.strategy_executor = StrategyExecutor()
        self.performance_calculator = PerformanceCalculator()
        DebugUtils.info("Initialized BacktestEngine")
    
    def run_backtest(
        self,
        strategy_name: str,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 100000.0,
        position_size_pct: float = 10.0,
        transaction_cost: float = 0.001,
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None
    ) -> BacktestResult:
        """
        Run a backtest on specified symbols and date range.
        
        Args:
            strategy_name: Name of the strategy
            symbols: List of stock symbols to test
            start_date: Start date for backtest
            end_date: End date for backtest
            initial_capital: Starting capital
            position_size_pct: Percentage of capital per position
            transaction_cost: Transaction cost as percentage (e.g., 0.001 = 0.1%)
            stop_loss_pct: Stop loss percentage (optional)
            take_profit_pct: Take profit percentage (optional)
            
        Returns:
            BacktestResult object
        """
        if not ENABLE_BACKTESTING:
            raise ValueError("Backtesting is disabled in configuration")
        
        backtest_id = str(uuid.uuid4())
        DebugUtils.info(f"Starting backtest {backtest_id} for {len(symbols)} symbols")
        
        # Execute strategy for each symbol
        all_trades: List[BacktestTrade] = []
        current_capital = initial_capital
        
        for symbol in symbols:
            try:
                # Get historical data and signals
                trades = self.strategy_executor.execute_strategy(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    analyzer=self.analyzer,
                    position_size=current_capital * (position_size_pct / 100),
                    transaction_cost=transaction_cost,
                    stop_loss_pct=stop_loss_pct,
                    take_profit_pct=take_profit_pct
                )
                
                all_trades.extend(trades)
                
                # Update capital based on closed trades
                for trade in trades:
                    if trade.status.value == 'closed' and trade.profit_loss:
                        current_capital += trade.profit_loss
                
            except Exception as e:
                DebugUtils.log_error(e, f"Error backtesting {symbol}")
        
        # Calculate performance metrics
        performance = self.performance_calculator.calculate_performance(
            initial_capital=initial_capital,
            final_capital=current_capital,
            trades=all_trades,
            start_date=start_date,
            end_date=end_date
        )
        
        # Create result
        result = BacktestResult(
            id=backtest_id,
            strategy_name=strategy_name,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_capital=current_capital,
            total_return=performance['total_return'],
            total_return_pct=performance['total_return_pct'],
            total_trades=performance['total_trades'],
            winning_trades=performance['winning_trades'],
            losing_trades=performance['losing_trades'],
            win_rate=performance['win_rate'],
            avg_profit=performance['avg_profit'],
            avg_loss=performance['avg_loss'],
            profit_factor=performance['profit_factor'],
            max_drawdown=performance['max_drawdown'],
            max_drawdown_pct=performance['max_drawdown_pct'],
            sharpe_ratio=performance.get('sharpe_ratio'),
            trades=all_trades,
            metadata={
                'position_size_pct': position_size_pct,
                'transaction_cost': transaction_cost,
                'stop_loss_pct': stop_loss_pct,
                'take_profit_pct': take_profit_pct
            }
        )
        
        DebugUtils.info(
            f"Backtest {backtest_id} completed: "
            f"{result.total_return_pct:.2f}% return, "
            f"{result.win_rate:.1f}% win rate"
        )
        
        return result

