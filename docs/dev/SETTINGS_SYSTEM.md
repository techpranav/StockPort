# Enterprise Settings System

## Overview

Stockport v4 includes an enterprise-level settings management system that allows all thresholds, timings, amounts, and capital values to be configured through a centralized settings system with **real-time updates** (no restart required).

## Features

### ✅ Enterprise-Level Capabilities
- **Persistent Storage**: Settings saved to JSON file (`data/settings.json`)
- **Real-Time Updates**: Changes reflect immediately across all modules
- **Validation**: Type checking, range validation, allowed values
- **Change Notifications**: Subscribers notified when settings change
- **Thread-Safe**: Lock-protected for concurrent access
- **Hot Reloading**: No restart required for most settings
- **Default Values**: Sensible defaults for all settings
- **Categories**: Organized by category (trading, risk, capital, timing, etc.)

## Settings Categories

### Trading Settings
- `trading.max_position_size_percent` - Maximum position size (default: 10%)
- `trading.default_risk_per_trade` - Default risk per trade (default: 1%)
- `trading.min_risk_reward_ratio` - Minimum risk-reward ratio (default: 1.5:1)

### Risk Settings
- `risk.max_daily_loss_percent` - Maximum daily loss (default: 5%)
- `risk.max_daily_trades` - Maximum trades per day (default: 20)
- `risk.max_sector_exposure_percent` - Maximum sector exposure (default: 25%)
- `risk.max_correlation` - Maximum position correlation (default: 0.7)
- `risk.max_portfolio_drawdown_percent` - Maximum portfolio drawdown (default: 20%)

### Capital Settings
- `capital.initial_capital` - Initial trading capital (default: $100,000)
- `capital.cash_reserve_percent` - Cash reserve percentage (default: 20%)

### Timing Settings
- `timing.signal_expiry_intraday_minutes` - Intraday signal expiry (default: 5 min)
- `timing.signal_expiry_swing_minutes` - Swing signal expiry (default: 60 min)
- `timing.signal_expiry_position_minutes` - Position signal expiry (default: 240 min)
- `timing.latency_budget_intraday_seconds` - Intraday latency budget (default: 2.0s)
- `timing.latency_budget_swing_seconds` - Swing latency budget (default: 10.0s)
- `timing.latency_budget_position_seconds` - Position latency budget (default: 30.0s)
- `timing.price_change_threshold_percent` - Price change threshold (default: 5%)
- `timing.volume_drop_threshold_percent` - Volume drop threshold (default: 50%)

### Data Settings
- `data.min_volume` - Minimum daily volume (default: $500K)
- `data.min_price` - Minimum stock price (default: $5)
- `data.min_market_cap` - Minimum market cap (default: $100M)

### Performance Settings
- `performance.decay_win_rate_threshold` - Win rate decline threshold (default: 10%)
- `performance.decay_profit_factor_threshold` - Minimum profit factor (default: 1.0)
- `performance.decay_sharpe_threshold` - Minimum Sharpe ratio (default: 0.3)
- `performance.decay_drawdown_threshold` - Maximum drawdown (default: 20%)

## Usage

### Basic Usage

```python
from backend.settings import get_settings_manager, get_settings

# Using SettingsManager directly
manager = get_settings_manager()
max_position = manager.get('trading.max_position_size_percent')
manager.set('trading.max_position_size_percent', 0.15)  # 15%

# Using SettingsAdapter (recommended)
settings = get_settings()
max_position = settings.get_max_position_size_percent()
risk_per_trade = settings.get_default_risk_per_trade()
```

### Real-Time Updates

```python
from backend.settings import get_settings

settings = get_settings()

def on_risk_change(key: str, old_value: float, new_value: float):
    print(f"Risk per trade changed from {old_value:.1%} to {new_value:.1%}")
    # Update your module's internal state
    my_module.risk_per_trade = new_value

# Subscribe to changes
settings.subscribe('trading.default_risk_per_trade', on_risk_change)

# Later, when setting is updated:
manager.set('trading.default_risk_per_trade', 0.02)  # Immediately triggers callback
```

### Module Integration

Modules automatically subscribe to relevant settings:

```python
# In your module
from backend.settings import get_settings

class MyModule:
    def __init__(self):
        self.settings = get_settings()
        
        # Subscribe to changes
        self.settings.subscribe('trading.max_position_size_percent', 
                               self._on_max_position_changed)
        
        # Initialize from settings
        self._max_position = self.settings.get_max_position_size_percent()
    
    def _on_max_position_changed(self, key: str, old_value: float, new_value: float):
        """Handle setting change in real-time."""
        self._max_position = new_value
        DebugUtils.info(f"Max position updated to {new_value:.1%}")
```

## Integrated Modules

The following modules are already integrated with the settings system:

1. **Position Sizer** - Uses `trading.default_risk_per_trade` and `trading.max_position_size_percent`
2. **Risk Limits** - Uses all risk settings
3. **Capital Manager** - Uses `capital.initial_capital` and `capital.cash_reserve_percent`
4. **Signal Expiry** - Uses all timing expiry settings
5. **Stale Detector** - Uses price and volume thresholds
6. **Latency Tracker** - Uses latency budget settings
7. **Decay Detector** - Uses performance thresholds
8. **Market Scanner** - Uses data filter settings

## Settings File

Settings are stored in `data/settings.json`:

```json
{
  "trading.max_position_size_percent": 0.10,
  "trading.default_risk_per_trade": 0.01,
  "risk.max_daily_loss_percent": 0.05,
  "capital.initial_capital": 100000.0,
  ...
}
```

## API Endpoints (Future)

Settings can be managed via:
- REST API: `GET /api/settings`, `PUT /api/settings/{key}`
- WebSocket: Real-time setting updates
- UI: Settings management panel

## Validation

All settings are validated:
- **Type checking**: Ensures correct data type
- **Range validation**: Min/max values enforced
- **Allowed values**: Enum-like restrictions where applicable
- **Custom validators**: Additional validation logic

## Benefits

1. **No Code Changes**: Adjust behavior without code changes
2. **Real-Time Updates**: Changes apply immediately
3. **Centralized**: Single source of truth
4. **Validated**: Prevents invalid configurations
5. **Auditable**: All changes logged
6. **User-Friendly**: Easy to understand and modify

## Example: Adjusting Risk Tolerance

```python
# Increase risk tolerance
manager = get_settings_manager()
manager.set('trading.default_risk_per_trade', 0.02)  # 2% instead of 1%
manager.set('risk.max_daily_loss_percent', 0.10)  # 10% instead of 5%

# All modules using these settings update immediately!
# PositionSizer, RiskEngine, etc. all reflect new values
```

## Adding New Settings

To add a new setting:

1. Add to `SettingsManager._initialize_default_settings()`:
```python
SettingDefinition(
    key="my_module.my_setting",
    category=SettingCategory.MY_CATEGORY,
    default_value=100.0,
    value_type=float,
    min_value=0.0,
    max_value=1000.0,
    description="My new setting"
)
```

2. Add getter to `SettingsAdapter`:
```python
def get_my_setting(self) -> float:
    """Get my setting."""
    return self._manager.get('my_module.my_setting', 100.0)
```

3. Use in your module:
```python
settings = get_settings()
value = settings.get_my_setting()
```

## Notes

- Settings file is automatically created on first use
- Invalid values are rejected with error messages
- Defaults are used if settings file is missing
- Thread-safe for concurrent access
- All changes are logged

