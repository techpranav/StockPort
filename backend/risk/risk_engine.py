"""
Risk Engine

Main risk engine for risk limit enforcement.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from utils.debug_utils import DebugUtils
from backend.risk.limits import RiskLimits
from backend.risk.correlation import CorrelationChecker
from backend.risk.kill_switch import KillSwitch


class RiskEngine:
    """
    Main risk engine.
    
    Responsibilities:
    - Enforce risk limits
    - Check correlations
    - Monitor drawdown
    - Enforce kill-switch
    """
    
    def __init__(
        self,
        risk_limits: Optional[RiskLimits] = None,
        correlation_checker: Optional[CorrelationChecker] = None,
        kill_switch: Optional[KillSwitch] = None
    ):
        """
        Initialize risk engine.
        
        Args:
            risk_limits: Risk limits instance
            correlation_checker: Correlation checker instance
            kill_switch: Kill switch instance
        """
        self.risk_limits = risk_limits or RiskLimits()
        self.correlation_checker = correlation_checker or CorrelationChecker()
        self.kill_switch = kill_switch or KillSwitch()
        
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.last_reset_date = datetime.now().date()
    
    def check_risk(
        self,
        symbol: str,
        risk_amount: float,
        position_size: Dict[str, float],
        existing_positions: List[Dict[str, Any]],
        sector: str
    ) -> Dict[str, Any]:
        """
        Check if trade passes risk limits.
        
        Args:
            symbol: Stock symbol
            risk_amount: Dollar amount at risk
            position_size: Position size dictionary
            existing_positions: List of existing positions
            sector: Sector of the stock
            
        Returns:
            Dictionary with approval status and reasoning
        """
        # Check kill-switch
        if self.kill_switch.is_active():
            return {
                'approved': False,
                'reason': 'Kill-switch is active'
            }
        
        # Reset daily counters if new day
        self._reset_daily_counters_if_needed()
        
        # Check per-trade risk
        if not self.risk_limits.check_per_trade_risk(risk_amount):
            return {
                'approved': False,
                'reason': 'Per-trade risk limit exceeded'
            }
        
        # Check daily loss limit
        if not self.risk_limits.check_daily_loss(self.daily_pnl):
            return {
                'approved': False,
                'reason': 'Daily loss limit exceeded'
            }
        
        # Check daily trade limit
        if not self.risk_limits.check_daily_trades(self.daily_trades):
            return {
                'approved': False,
                'reason': 'Daily trade limit exceeded'
            }
        
        # Check position size
        if not self.risk_limits.check_position_size(position_size['notional']):
            return {
                'approved': False,
                'reason': 'Position size limit exceeded'
            }
        
        # Check sector exposure
        if not self.risk_limits.check_sector_exposure(sector, existing_positions):
            return {
                'approved': False,
                'reason': 'Sector exposure limit exceeded'
            }
        
        # Check correlation
        correlation_result = self.correlation_checker.check_correlation(
            symbol, existing_positions
        )
        if not correlation_result['approved']:
            return correlation_result
        
        return {
            'approved': True,
            'reason': 'All risk checks passed'
        }
    
    def record_trade(self, pnl: float):
        """
        Record a trade for daily tracking.
        
        Args:
            pnl: Profit/loss from trade
        """
        self._reset_daily_counters_if_needed()
        self.daily_pnl += pnl
        self.daily_trades += 1
    
    def _reset_daily_counters_if_needed(self):
        """Reset daily counters if new day."""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.last_reset_date = today
            DebugUtils.debug("Reset daily risk counters")

