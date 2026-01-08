"""
State Recovery

Recovers system state after crashes.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.debug_utils import DebugUtils
from backend.core.state_manager import StateManager
from backend.execution.brokers.base_broker import BaseBroker
from backend.execution.order_manager import OrderManager


class StateRecovery:
    """
    Recovers system state after crashes.
    
    Recovers:
    - Open positions
    - Pending orders
    - Capital state
    - Strategy states
    """
    
    def __init__(
        self,
        state_manager: StateManager,
        broker: Optional[BaseBroker] = None,
        order_manager: Optional[OrderManager] = None
    ):
        """
        Initialize state recovery.
        
        Args:
            state_manager: State manager instance
            broker: Broker instance
            order_manager: Order manager instance
        """
        self.state_manager = state_manager
        self.broker = broker
        self.order_manager = order_manager
    
    def recover_after_crash(self) -> Dict[str, Any]:
        """
        Recover system state after crash.
        
        Returns:
            Recovery result dictionary
        """
        DebugUtils.info("Starting state recovery after crash")
        
        # Load persistent state
        system_state = self.state_manager.load_system_state()
        
        # Recover positions
        positions = self._recover_positions()
        
        # Recover pending orders
        pending_orders = self._recover_pending_orders()
        
        # Reconstruct capital state
        capital_state = self._reconstruct_capital(positions)
        
        DebugUtils.info("State recovery completed")
        
        return {
            'positions': positions,
            'pending_orders': pending_orders,
            'capital_state': capital_state,
            'system_state': system_state
        }
    
    def _recover_positions(self) -> List[Dict[str, Any]]:
        """Recover positions from broker."""
        positions = []
        
        if self.broker:
            try:
                # Get all positions from broker
                # This would iterate through all symbols or use broker API
                # Simplified for now
                pass
            except Exception as e:
                DebugUtils.log_error(e, "Error recovering positions from broker")
        
        return positions
    
    def _recover_pending_orders(self) -> List[Dict[str, Any]]:
        """Recover pending orders."""
        if self.order_manager:
            return self.order_manager.get_pending_orders()
        return []
    
    def _reconstruct_capital(self, positions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Reconstruct capital state."""
        allocated = sum(pos.get('value', 0) for pos in positions)
        
        return {
            'allocated': allocated,
            'available': 100000.0 - allocated  # Simplified
        }

