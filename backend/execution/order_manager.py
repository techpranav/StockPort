"""
Order Manager

Manages order lifecycle and tracking.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

from utils.debug_utils import DebugUtils


class OrderManager:
    """
    Manages order lifecycle.
    
    Tracks:
    - Order status
    - Order history
    - Fill details
    """
    
    def __init__(self):
        """Initialize order manager."""
        self.orders: Dict[str, Dict[str, Any]] = {}  # order_id -> order
        self.order_history: List[Dict[str, Any]] = []
    
    def track_order(self, decision_id: str, order: Dict[str, Any], result: Dict[str, Any]):
        """
        Track an order.
        
        Args:
            decision_id: Decision identifier
            order: Order dictionary
            result: Execution result
        """
        order_id = result.get('order_id', decision_id)
        
        order_record = {
            'order_id': order_id,
            'decision_id': decision_id,
            'symbol': order['symbol'],
            'side': order['side'],
            'quantity': order['quantity'],
            'order_type': order['order_type'],
            'status': result.get('status', 'pending'),
            'fill_price': result.get('fill_price'),
            'filled_quantity': result.get('filled_quantity'),
            'created_at': order.get('timestamp', datetime.now()),
            'filled_at': datetime.now() if result.get('status') == 'filled' else None
        }
        
        self.orders[order_id] = order_record
        self.order_history.append(order_record)
        
        # Keep only last 1000 orders in history
        if len(self.order_history) > 1000:
            self.order_history = self.order_history[-1000:]
    
    def update_order_status(self, order_id: str, status: str):
        """
        Update order status.
        
        Args:
            order_id: Order identifier
            status: New status
        """
        if order_id in self.orders:
            self.orders[order_id]['status'] = status
            if status == 'filled':
                self.orders[order_id]['filled_at'] = datetime.now()
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get order by ID.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order dictionary or None
        """
        return self.orders.get(order_id)
    
    def get_pending_orders(self) -> List[Dict[str, Any]]:
        """Get all pending orders."""
        return [
            order for order in self.orders.values()
            if order['status'] in ['pending', 'submitted']
        ]
    
    def get_order_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get order history.
        
        Args:
            limit: Maximum number of orders to return
            
        Returns:
            List of order dictionaries
        """
        return self.order_history[-limit:]

