"""
Settings Manager

Enterprise-level settings management with real-time updates and validation.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import threading
from enum import Enum

from utils.debug_utils import DebugUtils
from config.app_config import DATA_DIR


class SettingCategory(Enum):
    """Setting categories."""
    TRADING = "trading"
    RISK = "risk"
    CAPITAL = "capital"
    TIMING = "timing"
    DATA = "data"
    PERFORMANCE = "performance"
    UI = "ui"
    SYSTEM = "system"


@dataclass
class SettingDefinition:
    """Setting definition with validation."""
    key: str
    category: SettingCategory
    default_value: Any
    value_type: type
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    description: str = ""
    requires_restart: bool = False
    validator: Optional[Callable[[Any], bool]] = None


class SettingsManager:
    """
    Enterprise-level settings manager with real-time updates.
    
    Features:
    - Persistent storage (JSON)
    - Real-time updates (no restart required)
    - Validation
    - Change notifications
    - Version control
    - Hot reloading
    """
    
    def __init__(self, settings_file: Optional[Path] = None):
        """
        Initialize settings manager.
        
        Args:
            settings_file: Path to settings file (default: data/settings.json)
        """
        if settings_file is None:
            settings_file = DATA_DIR / "settings.json"
        
        self.settings_file = Path(settings_file)
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._settings: Dict[str, Any] = {}
        self._definitions: Dict[str, SettingDefinition] = {}
        self._subscribers: Dict[str, List[Callable[[str, Any, Any], None]]] = {}  # key -> [callbacks]
        self._lock = threading.RLock()
        
        # Initialize default settings
        self._initialize_default_settings()
        
        # Load from file
        self.load()
        
        DebugUtils.info(f"SettingsManager initialized with {len(self._settings)} settings")
    
    def _initialize_default_settings(self):
        """Initialize default setting definitions."""
        defaults = [
            # Trading Settings
            SettingDefinition(
                key="trading.max_position_size_percent",
                category=SettingCategory.TRADING,
                default_value=0.10,
                value_type=float,
                min_value=0.01,
                max_value=0.25,
                description="Maximum position size as percentage of capital (default: 10%)"
            ),
            SettingDefinition(
                key="trading.default_risk_per_trade",
                category=SettingCategory.TRADING,
                default_value=0.01,
                value_type=float,
                min_value=0.001,
                max_value=0.05,
                description="Default risk per trade as percentage of capital (default: 1%)"
            ),
            SettingDefinition(
                key="trading.min_risk_reward_ratio",
                category=SettingCategory.TRADING,
                default_value=1.5,
                value_type=float,
                min_value=1.0,
                max_value=5.0,
                description="Minimum risk-reward ratio for trade approval (default: 1.5:1)"
            ),
            
            # Risk Settings
            SettingDefinition(
                key="risk.max_daily_loss_percent",
                category=SettingCategory.RISK,
                default_value=0.05,
                value_type=float,
                min_value=0.01,
                max_value=0.20,
                description="Maximum daily loss as percentage of capital (default: 5%)"
            ),
            SettingDefinition(
                key="risk.max_daily_trades",
                category=SettingCategory.RISK,
                default_value=20,
                value_type=int,
                min_value=1,
                max_value=100,
                description="Maximum number of trades per day (default: 20)"
            ),
            SettingDefinition(
                key="risk.max_sector_exposure_percent",
                category=SettingCategory.RISK,
                default_value=0.25,
                value_type=float,
                min_value=0.05,
                max_value=0.50,
                description="Maximum sector exposure as percentage of capital (default: 25%)"
            ),
            SettingDefinition(
                key="risk.max_correlation",
                category=SettingCategory.RISK,
                default_value=0.7,
                value_type=float,
                min_value=0.0,
                max_value=1.0,
                description="Maximum correlation with existing positions (default: 0.7)"
            ),
            SettingDefinition(
                key="risk.max_portfolio_drawdown_percent",
                category=SettingCategory.RISK,
                default_value=0.20,
                value_type=float,
                min_value=0.05,
                max_value=0.50,
                description="Maximum portfolio drawdown before blocking new trades (default: 20%)"
            ),
            
            # Capital Settings
            SettingDefinition(
                key="capital.initial_capital",
                category=SettingCategory.CAPITAL,
                default_value=100000.0,
                value_type=float,
                min_value=1000.0,
                max_value=10000000.0,
                description="Initial trading capital in USD (default: $100,000)"
            ),
            SettingDefinition(
                key="capital.cash_reserve_percent",
                category=SettingCategory.CAPITAL,
                default_value=0.20,
                value_type=float,
                min_value=0.0,
                max_value=0.50,
                description="Cash reserve as percentage of capital (default: 20%)"
            ),
            
            # Timing Settings
            SettingDefinition(
                key="timing.signal_expiry_intraday_minutes",
                category=SettingCategory.TIMING,
                default_value=5,
                value_type=int,
                min_value=1,
                max_value=60,
                description="Signal expiry time for intraday strategies in minutes (default: 5)"
            ),
            SettingDefinition(
                key="timing.signal_expiry_swing_minutes",
                category=SettingCategory.TIMING,
                default_value=60,
                value_type=int,
                min_value=5,
                max_value=480,
                description="Signal expiry time for swing strategies in minutes (default: 60)"
            ),
            SettingDefinition(
                key="timing.signal_expiry_position_minutes",
                category=SettingCategory.TIMING,
                default_value=240,
                value_type=int,
                min_value=60,
                max_value=1440,
                description="Signal expiry time for position strategies in minutes (default: 240)"
            ),
            SettingDefinition(
                key="timing.latency_budget_intraday_seconds",
                category=SettingCategory.TIMING,
                default_value=2.0,
                value_type=float,
                min_value=0.5,
                max_value=10.0,
                description="Latency budget for intraday strategies in seconds (default: 2.0)"
            ),
            SettingDefinition(
                key="timing.latency_budget_swing_seconds",
                category=SettingCategory.TIMING,
                default_value=10.0,
                value_type=float,
                min_value=1.0,
                max_value=60.0,
                description="Latency budget for swing strategies in seconds (default: 10.0)"
            ),
            SettingDefinition(
                key="timing.latency_budget_position_seconds",
                category=SettingCategory.TIMING,
                default_value=30.0,
                value_type=float,
                min_value=5.0,
                max_value=300.0,
                description="Latency budget for position strategies in seconds (default: 30.0)"
            ),
            SettingDefinition(
                key="timing.price_change_threshold_percent",
                category=SettingCategory.TIMING,
                default_value=0.05,
                value_type=float,
                min_value=0.01,
                max_value=0.20,
                description="Price change threshold for staleness detection (default: 5%)"
            ),
            SettingDefinition(
                key="timing.volume_drop_threshold_percent",
                category=SettingCategory.TIMING,
                default_value=0.50,
                value_type=float,
                min_value=0.10,
                max_value=0.90,
                description="Volume drop threshold for staleness detection (default: 50%)"
            ),
            
            # Data Settings
            SettingDefinition(
                key="data.min_volume",
                category=SettingCategory.DATA,
                default_value=500000.0,
                value_type=float,
                min_value=10000.0,
                max_value=10000000.0,
                description="Minimum daily volume for stock selection (default: $500K)"
            ),
            SettingDefinition(
                key="data.min_price",
                category=SettingCategory.DATA,
                default_value=5.0,
                value_type=float,
                min_value=1.0,
                max_value=100.0,
                description="Minimum stock price for selection (default: $5)"
            ),
            SettingDefinition(
                key="data.min_market_cap",
                category=SettingCategory.DATA,
                default_value=100000000.0,
                value_type=float,
                min_value=1000000.0,
                max_value=10000000000.0,
                description="Minimum market capitalization for selection (default: $100M)"
            ),
            
            # Performance Settings
            SettingDefinition(
                key="performance.decay_win_rate_threshold",
                category=SettingCategory.PERFORMANCE,
                default_value=0.10,
                value_type=float,
                min_value=0.05,
                max_value=0.30,
                description="Win rate decline threshold for decay detection (default: 10%)"
            ),
            SettingDefinition(
                key="performance.decay_profit_factor_threshold",
                category=SettingCategory.PERFORMANCE,
                default_value=1.0,
                value_type=float,
                min_value=0.5,
                max_value=2.0,
                description="Minimum profit factor to avoid decay (default: 1.0)"
            ),
            SettingDefinition(
                key="performance.decay_sharpe_threshold",
                category=SettingCategory.PERFORMANCE,
                default_value=0.3,
                value_type=float,
                min_value=0.0,
                max_value=2.0,
                description="Minimum Sharpe ratio to avoid decay (default: 0.3)"
            ),
            SettingDefinition(
                key="performance.decay_drawdown_threshold",
                category=SettingCategory.PERFORMANCE,
                default_value=0.20,
                value_type=float,
                min_value=0.05,
                max_value=0.50,
                description="Maximum drawdown before decay detection (default: 20%)"
            ),
        ]
        
        for definition in defaults:
            self._definitions[definition.key] = definition
            self._settings[definition.key] = definition.default_value
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get setting value.
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value
        """
        with self._lock:
            return self._settings.get(key, default)
    
    def set(self, key: str, value: Any, validate: bool = True) -> bool:
        """
        Set setting value with validation and real-time update.
        
        Args:
            key: Setting key
            value: Setting value
            validate: Whether to validate the value
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            # Check if setting exists
            if key not in self._definitions:
                DebugUtils.warning(f"Unknown setting key: {key}")
                return False
            
            definition = self._definitions[key]
            old_value = self._settings.get(key)
            
            # Validate value
            if validate:
                if not self._validate_value(definition, value):
                    DebugUtils.error(f"Invalid value for setting {key}: {value}")
                    return False
            
            # Set value
            self._settings[key] = value
            
            # Save to file
            self.save()
            
            # Notify subscribers (real-time update)
            self._notify_subscribers(key, old_value, value)
            
            DebugUtils.info(f"Setting updated: {key} = {value} (was {old_value})")
            return True
    
    def _validate_value(self, definition: SettingDefinition, value: Any) -> bool:
        """Validate setting value."""
        # Type check
        if not isinstance(value, definition.value_type):
            try:
                value = definition.value_type(value)
            except (ValueError, TypeError):
                return False
        
        # Range check
        if definition.min_value is not None and value < definition.min_value:
            return False
        if definition.max_value is not None and value > definition.max_value:
            return False
        
        # Allowed values check
        if definition.allowed_values is not None and value not in definition.allowed_values:
            return False
        
        # Custom validator
        if definition.validator is not None:
            if not definition.validator(value):
                return False
        
        return True
    
    def subscribe(self, key: str, callback: Callable[[str, Any, Any], None]):
        """
        Subscribe to setting changes for real-time updates.
        
        Args:
            key: Setting key (or "*" for all settings)
            callback: Callback function(key, old_value, new_value)
        """
        with self._lock:
            if key not in self._subscribers:
                self._subscribers[key] = []
            self._subscribers[key].append(callback)
            DebugUtils.debug(f"Subscribed to setting changes: {key}")
    
    def unsubscribe(self, key: str, callback: Callable[[str, Any, Any], None]):
        """Unsubscribe from setting changes."""
        with self._lock:
            if key in self._subscribers:
                try:
                    self._subscribers[key].remove(callback)
                except ValueError:
                    pass
    
    def _notify_subscribers(self, key: str, old_value: Any, new_value: Any):
        """Notify all subscribers of setting change."""
        # Notify specific subscribers
        if key in self._subscribers:
            for callback in self._subscribers[key]:
                try:
                    callback(key, old_value, new_value)
                except Exception as e:
                    DebugUtils.log_error(e, f"Error in setting subscriber for {key}")
        
        # Notify wildcard subscribers
        if "*" in self._subscribers:
            for callback in self._subscribers["*"]:
                try:
                    callback(key, old_value, new_value)
                except Exception as e:
                    DebugUtils.log_error(e, f"Error in wildcard setting subscriber")
    
    def load(self):
        """Load settings from file."""
        if not self.settings_file.exists():
            DebugUtils.info("Settings file not found, using defaults")
            return
        
        try:
            with open(self.settings_file, 'r') as f:
                loaded = json.load(f)
            
            with self._lock:
                for key, value in loaded.items():
                    if key in self._definitions:
                        if self._validate_value(self._definitions[key], value):
                            self._settings[key] = value
                        else:
                            DebugUtils.warning(f"Invalid value for {key} in settings file, using default")
                    else:
                        DebugUtils.warning(f"Unknown setting {key} in settings file, ignoring")
            
            DebugUtils.info(f"Loaded {len(loaded)} settings from file")
        except Exception as e:
            DebugUtils.log_error(e, "Error loading settings file")
    
    def save(self):
        """Save settings to file."""
        try:
            with self._lock:
                with open(self.settings_file, 'w') as f:
                    json.dump(self._settings, f, indent=2, default=str)
            DebugUtils.debug("Settings saved to file")
        except Exception as e:
            DebugUtils.log_error(e, "Error saving settings file")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings."""
        with self._lock:
            return self._settings.copy()
    
    def get_definitions(self) -> Dict[str, SettingDefinition]:
        """Get all setting definitions."""
        return self._definitions.copy()
    
    def reset_to_default(self, key: str) -> bool:
        """Reset setting to default value."""
        if key not in self._definitions:
            return False
        
        definition = self._definitions[key]
        return self.set(key, definition.default_value, validate=False)
    
    def reset_all_to_defaults(self):
        """Reset all settings to defaults."""
        with self._lock:
            for key, definition in self._definitions.items():
                self._settings[key] = definition.default_value
            self.save()
            DebugUtils.info("All settings reset to defaults")


# Global settings manager instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """Get global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

