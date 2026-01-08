"""
Strategy Registry

Manages strategy registration and retrieval.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

from utils.debug_utils import DebugUtils
from backend.strategies.base_strategy import BaseStrategy


class StrategyRegistry:
    """
    Registry for trading strategies.
    
    Manages:
    - Strategy registration
    - Strategy retrieval
    - Strategy status (active, paused, disabled)
    """
    
    def __init__(self):
        """Initialize strategy registry."""
        self.strategies: Dict[str, BaseStrategy] = {}
        self.strategy_status: Dict[str, str] = {}  # strategy_id -> status
    
    def register(self, strategy: BaseStrategy):
        """
        Register a strategy.
        
        Args:
            strategy: Strategy instance to register
        """
        strategy_id = strategy.get_id()
        self.strategies[strategy_id] = strategy
        self.strategy_status[strategy_id] = strategy.get_status()
        
        DebugUtils.info(f"Registered strategy: {strategy_id}")
    
    def get(self, strategy_id: str) -> Optional[BaseStrategy]:
        """
        Get a strategy by ID.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Strategy instance or None
        """
        return self.strategies.get(strategy_id)
    
    def get_all(self) -> List[BaseStrategy]:
        """Get all registered strategies."""
        return list(self.strategies.values())
    
    def get_active(self) -> List[BaseStrategy]:
        """Get all active strategies."""
        return [
            strategy for strategy in self.strategies.values()
            if self.strategy_status.get(strategy.get_id()) == "active"
        ]
    
    def set_status(self, strategy_id: str, status: str):
        """
        Set strategy status.
        
        Args:
            strategy_id: Strategy identifier
            status: Status ("active", "paused", "disabled")
        """
        if strategy_id in self.strategies:
            self.strategy_status[strategy_id] = status
            DebugUtils.info(f"Strategy {strategy_id} status set to {status}")
    
    def remove(self, strategy_id: str):
        """
        Remove a strategy from registry.
        
        Args:
            strategy_id: Strategy identifier
        """
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            del self.strategy_status[strategy_id]
            DebugUtils.info(f"Removed strategy: {strategy_id}")

