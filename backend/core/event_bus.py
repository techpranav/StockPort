"""
Event Bus for Pub/Sub Messaging

Provides event-driven communication between system components.
"""

from typing import Dict, Any, Callable, List, Optional
from datetime import datetime
import redis
from threading import Lock
import json

from utils.debug_utils import DebugUtils
from config.app_config import REDIS_HOST, REDIS_PORT, REDIS_DB


class EventBus:
    """
    Event bus for pub/sub messaging using Redis.
    
    Provides:
    - Publish events to channels
    - Subscribe to events
    - Event routing
    """
    
    def __init__(
        self,
        redis_host: str = REDIS_HOST,
        redis_port: int = REDIS_PORT,
        redis_db: int = REDIS_DB
    ):
        """
        Initialize event bus.
        
        Args:
            redis_host: Redis host
            redis_port: Redis port
            redis_db: Redis database number
        """
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            DebugUtils.info(f"EventBus connected to Redis at {redis_host}:{redis_port}")
        except Exception as e:
            DebugUtils.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
        
        self.subscribers: Dict[str, List[Callable]] = {}
        self.lock = Lock()
    
    def publish(self, channel: str, event: Dict[str, Any]):
        """
        Publish an event to a channel.
        
        Args:
            channel: Channel name
            event: Event data dictionary
        """
        if not self.redis_client:
            DebugUtils.warning("Redis not available, event not published")
            return
        
        try:
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "channel": channel,
                "data": event
            }
            
            self.redis_client.publish(channel, json.dumps(event_data))
            DebugUtils.debug(f"Published event to channel {channel}: {event.get('type', 'unknown')}")
        except Exception as e:
            DebugUtils.log_error(e, f"Error publishing event to {channel}")
    
    def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to a channel.
        
        Args:
            channel: Channel name
            callback: Callback function to handle events
        """
        with self.lock:
            if channel not in self.subscribers:
                self.subscribers[channel] = []
            self.subscribers[channel].append(callback)
        
        DebugUtils.debug(f"Subscribed to channel {channel}")
    
    def unsubscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Unsubscribe from a channel.
        
        Args:
            channel: Channel name
            callback: Callback function to remove
        """
        with self.lock:
            if channel in self.subscribers:
                if callback in self.subscribers[channel]:
                    self.subscribers[channel].remove(callback)
        
        DebugUtils.debug(f"Unsubscribed from channel {channel}")

