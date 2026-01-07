"""
Alert Manager

Manages stock alerts - creation, updates, deletion, and monitoring.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid

from models.alert import Alert, AlertType, AlertStatus
from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException


class AlertManager:
    """
    Manages stock alerts.
    
    Features:
    - Create/edit/delete alerts
    - Monitor alerts and trigger notifications
    - Alert history tracking
    - Alert performance metrics
    """
    
    def __init__(self):
        """Initialize alert manager."""
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Dict[str, Any]] = []
        DebugUtils.info("Initialized AlertManager")
    
    def create_alert(
        self,
        symbol: str,
        alert_type: AlertType,
        threshold_value: Optional[float] = None,
        condition: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        notification_channels: Optional[List[str]] = None
    ) -> Alert:
        """
        Create a new alert.
        
        Args:
            symbol: Stock symbol to monitor
            alert_type: Type of alert
            threshold_value: Threshold value for price alerts
            condition: Custom condition expression
            expires_at: Optional expiration date
            notification_channels: List of notification channels
            
        Returns:
            Created Alert object
        """
        alert_id = str(uuid.uuid4())
        
        alert = Alert(
            id=alert_id,
            symbol=symbol,
            alert_type=alert_type,
            threshold_value=threshold_value,
            condition=condition,
            expires_at=expires_at,
            notification_channels=notification_channels or ['in_app'],
            status=AlertStatus.ACTIVE
        )
        
        self.alerts[alert_id] = alert
        DebugUtils.info(f"Created alert {alert_id} for {symbol} ({alert_type.value})")
        
        return alert
    
    def update_alert(
        self,
        alert_id: str,
        **updates
    ) -> Optional[Alert]:
        """
        Update an existing alert.
        
        Args:
            alert_id: Alert ID
            **updates: Fields to update
            
        Returns:
            Updated Alert or None if not found
        """
        if alert_id not in self.alerts:
            DebugUtils.warning(f"Alert {alert_id} not found")
            return None
        
        alert = self.alerts[alert_id]
        
        # Update allowed fields
        allowed_fields = ['threshold_value', 'condition', 'expires_at', 'notification_channels', 'status']
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(alert, field, value)
        
        DebugUtils.info(f"Updated alert {alert_id}")
        return alert
    
    def delete_alert(self, alert_id: str) -> bool:
        """
        Delete an alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if deleted, False if not found
        """
        if alert_id not in self.alerts:
            return False
        
        del self.alerts[alert_id]
        DebugUtils.info(f"Deleted alert {alert_id}")
        return True
    
    def get_alerts(
        self,
        symbol: Optional[str] = None,
        status: Optional[AlertStatus] = None
    ) -> List[Alert]:
        """
        Get alerts with optional filtering.
        
        Args:
            symbol: Filter by symbol
            status: Filter by status
            
        Returns:
            List of matching alerts
        """
        alerts = list(self.alerts.values())
        
        if symbol:
            alerts = [a for a in alerts if a.symbol == symbol]
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        return alerts
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """
        Get alert by ID.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert or None if not found
        """
        return self.alerts.get(alert_id)
    
    def check_alerts(
        self,
        symbol: str,
        current_data: Dict[str, Any]
    ) -> List[Alert]:
        """
        Check if any alerts should be triggered for a symbol.
        
        Args:
            symbol: Stock symbol
            current_data: Current stock data (price, signals, etc.)
            
        Returns:
            List of triggered alerts
        """
        triggered = []
        
        # Get active alerts for this symbol
        active_alerts = [
            a for a in self.alerts.values()
            if a.symbol == symbol and a.status == AlertStatus.ACTIVE
        ]
        
        for alert in active_alerts:
            # Check expiration
            if alert.expires_at and datetime.now() > alert.expires_at:
                alert.status = AlertStatus.EXPIRED
                continue
            
            # Check if alert should trigger
            if self._should_trigger(alert, current_data):
                alert.status = AlertStatus.TRIGGERED
                alert.triggered_at = datetime.now()
                alert.trigger_count += 1
                alert.last_triggered = datetime.now()
                
                # Record in history
                self.alert_history.append({
                    'alert_id': alert.id,
                    'symbol': symbol,
                    'triggered_at': alert.triggered_at,
                    'alert_type': alert.alert_type.value,
                    'data': current_data
                })
                
                triggered.append(alert)
                DebugUtils.info(f"Alert {alert.id} triggered for {symbol}")
        
        return triggered
    
    def _should_trigger(
        self,
        alert: Alert,
        current_data: Dict[str, Any]
    ) -> bool:
        """
        Check if alert should trigger based on current data.
        
        Args:
            alert: Alert to check
            current_data: Current stock data
            
        Returns:
            True if alert should trigger
        """
        try:
            if alert.alert_type == AlertType.PRICE_ABOVE:
                current_price = current_data.get('current_price') or current_data.get('price')
                if current_price and alert.threshold_value:
                    return current_price >= alert.threshold_value
            
            elif alert.alert_type == AlertType.PRICE_BELOW:
                current_price = current_data.get('current_price') or current_data.get('price')
                if current_price and alert.threshold_value:
                    return current_price <= alert.threshold_value
            
            elif alert.alert_type == AlertType.SIGNAL_BUY:
                signal_type = current_data.get('signal_type') or current_data.get('entry_signal', {}).get('signal_type')
                return signal_type in ['STRONG_BUY', 'BUY']
            
            elif alert.alert_type == AlertType.SIGNAL_SELL:
                signal_type = current_data.get('signal_type') or current_data.get('entry_signal', {}).get('signal_type')
                return signal_type in ['SELL', 'AVOID']
            
            elif alert.alert_type == AlertType.PATTERN_DETECTED:
                patterns = current_data.get('patterns', {})
                if patterns:
                    candlestick = patterns.get('candlestick_patterns', [])
                    chart = patterns.get('chart_patterns', [])
                    return len(candlestick) > 0 or len(chart) > 0
            
            elif alert.alert_type == AlertType.VOLUME_SPIKE:
                volume_data = current_data.get('volume_spike') or current_data.get('unusual_volume')
                return volume_data is True if isinstance(volume_data, bool) else False
            
            elif alert.alert_type == AlertType.RISK_HIGH:
                risk_metrics = current_data.get('risk_metrics', {})
                volatility = risk_metrics.get('volatility', 0)
                return volatility > 30.0  # High volatility threshold
            
            elif alert.alert_type == AlertType.CUSTOM:
                # Evaluate custom condition (simplified - would need proper expression evaluator)
                if alert.condition:
                    # Basic condition evaluation (can be enhanced)
                    return self._evaluate_condition(alert.condition, current_data)
            
            return False
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error checking alert {alert.id}")
            return False
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """
        Evaluate custom condition expression.
        
        Args:
            condition: Condition expression
            data: Current data
            
        Returns:
            True if condition is met
            
        Note:
            This is a simplified implementation. For production use,
            consider using a safe expression evaluator like 'simpleeval'.
        """
        # Simplified condition evaluation - only supports basic comparisons
        # For security, we avoid eval() and use simple string matching
        try:
            # Extract variable and comparison from condition
            # Example: "price > 100" or "rsi < 30"
            condition = condition.strip()
            
            # Basic safety check - only allow alphanumeric, spaces, and comparison operators
            if not all(c.isalnum() or c in ' <>=!&|()' for c in condition):
                DebugUtils.warning(f"Unsafe condition expression: {condition}")
                return False
            
            # Replace data references with actual values
            for key, value in data.items():
                if isinstance(value, (int, float, bool)):
                    # Replace common patterns
                    condition = condition.replace(f"data['{key}']", str(value))
                    condition = condition.replace(f'data["{key}"]', str(value))
                    condition = condition.replace(f"data.{key}", str(value))
                    condition = condition.replace(key, str(value))
            
            # Use simpleeval for safe evaluation (if available)
            try:
                from simpleeval import simple_eval
                return bool(simple_eval(condition))
            except ImportError:
                # Fallback: Only allow simple numeric comparisons
                # This is a very basic implementation
                DebugUtils.warning("simpleeval not available, using basic condition evaluation")
                # For now, return False to avoid security risks
                return False
                
        except Exception as e:
            DebugUtils.log_error(e, f"Error evaluating condition: {condition}")
            return False
    
    def get_alert_history(
        self,
        symbol: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get alert history.
        
        Args:
            symbol: Filter by symbol
            limit: Maximum number of records
            
        Returns:
            List of alert history records
        """
        history = self.alert_history.copy()
        
        if symbol:
            history = [h for h in history if h.get('symbol') == symbol]
        
        # Sort by triggered_at descending
        history.sort(key=lambda x: x.get('triggered_at', ''), reverse=True)
        
        return history[:limit]

