"""
Strategy Executor

Executes trading strategies on historical data.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from models.backtest_result import BacktestTrade, TradeType, TradeStatus
from core.enhanced_analyzer import EnhancedStockAnalyzer
from utils.debug_utils import DebugUtils


class StrategyExecutor:
    """
    Executes trading strategies on historical data.
    
    Features:
    - Generate entry signals based on analysis
    - Execute trades with position sizing
    - Handle stop-loss and take-profit
    - Track trade lifecycle
    """
    
    def __init__(self):
        """Initialize strategy executor."""
        DebugUtils.info("Initialized StrategyExecutor")
    
    def execute_strategy(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        analyzer: EnhancedStockAnalyzer,
        position_size: float,
        transaction_cost: float = 0.001,
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None
    ) -> List[BacktestTrade]:
        """
        Execute strategy for a symbol over date range.
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            analyzer: Enhanced analyzer instance
            position_size: Capital allocated per position
            transaction_cost: Transaction cost percentage
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
            
        Returns:
            List of trades executed
        """
        trades: List[BacktestTrade] = []
        current_trade: Optional[BacktestTrade] = None
        
        # Iterate through date range (daily)
        current_date = start_date
        days_step = timedelta(days=1)
        
        while current_date <= end_date:
            try:
                # Get analysis for this date (simplified - would need historical data)
                # For now, we'll use current analysis as proxy
                analysis = analyzer.analyze_stock_comprehensive(
                    symbol,
                    include_intraday=True,
                    include_patterns=True,
                    include_entry_signals=True
                )
                
                entry_signal = analysis.get('entry_signals', {})
                signal_type = entry_signal.get('signal_type', '')
                current_price = entry_signal.get('entry_price', 0)
                
                # Check if we should enter a trade
                if not current_trade and signal_type in ['STRONG_BUY', 'BUY']:
                    # Enter trade
                    if current_price <= 0:
                        DebugUtils.warning(f"Invalid price {current_price} for {symbol} on {current_date}")
                        current_date += days_step
                        continue
                    
                    quantity = int(position_size / current_price)
                    if quantity > 0:
                        current_trade = BacktestTrade(
                            id=str(uuid.uuid4()),
                            symbol=symbol,
                            trade_type=TradeType.BUY,
                            entry_date=current_date,
                            entry_price=current_price,
                            quantity=quantity,
                            status=TradeStatus.OPEN,
                            entry_signal=entry_signal,
                            stop_loss=entry_signal.get('stop_loss'),
                            take_profit=entry_signal.get('take_profit')
                        )
                        
                        # Apply transaction cost
                        current_trade.entry_price *= (1 + transaction_cost)
                        
                        trades.append(current_trade)
                        DebugUtils.debug(f"Entered trade for {symbol} at {current_price}")
                
                # Check if we should exit a trade
                elif current_trade and current_trade.status == TradeStatus.OPEN:
                    should_exit = False
                    exit_reason = ""
                    
                    # Check stop loss
                    if current_trade.stop_loss and current_price <= current_trade.stop_loss:
                        should_exit = True
                        exit_reason = "Stop Loss"
                    
                    # Check take profit
                    elif current_trade.take_profit and current_price >= current_trade.take_profit:
                        should_exit = True
                        exit_reason = "Take Profit"
                    
                    # Check sell signal
                    elif signal_type in ['SELL', 'AVOID']:
                        should_exit = True
                        exit_reason = "Sell Signal"
                    
                    # Check stop loss percentage
                    elif stop_loss_pct and current_trade.entry_price > 0:
                        loss_pct = ((current_price - current_trade.entry_price) / current_trade.entry_price) * 100
                        if loss_pct <= -stop_loss_pct:
                            should_exit = True
                            exit_reason = f"Stop Loss ({stop_loss_pct}%)"
                    
                    # Check take profit percentage
                    elif take_profit_pct and current_trade.entry_price > 0:
                        profit_pct = ((current_price - current_trade.entry_price) / current_trade.entry_price) * 100
                        if profit_pct >= take_profit_pct:
                            should_exit = True
                            exit_reason = f"Take Profit ({take_profit_pct}%)"
                    
                    if should_exit:
                        # Exit trade
                        exit_price = current_price * (1 - transaction_cost)  # Apply transaction cost
                        
                        current_trade.exit_date = current_date
                        current_trade.exit_price = exit_price
                        current_trade.status = TradeStatus.CLOSED
                        current_trade.exit_reason = exit_reason
                        
                        # Calculate P&L
                        current_trade.profit_loss = (exit_price - current_trade.entry_price) * current_trade.quantity
                        current_trade.profit_loss_pct = ((exit_price - current_trade.entry_price) / current_trade.entry_price) * 100
                        
                        DebugUtils.debug(
                            f"Exited trade for {symbol}: "
                            f"{current_trade.profit_loss_pct:.2f}% "
                            f"({exit_reason})"
                        )
                        
                        current_trade = None
                
            except Exception as e:
                DebugUtils.log_error(e, f"Error executing strategy for {symbol} on {current_date}")
            
            current_date += days_step
        
        # Close any remaining open trades
        if current_trade and current_trade.status == TradeStatus.OPEN:
            # Close at last price
            analysis = analyzer.analyze_stock_comprehensive(symbol)
            exit_price = analysis.get('entry_signals', {}).get('entry_price', current_trade.entry_price)
            exit_price *= (1 - transaction_cost)
            
            current_trade.exit_date = end_date
            current_trade.exit_price = exit_price
            current_trade.status = TradeStatus.CLOSED
            current_trade.exit_reason = "End of Period"
            
            current_trade.profit_loss = (exit_price - current_trade.entry_price) * current_trade.quantity
            if current_trade.entry_price > 0:
                current_trade.profit_loss_pct = ((exit_price - current_trade.entry_price) / current_trade.entry_price) * 100
            else:
                current_trade.profit_loss_pct = 0.0
        
        return trades

