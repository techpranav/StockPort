"""
Alert Engine

Monitors stocks and triggers alerts based on real-time data.
"""

from typing import Dict, List, Optional
from datetime import datetime
import threading
import time

from services.alerts.alert_manager import AlertManager
from services.alerts.notification_service import NotificationService
from core.enhanced_analyzer import EnhancedStockAnalyzer
from utils.debug_utils import DebugUtils
from config.app_config import ENABLE_ALERTS


class AlertEngine:
    """
    Alert monitoring engine.
    
    Features:
    - Continuous monitoring of active alerts
    - Real-time data fetching and analysis
    - Automatic alert triggering
    - Notification delivery
    """
    
    def __init__(self, analyzer: Optional[EnhancedStockAnalyzer] = None):
        """
        Initialize alert engine.
        
        Args:
            analyzer: Optional enhanced analyzer instance
        """
        self.alert_manager = AlertManager()
        self.notification_service = NotificationService()
        self.analyzer = analyzer or EnhancedStockAnalyzer()
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.check_interval = 60  # Check every 60 seconds
        DebugUtils.info("Initialized AlertEngine")
    
    def start_monitoring(self) -> None:
        """Start monitoring alerts in background thread."""
        if self.monitoring:
            DebugUtils.warning("Alert monitoring already running")
            return
        
        if not ENABLE_ALERTS:
            DebugUtils.info("Alerts are disabled in configuration")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        DebugUtils.info("Started alert monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring alerts."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        DebugUtils.info("Stopped alert monitoring")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring:
            try:
                # Get all active alerts
                active_alerts = self.alert_manager.get_alerts(status=AlertStatus.ACTIVE)
                
                if not active_alerts:
                    time.sleep(self.check_interval)
                    continue
                
                # Group by symbol
                symbols_to_check = list(set(a.symbol for a in active_alerts))
                
                # Check each symbol
                for symbol in symbols_to_check:
                    try:
                        # Fetch current data
                        analysis = self.analyzer.analyze_stock_comprehensive(
                            symbol,
                            include_intraday=True,
                            include_patterns=True,
                            include_entry_signals=True
                        )
                        
                        # Prepare current data for alert checking
                        current_data = {
                            'current_price': analysis.get('base_data', {}).get('current_price'),
                            'signal_type': analysis.get('entry_signals', {}).get('signal_type') if analysis.get('entry_signals') else None,
                            'patterns': analysis.get('patterns', {}),
                            'volume_spike': analysis.get('indicators', {}).get('unusual_volume'),
                            'risk_metrics': analysis.get('risk_metrics', {})
                        }
                        
                        # Check alerts
                        triggered = self.alert_manager.check_alerts(symbol, current_data)
                        
                        # Send notifications
                        for alert in triggered:
                            self.notification_service.send_alert_notification(alert, current_data)
                    
                    except Exception as e:
                        DebugUtils.log_error(e, f"Error checking alerts for {symbol}")
                
                # Sleep before next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                DebugUtils.log_error(e, "Error in alert monitoring loop")
                time.sleep(self.check_interval)
    
    def check_alerts_now(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Check alerts for a symbol immediately (synchronous).
        
        Args:
            symbol: Stock symbol to check
            
        Returns:
            List of triggered alerts
        """
        try:
            analysis = self.analyzer.analyze_stock_comprehensive(
                symbol,
                include_intraday=True,
                include_patterns=True,
                include_entry_signals=True
            )
            
            current_data = {
                'current_price': analysis.get('base_data', {}).get('current_price'),
                'signal_type': analysis.get('entry_signals', {}).get('signal_type') if analysis.get('entry_signals') else None,
                'patterns': analysis.get('patterns', {}),
                'volume_spike': analysis.get('indicators', {}).get('unusual_volume'),
                'risk_metrics': analysis.get('risk_metrics', {})
            }
            
            triggered = self.alert_manager.check_alerts(symbol, current_data)
            
            # Send notifications
            for alert in triggered:
                self.notification_service.send_alert_notification(alert, current_data)
            
            return [a.to_dict() for a in triggered]
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error checking alerts for {symbol}")
            return []

