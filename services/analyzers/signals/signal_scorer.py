"""
Signal Scoring Engine Module

This module provides weighted multi-factor signal scoring combining
technical, momentum, pattern, timeframe, and risk factors.
"""

from typing import Dict, Any, Optional
import pandas as pd

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException


class SignalScorer:
    """
    Signal scoring engine with weighted multi-factor analysis.
    
    Scoring Factors:
    - Technical Score (40%): RSI, MACD, Moving Averages, Bollinger Bands
    - Momentum Score (25%): ADX, Stochastic, CCI, Volume indicators
    - Pattern Score (20%): Candlestick patterns, Chart patterns
    - Multi-timeframe Score (10%): Alignment across timeframes
    - Risk Score (5%): ATR-based volatility, position sizing
    """
    
    def __init__(self):
        """Initialize signal scorer."""
        # Weight configuration
        self.weights = {
            'technical': 0.40,
            'momentum': 0.25,
            'pattern': 0.20,
            'timeframe': 0.10,
            'risk': 0.05
        }
    
    def calculate_entry_score(
        self,
        indicators: Dict[str, Any],
        patterns: Optional[Dict[str, Any]] = None,
        timeframe_analysis: Optional[Dict[str, Any]] = None,
        risk_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive entry signal score.
        
        Args:
            indicators: Dictionary of technical indicators
            patterns: Optional pattern analysis results
            timeframe_analysis: Optional multi-timeframe analysis
            risk_metrics: Optional risk metrics
            
        Returns:
            Dictionary with:
            - total_score: Overall score (0-100)
            - component_scores: Individual component scores
            - breakdown: Detailed scoring breakdown
        """
        try:
            # Calculate component scores
            technical_score = self._calculate_technical_score(indicators)
            momentum_score = self._calculate_momentum_score(indicators)
            pattern_score = self._calculate_pattern_score(patterns) if patterns else 50
            timeframe_score = self._calculate_timeframe_score(timeframe_analysis) if timeframe_analysis else 50
            risk_score = self._calculate_risk_score(risk_metrics, indicators) if risk_metrics else 50
            
            # Weighted sum
            total_score = (
                technical_score * self.weights['technical'] +
                momentum_score * self.weights['momentum'] +
                pattern_score * self.weights['pattern'] +
                timeframe_score * self.weights['timeframe'] +
                risk_score * self.weights['risk']
            )
            
            return {
                'total_score': min(100, max(0, total_score)),
                'component_scores': {
                    'technical': technical_score,
                    'momentum': momentum_score,
                    'pattern': pattern_score,
                    'timeframe': timeframe_score,
                    'risk': risk_score
                },
                'breakdown': {
                    'technical_contribution': technical_score * self.weights['technical'],
                    'momentum_contribution': momentum_score * self.weights['momentum'],
                    'pattern_contribution': pattern_score * self.weights['pattern'],
                    'timeframe_contribution': timeframe_score * self.weights['timeframe'],
                    'risk_contribution': risk_score * self.weights['risk']
                }
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating entry score")
            raise DataProcessingException(f"Signal scoring failed: {str(e)}") from e
    
    def _calculate_technical_score(
        self,
        indicators: Dict[str, Any]
    ) -> float:
        """Calculate technical indicator score."""
        score = 50  # Neutral starting point
        
        # RSI scoring
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if isinstance(rsi, pd.Series):
                rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            if 30 < rsi < 70:
                score += 10  # Neutral zone
            elif rsi < 30:
                score += 20  # Oversold (bullish)
            elif rsi > 70:
                score -= 20  # Overbought (bearish)
        
        # MACD scoring
        if 'macd' in indicators and 'macd_signal' in indicators:
            macd = indicators['macd']
            signal = indicators['macd_signal']
            if isinstance(macd, pd.Series):
                macd = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
            if isinstance(signal, pd.Series):
                signal = signal.iloc[-1] if not pd.isna(signal.iloc[-1]) else 0
            
            if macd > signal:
                score += 15  # Bullish crossover
            else:
                score -= 15  # Bearish crossover
        
        # Moving Average scoring
        if 'sma_20' in indicators and 'sma_50' in indicators:
            sma_20 = indicators['sma_20']
            sma_50 = indicators['sma_50']
            if isinstance(sma_20, pd.Series):
                sma_20 = sma_20.iloc[-1] if not pd.isna(sma_20.iloc[-1]) else 0
            if isinstance(sma_50, pd.Series):
                sma_50 = sma_50.iloc[-1] if not pd.isna(sma_50.iloc[-1]) else 0
            
            if sma_20 > sma_50:
                score += 15  # Bullish alignment
            else:
                score -= 15  # Bearish alignment
        
        return min(100, max(0, score))
    
    def _calculate_momentum_score(
        self,
        indicators: Dict[str, Any]
    ) -> float:
        """Calculate momentum indicator score."""
        score = 50  # Neutral starting point
        
        # ADX scoring (trend strength)
        if 'adx' in indicators:
            adx = indicators['adx']
            if isinstance(adx, pd.Series):
                adx = adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0
            
            if adx > 25:
                score += 10  # Strong trend
            elif adx < 20:
                score -= 10  # Weak trend
        
        # Stochastic scoring
        if 'stochastic_k' in indicators:
            stoch_k = indicators['stochastic_k']
            if isinstance(stoch_k, pd.Series):
                stoch_k = stoch_k.iloc[-1] if not pd.isna(stoch_k.iloc[-1]) else 50
            
            if stoch_k < 20:
                score += 15  # Oversold
            elif stoch_k > 80:
                score -= 15  # Overbought
        
        return min(100, max(0, score))
    
    def _calculate_pattern_score(
        self,
        patterns: Dict[str, Any]
    ) -> float:
        """Calculate pattern score."""
        if not patterns:
            return 50
        
        combined_score = patterns.get('combined_score', 50)
        bullish_signals = patterns.get('bullish_signals', 0)
        bearish_signals = patterns.get('bearish_signals', 0)
        
        # Adjust based on signal count
        if bullish_signals > bearish_signals:
            score = combined_score + (bullish_signals - bearish_signals) * 5
        elif bearish_signals > bullish_signals:
            score = combined_score - (bearish_signals - bullish_signals) * 5
        else:
            score = combined_score
        
        return min(100, max(0, score))
    
    def _calculate_timeframe_score(
        self,
        timeframe_analysis: Dict[str, Any]
    ) -> float:
        """Calculate multi-timeframe alignment score."""
        if not timeframe_analysis:
            return 50
        
        alignment_score = timeframe_analysis.get('alignment_score', 50)
        return alignment_score
    
    def _calculate_risk_score(
        self,
        risk_metrics: Dict[str, Any],
        indicators: Dict[str, Any]
    ) -> float:
        """Calculate risk-adjusted score."""
        score = 50  # Neutral
        
        # ATR-based volatility adjustment
        if 'atr' in indicators:
            atr = indicators['atr']
            if isinstance(atr, pd.Series):
                atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0
            
            # Lower volatility = better risk score
            # This is simplified - in practice, would compare to historical ATR
            if atr > 0:
                # Normalize ATR (simplified)
                score -= min(20, atr * 10)  # Penalize high volatility
        
        # Risk-reward ratio
        if 'risk_reward_ratio' in risk_metrics:
            rr = risk_metrics['risk_reward_ratio']
            if rr > 2:
                score += 10  # Good risk-reward
            elif rr < 1:
                score -= 10  # Poor risk-reward
        
        return min(100, max(0, score))

