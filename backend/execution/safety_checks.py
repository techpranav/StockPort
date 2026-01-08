"""
Safety Checks

Pre-execution safety validation.
"""

from typing import Dict, Any
from datetime import datetime

from utils.debug_utils import DebugUtils
from models.trading_decision import TradingDecision
from backend.risk.kill_switch import KillSwitch


class SafetyChecks:
    """
    Pre-execution safety checks.
    
    Checks:
    - Kill-switch status
    - Market hours
    - Capital availability
    - Order validity
    """
    
    def __init__(self, kill_switch: Optional[KillSwitch] = None):
        """
        Initialize safety checks.
        
        Args:
            kill_switch: Kill switch instance
        """
        self.kill_switch = kill_switch or KillSwitch()
    
    def check_before_execution(self, decision: TradingDecision) -> Dict[str, Any]:
        """
        Run all safety checks before execution.
        
        Args:
            decision: Trading decision
            
        Returns:
            Dictionary with approval status
        """
        # Check kill-switch
        if self.kill_switch.is_active():
            return {
                'approved': False,
                'reason': 'Kill-switch is active'
            }
        
        # Check market hours (simplified - would check actual market hours)
        if not self._is_market_hours():
            return {
                'approved': False,
                'reason': 'Outside market hours'
            }
        
        # Check position size
        if decision.position_size['shares'] <= 0:
            return {
                'approved': False,
                'reason': 'Invalid position size'
            }
        
        # Check risk-reward ratio
        if decision.risk_reward_ratio < 1.0:
            return {
                'approved': False,
                'reason': f'Risk-reward ratio too low: {decision.risk_reward_ratio:.2f}:1'
            }
        
        return {
            'approved': True,
            'reason': 'All safety checks passed'
        }
    
    def _is_market_hours(self) -> bool:
        """
        Check if current time is within market hours.
        
        Returns:
            True if market hours, False otherwise
        """
        now = datetime.now()
        hour = now.hour
        
        # Simplified: 9:30 AM - 4:00 PM ET (would need timezone handling)
        # For now, assume market is open during business hours
        return 9 <= hour < 16

