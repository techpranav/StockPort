"""
Capital Manager

Tracks available capital in real-time.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from threading import Lock

from utils.debug_utils import DebugUtils
from backend.settings import get_settings


class CapitalManager:
    """
    Manages capital tracking.
    
    Tracks:
    - Total capital
    - Allocated capital (open positions)
    - Reserved capital (pending orders)
    - Available capital
    
    Initial capital and cash reserve are configurable via SettingsManager.
    """
    
    def __init__(self, initial_capital: float = None):
        """
        Initialize capital manager.
        
        Args:
            initial_capital: Initial capital amount (uses settings if None)
        """
        self.settings = get_settings()
        
        # Subscribe to settings changes
        self.settings.subscribe('capital.initial_capital', self._on_initial_capital_changed)
        self.settings.subscribe('capital.cash_reserve_percent', self._on_cash_reserve_changed)
        
        # Initialize from settings or provided value
        if initial_capital is None:
            initial_capital = self.settings.get_initial_capital()
        
        self.initial_capital = initial_capital
        self.total_capital = initial_capital
        self.allocated_capital = 0.0
        self.reserved_capital: Dict[str, float] = {}  # order_id -> amount
        self._cash_reserve_percent = None
        self.lock = Lock()
        
        self._update_from_settings()
        DebugUtils.info(f"CapitalManager initialized with ${initial_capital:,.2f}")
    
    def _update_from_settings(self):
        """Update values from settings."""
        self._cash_reserve_percent = self.settings.get_cash_reserve_percent()
    
    def _on_initial_capital_changed(self, key: str, old_value: float, new_value: float):
        """Handle initial capital change (adjusts total capital)."""
        diff = new_value - self.initial_capital
        self.initial_capital = new_value
        self.total_capital += diff
        DebugUtils.info(f"CapitalManager: Initial capital updated to ${new_value:,.2f}")
    
    def _on_cash_reserve_changed(self, key: str, old_value: float, new_value: float):
        """Handle cash reserve percent change."""
        self._cash_reserve_percent = new_value
        DebugUtils.info(f"CapitalManager: Cash reserve percent updated to {new_value:.1%}")
    
    def get_cash_reserve_percent(self) -> float:
        """Get current cash reserve percent."""
        if self._cash_reserve_percent is None:
            self._cash_reserve_percent = self.settings.get_cash_reserve_percent()
        return self._cash_reserve_percent
    
    def get_total_capital(self) -> float:
        """Get total capital."""
        return self.total_capital
    
    def get_allocated_capital(self) -> float:
        """Get allocated capital (open positions)."""
        return self.allocated_capital
    
    def get_reserved_capital(self) -> float:
        """Get reserved capital (pending orders)."""
        return sum(self.reserved_capital.values())
    
    def get_available_capital(self) -> float:
        """
        Get free capital available for new positions.
        
        Returns:
            Available capital amount
        """
        with self.lock:
            return self.total_capital - self.allocated_capital - self.get_reserved_capital()
    
    def allocate_capital(self, amount: float, order_id: str):
        """
        Reserve capital for pending order.
        
        Args:
            amount: Amount to reserve
            order_id: Order identifier
        """
        with self.lock:
            available = self.get_available_capital()
            if amount > available:
                raise ValueError(f"Insufficient capital: requested ${amount:,.2f}, available ${available:,.2f}")
            
            self.reserved_capital[order_id] = amount
            DebugUtils.debug(f"Reserved ${amount:,.2f} for order {order_id}")
    
    def release_capital(self, order_id: str):
        """
        Release reserved capital on order fill/cancel.
        
        Args:
            order_id: Order identifier
        """
        with self.lock:
            if order_id in self.reserved_capital:
                amount = self.reserved_capital.pop(order_id)
                DebugUtils.debug(f"Released ${amount:,.2f} for order {order_id}")
    
    def update_allocated(self, allocated: float):
        """
        Update allocated capital (from positions).
        
        Args:
            allocated: New allocated capital amount
        """
        with self.lock:
            self.allocated_capital = allocated
    
    def update_total(self, total: float):
        """
        Update total capital (from broker account).
        
        Args:
            total: New total capital amount
        """
        with self.lock:
            self.total_capital = total
    
    def get_capital_state(self) -> Dict[str, float]:
        """
        Get current capital state.
        
        Returns:
            Dictionary with capital breakdown
        """
        return {
            'total': self.total_capital,
            'allocated': self.allocated_capital,
            'reserved': self.get_reserved_capital(),
            'available': self.get_available_capital()
        }

