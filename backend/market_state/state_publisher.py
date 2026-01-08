"""
State Publisher

Publishes market state to subscribers via Redis pub/sub.
"""

from typing import Optional
from datetime import datetime

from utils.debug_utils import DebugUtils
from backend.core.event_bus import EventBus
from backend.market_state.state_engine import MarketState


class StatePublisher:
    """
    Publishes market state to subscribers.
    
    Publishing mechanisms:
    - Redis pub/sub
    - WebSocket broadcast
    - Event bus
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize state publisher.
        
        Args:
            event_bus: Event bus for publishing
        """
        self.event_bus = event_bus or EventBus()
        self.update_frequency_seconds = 300  # 5 minutes
        self.last_publish_time: Optional[datetime] = None
    
    def publish_state(self, state: MarketState, force: bool = False):
        """
        Publish market state.
        
        Args:
            state: MarketState to publish
            force: Force publish even if within frequency limit
        """
        now = datetime.now()
        
        # Check if we should publish (respect frequency limit)
        if not force and self.last_publish_time:
            elapsed = (now - self.last_publish_time).total_seconds()
            if elapsed < self.update_frequency_seconds:
                return  # Too soon to publish
        
        # Publish to Redis
        self.event_bus.publish("market_state:current", {
            'type': 'market_state_update',
            'state': {
                'timestamp': state.timestamp.isoformat(),
                'regime': state.regime,
                'volatility_state': state.volatility_state,
                'breadth_state': state.breadth_state,
                'liquidity_state': state.liquidity_state,
                'vix_level': state.vix_level,
                'market_direction': state.market_direction,
                'confidence': state.confidence,
                'indicators': state.indicators
            }
        })
        
        self.last_publish_time = now
        DebugUtils.debug(f"Published market state: {state.regime}")

