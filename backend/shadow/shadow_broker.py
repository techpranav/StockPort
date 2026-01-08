"""
Shadow Broker

Paper trading broker for shadow trading.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import random
import uuid

from backend.execution.brokers.base_broker import BaseBroker, Order, Position, AccountInfo, OrderResult
from utils.debug_utils import DebugUtils


class ShadowBroker(BaseBroker):
    """
    Shadow broker for paper trading.
    
    Simulates execution with realistic slippage.
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize shadow broker.
        
        Args:
            initial_capital: Initial virtual capital
        """
        self.cash = initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.order_counter = 0
    
    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place shadow order.
        
        Args:
            order: Order dictionary with symbol, side, quantity, price, etc.
            
        Returns:
            Order result dictionary
        """
        self.order_counter += 1
        order_id = f"SHADOW_{self.order_counter}"
        
        symbol = order.get('symbol', '')
        side = order.get('side', 'buy')
        quantity = order.get('quantity', 0)
        price = order.get('price', 100.0)
        
        # Simulate slippage
        slippage = random.uniform(0.001, 0.005)
        if side == "buy":
            fill_price = price * (1 + slippage)
        else:
            fill_price = price * (1 - slippage)
        
        # Execute
        cost = fill_price * quantity
        if side == "buy":
            self.cash -= cost
            if symbol in self.positions:
                pos = self.positions[symbol]
                total_cost = (pos['avg_price'] * pos['quantity'] + cost)
                total_quantity = pos['quantity'] + quantity
                pos['avg_price'] = total_cost / total_quantity
                pos['quantity'] = total_quantity
            else:
                self.positions[symbol] = {
                    'symbol': symbol,
                    'quantity': quantity,
                    'avg_price': fill_price,
                    'entry_date': datetime.now()
                }
        else:  # sell
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos['quantity'] -= quantity
                self.cash += fill_price * quantity
                if pos['quantity'] == 0:
                    del self.positions[symbol]
        
        self.orders[order_id] = {
            'order_id': order_id,
            'status': 'filled',
            'fill_price': fill_price,
            'filled_quantity': quantity
        }
        
        return {
            'order_id': order_id,
            'status': 'filled',
            'fill_price': fill_price,
            'filled_quantity': quantity
        }
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel shadow order."""
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'cancelled'
            return True
        return False
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get shadow position.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Position dictionary or None
        """
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> List[Dict[str, Any]]:
        """Get all shadow positions."""
        return list(self.positions.values())
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get shadow account info.
        
        Returns:
            Account info dictionary
        """
        # Calculate positions value (would use current market prices in real system)
        positions_value = sum(
            pos.get('quantity', 0) * pos.get('avg_price', 0)
            for pos in self.positions.values()
        )
        
        return {
            'cash': self.cash,
            'positions_value': positions_value,
            'total_value': self.cash + positions_value,
            'buying_power': self.cash
        }
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get shadow order status.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order status dictionary
        """
        return self.orders.get(order_id, {'status': 'not_found', 'order_id': order_id})

