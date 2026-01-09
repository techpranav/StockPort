# Alerts & Notifications System

## Overview

The Alerts System provides real-time monitoring and notifications for stock price movements, trading signals, patterns, and risk conditions.

## Features

- **Multiple Alert Types**: Price, Signal, Pattern, Volume, Risk alerts
- **Real-time Monitoring**: Background thread continuously checks alerts
- **Multi-channel Notifications**: In-app, Email, Browser Push
- **Alert History**: Track alert performance and triggers
- **Flexible Configuration**: Custom thresholds and conditions

## Alert Types

### 1. Price Alerts
- **Price Above**: Trigger when price exceeds threshold
- **Price Below**: Trigger when price falls below threshold

### 2. Signal Alerts
- **Buy Signal**: Trigger on STRONG_BUY or BUY signals
- **Sell Signal**: Trigger on SELL or AVOID signals

### 3. Pattern Alerts
- **Pattern Detected**: Trigger when candlestick or chart patterns are detected

### 4. Volume Alerts
- **Volume Spike**: Trigger on unusual volume activity

### 5. Risk Alerts
- **High Risk**: Trigger when volatility exceeds threshold

## Usage

### Creating Alerts

```python
from services.alerts.alert_manager import AlertManager
from models.alert import AlertType

alert_manager = AlertManager()

# Create price alert
alert = alert_manager.create_alert(
    symbol="AAPL",
    alert_type=AlertType.PRICE_ABOVE,
    threshold_value=150.0,
    notification_channels=['in_app', 'email']
)
```

### Starting Monitoring

```python
from services.alerts.alert_engine import AlertEngine

alert_engine = AlertEngine()
alert_engine.start_monitoring()  # Starts background thread
```

### Checking Alerts Manually

```python
# Check alerts for a symbol
triggered = alert_engine.check_alerts_now("AAPL")
```

## UI Components

### Alerts Panel
- View active alerts
- Create new alerts
- Delete alerts
- Start/stop monitoring

### Alert Creator
- Select symbol
- Choose alert type
- Set thresholds
- Configure notification channels

### Notifications
- View recent notifications
- Mark as read
- Filter by symbol or type

## Configuration

Alert settings can be configured in `config/constants/AlertConstants.py`:

- `ALERT_CHECK_INTERVAL_SECONDS`: How often to check alerts (default: 60s)
- `MAX_NOTIFICATIONS_QUEUE`: Maximum notifications to store (default: 1000)
- `HIGH_VOLATILITY_THRESHOLD`: Volatility threshold for risk alerts (default: 30%)

## Notification Channels

### In-App Notifications
- Stored in notification queue
- Displayed in UI
- Persist during session

### Email Notifications
- Requires email configuration
- Sent when alert triggers
- Includes alert details and current data

### Browser Push Notifications
- Requires browser push API setup
- Real-time browser notifications
- Works even when app is not active

## Alert Lifecycle

1. **Created**: Alert is created and set to ACTIVE
2. **Monitoring**: Background thread checks alert conditions
3. **Triggered**: Alert condition is met
4. **Notification**: Notification sent through configured channels
5. **History**: Alert trigger recorded in history

## Best Practices

1. **Set Realistic Thresholds**: Avoid too many false triggers
2. **Use Appropriate Channels**: In-app for frequent, Email for important
3. **Monitor Alert Performance**: Review alert history regularly
4. **Set Expiration Dates**: Avoid stale alerts
5. **Combine Alert Types**: Use multiple alerts for comprehensive monitoring

