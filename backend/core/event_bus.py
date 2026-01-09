"""
Event Bus for Pub/Sub Messaging

Provides event-driven communication between system components.
"""

from typing import Dict, Any, Callable, List, Optional
from datetime import datetime
import redis
from threading import Lock
import json
import os

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
        # Check if using fakeredis for development (when Redis server not available)
        use_fakeredis = os.getenv("USE_FAKEREDIS", "false").lower() == "true"
        
        if use_fakeredis:
            try:
                import fakeredis
                self.redis_client = fakeredis.FakeStrictRedis(decode_responses=True)
                self.redis_client.ping()
                DebugUtils.warning("Using fakeredis (in-memory mock) for development. NOT for production!")
                DebugUtils.info("EventBus using fakeredis (mock Redis)")
            except ImportError:
                DebugUtils.error("fakeredis not installed. Install with: pip install fakeredis")
                raise ImportError("fakeredis not installed. Install with: pip install fakeredis")
        else:
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
                # Redis is REQUIRED - raise error if not available
                error_msg = f"Redis connection failed at {redis_host}:{redis_port}. Redis is required for EventBus. Error: {e}"
                DebugUtils.error(error_msg)
                DebugUtils.error("To use fakeredis for development, set USE_FAKEREDIS=true environment variable")
                raise ConnectionError(error_msg) from e
        
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
            raise RuntimeError("Redis client not initialized. Cannot publish event.")
        
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

