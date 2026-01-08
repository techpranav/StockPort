"""
Heartbeat Monitor

Monitors service health via heartbeats.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from threading import Lock
from collections import defaultdict

from utils.debug_utils import DebugUtils


@dataclass
class Heartbeat:
    """Service heartbeat."""
    service_id: str
    timestamp: datetime
    status: str  # healthy, degraded, unhealthy
    metrics: Dict[str, Any]


class HeartbeatMonitor:
    """
    Monitors service health via heartbeats.
    
    Features:
    - Heartbeat tracking
    - Health status monitoring
    - Auto-alert on failures
    """
    
    def __init__(self, heartbeat_timeout: int = 90):
        """
        Initialize heartbeat monitor.
        
        Args:
            heartbeat_timeout: Timeout in seconds before considering service dead
        """
        self.heartbeat_timeout = heartbeat_timeout
        self.heartbeats: Dict[str, Heartbeat] = {}
        self.lock = Lock()
    
    def record_heartbeat(
        self,
        service_id: str,
        status: str = "healthy",
        metrics: Optional[Dict[str, Any]] = None
    ):
        """
        Record a heartbeat.
        
        Args:
            service_id: Service identifier
            status: Service status
            metrics: Service metrics (optional)
        """
        with self.lock:
            self.heartbeats[service_id] = Heartbeat(
                service_id=service_id,
                timestamp=datetime.now(),
                status=status,
                metrics=metrics or {}
            )
    
    def is_service_healthy(self, service_id: str) -> bool:
        """
        Check if service is healthy.
        
        Args:
            service_id: Service identifier
            
        Returns:
            True if healthy, False otherwise
        """
        with self.lock:
            heartbeat = self.heartbeats.get(service_id)
            if not heartbeat:
                return False
            
            elapsed = (datetime.now() - heartbeat.timestamp).total_seconds()
            if elapsed > self.heartbeat_timeout:
                return False
            
            return heartbeat.status == "healthy"
    
    def get_unhealthy_services(self) -> List[str]:
        """
        Get list of unhealthy services.
        
        Returns:
            List of unhealthy service IDs
        """
        unhealthy = []
        
        with self.lock:
            now = datetime.now()
            for service_id, heartbeat in self.heartbeats.items():
                elapsed = (now - heartbeat.timestamp).total_seconds()
                if elapsed > self.heartbeat_timeout or heartbeat.status != "healthy":
                    unhealthy.append(service_id)
        
        return unhealthy

