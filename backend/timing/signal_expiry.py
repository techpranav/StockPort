"""
Signal Expiry

Manages signal expiry logic.
"""

from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from utils.debug_utils import DebugUtils
from models.strategy_signal import StrategySignal


@dataclass
class SignalExpiry:
    """Signal expiry information."""
    signal_id: str
    generated_at: datetime
    expires_at: datetime
    strategy_type: str
    expiry_minutes: int
    is_expired: bool
    age_seconds: float


class SignalExpiryManager:
    """
    Manages signal expiry.
    
    Expiry rules:
    - Intraday: 5 minutes
    - Swing: 1 hour
    - Position: 4 hours
    """
    
    def __init__(self):
        """Initialize signal expiry manager."""
        from backend.settings import get_settings
        self.settings = get_settings()
        
        # Subscribe to settings changes for real-time updates
        self.settings.subscribe('timing.signal_expiry_intraday_minutes', self._on_intraday_changed)
        self.settings.subscribe('timing.signal_expiry_swing_minutes', self._on_swing_changed)
        self.settings.subscribe('timing.signal_expiry_position_minutes', self._on_position_changed)
        self.settings.subscribe('timing.price_change_threshold_percent', self._on_price_threshold_changed)
        
        # Initialize expiry times from settings
        self._expiry_times = {}
        self._price_change_threshold = None
        self._update_from_settings()
    
    def _update_from_settings(self):
        """Update expiry times from settings."""
        self._expiry_times = {
            'intraday': self.settings.get_signal_expiry_intraday_minutes(),
            'swing': self.settings.get_signal_expiry_swing_minutes(),
            'position': self.settings.get_signal_expiry_position_minutes()
        }
        self._price_change_threshold = self.settings.get_price_change_threshold_percent()
    
    def _on_intraday_changed(self, key: str, old_value: int, new_value: int):
        """Handle intraday expiry change."""
        self._expiry_times['intraday'] = new_value
        DebugUtils.info(f"SignalExpiryManager: Intraday expiry updated to {new_value} minutes")
    
    def _on_swing_changed(self, key: str, old_value: int, new_value: int):
        """Handle swing expiry change."""
        self._expiry_times['swing'] = new_value
        DebugUtils.info(f"SignalExpiryManager: Swing expiry updated to {new_value} minutes")
    
    def _on_position_changed(self, key: str, old_value: int, new_value: int):
        """Handle position expiry change."""
        self._expiry_times['position'] = new_value
        DebugUtils.info(f"SignalExpiryManager: Position expiry updated to {new_value} minutes")
    
    def _on_price_threshold_changed(self, key: str, old_value: float, new_value: float):
        """Handle price change threshold change."""
        self._price_change_threshold = new_value
        DebugUtils.info(f"SignalExpiryManager: Price change threshold updated to {new_value:.1%}")
    
    @property
    def expiry_times(self) -> Dict[str, int]:
        """Get current expiry times."""
        if not self._expiry_times:
            self._update_from_settings()
        return self._expiry_times
    
    def is_signal_stale(
        self,
        signal: StrategySignal,
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Check if signal is stale.
        
        Args:
            signal: Strategy signal
            current_time: Current time (default: now)
            
        Returns:
            True if stale, False otherwise
        """
        if current_time is None:
            current_time = datetime.now()
        
        if signal.timestamp is None:
            return True  # No timestamp = stale
        
        # Determine strategy type (simplified)
        strategy_type = self._get_strategy_type(signal.strategy_id)
        expiry_minutes = self.expiry_times.get(strategy_type, 60)
        
        age = (current_time - signal.timestamp).total_seconds() / 60  # minutes
        
        if age > expiry_minutes:
            return True
        
        # Check if price changed significantly (if opportunity is available)
        if hasattr(signal, 'opportunity') and signal.opportunity:
            price_change = abs(
                signal.opportunity.price - signal.entry_price
            ) / signal.entry_price if signal.entry_price > 0 else 0
            
            threshold = self._price_change_threshold or 0.05
            if price_change > threshold:
                DebugUtils.debug(f"Signal {signal.signal_id} stale: price changed {price_change:.2%} (threshold: {threshold:.1%})")
                return True
        
        return False
    
    def get_expiry_info(self, signal: StrategySignal) -> SignalExpiry:
        """
        Get expiry information for signal.
        
        Args:
            signal: Strategy signal
            
        Returns:
            SignalExpiry object
        """
        strategy_type = self._get_strategy_type(signal.strategy_id)
        expiry_minutes = self.expiry_times.get(strategy_type, 60)
        
        generated_at = signal.timestamp or datetime.now()
        expires_at = generated_at + timedelta(minutes=expiry_minutes)
        
        current_time = datetime.now()
        age_seconds = (current_time - generated_at).total_seconds()
        is_expired = age_seconds > (expiry_minutes * 60)
        
        return SignalExpiry(
            signal_id=signal.signal_id,
            generated_at=generated_at,
            expires_at=expires_at,
            strategy_type=strategy_type,
            expiry_minutes=expiry_minutes,
            is_expired=is_expired,
            age_seconds=age_seconds
        )
    
    def _get_strategy_type(self, strategy_id: str) -> str:
        """Get strategy type from strategy ID."""
        if 'intraday' in strategy_id.lower():
            return 'intraday'
        elif 'swing' in strategy_id.lower():
            return 'swing'
        elif 'position' in strategy_id.lower():
            return 'position'
        else:
            return 'swing'  # Default

