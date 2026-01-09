"""
Entry Point Detector Module

This module detects entry points with classification (Strong Buy/Buy/Watch/Avoid)
and calculates risk metrics including stop-loss and take-profit levels.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
from dataclasses import dataclass
from datetime import datetime

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from .signal_scorer import SignalScorer
from services.data_providers.adapters.adapter_factory import AdapterFactory
from services.analyzers.indicators.support_resistance import SupportResistanceCalculator
from services.analyzers.indicators.support_resistance_validator import SupportResistanceValidator
from config.constants.DataConstants import DEFAULT_PROVIDER


@dataclass
class EntrySignal:
    """Represents a trading entry signal."""
    symbol: str
    signal_type: str  # "STRONG_BUY", "BUY", "WATCH", "AVOID"
    score: float  # 0-100
    confidence: float  # 0-1
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timestamp: Optional[datetime] = None
    indicators: Optional[Dict[str, float]] = None
    reasoning: Optional[str] = None


class EntryDetector:
    """
    Entry point detector with multi-factor confirmation.
    
    Detection Logic:
    - Multi-factor confirmation (minimum 3 indicators aligned)
    - Entry type classification based on score
    - Entry price calculation (optimal entry zone)
    - Stop-loss and take-profit levels
    """
    
    # Score thresholds
    STRONG_BUY_THRESHOLD = 80
    BUY_THRESHOLD = 60
    WATCH_THRESHOLD = 40
    
    def __init__(self, provider_name: str = DEFAULT_PROVIDER):
        """
        Initialize entry detector.
        
        Args:
            provider_name: Data provider name for adapter
        """
        self.signal_scorer = SignalScorer()
        self.provider_name = provider_name
        self.support_resistance_calc = SupportResistanceCalculator(provider_name)
        self.support_resistance_validator = SupportResistanceValidator(provider_name)
    
    def detect_entry(
        self,
        symbol: str,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        patterns: Optional[Dict[str, Any]] = None,
        timeframe_analysis: Optional[Dict[str, Any]] = None,
        risk_metrics: Optional[Dict[str, Any]] = None,
        provider_name: str = DEFAULT_PROVIDER
    ) -> EntrySignal:
        """
        Detect entry point for a stock.
        
        Args:
            symbol: Stock symbol
            data: DataFrame with OHLCV data (will be normalized)
            indicators: Dictionary of technical indicators
            patterns: Optional pattern analysis results
            timeframe_analysis: Optional multi-timeframe analysis
            risk_metrics: Optional risk metrics
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            EntrySignal object
        """
        try:
            # Normalize data using adapter
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty:
                raise DataProcessingException("Data cannot be empty for entry detection")
            
            # Calculate signal score
            score_result = self.signal_scorer.calculate_entry_score(
                indicators,
                patterns,
                timeframe_analysis,
                risk_metrics
            )
            
            total_score = score_result['total_score']
            
            # Determine signal type
            signal_type = self._classify_signal(total_score, score_result)
            
            # Calculate support/resistance levels
            support_resistance = self.support_resistance_calc.get_current_support_resistance(
                normalized_data,
                include_pivot_points=True,
                include_volume_profile=True,
                include_dynamic=True
            )
            
            # Validate support/resistance levels
            validated_levels = self.support_resistance_validator.validate_levels(
                support_resistance.get('support_levels', []),
                support_resistance.get('resistance_levels', []),
                normalized_data
            )
            
            # Calculate entry price (optimize using support/resistance)
            entry_price = self._calculate_entry_price(
                normalized_data,
                indicators,
                adapter,
                support_resistance=validated_levels
            )
            
            # Calculate risk metrics (use support/resistance for stop-loss and take-profit)
            stop_loss, take_profit = self._calculate_risk_levels(
                entry_price,
                normalized_data,
                indicators,
                adapter,
                risk_metrics,
                support_resistance=validated_levels
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                score_result,
                patterns,
                timeframe_analysis
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                signal_type,
                score_result,
                patterns
            )
            
            return EntrySignal(
                symbol=symbol,
                signal_type=signal_type,
                score=total_score,
                confidence=confidence,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timestamp=datetime.now(),
                indicators=self._extract_latest_indicators(indicators),
                reasoning=reasoning
            )
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error detecting entry for {symbol}")
            raise DataProcessingException(f"Entry detection failed: {str(e)}") from e
    
    def _classify_signal(
        self,
        score: float,
        score_result: Dict[str, Any]
    ) -> str:
        """Classify signal based on score and confirmations."""
        component_scores = score_result.get('component_scores', {})
        
        # Count confirmations (scores > 60)
        confirmations = sum(
            1 for s in component_scores.values()
            if s > 60
        )
        
        if score >= self.STRONG_BUY_THRESHOLD and confirmations >= 3:
            return "STRONG_BUY"
        elif score >= self.BUY_THRESHOLD and confirmations >= 2:
            return "BUY"
        elif score >= self.WATCH_THRESHOLD:
            return "WATCH"
        else:
            return "AVOID"
    
    def _calculate_entry_price(
        self,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        adapter,
        support_resistance: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate optimal entry price using support/resistance levels.
        
        Prefers entry near support for long positions.
        """
        current_price = adapter.get_column(data, 'CLOSE').iloc[-1]
        
        # If near strong support, use support level as entry target
        if support_resistance:
            near_support = support_resistance.get('near_support')
            if near_support and near_support.get('bounce_probability', 0) > 0.6:
                support_level = near_support.get('level', current_price)
                # Entry slightly above support (0.5% buffer)
                entry_price = support_level * 1.005
                return round(entry_price, 2)
        
        # Use VWAP if available
        if 'vwap' in indicators:
            vwap = indicators['vwap']
            if isinstance(vwap, pd.Series):
                vwap = vwap.iloc[-1] if not pd.isna(vwap.iloc[-1]) else current_price
            # Entry between current price and VWAP
            entry_price = (current_price + vwap) / 2
        else:
            entry_price = current_price
        
        return round(entry_price, 2)
    
    def _calculate_risk_levels(
        self,
        entry_price: float,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        adapter,
        risk_metrics: Optional[Dict[str, Any]] = None,
        support_resistance: Optional[Dict[str, Any]] = None
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Calculate stop-loss and take-profit levels using support/resistance.
        
        Stop-loss: Below nearest support level
        Take-profit: At nearest resistance level
        """
        # Use support/resistance levels if available
        if support_resistance:
            # Stop-loss: Below nearest support (with buffer)
            near_support = support_resistance.get('near_support')
            if near_support:
                support_level = near_support.get('level', entry_price * 0.98)
                # Stop-loss 1% below support
                stop_loss = support_level * 0.99
            else:
                # Use strongest support level
                valid_support = support_resistance.get('valid_support', [])
                if valid_support:
                    strongest_support = valid_support[0].get('level', entry_price * 0.98)
                    stop_loss = strongest_support * 0.99
                else:
                    stop_loss = None
            
            # Take-profit: At nearest resistance
            near_resistance = support_resistance.get('near_resistance')
            if near_resistance:
                resistance_level = near_resistance.get('level', entry_price * 1.03)
                take_profit = resistance_level
            else:
                # Use strongest resistance level
                valid_resistance = support_resistance.get('valid_resistance', [])
                if valid_resistance:
                    strongest_resistance = valid_resistance[0].get('level', entry_price * 1.03)
                    take_profit = strongest_resistance
                else:
                    take_profit = None
            
            # Fallback to ATR if no support/resistance available
            if stop_loss is None or take_profit is None:
                if 'atr' in indicators:
                    atr = indicators['atr']
                    if isinstance(atr, pd.Series):
                        atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else entry_price * 0.02
                    
                    if stop_loss is None:
                        stop_loss = entry_price - (atr * 2)
                    if take_profit is None:
                        take_profit = entry_price + (atr * 3)
                else:
                    if stop_loss is None:
                        stop_loss = entry_price * 0.98
                    if take_profit is None:
                        take_profit = entry_price * 1.03
        else:
            # Use ATR for stop-loss
            if 'atr' in indicators:
                atr = indicators['atr']
                if isinstance(atr, pd.Series):
                    atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else entry_price * 0.02
                
                # Stop-loss: 2 ATR below entry (for long positions)
                stop_loss = entry_price - (atr * 2)
                
                # Take-profit: 3 ATR above entry (1.5:1 risk-reward)
                take_profit = entry_price + (atr * 3)
            else:
                # Fallback: 2% stop-loss, 3% take-profit
                stop_loss = entry_price * 0.98
                take_profit = entry_price * 1.03
        
        return round(stop_loss, 2), round(take_profit, 2)
    
    def _calculate_confidence(
        self,
        score_result: Dict[str, Any],
        patterns: Optional[Dict[str, Any]],
        timeframe_analysis: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate signal confidence (0-1)."""
        component_scores = score_result.get('component_scores', {})
        
        # Base confidence from score
        base_confidence = score_result['total_score'] / 100
        
        # Boost confidence if patterns confirm
        if patterns:
            pattern_score = patterns.get('combined_score', 50) / 100
            base_confidence = (base_confidence + pattern_score) / 2
        
        # Boost confidence if timeframes align
        if timeframe_analysis:
            alignment = timeframe_analysis.get('alignment_score', 50) / 100
            base_confidence = (base_confidence + alignment) / 2
        
        return min(1.0, max(0.0, base_confidence))
    
    def _generate_reasoning(
        self,
        signal_type: str,
        score_result: Dict[str, Any],
        patterns: Optional[Dict[str, Any]]
    ) -> str:
        """Generate human-readable reasoning for the signal."""
        component_scores = score_result.get('component_scores', {})
        
        reasons = []
        
        if component_scores.get('technical', 0) > 60:
            reasons.append("Strong technical indicators")
        if component_scores.get('momentum', 0) > 60:
            reasons.append("Positive momentum")
        if patterns and patterns.get('bullish_signals', 0) > 0:
            reasons.append(f"{patterns['bullish_signals']} bullish patterns detected")
        
        if not reasons:
            reasons.append("Mixed signals")
        
        return f"{signal_type}: " + ", ".join(reasons)
    
    def _extract_latest_indicators(
        self,
        indicators: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract latest values from indicator Series."""
        latest = {}
        
        for key, value in indicators.items():
            if isinstance(value, pd.Series):
                latest_value = value.iloc[-1]
                if not pd.isna(latest_value):
                    latest[key] = float(latest_value)
            elif isinstance(value, (int, float)):
                latest[key] = float(value)
        
        return latest

