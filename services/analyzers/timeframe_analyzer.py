"""
Multi-Timeframe Analysis Module

This module provides multi-timeframe analysis capabilities supporting
multiple intervals (1m, 5m, 15m, 30m, 1h, 4h, 1d) with timeframe alignment.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException


class TimeframeAnalyzer:
    """
    Analyzer for multi-timeframe analysis.
    
    Features:
    - Support for multiple intervals: 1m, 5m, 15m, 30m, 1h, 4h, 1d
    - Timeframe alignment (higher timeframe confirms lower)
    - Multi-timeframe signal aggregation
    - Timeframe-specific indicator calculations
    """
    
    SUPPORTED_TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    
    def __init__(self):
        """Initialize timeframe analyzer."""
        pass
    
    def analyze_multi_timeframe(
        self,
        data_by_timeframe: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """
        Analyze signals across multiple timeframes.
        
        Args:
            data_by_timeframe: Dictionary mapping timeframe to DataFrame
            
        Returns:
            Dictionary with multi-timeframe analysis results
        """
        try:
            if not data_by_timeframe:
                return {'alignment_score': 0, 'signals': {}}
            
            # Analyze each timeframe
            timeframe_signals = {}
            for timeframe, data in data_by_timeframe.items():
                if not data.empty:
                    timeframe_signals[timeframe] = self._analyze_timeframe(data)
            
            # Calculate alignment score
            alignment_score = self._calculate_alignment_score(timeframe_signals)
            
            return {
                'alignment_score': alignment_score,
                'signals': timeframe_signals,
                'timeframes_analyzed': list(timeframe_signals.keys())
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error in multi-timeframe analysis")
            raise DataProcessingException(f"Multi-timeframe analysis failed: {str(e)}") from e
    
    def _analyze_timeframe(
        self,
        data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Analyze a single timeframe.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Dictionary with timeframe analysis
        """
        if data.empty:
            return {'trend': 'neutral', 'strength': 0}
        
        close = data['Close']
        
        # Simple trend detection
        if len(close) >= 20:
            sma_20 = close.rolling(20).mean()
            current_price = close.iloc[-1]
            sma_value = sma_20.iloc[-1]
            
            if current_price > sma_value:
                trend = 'bullish'
                strength = min(100, ((current_price - sma_value) / sma_value) * 1000)
            elif current_price < sma_value:
                trend = 'bearish'
                strength = min(100, ((sma_value - current_price) / sma_value) * 1000)
            else:
                trend = 'neutral'
                strength = 0
        else:
            trend = 'neutral'
            strength = 0
        
        return {
            'trend': trend,
            'strength': strength,
            'current_price': close.iloc[-1]
        }
    
    def _calculate_alignment_score(
        self,
        timeframe_signals: Dict[str, Dict[str, Any]]
    ) -> float:
        """
        Calculate alignment score across timeframes.
        
        Higher score means more timeframes agree on direction.
        
        Args:
            timeframe_signals: Dictionary of timeframe analysis results
            
        Returns:
            Alignment score (0-100)
        """
        if not timeframe_signals:
            return 0.0
        
        bullish_count = sum(
            1 for sig in timeframe_signals.values()
            if sig.get('trend') == 'bullish'
        )
        bearish_count = sum(
            1 for sig in timeframe_signals.values()
            if sig.get('trend') == 'bearish'
        )
        
        total = len(timeframe_signals)
        
        if total == 0:
            return 0.0
        
        # Score based on agreement
        if bullish_count > bearish_count:
            alignment = (bullish_count / total) * 100
        elif bearish_count > bullish_count:
            alignment = (bearish_count / total) * 100
        else:
            alignment = 50  # Neutral/conflicting
        
        return alignment

