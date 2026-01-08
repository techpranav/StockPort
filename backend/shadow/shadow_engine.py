"""
Shadow Engine

Main shadow trading engine.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.debug_utils import DebugUtils
from models.strategy_signal import StrategySignal
from backend.shadow.shadow_broker import ShadowBroker
from backend.shadow.isolation_layer import IsolationLayer


class ShadowEngine:
    """
    Shadow trading engine.
    
    Executes shadow trades in parallel with live trading.
    """
    
    def __init__(
        self,
        shadow_broker: Optional[ShadowBroker] = None,
        isolation_layer: Optional[IsolationLayer] = None
    ):
        """
        Initialize shadow engine.
        
        Args:
            shadow_broker: Shadow broker instance
            isolation_layer: Isolation layer instance
        """
        self.shadow_broker = shadow_broker or ShadowBroker()
        self.isolation_layer = isolation_layer or IsolationLayer()
        self.shadow_positions: Dict[str, Dict[str, Any]] = {}
        self.shadow_capital = 100000.0  # Virtual capital
    
    def execute_shadow_trade(self, signal: StrategySignal) -> Dict[str, Any]:
        """
        Execute shadow trade.
        
        Args:
            signal: Strategy signal
            
        Returns:
            Execution result
        """
        # Check if strategy is shadow-only
        if not self.isolation_layer.is_shadow_strategy(signal.strategy_id):
            return {
                'success': False,
                'reason': 'Strategy is not shadow-only'
            }
        
        # Calculate position size (simplified - would use position sizer)
        # Use 1% of shadow capital per trade
        position_size = int((self.shadow_capital * 0.01) / signal.entry_price) if signal.entry_price > 0 else 10
        
        # Create shadow order
        order = {
            'symbol': signal.opportunity.symbol,
            'side': 'buy',
            'quantity': max(1, position_size),  # At least 1 share
            'order_type': 'market',
            'strategy_id': signal.strategy_id,
            'signal_id': signal.signal_id,
            'price': signal.entry_price,
            'broker': 'shadow'  # Mark as shadow order
        }
        
        # Execute via shadow broker
        try:
            result = self.shadow_broker.place_order(order)
            
            # Track shadow position
            if result.get('status') == 'filled':
                symbol = order['symbol']
                self.shadow_positions[symbol] = {
                    'symbol': symbol,
                    'quantity': order['quantity'],
                    'entry_price': result.get('fill_price', signal.entry_price),
                    'entry_date': datetime.now(),
                    'strategy_id': signal.strategy_id
                }
            
            DebugUtils.debug(f"Shadow trade executed: {order['symbol']}")
            
            return result
        except Exception as e:
            DebugUtils.log_error(e, f"Error executing shadow trade for {signal.opportunity.symbol}")
            return {'success': False, 'reason': str(e)}

