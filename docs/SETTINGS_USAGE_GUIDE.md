# Settings System Usage Guide

## Quick Start

### Getting Settings

```python
from backend.settings import get_settings

settings = get_settings()

# Get any setting
max_position = settings.get_max_position_size_percent()  # 0.10 (10%)
risk_per_trade = settings.get_default_risk_per_trade()  # 0.01 (1%)
initial_capital = settings.get_initial_capital()  # 100000.0
```

### Updating Settings

```python
from backend.settings import get_settings_manager

manager = get_settings_manager()

# Update a setting (applies immediately!)
manager.set('trading.max_position_size_percent', 0.15)  # 15%
manager.set('risk.max_daily_loss_percent', 0.10)  # 10%
manager.set('capital.initial_capital', 200000.0)  # $200K
```

### Subscribing to Changes

```python
from backend.settings import get_settings

settings = get_settings()

def on_risk_change(key: str, old_value: float, new_value: float):
    print(f"Risk per trade changed: {old_value:.1%} -> {new_value:.1%}")
    # Your module updates automatically here

# Subscribe
settings.subscribe('trading.default_risk_per_trade', on_risk_change)

# When setting changes, callback is triggered immediately
```

## All Available Settings

### Trading Settings
```python
settings.get_max_position_size_percent()  # Max position size (default: 10%)
settings.get_default_risk_per_trade()  # Risk per trade (default: 1%)
settings.get_min_risk_reward_ratio()  # Min risk-reward (default: 1.5)
```

### Risk Settings
```python
settings.get_max_daily_loss_percent()  # Max daily loss (default: 5%)
settings.get_max_daily_trades()  # Max trades per day (default: 20)
settings.get_max_sector_exposure_percent()  # Max sector exposure (default: 25%)
settings.get_max_correlation()  # Max correlation (default: 0.7)
settings.get_max_portfolio_drawdown_percent()  # Max drawdown (default: 20%)
```

### Capital Settings
```python
settings.get_initial_capital()  # Initial capital (default: $100K)
settings.get_cash_reserve_percent()  # Cash reserve (default: 20%)
```

### Timing Settings
```python
settings.get_signal_expiry_intraday_minutes()  # Intraday expiry (default: 5 min)
settings.get_signal_expiry_swing_minutes()  # Swing expiry (default: 60 min)
settings.get_signal_expiry_position_minutes()  # Position expiry (default: 240 min)
settings.get_latency_budget_intraday_seconds()  # Intraday latency (default: 2.0s)
settings.get_latency_budget_swing_seconds()  # Swing latency (default: 10.0s)
settings.get_latency_budget_position_seconds()  # Position latency (default: 30.0s)
settings.get_price_change_threshold_percent()  # Price threshold (default: 5%)
settings.get_volume_drop_threshold_percent()  # Volume threshold (default: 50%)
```

### Data Settings
```python
settings.get_min_volume()  # Min volume (default: $500K)
settings.get_min_price()  # Min price (default: $5)
settings.get_min_market_cap()  # Min market cap (default: $100M)
```

### Performance Settings
```python
settings.get_decay_win_rate_threshold()  # Win rate threshold (default: 10%)
settings.get_decay_profit_factor_threshold()  # Profit factor (default: 1.0)
settings.get_decay_sharpe_threshold()  # Sharpe threshold (default: 0.3)
settings.get_decay_drawdown_threshold()  # Drawdown threshold (default: 20%)
```

## Settings File Location

Settings are stored in: `data/settings.json`

You can edit this file directly, or use the SettingsManager API.

## Real-Time Updates

When you update a setting:

1. **Validation**: Setting is validated (type, range, etc.)
2. **Storage**: Saved to `data/settings.json`
3. **Notification**: All subscribers notified immediately
4. **Update**: Modules update internal state
5. **Effect**: Changes take effect immediately (no restart!)

## Example: Adjusting Risk Tolerance

```python
from backend.settings import get_settings_manager

manager = get_settings_manager()

# Increase risk tolerance
manager.set('trading.default_risk_per_trade', 0.02)  # 2% per trade
manager.set('risk.max_daily_loss_percent', 0.10)  # 10% daily loss
manager.set('risk.max_daily_trades', 30)  # 30 trades per day

# All modules update immediately:
# - PositionSizer uses 2% risk
# - RiskEngine allows 10% daily loss
# - RiskEngine allows 30 trades per day
```

## Example: Adjusting Timing

```python
# Make signals expire faster
manager.set('timing.signal_expiry_intraday_minutes', 3)  # 3 minutes
manager.set('timing.signal_expiry_swing_minutes', 30)  # 30 minutes

# All timing modules update immediately
```

## Example: Adjusting Capital

```python
# Increase initial capital
manager.set('capital.initial_capital', 200000.0)  # $200K

# CapitalManager updates immediately
```

## Validation

Invalid values are rejected:

```python
# This will fail (max is 25%)
manager.set('trading.max_position_size_percent', 0.50)  # Error!

# This will fail (must be float)
manager.set('trading.max_position_size_percent', '15%')  # Error!
```

## Best Practices

1. **Use Settings Adapter**: Prefer `get_settings()` over direct manager access
2. **Subscribe Early**: Subscribe in `__init__` methods
3. **Update State**: Update internal state in callbacks
4. **Log Changes**: Log setting changes for debugging
5. **Validate**: Always validate user input before setting

## Notes

- Settings file created automatically on first use
- Defaults used if settings file missing
- Thread-safe for concurrent access
- All changes logged
- Real-time updates work across all modules

