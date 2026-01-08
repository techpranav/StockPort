"""
Stale Detector

Detects stale opportunities and signals.
"""

from typing import Optional
from datetime import datetime

from utils.debug_utils import DebugUtils
from models.opportunity import Opportunity
from models.strategy_signal import StrategySignal
from backend.timing.signal_expiry import SignalExpiryManager


class StaleDetector:
    """
    Detects stale opportunities and signals.
    
    Staleness indicators:
    - Time elapsed > expiry time
    - Price changed > 5%
    - Volume dropped > 50%
    """
    
    def __init__(self):
        """Initialize stale detector."""
        from backend.settings import get_settings
        self.settings = get_settings()
        self.expiry_manager = SignalExpiryManager()
        
        # Subscribe to settings changes
        self.settings.subscribe('timing.price_change_threshold_percent', self._on_price_threshold_changed)
        self.settings.subscribe('timing.volume_drop_threshold_percent', self._on_volume_threshold_changed)
        
        # Initialize from settings
        self._price_change_threshold = None
        self._volume_drop_threshold = None
        self._update_from_settings()
    
    def _update_from_settings(self):
        """Update thresholds from settings."""
        self._price_change_threshold = self.settings.get_price_change_threshold_percent()
        self._volume_drop_threshold = self.settings.get_volume_drop_threshold_percent()
    
    def _on_price_threshold_changed(self, key: str, old_value: float, new_value: float):
        """Handle price threshold change."""
        self._price_change_threshold = new_value
        DebugUtils.info(f"StaleDetector: Price change threshold updated to {new_value:.1%}")
    
    def _on_volume_threshold_changed(self, key: str, old_value: float, new_value: float):
        """Handle volume threshold change."""
        self._volume_drop_threshold = new_value
        DebugUtils.info(f"StaleDetector: Volume drop threshold updated to {new_value:.1%}")
    
    @property
    def price_change_threshold(self) -> float:
        """Get current price change threshold."""
        if self._price_change_threshold is None:
            self._price_change_threshold = self.settings.get_price_change_threshold_percent()
        return self._price_change_threshold
    
    @property
    def volume_drop_threshold(self) -> float:
        """Get current volume drop threshold."""
        if self._volume_drop_threshold is None:
            self._volume_drop_threshold = self.settings.get_volume_drop_threshold_percent()
        return self._volume_drop_threshold
    
    def is_opportunity_stale(
        self,
        opportunity: Opportunity,
        signal: StrategySignal
    ) -> bool:
        """
        Check if opportunity is stale.
        
        Args:
            opportunity: Opportunity to check
            signal: Strategy signal
            
        Returns:
            True if stale, False otherwise
        """
        # Check signal expiry
        if self.expiry_manager.is_signal_stale(signal):
            return True
        
        # Check price change
        price_change = abs(
            opportunity.price - signal.entry_price
        ) / signal.entry_price if signal.entry_price > 0 else 0
        
        if price_change > self.price_change_threshold:
            DebugUtils.debug(f"Opportunity {opportunity.symbol} stale: price changed {price_change:.2%}")
            return True
        
        # Check volume (if available)
        if hasattr(opportunity, 'volume') and hasattr(signal, 'opportunity') and signal.opportunity:
            if hasattr(signal.opportunity, 'volume') and signal.opportunity.volume > 0:
                volume_ratio = opportunity.volume / signal.opportunity.volume
                if volume_ratio < self.volume_drop_threshold:
                    DebugUtils.debug(f"Opportunity {opportunity.symbol} stale: volume dropped {volume_ratio:.2%}")
                    return True
        
        return False

