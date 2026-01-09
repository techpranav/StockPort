"""
Signal Confidence Calculator

Calculates multi-factor confidence scores for trading signals.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd

from utils.debug_utils import DebugUtils
from services.analyzers.indicators.support_resistance_validator import SupportResistanceValidator


class ConfidenceCalculator:
    """
    Confidence calculator for signals.
    
    Features:
    - Multi-factor confidence scoring
    - Historical accuracy tracking
    - Regime-adjusted confidence
    - Support/resistance validation impact
    - Signal quality metrics
    """
    
    def __init__(self):
        """Initialize confidence calculator."""
        self.historical_accuracy: Dict[str, Dict[str, Any]] = {}  # strategy_id -> accuracy metrics
        self.support_resistance_validator = SupportResistanceValidator()
    
    def calculate_confidence(
        self,
        signal_score: float,
        indicators: Dict[str, Any],
        patterns: Optional[Dict[str, Any]] = None,
        support_resistance: Optional[Dict[str, Any]] = None,
        market_regime: Optional[str] = None,
        strategy_id: Optional[str] = None,
        historical_accuracy: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive confidence score.
        
        Args:
            signal_score: Base signal score (0-100)
            indicators: Technical indicators
            patterns: Pattern analysis results
            support_resistance: Support/resistance validation results
            market_regime: Current market regime
            strategy_id: Strategy identifier
            historical_accuracy: Historical accuracy for this strategy (optional)
            
        Returns:
            Dictionary with confidence metrics
        """
        try:
            # Base confidence from signal score
            base_confidence = signal_score / 100.0
            
            # Factor 1: Indicator alignment (0-0.3)
            indicator_confidence = self._calculate_indicator_confidence(indicators)
            
            # Factor 2: Pattern confirmation (0-0.2)
            pattern_confidence = self._calculate_pattern_confidence(patterns)
            
            # Factor 3: Support/resistance validation (0-0.2)
            sr_confidence = self._calculate_sr_confidence(support_resistance)
            
            # Factor 4: Regime compatibility (0-0.1)
            regime_confidence = self._calculate_regime_confidence(market_regime, strategy_id)
            
            # Factor 5: Historical accuracy (0-0.2)
            accuracy_confidence = historical_accuracy if historical_accuracy else self._get_historical_accuracy(strategy_id)
            
            # Weighted combination
            total_confidence = (
                base_confidence * 0.3 +
                indicator_confidence * 0.3 +
                pattern_confidence * 0.2 +
                sr_confidence * 0.2 +
                regime_confidence * 0.1 +
                accuracy_confidence * 0.2
            ) / 1.3  # Normalize to account for all factors
            
            # Clamp to [0, 1]
            total_confidence = max(0.0, min(1.0, total_confidence))
            
            return {
                'total_confidence': float(total_confidence),
                'base_confidence': float(base_confidence),
                'indicator_confidence': float(indicator_confidence),
                'pattern_confidence': float(pattern_confidence),
                'support_resistance_confidence': float(sr_confidence),
                'regime_confidence': float(regime_confidence),
                'historical_accuracy': float(accuracy_confidence),
                'confidence_level': self._classify_confidence(total_confidence)
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating confidence")
            return {
                'total_confidence': 0.5,
                'confidence_level': 'MODERATE'
            }
    
    def _calculate_indicator_confidence(self, indicators: Dict[str, Any]) -> float:
        """Calculate confidence from indicator alignment."""
        if not indicators:
            return 0.5
        
        # Count aligned indicators
        aligned_count = 0
        total_count = 0
        
        # RSI alignment
        rsi = indicators.get('rsi', 50)
        if 40 <= rsi <= 70:
            aligned_count += 1
        total_count += 1
        
        # MACD alignment
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        if macd > macd_signal:
            aligned_count += 1
        total_count += 1
        
        # Moving average alignment
        sma_20 = indicators.get('sma_20', 0)
        sma_50 = indicators.get('sma_50', 0)
        if sma_20 > sma_50:
            aligned_count += 1
        total_count += 1
        
        return aligned_count / total_count if total_count > 0 else 0.5
    
    def _calculate_pattern_confidence(self, patterns: Optional[Dict[str, Any]]) -> float:
        """Calculate confidence from pattern confirmation."""
        if not patterns:
            return 0.5
        
        pattern_score = patterns.get('combined_score', 50)
        return pattern_score / 100.0
    
    def _calculate_sr_confidence(self, support_resistance: Optional[Dict[str, Any]]) -> float:
        """Calculate confidence from support/resistance validation."""
        if not support_resistance:
            return 0.5
        
        near_support = support_resistance.get('near_support')
        near_resistance = support_resistance.get('near_resistance')
        
        if near_support:
            bounce_prob = near_support.get('bounce_probability', 0.5)
            return bounce_prob
        elif near_resistance:
            breakout_prob = near_resistance.get('breakout_probability', 0.5)
            return breakout_prob
        
        return 0.5
    
    def _calculate_regime_confidence(
        self,
        market_regime: Optional[str],
        strategy_id: Optional[str]
    ) -> float:
        """Calculate confidence from regime compatibility."""
        # Simplified - would check if strategy is compatible with regime
        if not market_regime or not strategy_id:
            return 0.5
        
        # Assume compatible for now (would check strategy's regime list)
        return 0.8
    
    def _get_historical_accuracy(self, strategy_id: Optional[str]) -> float:
        """Get historical accuracy for strategy."""
        if not strategy_id:
            return 0.5
        
        if strategy_id in self.historical_accuracy:
            stats = self.historical_accuracy[strategy_id]
            return stats.get('win_rate', 0.5)
        
        return 0.5
    
    def track_signal_outcome(
        self,
        signal_id: str,
        strategy_id: str,
        outcome: str,  # 'profit', 'loss', 'breakeven'
        profit_loss: Optional[float] = None
    ):
        """
        Track signal outcome for historical accuracy.
        
        Args:
            signal_id: Signal identifier
            strategy_id: Strategy identifier
            outcome: Outcome type
            profit_loss: Profit/loss amount
        """
        if strategy_id not in self.historical_accuracy:
            self.historical_accuracy[strategy_id] = {
                'total_signals': 0,
                'profitable_signals': 0,
                'losing_signals': 0,
                'win_rate': 0.0,
                'avg_profit': 0.0,
                'avg_loss': 0.0
            }
        
        stats = self.historical_accuracy[strategy_id]
        stats['total_signals'] += 1
        
        if outcome == 'profit':
            stats['profitable_signals'] += 1
            if profit_loss:
                # Update average profit
                current_avg = stats['avg_profit']
                count = stats['profitable_signals']
                stats['avg_profit'] = ((current_avg * (count - 1)) + profit_loss) / count
        elif outcome == 'loss':
            stats['losing_signals'] += 1
            if profit_loss:
                # Update average loss
                current_avg = stats['avg_loss']
                count = stats['losing_signals']
                stats['avg_loss'] = ((current_avg * (count - 1)) + abs(profit_loss)) / count
        
        # Update win rate
        if stats['total_signals'] > 0:
            stats['win_rate'] = stats['profitable_signals'] / stats['total_signals']
    
    def _classify_confidence(self, confidence: float) -> str:
        """Classify confidence level."""
        if confidence >= 0.8:
            return 'VERY_HIGH'
        elif confidence >= 0.7:
            return 'HIGH'
        elif confidence >= 0.6:
            return 'MODERATE_HIGH'
        elif confidence >= 0.5:
            return 'MODERATE'
        elif confidence >= 0.4:
            return 'MODERATE_LOW'
        else:
            return 'LOW'

