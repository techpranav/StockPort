"""
Safe Shutdown

Handles graceful shutdown of the system.
"""

from typing import Dict, Any, List
from datetime import datetime
import signal
import sys

from utils.debug_utils import DebugUtils
from backend.core.state_manager import StateManager
from backend.execution.order_manager import OrderManager
from backend.execution.brokers.base_broker import BaseBroker


class SafeShutdown:
    """
    Handles graceful shutdown.
    
    Process:
    1. Stop accepting new signals
    2. Complete in-flight operations
    3. Cancel pending orders (optional)
    4. Save state
    5. Close connections
    """
    
    def __init__(
        self,
        state_manager: StateManager,
        order_manager: Optional[OrderManager] = None,
        broker: Optional[BaseBroker] = None
    ):
        """
        Initialize safe shutdown handler.
        
        Args:
            state_manager: State manager instance
            order_manager: Order manager instance
            broker: Broker instance
        """
        self.state_manager = state_manager
        self.order_manager = order_manager
        self.broker = broker
        self.is_shutting_down = False
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        DebugUtils.warning(f"Received signal {signum}, initiating shutdown")
        self.shutdown()
        sys.exit(0)
    
    def shutdown(self, cancel_orders: bool = False):
        """
        Perform graceful shutdown.
        
        Args:
            cancel_orders: Whether to cancel pending orders
        """
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        DebugUtils.info("Starting graceful shutdown")
        
        # 1. Stop accepting new signals (handled by engine)
        
        # 2. Complete in-flight operations (wait briefly)
        import time
        time.sleep(2)  # Wait for in-flight operations
        
        # 3. Cancel pending orders if requested
        if cancel_orders and self.order_manager and self.broker:
            pending_orders = self.order_manager.get_pending_orders()
            for order in pending_orders:
                try:
                    self.broker.cancel_order(order['order_id'])
                except Exception as e:
                    DebugUtils.log_error(e, f"Error cancelling order {order['order_id']}")
        
        # 4. Save state
        self.state_manager.save_system_state({
            'status': 'stopped',
            'stopped_at': datetime.now().isoformat()
        })
        
        # 5. Close connections (handled by individual components)
        
        DebugUtils.info("Graceful shutdown completed")

