"""
Position Sizer

Calculates position sizes based on risk.
"""

from typing import Dict, Any
from utils.debug_utils import DebugUtils
from backend.settings import get_settings


class PositionSizer:
    """
    Calculates position sizes based on risk.
    
    Methods:
    - Risk-based sizing (default)
    - Fixed amount
    - Volatility-based
    
    Settings are loaded from SettingsManager and update in real-time.
    """
    
    def __init__(
        self,
        risk_per_trade: float = None,  # Will use settings if None
        max_position_size: float = None  # Will use settings if None
    ):
        """
        Initialize position sizer.
        
        Args:
            risk_per_trade: Percentage of capital to risk per trade (uses settings if None)
            max_position_size: Maximum position size as percentage of capital (uses settings if None)
        """
        self.settings = get_settings()
        
        # Subscribe to settings changes for real-time updates
        self.settings.subscribe('trading.default_risk_per_trade', self._on_risk_per_trade_changed)
        self.settings.subscribe('trading.max_position_size_percent', self._on_max_position_changed)
        
        # Initialize with settings or provided values
        self._risk_per_trade = risk_per_trade
        self._max_position_size = max_position_size
        self._update_from_settings()
    
    def _update_from_settings(self):
        """Update values from settings."""
        if self._risk_per_trade is None:
            self._risk_per_trade = self.settings.get_default_risk_per_trade()
        if self._max_position_size is None:
            self._max_position_size = self.settings.get_max_position_size_percent()
    
    def _on_risk_per_trade_changed(self, key: str, old_value: float, new_value: float):
        """Handle risk per trade setting change."""
        self._risk_per_trade = new_value
        DebugUtils.info(f"PositionSizer: Risk per trade updated to {new_value:.1%}")
    
    def _on_max_position_changed(self, key: str, old_value: float, new_value: float):
        """Handle max position size setting change."""
        self._max_position_size = new_value
        DebugUtils.info(f"PositionSizer: Max position size updated to {new_value:.1%}")
    
    @property
    def risk_per_trade(self) -> float:
        """Get current risk per trade (from settings)."""
        if self._risk_per_trade is None:
            self._risk_per_trade = self.settings.get_default_risk_per_trade()
        return self._risk_per_trade
    
    @property
    def max_position_size(self) -> float:
        """Get current max position size (from settings)."""
        if self._max_position_size is None:
            self._max_position_size = self.settings.get_max_position_size_percent()
        return self._max_position_size
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        available_capital: float,
        method: str = "risk_based"
    ) -> Dict[str, float]:
        """
        Calculate position size based on risk.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            available_capital: Available capital
            method: Sizing method ("risk_based", "fixed_amount", "volatility_based")
            
        Returns:
            Dictionary with shares, notional, risk_amount
        """
        if method == "risk_based":
            return self._calculate_risk_based(entry_price, stop_loss, available_capital)
        elif method == "fixed_amount":
            return self._calculate_fixed(entry_price, available_capital)
        else:
            return self._calculate_risk_based(entry_price, stop_loss, available_capital)
    
    def _calculate_risk_based(
        self,
        entry_price: float,
        stop_loss: float,
        available_capital: float
    ) -> Dict[str, float]:
        """Calculate risk-based position size."""
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return {'shares': 0, 'notional': 0, 'risk_amount': 0}
        
        # Risk amount for this trade
        risk_amount = available_capital * self.risk_per_trade
        
        # Number of shares based on risk
        shares = int(risk_amount / risk_per_share)
        
        # Dollar amount to invest
        notional = shares * entry_price
        
        # Apply max position size limit
        max_notional = available_capital * self.max_position_size
        if notional > max_notional:
            shares = int(max_notional / entry_price)
            notional = shares * entry_price
            risk_amount = shares * risk_per_share
        
        return {
            'shares': shares,
            'notional': notional,
            'risk_amount': risk_amount
        }
    
    def _calculate_fixed(
        self,
        entry_price: float,
        available_capital: float
    ) -> Dict[str, float]:
        """Calculate fixed amount position size."""
        fixed_amount = available_capital * 0.05  # 5% fixed
        shares = int(fixed_amount / entry_price)
        notional = shares * entry_price
        
        return {
            'shares': shares,
            'notional': notional,
            'risk_amount': notional  # Full amount at risk for fixed
        }

