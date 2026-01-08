"""
Resilience Module

Provides operational resilience and disaster recovery:
- Heartbeat monitoring
- Service management with auto-restart
- State recovery after crashes
- Duplicate prevention with idempotency
- Safe shutdown handling
"""

from backend.resilience.heartbeat_monitor import HeartbeatMonitor, Heartbeat
from backend.resilience.service_manager import ServiceManager
from backend.resilience.state_recovery import StateRecovery
from backend.resilience.duplicate_prevention import DuplicatePrevention
from backend.resilience.safe_shutdown import SafeShutdown

__all__ = [
    'HeartbeatMonitor',
    'Heartbeat',
    'ServiceManager',
    'StateRecovery',
    'DuplicatePrevention',
    'SafeShutdown'
]
