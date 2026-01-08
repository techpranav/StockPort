"""
Kill Switch

Emergency stop mechanism for trading.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from threading import Lock

from utils.debug_utils import DebugUtils


class KillSwitch:
    """
    Kill switch for emergency stops.
    
    Activation triggers:
    - Manual activation
    - Portfolio drawdown > 30%
    - Daily loss > 10%
    - System error detected
    """
    
    def __init__(self):
        """Initialize kill switch."""
        self.is_active_flag = False
        self.activation_reason: Optional[str] = None
        self.activated_at: Optional[datetime] = None
        self.lock = Lock()
    
    def activate(self, reason: str = "Manual activation"):
        """
        Activate kill switch.
        
        Args:
            reason: Reason for activation
        """
        with self.lock:
            self.is_active_flag = True
            self.activation_reason = reason
            self.activated_at = datetime.now()
            
            DebugUtils.warning(f"KILL SWITCH ACTIVATED: {reason}")
    
    def deactivate(self):
        """Deactivate kill switch."""
        with self.lock:
            self.is_active_flag = False
            self.activation_reason = None
            self.activated_at = None
            
            DebugUtils.info("Kill switch deactivated")
    
    def is_active(self) -> bool:
        """
        Check if kill switch is active.
        
        Returns:
            True if active, False otherwise
        """
        with self.lock:
            return self.is_active_flag
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get kill switch status.
        
        Returns:
            Dictionary with status information
        """
        with self.lock:
            return {
                'is_active': self.is_active_flag,
                'reason': self.activation_reason,
                'activated_at': self.activated_at.isoformat() if self.activated_at else None
            }
    
    def check_drawdown(self, drawdown_percent: float):
        """
        Check drawdown and activate if threshold exceeded.
        
        Args:
            drawdown_percent: Current drawdown percentage
        """
        if drawdown_percent > 0.30:  # 30%
            if not self.is_active():
                self.activate(f"Portfolio drawdown exceeded: {drawdown_percent:.1%}")
    
    def check_daily_loss(self, daily_loss_percent: float):
        """
        Check daily loss and activate if threshold exceeded.
        
        Args:
            daily_loss_percent: Daily loss percentage
        """
        if daily_loss_percent > 0.10:  # 10%
            if not self.is_active():
                self.activate(f"Daily loss exceeded: {daily_loss_percent:.1%}")

