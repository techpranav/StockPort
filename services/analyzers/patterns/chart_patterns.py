"""
Chart Pattern Detection Module

This module detects chart patterns including support/resistance levels,
trend lines, triangles, and other geometric patterns.
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
class ChartPattern:
    """Represents a detected chart pattern."""
    pattern_type: str
    pattern_name: str
    strength: float  # 0-100
    detected_at: datetime
    price_levels: List[float]
    is_bullish: Optional[bool] = None
    target_price: Optional[float] = None


class ChartPatternDetector:
    """
    Detects chart patterns in price data.
    
    Supports:
    - Support/Resistance levels
    - Trend lines (uptrend, downtrend, horizontal)
    - Triangles (ascending, descending, symmetrical)
    - Head and Shoulders
    - Double Top/Bottom
    - Flags and Pennants
    - Cup and Handle
    """
    
    def __init__(self, lookback_period: int = 50):
        """
        Initialize chart pattern detector.
        
        Args:
            lookback_period: Number of periods to look back for patterns
        """
        self.lookback_period = lookback_period
        self.patterns_detected: List[ChartPattern] = []
    
    def detect_all_patterns(
        self,
        data: pd.DataFrame,
        provider_name: str = DEFAULT_PROVIDER
    ) -> List[ChartPattern]:
        """
        Detect all chart patterns in the data.
        
        Args:
            data: DataFrame with High, Low, Close columns (will be normalized)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            List of ChartPattern objects
        """
        # Normalize data using adapter
        adapter = AdapterFactory.get_adapter(provider_name)
        normalized_data = adapter.normalize_dataframe(data)
        
        if normalized_data.empty or len(normalized_data) < 20:
            return []
        
        self.patterns_detected = []
        
        # Detect patterns
        self._detect_support_resistance(normalized_data, adapter)
        self._detect_trend_lines(normalized_data, adapter)
        self._detect_triangles(normalized_data, adapter)
        self._detect_head_and_shoulders(normalized_data, adapter)
        self._detect_double_top_bottom(normalized_data, adapter)
        
        return self.patterns_detected
    
    def _detect_support_resistance(
        self,
        data: pd.DataFrame,
        adapter
    ) -> None:
        """Detect support and resistance levels."""
        try:
            high = adapter.get_column(data, 'HIGH')
            low = adapter.get_column(data, 'LOW')
            close = adapter.get_column(data, 'CLOSE')
            
            # Find local highs and lows
            window = min(10, len(data) // 4)
            local_highs = high.rolling(window=window, center=True).max() == high
            local_lows = low.rolling(window=window, center=True).min() == low
            
            # Cluster similar price levels
            high_prices = high[local_highs].tolist()
            low_prices = low[local_lows].tolist()
            
            # Find resistance levels (clustered highs)
            if len(high_prices) >= 2:
                resistance_levels = self._cluster_levels(high_prices, threshold=0.02)
                for level in resistance_levels:
                    self.patterns_detected.append(ChartPattern(
                        pattern_type='level',
                        pattern_name='Resistance',
                        strength=70,
                        detected_at=data.index[-1],
                        price_levels=[level],
                        is_bullish=False
                    ))
            
            # Find support levels (clustered lows)
            if len(low_prices) >= 2:
                support_levels = self._cluster_levels(low_prices, threshold=0.02)
                for level in support_levels:
                    self.patterns_detected.append(ChartPattern(
                        pattern_type='level',
                        pattern_name='Support',
                        strength=70,
                        detected_at=data.index[-1],
                        price_levels=[level],
                        is_bullish=True
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting support/resistance")
    
    def _detect_trend_lines(
        self,
        data: pd.DataFrame,
        adapter
    ) -> None:
        """Detect trend lines."""
        try:
            high = adapter.get_column(data, 'HIGH')
            low = adapter.get_column(data, 'LOW')
            close = adapter.get_column(data, 'CLOSE')
            
            # Simple trend detection using linear regression
            recent_data = data.tail(self.lookback_period)
            
            if len(recent_data) < 10:
                return
            
            # Uptrend: price generally increasing
            x = np.arange(len(recent_data))
            y_high = adapter.get_column(recent_data, 'HIGH').values
            y_low = adapter.get_column(recent_data, 'LOW').values
            y_close = adapter.get_column(recent_data, 'CLOSE').values
            
            # Linear regression on close prices
            coeffs = np.polyfit(x, y_close, 1)
            slope = coeffs[0]
            
            if slope > 0:
                # Uptrend
                self.patterns_detected.append(ChartPattern(
                    pattern_type='trend',
                    pattern_name='Uptrend',
                    strength=min(100, abs(slope) * 1000),
                    detected_at=data.index[-1],
                    price_levels=[y_close[0], y_close[-1]],
                    is_bullish=True
                ))
            elif slope < 0:
                # Downtrend
                self.patterns_detected.append(ChartPattern(
                    pattern_type='trend',
                    pattern_name='Downtrend',
                    strength=min(100, abs(slope) * 1000),
                    detected_at=data.index[-1],
                    price_levels=[y_close[0], y_close[-1]],
                    is_bullish=False
                ))
            else:
                # Sideways
                self.patterns_detected.append(ChartPattern(
                    pattern_type='trend',
                    pattern_name='Sideways',
                    strength=50,
                    detected_at=data.index[-1],
                    price_levels=[y_close[0], y_close[-1]],
                    is_bullish=None
                ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting trend lines")
    
    def _detect_triangles(
        self,
        data: pd.DataFrame,
        adapter
    ) -> None:
        """Detect triangle patterns."""
        try:
            if len(data) < 20:
                return
            
            recent_data = data.tail(30)
            high = adapter.get_column(recent_data, 'HIGH')
            low = adapter.get_column(recent_data, 'LOW')
            
            # Find converging trend lines
            high_trend = np.polyfit(range(len(high)), high.values, 1)[0]
            low_trend = np.polyfit(range(len(low)), low.values, 1)[0]
            
            # Ascending triangle: horizontal resistance, rising support
            if abs(high_trend) < 0.01 and low_trend > 0.01:
                self.patterns_detected.append(ChartPattern(
                    pattern_type='triangle',
                    pattern_name='Ascending Triangle',
                    strength=65,
                    detected_at=data.index[-1],
                    price_levels=[high.max(), low.min()],
                    is_bullish=True
                ))
            
            # Descending triangle: falling resistance, horizontal support
            elif high_trend < -0.01 and abs(low_trend) < 0.01:
                self.patterns_detected.append(ChartPattern(
                    pattern_type='triangle',
                    pattern_name='Descending Triangle',
                    strength=65,
                    detected_at=data.index[-1],
                    price_levels=[high.max(), low.min()],
                    is_bullish=False
                ))
            
            # Symmetrical triangle: converging lines
            elif (high_trend < 0 and low_trend > 0 and
                  abs(high_trend) > 0.01 and abs(low_trend) > 0.01):
                self.patterns_detected.append(ChartPattern(
                    pattern_type='triangle',
                    pattern_name='Symmetrical Triangle',
                    strength=60,
                    detected_at=data.index[-1],
                    price_levels=[high.max(), low.min()],
                    is_bullish=None
                ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting triangles")
    
    def _detect_head_and_shoulders(
        self,
        data: pd.DataFrame,
        adapter
    ) -> None:
        """Detect Head and Shoulders pattern."""
        try:
            if len(data) < 30:
                return
            
            close = adapter.get_column(data, 'CLOSE')
            high = adapter.get_column(data, 'HIGH')
            
            # Find three peaks
            window = 5
            peaks = high.rolling(window=window, center=True).max() == high
            
            peak_indices = high[peaks].index.tolist()
            
            if len(peak_indices) >= 3:
                # Check last three peaks
                last_three_peaks = peak_indices[-3:]
                peak_values = [high.loc[idx] for idx in last_three_peaks]
                
                # Head and Shoulders: middle peak higher than sides
                if (peak_values[1] > peak_values[0] and
                    peak_values[1] > peak_values[2] and
                    abs(peak_values[0] - peak_values[2]) / peak_values[1] < 0.05):  # Shoulders similar
                    
                    self.patterns_detected.append(ChartPattern(
                        pattern_type='reversal',
                        pattern_name='Head and Shoulders',
                        strength=75,
                        detected_at=data.index[-1],
                        price_levels=peak_values,
                        is_bullish=False
                    ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Head and Shoulders")
    
    def _detect_double_top_bottom(
        self,
        data: pd.DataFrame,
        adapter
    ) -> None:
        """Detect Double Top and Double Bottom patterns."""
        try:
            if len(data) < 20:
                return
            
            close = adapter.get_column(data, 'CLOSE')
            high = adapter.get_column(data, 'HIGH')
            low = adapter.get_column(data, 'LOW')
            
            # Find peaks and troughs
            window = 5
            peaks = high.rolling(window=window, center=True).max() == high
            troughs = low.rolling(window=window, center=True).min() == low
            
            peak_indices = high[peaks].index.tolist()
            trough_indices = low[troughs].index.tolist()
            
            # Double Top: two similar peaks with trough between
            if len(peak_indices) >= 2:
                last_two_peaks = peak_indices[-2:]
                peak_values = [high.loc[idx] for idx in last_two_peaks]
                
                if abs(peak_values[0] - peak_values[1]) / peak_values[0] < 0.02:  # Similar peaks
                    # Check for trough between
                    between_data = data.loc[last_two_peaks[0]:last_two_peaks[1]]
                    if len(between_data) > 0:
                        trough_between = adapter.get_column(between_data, 'LOW').min()
                        if trough_between < peak_values[0] * 0.95:  # Significant drop
                            self.patterns_detected.append(ChartPattern(
                                pattern_type='reversal',
                                pattern_name='Double Top',
                                strength=70,
                                detected_at=data.index[-1],
                                price_levels=peak_values,
                                is_bullish=False
                            ))
            
            # Double Bottom: two similar troughs with peak between
            if len(trough_indices) >= 2:
                last_two_troughs = trough_indices[-2:]
                trough_values = [low.loc[idx] for idx in last_two_troughs]
                
                if abs(trough_values[0] - trough_values[1]) / trough_values[0] < 0.02:  # Similar troughs
                    # Check for peak between
                    between_data = data.loc[last_two_troughs[0]:last_two_troughs[1]]
                    if len(between_data) > 0:
                        peak_between = adapter.get_column(between_data, 'HIGH').max()
                        if peak_between > trough_values[0] * 1.05:  # Significant rise
                            self.patterns_detected.append(ChartPattern(
                                pattern_type='reversal',
                                pattern_name='Double Bottom',
                                strength=70,
                                detected_at=data.index[-1],
                                price_levels=trough_values,
                                is_bullish=True
                            ))
        except Exception as e:
            DebugUtils.log_error(e, "Error detecting Double Top/Bottom")
    
    def _cluster_levels(
        self,
        levels: List[float],
        threshold: float = 0.02
    ) -> List[float]:
        """
        Cluster similar price levels together.
        
        Args:
            levels: List of price levels
            threshold: Percentage threshold for clustering
            
        Returns:
            List of clustered level averages
        """
        if not levels:
            return []
        
        sorted_levels = sorted(levels)
        clusters = []
        current_cluster = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] < threshold:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        
        if current_cluster:
            clusters.append(np.mean(current_cluster))
        
        return clusters

