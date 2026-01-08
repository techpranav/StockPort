"""
Paper Trading Broker

Simulates broker execution for paper trading.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import random

from backend.execution.brokers.base_broker import BaseBroker
from utils.debug_utils import DebugUtils


class PaperBroker(BaseBroker):
    """
    Paper trading broker that simulates execution.
    
    Features:
    - Realistic slippage simulation
    - Realistic fill simulation
    - Position tracking
    - P&L calculation
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize paper broker.
        
        Args:
            initial_capital: Initial capital for paper trading
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}  # symbol -> position
        self.orders: Dict[str, Dict[str, Any]] = {}  # order_id -> order
        self.order_counter = 0
        
        DebugUtils.info(f"PaperBroker initialized with ${initial_capital:,.2f}")
    
    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place a paper order.
        
        Args:
            order: Order dictionary
            
        Returns:
            Order result dictionary
        """
        self.order_counter += 1
        order_id = f"PAPER_{self.order_counter}"
        
        symbol = order['symbol']
        side = order['side']  # "buy" or "sell"
        quantity = order['quantity']
        order_type = order.get('order_type', 'market')
        limit_price = order.get('limit_price')
        
        # Get current price (simulated)
        current_price = order.get('price', 100.0)
        
        # Simulate slippage (0.1% to 0.5%)
        slippage = random.uniform(0.001, 0.005)
        if side == "buy":
            fill_price = current_price * (1 + slippage)
        else:
            fill_price = current_price * (1 - slippage)
        
        # For limit orders, check if price is acceptable
        if order_type == "limit" and limit_price:
            if side == "buy" and fill_price > limit_price:
                return {
                    'order_id': order_id,
                    'status': 'rejected',
                    'reason': 'Limit price not met'
                }
            elif side == "sell" and fill_price < limit_price:
                return {
                    'order_id': order_id,
                    'status': 'rejected',
                    'reason': 'Limit price not met'
                }
            fill_price = limit_price
        
        # Calculate cost
        cost = fill_price * quantity
        
        # Check if we have enough cash for buy orders
        if side == "buy" and cost > self.cash:
            return {
                'order_id': order_id,
                'status': 'rejected',
                'reason': 'Insufficient funds'
            }
        
        # Execute the order
        if side == "buy":
            self.cash -= cost
            if symbol in self.positions:
                # Add to existing position
                pos = self.positions[symbol]
                total_cost = (pos['avg_price'] * pos['quantity'] + cost)
                total_quantity = pos['quantity'] + quantity
                pos['avg_price'] = total_cost / total_quantity
                pos['quantity'] = total_quantity
            else:
                # New position
                self.positions[symbol] = {
                    'symbol': symbol,
                    'quantity': quantity,
                    'avg_price': fill_price,
                    'entry_date': datetime.now()
                }
        else:  # sell
            if symbol not in self.positions or self.positions[symbol]['quantity'] < quantity:
                return {
                    'order_id': order_id,
                    'status': 'rejected',
                    'reason': 'Insufficient shares'
                }
            
            # Update position
            pos = self.positions[symbol]
            pos['quantity'] -= quantity
            self.cash += fill_price * quantity
            
            # Remove position if fully closed
            if pos['quantity'] == 0:
                del self.positions[symbol]
        
        # Store order
        self.orders[order_id] = {
            'order_id': order_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'fill_price': fill_price,
            'status': 'filled',
            'filled_at': datetime.now()
        }
        
        DebugUtils.info(f"Paper order filled: {side} {quantity} {symbol} @ ${fill_price:.2f}")
        
        return {
            'order_id': order_id,
            'status': 'filled',
            'fill_price': fill_price,
            'filled_quantity': quantity,
            'filled_at': datetime.now().isoformat()
        }
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order (not applicable for paper trading - orders fill immediately)."""
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'cancelled'
            return True
        return False
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current position for symbol."""
        return self.positions.get(symbol)
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        positions_value = sum(
            pos['quantity'] * 100.0  # Simplified: use fixed price for valuation
            for pos in self.positions.values()
        )
        
        return {
            'cash': self.cash,
            'positions_value': positions_value,
            'total_value': self.cash + positions_value,
            'buying_power': self.cash,
            'initial_capital': self.initial_capital
        }
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status."""
        return self.orders.get(order_id, {'status': 'not_found'})

