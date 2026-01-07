"""
Notification Service

Handles delivery of alert notifications through various channels.
"""

from typing import Dict, Any, List
from models.alert import Alert
from utils.debug_utils import DebugUtils


class NotificationService:
    """
    Notification service for alert delivery.
    
    Supports:
    - In-app notifications
    - Email notifications
    - Browser push notifications (future)
    """
    
    def __init__(self):
        """Initialize notification service."""
        self.notification_queue: List[Dict[str, Any]] = []
        DebugUtils.info("Initialized NotificationService")
    
    def send_alert_notification(
        self,
        alert: Alert,
        current_data: Dict[str, Any]
    ) -> None:
        """
        Send alert notification through configured channels.
        
        Args:
            alert: Triggered alert
            current_data: Current stock data
        """
        notification = {
            'alert_id': alert.id,
            'symbol': alert.symbol,
            'alert_type': alert.alert_type.value,
            'message': self._generate_message(alert, current_data),
            'timestamp': alert.triggered_at.isoformat() if alert.triggered_at else None,
            'data': current_data
        }
        
        # Send through each configured channel
        for channel in alert.notification_channels:
            try:
                if channel == 'in_app':
                    self._send_in_app(notification)
                elif channel == 'email':
                    self._send_email(alert, notification)
                elif channel == 'push':
                    self._send_push(notification)
            except Exception as e:
                DebugUtils.log_error(e, f"Error sending notification via {channel}")
        
        # Add to queue for UI retrieval
        self.notification_queue.append(notification)
        
        # Keep queue size manageable
        if len(self.notification_queue) > 1000:
            self.notification_queue = self.notification_queue[-1000:]
    
    def _generate_message(
        self,
        alert: Alert,
        current_data: Dict[str, Any]
    ) -> str:
        """Generate notification message."""
        symbol = alert.symbol
        
        if alert.alert_type.value == 'price_above':
            price = current_data.get('current_price', 'N/A')
            return f"🚨 {symbol} price is above {alert.threshold_value} (Current: {price})"
        
        elif alert.alert_type.value == 'price_below':
            price = current_data.get('current_price', 'N/A')
            return f"🚨 {symbol} price is below {alert.threshold_value} (Current: {price})"
        
        elif alert.alert_type.value == 'signal_buy':
            return f"✅ {symbol} - Buy signal detected!"
        
        elif alert.alert_type.value == 'signal_sell':
            return f"⚠️ {symbol} - Sell signal detected!"
        
        elif alert.alert_type.value == 'pattern_detected':
            return f"📊 {symbol} - Trading pattern detected!"
        
        elif alert.alert_type.value == 'volume_spike':
            return f"📈 {symbol} - Unusual volume spike detected!"
        
        elif alert.alert_type.value == 'risk_high':
            return f"⚠️ {symbol} - High risk detected!"
        
        else:
            return f"🔔 {symbol} - Alert triggered!"
    
    def _send_in_app(self, notification: Dict[str, Any]) -> None:
        """Send in-app notification."""
        DebugUtils.info(f"In-app notification: {notification['message']}")
        # In-app notifications are stored in queue for UI retrieval
    
    def _send_email(self, alert: Alert, notification: Dict[str, Any]) -> None:
        """Send email notification."""
        # Email sending would require email configuration
        DebugUtils.info(f"Email notification sent for alert {alert.id}")
        # TODO: Implement email sending
    
    def _send_push(self, notification: Dict[str, Any]) -> None:
        """Send browser push notification."""
        # Push notifications would require browser push API
        DebugUtils.info(f"Push notification sent: {notification['message']}")
        # TODO: Implement push notifications
    
    def get_notifications(
        self,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get notifications from queue.
        
        Args:
            limit: Maximum number of notifications
            unread_only: Only return unread notifications
            
        Returns:
            List of notifications
        """
        notifications = self.notification_queue.copy()
        
        if unread_only:
            notifications = [n for n in notifications if not n.get('read', False)]
        
        # Sort by timestamp descending
        notifications.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return notifications[:limit]
    
    def mark_as_read(self, notification_id: str) -> None:
        """Mark notification as read."""
        for notification in self.notification_queue:
            if notification.get('alert_id') == notification_id:
                notification['read'] = True
                break

