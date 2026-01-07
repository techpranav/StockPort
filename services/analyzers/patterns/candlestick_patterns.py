"""
Candlestick Pattern Detection Module

This module detects various candlestick patterns including reversal patterns,
continuation patterns, and multi-candle patterns with strength scoring.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from services.data_providers.adapters.adapter_factory import AdapterFactory
from config.constants.DataConstants import DEFAULT_PROVIDER


@dataclass
class PatternDetection:
    """Represents a detected candlestick pattern."""
    pattern_type: str
    pattern_name: str
    strength: float  # 0-100
    reliability: float  # 0-1
    detected_at: datetime
    price: float
    is_bullish: bool
    target_price: Optional[float] = None


class CandlestickPatternDetector:
    """
    Detects candlestick patterns in price data.
    
    Supports:
    - Reversal patterns: Hammer, Doji, Engulfing, Harami, Shooting Star
    - Continuation patterns: Three Line Strike, Rising/Falling Three Methods
    - Multi-candle patterns: Morning Star, Evening Star, Three Black Crows
    """
    
    def __init__(self):
        """Initialize candlestick pattern detector."""
        self.patterns_detected: List[PatternDetection] = []
    
    def detect_all_patterns(
        self,
        data: pd.DataFrame,
        provider_name: str = DEFAULT_PROVIDER
    ) -> List[PatternDetection]:
        """
        Detect all candlestick patterns in the data.
        
        Args:
            data: DataFrame with Open, High, Low, Close columns (will be normalized)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            List of PatternDetection objects
        """
        # Normalize data using adapter
        adapter = AdapterFactory.get_adapter(provider_name)
        normalized_data = adapter.normalize_dataframe(data)
        
        if normalized_data.empty or len(normalized_data) < 3:
            return []
        
        self.patterns_detected = []
        
        # Detect single-candle patterns
        self._detect_hammer(normalized_data, adapter)
        self._detect_doji(normalized_data, adapter)
        self._detect_shooting_star(normalized_data, adapter)
        
        # Detect two-candle patterns
        if len(normalized_data) >= 2:
            self._detect_engulfing(normalized_data, adapter)
            self._detect_harami(normalized_data, adapter)
        
        # Detect three-candle patterns
        if len(normalized_data) >= 3:
            self._detect_morning_star(normalized_data, adapter)
            self._detect_evening_star(normalized_data, adapter)
            self._detect_three_black_crows(normalized_data, adapter)
            self._detect_three_white_soldiers(normalized_data, adapter)
            self._detect_three_line_strike(normalized_data, adapter)
            self._detect_rising_three_methods(normalized_data, adapter)
            self._detect_falling_three_methods(normalized_data, adapter)
        
        return self.patterns_detected
    
    def _detect_hammer(self, data: pd.DataFrame, adapter) -> None:
        """Detect Hammer pattern (bullish reversal)."""
        try:
            open_col = adapter.get_column(data, 'OPEN')
            high_col = adapter.get_column(data, 'HIGH')
            low_col = adapter.get_column(data, 'LOW')
            close_col = adapter.get_column(data, 'CLOSE')
            
            for i in range(1, len(data)):
                open_price = open_col.iloc[i]
                high = high_col.iloc[i]
                low = low_col.iloc[i]
                close = close_col.iloc[i]
                
                body = abs(close - open_price)
                lower_shadow = min(open_price, close) - low
                upper_shadow = high - max(open_price, close)
                
                # Hammer criteria: small body, long lower shadow, little/no upper shadow
                if (lower_shadow > body * 2 and 
                    upper_shadow < body * 0.1 and
                    body > 0):
                    
                    strength = min(100, (lower_shadow / body) * 20)
                    
                    self.patterns_detected.append(PatternDetection(
                        pattern_type='reversal',
                        pattern_name='Hammer',
                        strength=strength,
                        reliability=0.6,
                        detected_at=data.index[i],
                        price=close,
                        is_bullish=True
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Hammer pattern")
    
    def _get_ohlc_columns(self, data: pd.DataFrame, adapter):
        """Helper to get OHLC columns using adapter."""
        return {
            'open': adapter.get_column(data, 'OPEN'),
            'high': adapter.get_column(data, 'HIGH'),
            'low': adapter.get_column(data, 'LOW'),
            'close': adapter.get_column(data, 'CLOSE')
        }
    
    def _detect_doji(self, data: pd.DataFrame, adapter) -> None:
        """Detect Doji pattern (indecision/reversal)."""
        try:
            ohlc = self._get_ohlc_columns(data, adapter)
            for i in range(len(data)):
                open_price = ohlc['open'].iloc[i]
                high = ohlc['high'].iloc[i]
                low = ohlc['low'].iloc[i]
                close = ohlc['close'].iloc[i]
                
                body = abs(close - open_price)
                total_range = high - low
                
                # Doji criteria: very small body relative to range
                if total_range > 0 and body / total_range < 0.1:
                    strength = 50  # Neutral strength
                    
                    self.patterns_detected.append(PatternDetection(
                        pattern_type='reversal',
                        pattern_name='Doji',
                        strength=strength,
                        reliability=0.5,
                        detected_at=data.index[i],
                        price=close,
                        is_bullish=None  # Doji is neutral
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Doji pattern")
    
    def _detect_shooting_star(self, data: pd.DataFrame, adapter) -> None:
        """Detect Shooting Star pattern (bearish reversal)."""
        try:
            ohlc = self._get_ohlc_columns(data, adapter)
            for i in range(1, len(data)):
                open_price = ohlc['open'].iloc[i]
                high = ohlc['high'].iloc[i]
                low = ohlc['low'].iloc[i]
                close = ohlc['close'].iloc[i]
                
                body = abs(close - open_price)
                upper_shadow = high - max(open_price, close)
                lower_shadow = min(open_price, close) - low
                
                # Shooting Star criteria: small body, long upper shadow, little lower shadow
                if (upper_shadow > body * 2 and
                    lower_shadow < body * 0.1 and
                    body > 0):
                    
                    strength = min(100, (upper_shadow / body) * 20)
                    
                    self.patterns_detected.append(PatternDetection(
                        pattern_type='reversal',
                        pattern_name='Shooting Star',
                        strength=strength,
                        reliability=0.6,
                        detected_at=data.index[i],
                        price=close,
                        is_bullish=False
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Shooting Star pattern")
    
    def _detect_engulfing(self, data: pd.DataFrame, adapter) -> None:
        """Detect Engulfing patterns (bullish/bearish reversal)."""
        try:
            ohlc = self._get_ohlc_columns(data, adapter)
            for i in range(1, len(data)):
                prev_open = ohlc['open'].iloc[i-1]
                prev_close = ohlc['close'].iloc[i-1]
                curr_open = ohlc['open'].iloc[i]
                curr_close = ohlc['close'].iloc[i]
                
                prev_body = abs(prev_close - prev_open)
                curr_body = abs(curr_close - curr_open)
                
                # Bullish Engulfing
                if (prev_close < prev_open and  # Previous candle bearish
                    curr_close > curr_open and  # Current candle bullish
                    curr_open < prev_close and  # Current opens below previous close
                    curr_close > prev_open):     # Current closes above previous open
                    
                    strength = min(100, (curr_body / prev_body) * 30)
                    
                    self.patterns_detected.append(PatternDetection(
                        pattern_type='reversal',
                        pattern_name='Bullish Engulfing',
                        strength=strength,
                        reliability=0.7,
                        detected_at=data.index[i],
                        price=curr_close,
                        is_bullish=True
                    ))
                
                # Bearish Engulfing
                elif (prev_close > prev_open and  # Previous candle bullish
                      curr_close < curr_open and  # Current candle bearish
                      curr_open > prev_close and  # Current opens above previous close
                      curr_close < prev_open):    # Current closes below previous open
                    
                    strength = min(100, (curr_body / prev_body) * 30)
                    
                    self.patterns_detected.append(PatternDetection(
                        pattern_type='reversal',
                        pattern_name='Bearish Engulfing',
                        strength=strength,
                        reliability=0.7,
                        detected_at=data.index[i],
                        price=curr_close,
                        is_bullish=False
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Engulfing pattern")
    
    def _detect_harami(self, data: pd.DataFrame, adapter) -> None:
        """Detect Harami patterns (reversal)."""
        try:
            ohlc = self._get_ohlc_columns(data, adapter)
            for i in range(1, len(data)):
                prev_open = ohlc['open'].iloc[i-1]
                prev_close = ohlc['close'].iloc[i-1]
                curr_open = ohlc['open'].iloc[i]
                curr_close = ohlc['close'].iloc[i]
                
                prev_body = abs(prev_close - prev_open)
                curr_body = abs(curr_close - curr_open)
                
                # Harami criteria: small body inside large previous body
                if (prev_body > curr_body * 2 and
                    min(curr_open, curr_close) > min(prev_open, prev_close) and
                    max(curr_open, curr_close) < max(prev_open, prev_close)):
                    
                    is_bullish = prev_close < prev_open  # Reversal of previous trend
                    strength = 40
                    
                    pattern_name = 'Bullish Harami' if is_bullish else 'Bearish Harami'
                    
                    self.patterns_detected.append(PatternDetection(
                        pattern_type='reversal',
                        pattern_name=pattern_name,
                        strength=strength,
                        reliability=0.5,
                        detected_at=data.index[i],
                        price=curr_close,
                        is_bullish=is_bullish
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Harami pattern")
    
    def _detect_morning_star(self, data: pd.DataFrame, adapter) -> None:
        """Detect Morning Star pattern (bullish reversal)."""
        try:
            ohlc = self._get_ohlc_columns(data, adapter)
            for i in range(2, len(data)):
                first_close = ohlc['close'].iloc[i-2]
                first_open = ohlc['open'].iloc[i-2]
                second_close = ohlc['close'].iloc[i-1]
                second_open = ohlc['open'].iloc[i-1]
                third_close = ohlc['close'].iloc[i]
                third_open = ohlc['open'].iloc[i]
                
                # Morning Star: bearish, small body, bullish
                if (first_close < first_open and  # First candle bearish
                    abs(second_close - second_open) < abs(first_close - first_open) * 0.3 and  # Small second body
                    third_close > third_open and  # Third candle bullish
                    third_close > (first_open + first_close) / 2):  # Third closes above midpoint
                    
                    strength = 70
                    
                    self.patterns_detected.append(PatternDetection(
                        pattern_type='reversal',
                        pattern_name='Morning Star',
                        strength=strength,
                        reliability=0.75,
                        detected_at=data.index[i],
                        price=third_close,
                        is_bullish=True
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Morning Star pattern")
    
    def _detect_evening_star(self, data: pd.DataFrame, adapter) -> None:
        """Detect Evening Star pattern (bearish reversal)."""
        try:
            ohlc = self._get_ohlc_columns(data, adapter)
            for i in range(2, len(data)):
                first_close = ohlc['close'].iloc[i-2]
                first_open = ohlc['open'].iloc[i-2]
                second_close = ohlc['close'].iloc[i-1]
                second_open = ohlc['open'].iloc[i-1]
                third_close = ohlc['close'].iloc[i]
                third_open = ohlc['open'].iloc[i]
                
                # Evening Star: bullish, small body, bearish
                if (first_close > first_open and  # First candle bullish
                    abs(second_close - second_open) < abs(first_close - first_open) * 0.3 and  # Small second body
                    third_close < third_open and  # Third candle bearish
                    third_close < (first_open + first_close) / 2):  # Third closes below midpoint
                    
                    strength = 70
                    
                    self.patterns_detected.append(PatternDetection(
                        pattern_type='reversal',
                        pattern_name='Evening Star',
                        strength=strength,
                        reliability=0.75,
                        detected_at=data.index[i],
                        price=third_close,
                        is_bullish=False
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Evening Star pattern")
    
    def _detect_three_black_crows(self, data: pd.DataFrame, adapter) -> None:
        """Detect Three Black Crows pattern (bearish reversal)."""
        try:
            ohlc = self._get_ohlc_columns(data, adapter)
            for i in range(3, len(data)):
                # Get candle data using adapter columns
                c0_close = ohlc['close'].iloc[i-2]
                c0_open = ohlc['open'].iloc[i-2]
                c1_close = ohlc['close'].iloc[i-1]
                c1_open = ohlc['open'].iloc[i-1]
                c2_close = ohlc['close'].iloc[i]
                c2_open = ohlc['open'].iloc[i]
                
                # All three candles bearish and closing lower
                if (c0_close < c0_open and c1_close < c1_open and c2_close < c2_open):
                    if (c0_close > c1_close > c2_close):
                        strength = 80
                        
                        self.patterns_detected.append(PatternDetection(
                            pattern_type='reversal',
                            pattern_name='Three Black Crows',
                            strength=strength,
                            reliability=0.8,
                            detected_at=data.index[i],
                            price=c2_close,
                            is_bullish=False
                        ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Three Black Crows pattern")
    
    def _detect_three_white_soldiers(self, data: pd.DataFrame, adapter) -> None:
        """Detect Three White Soldiers pattern (bullish continuation/reversal)."""
        try:
            ohlc = self._get_ohlc_columns(data, adapter)
            for i in range(3, len(data)):
                # Get candle data using adapter columns
                c0_close = ohlc['close'].iloc[i-2]
                c0_open = ohlc['open'].iloc[i-2]
                c1_close = ohlc['close'].iloc[i-1]
                c1_open = ohlc['open'].iloc[i-1]
                c2_close = ohlc['close'].iloc[i]
                c2_open = ohlc['open'].iloc[i]
                
                # All three candles bullish and closing higher
                if (c0_close > c0_open and c1_close > c1_open and c2_close > c2_open):
                    if (c0_close < c1_close < c2_close):
                        strength = 80
                        
                        self.patterns_detected.append(PatternDetection(
                            pattern_type='continuation',
                            pattern_name='Three White Soldiers',
                            strength=strength,
                            reliability=0.8,
                            detected_at=data.index[i],
                            price=c2_close,
                            is_bullish=True
                        ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Three White Soldiers pattern")
    
    def _detect_three_line_strike(self, data: pd.DataFrame, adapter) -> None:
        """Detect Three Line Strike pattern (continuation)."""
        try:
            ohlc = self._get_ohlc_columns(data, adapter)
            for i in range(4, len(data)):
                # Three consecutive same-direction candles followed by opposite
                c0_close = ohlc['close'].iloc[i-3]
                c0_open = ohlc['open'].iloc[i-3]
                c1_close = ohlc['close'].iloc[i-2]
                c1_open = ohlc['open'].iloc[i-2]
                c2_close = ohlc['close'].iloc[i-1]
                c2_open = ohlc['open'].iloc[i-1]
                c3_close = ohlc['close'].iloc[i]
                c3_open = ohlc['open'].iloc[i]
                
                # Check if first three are same direction
                if (c0_close > c0_open and c1_close > c1_open and c2_close > c2_open):
                    # Bullish three line strike
                    if (c3_close < c3_open and c3_close < c0_open):
                        strength = 60
                        
                        self.patterns_detected.append(PatternDetection(
                            pattern_type='continuation',
                            pattern_name='Bullish Three Line Strike',
                            strength=strength,
                            reliability=0.65,
                            detected_at=data.index[i],
                            price=c3_close,
                            is_bullish=True
                        ))
                elif (c0_close < c0_open and c1_close < c1_open and c2_close < c2_open):
                    # Bearish three line strike
                    if (c3_close > c3_open and c3_close > c0_open):
                        strength = 60
                        
                        self.patterns_detected.append(PatternDetection(
                            pattern_type='continuation',
                            pattern_name='Bearish Three Line Strike',
                            strength=strength,
                            reliability=0.65,
                            detected_at=data.index[i],
                            price=c3_close,
                            is_bullish=False
                        ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Three Line Strike pattern")
    
    def _detect_rising_three_methods(self, data: pd.DataFrame, adapter) -> None:
        """Detect Rising Three Methods pattern (bullish continuation)."""
        try:
            ohlc = self._get_ohlc_columns(data, adapter)
            for i in range(5, len(data)):
                # Get candle data
                first_close = ohlc['close'].iloc[i-4]
                first_open = ohlc['open'].iloc[i-4]
                first_low = ohlc['low'].iloc[i-4]
                first_high = ohlc['high'].iloc[i-4]
                
                m1_close = ohlc['close'].iloc[i-3]
                m1_open = ohlc['open'].iloc[i-3]
                m1_low = ohlc['low'].iloc[i-3]
                m1_high = ohlc['high'].iloc[i-3]
                
                m2_close = ohlc['close'].iloc[i-2]
                m2_open = ohlc['open'].iloc[i-2]
                m2_low = ohlc['low'].iloc[i-2]
                m2_high = ohlc['high'].iloc[i-2]
                
                m3_close = ohlc['close'].iloc[i-1]
                m3_open = ohlc['open'].iloc[i-1]
                m3_low = ohlc['low'].iloc[i-1]
                m3_high = ohlc['high'].iloc[i-1]
                
                last_close = ohlc['close'].iloc[i]
                last_open = ohlc['open'].iloc[i]
                
                # First and last bullish, middle bearish but within range
                if (first_close > first_open and
                    last_close > last_open and
                    m1_close < m1_open and m2_close < m2_open and m3_close < m3_open and
                    m1_low > first_low and m1_high < first_high and
                    m2_low > first_low and m2_high < first_high and
                    m3_low > first_low and m3_high < first_high):
                    
                    strength = 65
                    
                    self.patterns_detected.append(PatternDetection(
                        pattern_type='continuation',
                        pattern_name='Rising Three Methods',
                        strength=strength,
                        reliability=0.7,
                        detected_at=data.index[i],
                        price=last_close,
                        is_bullish=True
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Rising Three Methods pattern")
    
    def _detect_falling_three_methods(self, data: pd.DataFrame) -> None:
        """Detect Falling Three Methods pattern (bearish continuation)."""
        try:
            for i in range(5, len(data)):
                first = data.iloc[i-4]
                last = data.iloc[i]
                middle = [data.iloc[i-3], data.iloc[i-2], data.iloc[i-1]]
                
                # First and last bearish, middle bullish but within range
                if (first['Close'] < first['Open'] and
                    last['Close'] < last['Open'] and
                    all(c['Close'] > c['Open'] for c in middle) and
                    all(c['Low'] > first['Low'] and c['High'] < first['High'] for c in middle)):
                    
                    strength = 65
                    
                    self.patterns_detected.append(PatternDetection(
                        pattern_type='continuation',
                        pattern_name='Falling Three Methods',
                        strength=strength,
                        reliability=0.7,
                        detected_at=data.index[i],
                        price=last['Close'],
                        is_bullish=False
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Falling Three Methods pattern")

