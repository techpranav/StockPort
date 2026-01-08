"""
Settings Adapter

Provides easy access to settings with real-time updates for modules.
"""

from typing import Any, Optional, Callable
from backend.settings.settings_manager import get_settings_manager, SettingCategory


class SettingsAdapter:
    """
    Adapter for easy settings access with real-time updates.
    
    Usage:
        settings = SettingsAdapter()
        max_position = settings.get_max_position_size_percent()
        
        # Subscribe to changes
        def on_max_position_change(key, old_val, new_val):
            print(f"Max position changed from {old_val} to {new_val}")
        settings.subscribe('trading.max_position_size_percent', on_max_position_change)
    """
    
    def __init__(self):
        """Initialize settings adapter."""
        self._manager = get_settings_manager()
        self._callbacks: dict = {}
    
    # Trading Settings
    def get_max_position_size_percent(self) -> float:
        """Get maximum position size as percentage of capital."""
        return self._manager.get('trading.max_position_size_percent', 0.10)
    
    def get_default_risk_per_trade(self) -> float:
        """Get default risk per trade as percentage of capital."""
        return self._manager.get('trading.default_risk_per_trade', 0.01)
    
    def get_min_risk_reward_ratio(self) -> float:
        """Get minimum risk-reward ratio for trade approval."""
        return self._manager.get('trading.min_risk_reward_ratio', 1.5)
    
    # Risk Settings
    def get_max_daily_loss_percent(self) -> float:
        """Get maximum daily loss as percentage of capital."""
        return self._manager.get('risk.max_daily_loss_percent', 0.05)
    
    def get_max_daily_trades(self) -> int:
        """Get maximum number of trades per day."""
        return self._manager.get('risk.max_daily_trades', 20)
    
    def get_max_sector_exposure_percent(self) -> float:
        """Get maximum sector exposure as percentage of capital."""
        return self._manager.get('risk.max_sector_exposure_percent', 0.25)
    
    def get_max_correlation(self) -> float:
        """Get maximum correlation with existing positions."""
        return self._manager.get('risk.max_correlation', 0.7)
    
    def get_max_portfolio_drawdown_percent(self) -> float:
        """Get maximum portfolio drawdown before blocking trades."""
        return self._manager.get('risk.max_portfolio_drawdown_percent', 0.20)
    
    # Capital Settings
    def get_initial_capital(self) -> float:
        """Get initial trading capital."""
        return self._manager.get('capital.initial_capital', 100000.0)
    
    def get_cash_reserve_percent(self) -> float:
        """Get cash reserve as percentage of capital."""
        return self._manager.get('capital.cash_reserve_percent', 0.20)
    
    # Timing Settings
    def get_signal_expiry_intraday_minutes(self) -> int:
        """Get signal expiry for intraday strategies."""
        return self._manager.get('timing.signal_expiry_intraday_minutes', 5)
    
    def get_signal_expiry_swing_minutes(self) -> int:
        """Get signal expiry for swing strategies."""
        return self._manager.get('timing.signal_expiry_swing_minutes', 60)
    
    def get_signal_expiry_position_minutes(self) -> int:
        """Get signal expiry for position strategies."""
        return self._manager.get('timing.signal_expiry_position_minutes', 240)
    
    def get_latency_budget_intraday_seconds(self) -> float:
        """Get latency budget for intraday strategies."""
        return self._manager.get('timing.latency_budget_intraday_seconds', 2.0)
    
    def get_latency_budget_swing_seconds(self) -> float:
        """Get latency budget for swing strategies."""
        return self._manager.get('timing.latency_budget_swing_seconds', 10.0)
    
    def get_latency_budget_position_seconds(self) -> float:
        """Get latency budget for position strategies."""
        return self._manager.get('timing.latency_budget_position_seconds', 30.0)
    
    def get_price_change_threshold_percent(self) -> float:
        """Get price change threshold for staleness detection."""
        return self._manager.get('timing.price_change_threshold_percent', 0.05)
    
    def get_volume_drop_threshold_percent(self) -> float:
        """Get volume drop threshold for staleness detection."""
        return self._manager.get('timing.volume_drop_threshold_percent', 0.50)
    
    # Data Settings
    def get_min_volume(self) -> float:
        """Get minimum daily volume for stock selection."""
        return self._manager.get('data.min_volume', 500000.0)
    
    def get_min_price(self) -> float:
        """Get minimum stock price for selection."""
        return self._manager.get('data.min_price', 5.0)
    
    def get_min_market_cap(self) -> float:
        """Get minimum market capitalization for selection."""
        return self._manager.get('data.min_market_cap', 100000000.0)
    
    # Performance Settings
    def get_decay_win_rate_threshold(self) -> float:
        """Get win rate decline threshold for decay detection."""
        return self._manager.get('performance.decay_win_rate_threshold', 0.10)
    
    def get_decay_profit_factor_threshold(self) -> float:
        """Get minimum profit factor to avoid decay."""
        return self._manager.get('performance.decay_profit_factor_threshold', 1.0)
    
    def get_decay_sharpe_threshold(self) -> float:
        """Get minimum Sharpe ratio to avoid decay."""
        return self._manager.get('performance.decay_sharpe_threshold', 0.3)
    
    def get_decay_drawdown_threshold(self) -> float:
        """Get maximum drawdown before decay detection."""
        return self._manager.get('performance.decay_drawdown_threshold', 0.20)
    
    def subscribe(self, key: str, callback: Callable[[str, Any, Any], None]):
        """
        Subscribe to setting changes.
        
        Args:
            key: Setting key
            callback: Callback function(key, old_value, new_value)
        """
        self._manager.subscribe(key, callback)
        if key not in self._callbacks:
            self._callbacks[key] = []
        self._callbacks[key].append(callback)
    
    def unsubscribe(self, key: str, callback: Callable[[str, Any, Any], None]):
        """Unsubscribe from setting changes."""
        self._manager.unsubscribe(key, callback)
        if key in self._callbacks:
            try:
                self._callbacks[key].remove(callback)
            except ValueError:
                pass


# Global adapter instance
_settings_adapter: Optional[SettingsAdapter] = None


def get_settings() -> SettingsAdapter:
    """Get global settings adapter instance."""
    global _settings_adapter
    if _settings_adapter is None:
        _settings_adapter = SettingsAdapter()
    return _settings_adapter

