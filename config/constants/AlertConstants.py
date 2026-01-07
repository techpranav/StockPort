"""
Alert Constants

Constants for alert system configuration.
"""

# Alert check intervals
ALERT_CHECK_INTERVAL_SECONDS = 60
ALERT_BATCH_SIZE = 10

# Notification limits
MAX_NOTIFICATIONS_QUEUE = 1000
MAX_NOTIFICATIONS_DISPLAY = 50

# Alert expiration
DEFAULT_ALERT_EXPIRY_DAYS = 30

# Thresholds
HIGH_VOLATILITY_THRESHOLD = 30.0
VOLUME_SPIKE_MULTIPLIER = 2.0

# Notification channels
CHANNEL_IN_APP = "in_app"
CHANNEL_EMAIL = "email"
CHANNEL_PUSH = "push"

# Alert status
STATUS_ACTIVE = "active"
STATUS_TRIGGERED = "triggered"
STATUS_DISABLED = "disabled"
STATUS_EXPIRED = "expired"

