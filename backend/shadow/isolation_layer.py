"""
Isolation Layer

Prevents shadow leakage into live trading.
"""

from typing import Dict, Any
from utils.debug_utils import DebugUtils


class IsolationLayer:
    """
    Prevents shadow strategies from executing live trades.
    """
    
    def __init__(self):
        """Initialize isolation layer."""
        self.shadow_strategies: set = set()  # Set of shadow strategy IDs
    
    def register_shadow_strategy(self, strategy_id: str):
        """
        Register a strategy as shadow-only.
        
        Args:
            strategy_id: Strategy identifier
        """
        self.shadow_strategies.add(strategy_id)
        DebugUtils.info(f"Registered shadow strategy: {strategy_id}")
    
    def is_shadow_strategy(self, strategy_id: str) -> bool:
        """
        Check if strategy is shadow-only.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            True if shadow-only, False otherwise
        """
        return strategy_id in self.shadow_strategies
    
    def prevent_shadow_leakage(self, order: Dict[str, Any]):
        """
        Prevent shadow orders from executing live.
        
        Args:
            order: Order dictionary
            
        Raises:
            IsolationError: If shadow strategy attempts live execution
        """
        strategy_id = order.get('strategy_id')
        broker_type = order.get('broker', 'live')
        
        if self.is_shadow_strategy(strategy_id):
            if broker_type != 'shadow':
                raise IsolationError(
                    f"Shadow strategy {strategy_id} attempted live execution"
                )


class IsolationError(Exception):
    """Exception raised when shadow leakage is detected."""
    pass

