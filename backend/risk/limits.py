"""
Risk Limits

Defines and enforces risk limits.
"""

from typing import Dict, Any, List

from utils.debug_utils import DebugUtils
from backend.settings import get_settings


class RiskLimits:
    """
    Defines and enforces risk limits.
    
    All limits are configurable via SettingsManager and update in real-time.
    """
    
    def __init__(
        self,
        max_risk_per_trade: float = None,  # Uses settings if None
        max_daily_loss: float = None,  # Uses settings if None
        max_daily_trades: int = None,  # Uses settings if None
        max_position_size: float = None,  # Uses settings if None
        max_sector_exposure: float = None  # Uses settings if None
    ):
        """
        Initialize risk limits.
        
        Args:
            max_risk_per_trade: Maximum risk per trade as percentage (uses settings if None)
            max_daily_loss: Maximum daily loss as percentage (uses settings if None)
            max_daily_trades: Maximum trades per day (uses settings if None)
            max_position_size: Maximum position size as percentage (uses settings if None)
            max_sector_exposure: Maximum sector exposure as percentage (uses settings if None)
        """
        self.settings = get_settings()
        
        # Subscribe to settings changes for real-time updates
        self.settings.subscribe('risk.max_daily_loss_percent', self._on_daily_loss_changed)
        self.settings.subscribe('risk.max_daily_trades', self._on_daily_trades_changed)
        self.settings.subscribe('risk.max_sector_exposure_percent', self._on_sector_exposure_changed)
        self.settings.subscribe('risk.max_portfolio_drawdown_percent', self._on_drawdown_changed)
        
        # Initialize with settings or provided values
        self._max_risk_per_trade = max_risk_per_trade
        self._max_daily_loss = max_daily_loss
        self._max_daily_trades = max_daily_trades
        self._max_position_size = max_position_size
        self._max_sector_exposure = max_sector_exposure
        self._max_portfolio_drawdown = None
        self._update_from_settings()
    
    def _update_from_settings(self):
        """Update values from settings."""
        if self._max_risk_per_trade is None:
            self._max_risk_per_trade = self.settings.get_default_risk_per_trade()
        if self._max_daily_loss is None:
            self._max_daily_loss = self.settings.get_max_daily_loss_percent()
        if self._max_daily_trades is None:
            self._max_daily_trades = self.settings.get_max_daily_trades()
        if self._max_position_size is None:
            self._max_position_size = self.settings.get_max_position_size_percent()
        if self._max_sector_exposure is None:
            self._max_sector_exposure = self.settings.get_max_sector_exposure_percent()
        if self._max_portfolio_drawdown is None:
            self._max_portfolio_drawdown = self.settings.get_max_portfolio_drawdown_percent()
    
    def _on_daily_loss_changed(self, key: str, old_value: float, new_value: float):
        """Handle daily loss limit change."""
        self._max_daily_loss = new_value
        DebugUtils.info(f"RiskLimits: Max daily loss updated to {new_value:.1%}")
    
    def _on_daily_trades_changed(self, key: str, old_value: int, new_value: int):
        """Handle daily trades limit change."""
        self._max_daily_trades = new_value
        DebugUtils.info(f"RiskLimits: Max daily trades updated to {new_value}")
    
    def _on_sector_exposure_changed(self, key: str, old_value: float, new_value: float):
        """Handle sector exposure limit change."""
        self._max_sector_exposure = new_value
        DebugUtils.info(f"RiskLimits: Max sector exposure updated to {new_value:.1%}")
    
    def _on_drawdown_changed(self, key: str, old_value: float, new_value: float):
        """Handle portfolio drawdown limit change."""
        self._max_portfolio_drawdown = new_value
        DebugUtils.info(f"RiskLimits: Max portfolio drawdown updated to {new_value:.1%}")
    
    @property
    def max_risk_per_trade(self) -> float:
        """Get current max risk per trade."""
        if self._max_risk_per_trade is None:
            self._max_risk_per_trade = self.settings.get_default_risk_per_trade()
        return self._max_risk_per_trade
    
    @property
    def max_daily_loss(self) -> float:
        """Get current max daily loss."""
        if self._max_daily_loss is None:
            self._max_daily_loss = self.settings.get_max_daily_loss_percent()
        return self._max_daily_loss
    
    @property
    def max_daily_trades(self) -> int:
        """Get current max daily trades."""
        if self._max_daily_trades is None:
            self._max_daily_trades = self.settings.get_max_daily_trades()
        return self._max_daily_trades
    
    @property
    def max_position_size(self) -> float:
        """Get current max position size."""
        if self._max_position_size is None:
            self._max_position_size = self.settings.get_max_position_size_percent()
        return self._max_position_size
    
    @property
    def max_sector_exposure(self) -> float:
        """Get current max sector exposure."""
        if self._max_sector_exposure is None:
            self._max_sector_exposure = self.settings.get_max_sector_exposure_percent()
        return self._max_sector_exposure
    
    @property
    def max_portfolio_drawdown(self) -> float:
        """Get current max portfolio drawdown."""
        if self._max_portfolio_drawdown is None:
            self._max_portfolio_drawdown = self.settings.get_max_portfolio_drawdown_percent()
        return self._max_portfolio_drawdown
    
    def check_per_trade_risk(self, risk_amount: float, total_capital: float = 100000.0) -> bool:
        """
        Check if per-trade risk is within limits.
        
        Args:
            risk_amount: Dollar amount at risk
            total_capital: Total capital
            
        Returns:
            True if within limits, False otherwise
        """
        max_risk = total_capital * self.max_risk_per_trade
        return risk_amount <= max_risk
    
    def check_daily_loss(self, daily_pnl: float, total_capital: float = 100000.0) -> bool:
        """
        Check if daily loss is within limits.
        
        Args:
            daily_pnl: Daily profit/loss
            total_capital: Total capital
            
        Returns:
            True if within limits, False otherwise
        """
        if daily_pnl >= 0:
            return True  # Profit is always OK
        
        max_loss = total_capital * self.max_daily_loss
        return abs(daily_pnl) <= max_loss
    
    def check_daily_trades(self, daily_trades: int) -> bool:
        """
        Check if daily trade count is within limits.
        
        Args:
            daily_trades: Number of trades today
            
        Returns:
            True if within limits, False otherwise
        """
        return daily_trades < self.max_daily_trades
    
    def check_position_size(self, position_size: float, total_capital: float = 100000.0) -> bool:
        """
        Check if position size is within limits.
        
        Args:
            position_size: Position size in dollars
            total_capital: Total capital
            
        Returns:
            True if within limits, False otherwise
        """
        max_size = total_capital * self.max_position_size
        return position_size <= max_size
    
    def check_sector_exposure(
        self,
        sector: str,
        existing_positions: List[Dict[str, Any]],
        total_capital: float = 100000.0
    ) -> bool:
        """
        Check if sector exposure is within limits.
        
        Args:
            sector: Sector to check
            existing_positions: List of existing positions
            total_capital: Total capital
            
        Returns:
            True if within limits, False otherwise
        """
        # Calculate current sector exposure
        sector_value = sum(
            pos.get('value', 0) for pos in existing_positions
            if pos.get('sector') == sector
        )
        
        sector_exposure = sector_value / total_capital if total_capital > 0 else 0.0
        max_exposure = self.max_sector_exposure
        
        return sector_exposure < max_exposure

