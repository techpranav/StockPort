"""
Attribution Engine

Main attribution engine for trade attribution.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from utils.debug_utils import DebugUtils
from backend.attribution.trade_attributor import TradeAttributor
from backend.attribution.indicator_contributor import IndicatorContributor
from backend.attribution.failure_classifier import FailureClassifier


@dataclass
class TradeAttribution:
    """Trade attribution data."""
    trade_id: str
    strategy_id: str
    symbol: str
    entry_reason: str
    exit_reason: str
    pnl: float
    pnl_percent: float
    entry_indicators: Dict[str, float]
    entry_indicator_contributions: Dict[str, float]
    entry_patterns: List[str]
    entry_regime: str
    exit_indicators: Dict[str, float]
    exit_reason_category: str
    exit_timing: str
    max_favorable_excursion: float
    max_adverse_excursion: float
    entry_quality: float
    exit_quality: float


class AttributionEngine:
    """
    Main attribution engine.
    
    Attributes trades to:
    - Entry indicators
    - Exit reasons
    - Performance factors
    """
    
    def __init__(self):
        """Initialize attribution engine."""
        self.trade_attributor = TradeAttributor()
        self.indicator_contributor = IndicatorContributor()
        self.failure_classifier = FailureClassifier()
    
    def attribute_trade(self, trade: Dict[str, Any]) -> TradeAttribution:
        """
        Attribute a trade.
        
        Args:
            trade: Trade dictionary
            
        Returns:
            TradeAttribution object
        """
        # Get entry attribution
        entry_attribution = self.trade_attributor.attribute_entry(trade)
        
        # Get exit attribution
        exit_attribution = self.trade_attributor.attribute_exit(trade)
        
        # Get indicator contributions
        indicator_contributions = self.indicator_contributor.calculate_contributions(trade)
        
        # Calculate entry/exit quality
        entry_quality = self._calculate_entry_quality(trade, entry_attribution)
        exit_quality = self._calculate_exit_quality(trade, exit_attribution)
        
        return TradeAttribution(
            trade_id=trade.get('trade_id', ''),
            strategy_id=trade.get('strategy_id', ''),
            symbol=trade.get('symbol', ''),
            entry_reason=entry_attribution.get('reason', ''),
            exit_reason=exit_attribution.get('reason', ''),
            pnl=trade.get('pnl', 0.0),
            pnl_percent=trade.get('pnl_percent', 0.0),
            entry_indicators=entry_attribution.get('indicators', {}),
            entry_indicator_contributions=indicator_contributions,
            entry_patterns=entry_attribution.get('patterns', []),
            entry_regime=entry_attribution.get('regime', ''),
            exit_indicators=exit_attribution.get('indicators', {}),
            exit_reason_category=exit_attribution.get('category', ''),
            exit_timing=exit_attribution.get('timing', ''),
            max_favorable_excursion=trade.get('max_favorable_excursion', 0.0),
            max_adverse_excursion=trade.get('max_adverse_excursion', 0.0),
            entry_quality=entry_quality,
            exit_quality=exit_quality
        )
    
    def _calculate_entry_quality(
        self,
        trade: Dict[str, Any],
        entry_attribution: Dict[str, Any]
    ) -> float:
        """
        Calculate entry quality (0-1).
        
        Factors:
        - Entry price vs optimal entry
        - Signal strength
        - Indicator alignment
        - Regime match
        """
        quality = 0.5  # Base quality
        
        # Check signal strength (if available)
        signal = trade.get('signal', {})
        score = signal.get('score', 50) / 100.0  # Normalize to 0-1
        quality += score * 0.3
        
        # Check indicator contributions
        contributions = entry_attribution.get('entry_indicator_contributions', {})
        if contributions:
            # Higher contribution diversity = better quality
            num_indicators = len(contributions)
            if num_indicators >= 3:
                quality += 0.1
            if num_indicators >= 5:
                quality += 0.1
        
        # Check regime match
        regime = entry_attribution.get('regime', '')
        if regime and regime != 'unknown':
            quality += 0.05
        
        return min(1.0, quality)
    
    def _calculate_exit_quality(
        self,
        trade: Dict[str, Any],
        exit_attribution: Dict[str, Any]
    ) -> float:
        """
        Calculate exit quality (0-1).
        
        Factors:
        - Exit timing
        - Exit reason category
        - Max favorable excursion captured
        """
        quality = 0.5  # Base quality
        
        # Check exit category
        category = exit_attribution.get('category', '')
        if category == 'profit_target':
            quality += 0.3  # Good exit
        elif category == 'stop_loss':
            quality += 0.1  # Necessary but not ideal
        elif category == 'time_based':
            quality += 0.2  # Reasonable
        
        # Check if captured favorable excursion
        mfe = trade.get('max_favorable_excursion', 0.0)
        pnl = trade.get('pnl', 0.0)
        if mfe > 0 and pnl > 0:
            capture_ratio = pnl / mfe if mfe > 0 else 0.0
            quality += capture_ratio * 0.2
        
        return min(1.0, quality)

