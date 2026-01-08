"""
Execution Engine

Main execution engine for order management.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from utils.debug_utils import DebugUtils
from models.trading_decision import TradingDecision
from backend.execution.order_manager import OrderManager
from backend.execution.brokers.base_broker import BaseBroker
from backend.learning.performance_tracker import PerformanceTracker
from typing import Optional
from backend.execution.safety_checks import SafetyChecks
from backend.governance.audit_logger import AuditLogger


class ExecutionEngine:
    """
    Main execution engine.
    
    Responsibilities:
    - Convert decisions to orders
    - Execute orders via broker
    - Handle order lifecycle
    - Track execution results
    """
    
    def __init__(
        self,
        broker: BaseBroker,
        order_manager: Optional[OrderManager] = None,
        safety_checks: Optional[SafetyChecks] = None,
        performance_tracker: Optional[PerformanceTracker] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize execution engine.
        
        Args:
            broker: Broker instance
            order_manager: Order manager instance
            safety_checks: Safety checks instance
            performance_tracker: Performance tracker instance (optional)
            audit_logger: Audit logger instance (optional)
        """
        self.broker = broker
        self.order_manager = order_manager or OrderManager()
        self.safety_checks = safety_checks or SafetyChecks()
        self.performance_tracker = performance_tracker
        self.audit_logger = audit_logger
    
    def execute_decision(self, decision: TradingDecision) -> Dict[str, Any]:
        """
        Execute a trading decision.
        
        Args:
            decision: Trading decision
            
        Returns:
            Execution result dictionary
        """
        # Check if decision is approved
        if decision.decision != "APPROVE":
            return {
                'success': False,
                'reason': f"Decision not approved: {decision.decision}",
                'decision_id': decision.decision_id
            }
        
        # Run safety checks
        safety_result = self.safety_checks.check_before_execution(decision)
        if not safety_result['approved']:
            return {
                'success': False,
                'reason': f"Safety check failed: {safety_result.get('reason', 'Unknown')}",
                'decision_id': decision.decision_id
            }
        
        # Create order
        order = {
            'symbol': decision.symbol,
            'side': 'buy',  # Assuming buy for now
            'quantity': int(decision.position_size['shares']),
            'order_type': 'market',
            'strategy_id': decision.strategy_id,
            'signal_id': decision.signal.signal_id,
            'decision_id': decision.decision_id,
            'risk_justification': {
                'risk_amount': decision.risk_amount,
                'risk_percent': decision.risk_percent,
                'risk_reward_ratio': decision.risk_reward_ratio
            },
            'timestamp': datetime.now()
        }
        
        # Place order via broker
        try:
            result = self.broker.place_order(order)
            
            # Track order
            self.order_manager.track_order(decision.decision_id, order, result)
            
            DebugUtils.info(
                f"Order executed: {order['side']} {order['quantity']} {order['symbol']} "
                f"@ ${result.get('fill_price', 0):.2f}"
            )
            
            return {
                'success': True,
                'order_id': result.get('order_id'),
                'fill_price': result.get('fill_price'),
                'filled_quantity': result.get('filled_quantity'),
                'decision_id': decision.decision_id
            }
        except Exception as e:
            DebugUtils.log_error(e, f"Error executing order for {decision.symbol}")
            return {
                'success': False,
                'reason': str(e),
                'decision_id': decision.decision_id
            }
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.broker.cancel_order(order_id)
            self.order_manager.update_order_status(order_id, 'cancelled')
            return result
        except Exception as e:
            DebugUtils.log_error(e, f"Error cancelling order {order_id}")
            return False

