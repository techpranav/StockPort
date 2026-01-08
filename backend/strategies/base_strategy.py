"""
Base Strategy Class

Abstract base class for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from models.opportunity import Opportunity
from models.strategy_signal import StrategySignal, StrategyCondition


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    
    All strategies must implement:
    - evaluate(): Evaluate opportunity against strategy
    - get_entry_conditions(): Get entry conditions
    - get_exit_conditions(): Get exit conditions
    """
    
    def __init__(
        self,
        strategy_id: str,
        name: str,
        strategy_type: str,
        status: str = "active"
    ):
        """
        Initialize strategy.
        
        Args:
            strategy_id: Unique strategy identifier
            name: Strategy name
            strategy_type: Strategy type (trend_following, momentum, etc.)
            status: Strategy status (active, paused, disabled)
        """
        self.strategy_id = strategy_id
        self.name = name
        self.strategy_type = strategy_type
        self.status = status
        self.market_regimes: List[str] = []
        self.exclude_regimes: List[str] = []
    
    def get_id(self) -> str:
        """Get strategy ID."""
        return self.strategy_id
    
    def get_status(self) -> str:
        """Get strategy status."""
        return self.status
    
    def set_status(self, status: str):
        """Set strategy status."""
        self.status = status
    
    def is_applicable(self, market_regime: str) -> bool:
        """
        Check if strategy is applicable to current market regime.
        
        Args:
            market_regime: Current market regime
            
        Returns:
            True if applicable, False otherwise
        """
        if market_regime in self.exclude_regimes:
            return False
        
        if self.market_regimes:
            return market_regime in self.market_regimes
        
        return True
    
    @abstractmethod
    def evaluate(
        self,
        opportunity: Opportunity,
        market_state: Optional[Dict[str, Any]] = None
    ) -> Optional[StrategySignal]:
        """
        Evaluate opportunity against strategy.
        
        Args:
            opportunity: Opportunity to evaluate
            market_state: Current market state (optional)
            
        Returns:
            StrategySignal if opportunity matches, None otherwise
        """
        pass
    
    @abstractmethod
    def get_entry_conditions(self) -> List[Dict[str, Any]]:
        """
        Get entry conditions for this strategy.
        
        Returns:
            List of condition dictionaries
        """
        pass
    
    @abstractmethod
    def get_exit_conditions(self) -> Dict[str, Any]:
        """
        Get exit conditions for this strategy.
        
        Returns:
            Exit conditions dictionary
        """
        pass

