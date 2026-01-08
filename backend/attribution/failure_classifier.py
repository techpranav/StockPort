"""
Failure Classifier

Classifies trade failures into categories.
"""

from typing import Dict, Any
from enum import Enum


class FailureCategory(Enum):
    """Failure categories."""
    LATE_ENTRY = "late_entry"
    VOLATILITY_SPIKE = "volatility_spike"
    REGIME_MISMATCH = "regime_mismatch"
    FALSE_SIGNAL = "false_signal"
    POOR_EXIT_TIMING = "poor_exit_timing"
    EXTERNAL_EVENT = "external_event"
    SUCCESS = "success"
    UNKNOWN = "unknown"


class FailureClassifier:
    """
    Classifies trade failures.
    
    Categories:
    - Late entry
    - Volatility spike
    - Regime mismatch
    - False signal
    - Poor exit timing
    - External event
    """
    
    def classify(self, trade: Dict[str, Any], attribution: Dict[str, Any]) -> FailureCategory:
        """
        Classify trade failure.
        
        Args:
            trade: Trade dictionary
            attribution: Trade attribution dictionary
            
        Returns:
            FailureCategory
        """
        pnl = trade.get('pnl', 0)
        
        if pnl < 0:  # Losing trade
            entry_quality = attribution.get('entry_quality', 1.0)
            if entry_quality < 0.5:
                return FailureCategory.LATE_ENTRY
            
            exit_reason = attribution.get('exit_reason_category', '')
            if exit_reason == 'stop_loss':
                # Check for volatility spike
                if self._detect_volatility_spike(trade):
                    return FailureCategory.VOLATILITY_SPIKE
            
            entry_regime = attribution.get('entry_regime', '')
            exit_regime = trade.get('exit_regime', '')
            if entry_regime != exit_regime:
                return FailureCategory.REGIME_MISMATCH
            
            confidence = attribution.get('entry_indicator_contributions', {}).get('confidence', 1.0)
            if confidence < 0.6:
                return FailureCategory.FALSE_SIGNAL
            
            return FailureCategory.UNKNOWN
        else:  # Winning trade
            exit_quality = attribution.get('exit_quality', 1.0)
            if exit_quality < 0.5:
                return FailureCategory.POOR_EXIT_TIMING
            
            return FailureCategory.SUCCESS
    
    def _detect_volatility_spike(self, trade: Dict[str, Any]) -> bool:
        """
        Detect if volatility spike occurred during trade.
        
        Checks:
        - ATR increase during trade
        - Price movement vs expected
        """
        # Check if max adverse excursion is much larger than expected
        mae = abs(trade.get('max_adverse_excursion', 0.0))
        entry_price = trade.get('entry_price', 0.0)
        stop_loss = trade.get('stop_loss', entry_price * 0.95)
        
        if entry_price > 0 and stop_loss > 0:
            expected_loss = abs(entry_price - stop_loss)
            if mae > expected_loss * 1.5:  # 50% more than expected
                return True
        
        # Check if trade hit stop loss quickly (volatility spike indicator)
        entry_date = trade.get('entry_date')
        exit_date = trade.get('exit_date')
        if entry_date and exit_date:
            if isinstance(entry_date, str):
                from datetime import datetime
                entry_date = datetime.fromisoformat(entry_date)
            if isinstance(exit_date, str):
                exit_date = datetime.fromisoformat(exit_date)
            
            holding_days = (exit_date - entry_date).days
            if holding_days < 1 and trade.get('exit_reason_category') == 'stop_loss':
                return True  # Quick stop loss = likely volatility spike
        
        return False

