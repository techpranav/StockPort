"""
Alert Model

Defines alert types and alert data structures.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AlertType(Enum):
    """Types of alerts."""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    SIGNAL_BUY = "signal_buy"
    SIGNAL_SELL = "signal_sell"
    PATTERN_DETECTED = "pattern_detected"
    VOLUME_SPIKE = "volume_spike"
    RISK_HIGH = "risk_high"
    SUPPORT_BREAKOUT = "support_breakout"
    RESISTANCE_BREAKOUT = "resistance_breakout"
    SUPPORT_BOUNCE = "support_bounce"
    CUSTOM = "custom"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"
    EXPIRED = "expired"


@dataclass
class Alert:
    """Represents a stock alert."""
    id: str
    symbol: str
    alert_type: AlertType
    status: AlertStatus = AlertStatus.ACTIVE
    threshold_value: Optional[float] = None
    condition: Optional[str] = None  # Custom condition expression
    created_at: datetime = field(default_factory=datetime.now)
    triggered_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    notification_channels: List[str] = field(default_factory=lambda: ['in_app'])  # in_app, email, push
    metadata: Dict[str, Any] = field(default_factory=dict)
    trigger_count: int = 0
    last_triggered: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'alert_type': self.alert_type.value,
            'status': self.status.value,
            'threshold_value': self.threshold_value,
            'condition': self.condition,
            'created_at': self.created_at.isoformat(),
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'notification_channels': self.notification_channels,
            'metadata': self.metadata,
            'trigger_count': self.trigger_count,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None
        }

