"""
Base Broker Interface

Abstract base class for all broker adapters.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime


class BaseBroker(ABC):
    """Abstract broker interface."""
    
    @abstractmethod
    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place an order.
        
        Args:
            order: Order dictionary with symbol, side, quantity, etc.
            
        Returns:
            Order result dictionary
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current position for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Position dictionary or None if no position
        """
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Account info dictionary with balance, buying power, etc.
        """
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order status dictionary
        """
        pass

