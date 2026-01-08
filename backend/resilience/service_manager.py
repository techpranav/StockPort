"""
Service Manager

Auto-restarts failed services.
"""

from typing import Dict, Any, List
import time

from utils.debug_utils import DebugUtils
from backend.resilience.heartbeat_monitor import HeartbeatMonitor


class ServiceManager:
    """
    Manages services with auto-restart.
    
    Features:
    - Service monitoring
    - Auto-restart on failure
    - Health verification
    """
    
    def __init__(self, heartbeat_monitor: HeartbeatMonitor):
        """
        Initialize service manager.
        
        Args:
            heartbeat_monitor: Heartbeat monitor instance
        """
        self.heartbeat_monitor = heartbeat_monitor
        self.services: Dict[str, Any] = {}  # service_id -> service instance
    
    def register_service(self, service_id: str, service: Any):
        """
        Register a service.
        
        Args:
            service_id: Service identifier
            service: Service instance
        """
        self.services[service_id] = service
        DebugUtils.info(f"Registered service: {service_id}")
    
    def monitor_services(self):
        """Monitor all services and restart if needed."""
        unhealthy = self.heartbeat_monitor.get_unhealthy_services()
        
        for service_id in unhealthy:
            if service_id in self.services:
                DebugUtils.warning(f"Service {service_id} is unhealthy, attempting restart")
                self.restart_service(service_id)
    
    def restart_service(self, service_id: str):
        """
        Restart a service.
        
        Args:
            service_id: Service identifier
        """
        if service_id not in self.services:
            DebugUtils.warning(f"Service {service_id} not found")
            return
        
        service = self.services[service_id]
        
        try:
            # Attempt graceful shutdown
            if hasattr(service, 'shutdown'):
                service.shutdown()
            
            time.sleep(10)  # Wait before restart
            
            # Restart service
            if hasattr(service, 'start'):
                service.start()
            
            # Verify health
            if self.heartbeat_monitor.is_service_healthy(service_id):
                DebugUtils.info(f"Service {service_id} restarted successfully")
            else:
                DebugUtils.error(f"Service {service_id} failed to restart")
        except Exception as e:
            DebugUtils.log_error(e, f"Error restarting service {service_id}")

