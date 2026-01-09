"""
Polling Service

Primary method for real-time updates via REST API polling.
Polling-first design with configurable intervals per workspace.
"""

import time
import threading
from typing import Dict, Any, Callable, Optional
from datetime import datetime

from utils.debug_utils import DebugUtils


class PollingService:
    """
    Polling service for real-time updates.
    
    Primary method for getting real-time data updates.
    Polls existing REST endpoints at configurable intervals.
    """
    
    def __init__(self, default_interval: float = 2.0):
        """
        Initialize polling service.
        
        Args:
            default_interval: Default polling interval in seconds
        """
        self.default_interval = default_interval
        self.workspace_intervals = {
            'insight': 3.0,  # 3 seconds for insight
            'discover': 2.0,  # 2 seconds for discover (more active)
            'decide': 5.0,  # 5 seconds for decide (less frequent)
            'execute': 1.0,  # 1 second for execute (most critical)
            'review': 5.0   # 5 seconds for review (less frequent)
        }
        self._running = False
        self._threads: Dict[str, threading.Thread] = {}
        self._callbacks: Dict[str, Callable] = {}
        self._last_poll: Dict[str, datetime] = {}
    
    def start_polling(
        self,
        workspace: str,
        callback: Callable[[], None],
        interval: Optional[float] = None
    ) -> None:
        """
        Start polling for a workspace.
        
        Args:
            workspace: Workspace ID
            callback: Callback function to call on each poll
            interval: Polling interval in seconds (uses default if None)
        """
        if workspace in self._threads and self._threads[workspace].is_alive():
            # Already polling, update callback
            self._callbacks[workspace] = callback
            return
        
        self._callbacks[workspace] = callback
        poll_interval = interval or self.workspace_intervals.get(workspace, self.default_interval)
        
        def poll_loop():
            while self._running and workspace in self._callbacks:
                try:
                    if workspace in self._callbacks:
                        self._callbacks[workspace]()
                        self._last_poll[workspace] = datetime.now()
                    time.sleep(poll_interval)
                except Exception as e:
                    DebugUtils.debug(f"Error in polling loop for {workspace}: {e}")
                    time.sleep(poll_interval)  # Continue polling even on error
        
        thread = threading.Thread(target=poll_loop, daemon=True)
        thread.start()
        self._threads[workspace] = thread
        self._running = True
    
    def stop_polling(self, workspace: str) -> None:
        """
        Stop polling for a workspace.
        
        Args:
            workspace: Workspace ID
        """
        if workspace in self._callbacks:
            del self._callbacks[workspace]
    
    def stop_all(self) -> None:
        """Stop all polling."""
        self._running = False
        self._callbacks.clear()
        self._threads.clear()
    
    def get_last_poll_time(self, workspace: str) -> Optional[datetime]:
        """
        Get last poll time for a workspace.
        
        Args:
            workspace: Workspace ID
            
        Returns:
            Last poll datetime or None
        """
        return self._last_poll.get(workspace)
    
    def is_polling(self, workspace: str) -> bool:
        """
        Check if polling is active for a workspace.
        
        Args:
            workspace: Workspace ID
            
        Returns:
            True if polling is active
        """
        return workspace in self._threads and self._threads[workspace].is_alive()


# Global polling service instance
_polling_service: Optional[PollingService] = None


def get_polling_service() -> PollingService:
    """
    Get global polling service instance.
    
    Returns:
        PollingService instance
    """
    global _polling_service
    if _polling_service is None:
        _polling_service = PollingService()
    return _polling_service

