"""
Advanced Support/Resistance Calculator

Provides sophisticated support and resistance level calculation using multiple methods:
- Pivot Points (Classic, Fibonacci, Camarilla, Woodie)
- Volume Profile Analysis
- Dynamic Levels
- Strength Scoring
- Level Clustering
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from services.data_providers.adapters.adapter_factory import AdapterFactory
from config.constants.DataConstants import DEFAULT_PROVIDER


@dataclass
class SupportResistanceLevel:
    """Represents a support or resistance level."""
    level: float
    level_type: str  # 'support' or 'resistance'
    strength: float  # 0-100
    touches: int
    volume_at_level: float
    last_touch: Optional[datetime]
    method: str  # 'pivot', 'volume_profile', 'dynamic', 'clustered'
    price_levels: List[float]  # For clustered levels


class SupportResistanceCalculator:
    """
    Advanced support/resistance calculator.
    
    Features:
    - Multiple pivot point calculations
    - Volume profile analysis
    - Dynamic level detection
    - Strength scoring
    - Level clustering
    """
    
    def __init__(self, provider_name: str = DEFAULT_PROVIDER):
        """
        Initialize calculator.
        
        Args:
            provider_name: Data provider name for adapter
        """
        self.provider_name = provider_name
        self.adapter = AdapterFactory.get_adapter(provider_name)
    
    def calculate_pivot_points(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series
    ) -> Dict[str, float]:
        """
        Calculate pivot points using multiple methods.
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            
        Returns:
            Dictionary with pivot point levels
        """
        if len(high) < 1 or len(low) < 1 or len(close) < 1:
            raise DataProcessingException("Insufficient data for pivot points")
        
        # Use most recent period
        h = high.iloc[-1] if isinstance(high, pd.Series) else high
        l = low.iloc[-1] if isinstance(low, pd.Series) else low
        c = close.iloc[-1] if isinstance(close, pd.Series) else close
        
        # Classic Pivot Points
        pivot = (h + l + c) / 3
        r1 = 2 * pivot - l
        s1 = 2 * pivot - h
        r2 = pivot + (h - l)
        s2 = pivot - (h - l)
        r3 = h + 2 * (pivot - l)
        s3 = l - 2 * (h - pivot)
        
        # Fibonacci Pivot Points
        fib_pivot = (h + l + c) / 3
        fib_r1 = fib_pivot + 0.382 * (h - l)
        fib_s1 = fib_pivot - 0.382 * (h - l)
        fib_r2 = fib_pivot + 0.618 * (h - l)
        fib_s2 = fib_pivot - 0.618 * (h - l)
        fib_r3 = fib_pivot + 1.000 * (h - l)
        fib_s3 = fib_pivot - 1.000 * (h - l)
        
        # Camarilla Pivot Points
        camarilla_pivot = (h + l + c) / 3
        cam_r1 = c + (h - l) * 1.1 / 12
        cam_s1 = c - (h - l) * 1.1 / 12
        cam_r2 = c + (h - l) * 1.1 / 6
        cam_s2 = c - (h - l) * 1.1 / 6
        cam_r3 = c + (h - l) * 1.1 / 4
        cam_s3 = c - (h - l) * 1.1 / 4
        cam_r4 = c + (h - l) * 1.1 / 2
        cam_s4 = c - (h - l) * 1.1 / 2
        
        # Woodie Pivot Points
        woodie_pivot = (h + l + 2 * c) / 4
        woodie_r1 = 2 * woodie_pivot - l
        woodie_s1 = 2 * woodie_pivot - h
        woodie_r2 = woodie_pivot + (h - l)
        woodie_s2 = woodie_pivot - (h - l)
        
        return {
            'classic': {
                'pivot': float(pivot),
                'r1': float(r1),
                'r2': float(r2),
                'r3': float(r3),
                's1': float(s1),
                's2': float(s2),
                's3': float(s3)
            },
            'fibonacci': {
                'pivot': float(fib_pivot),
                'r1': float(fib_r1),
                'r2': float(fib_r2),
                'r3': float(fib_r3),
                's1': float(fib_s1),
                's2': float(fib_s2),
                's3': float(fib_s3)
            },
            'camarilla': {
                'pivot': float(camarilla_pivot),
                'r1': float(cam_r1),
                'r2': float(cam_r2),
                'r3': float(cam_r3),
                'r4': float(cam_r4),
                's1': float(cam_s1),
                's2': float(cam_s2),
                's3': float(cam_s3),
                's4': float(cam_s4)
            },
            'woodie': {
                'pivot': float(woodie_pivot),
                'r1': float(woodie_r1),
                'r2': float(woodie_r2),
                's1': float(woodie_s1),
                's2': float(woodie_s2)
            }
        }
    
    def calculate_volume_profile_levels(
        self,
        data: pd.DataFrame,
        bins: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Calculate support/resistance levels based on volume profile.
        
        High volume price zones act as support/resistance.
        
        Args:
            data: DataFrame with High, Low, Close, Volume columns
            bins: Number of price bins for volume profile
            
        Returns:
            List of volume profile levels with strength scores
        """
        try:
            # Normalize data
            normalized_data = self.adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < 10:
                return []
            
            high = self.adapter.get_column(normalized_data, 'HIGH')
            low = self.adapter.get_column(normalized_data, 'LOW')
            close = self.adapter.get_column(normalized_data, 'CLOSE')
            volume = self.adapter.get_column(normalized_data, 'VOLUME')
            
            # Calculate price range
            price_min = low.min()
            price_max = high.max()
            price_range = price_max - price_min
            
            if price_range == 0:
                return []
            
            # Create price bins
            bin_edges = np.linspace(price_min, price_max, bins + 1)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            # Calculate volume at each price level
            volume_profile = np.zeros(bins)
            
            for i in range(len(normalized_data)):
                price_low = low.iloc[i]
                price_high = high.iloc[i]
                vol = volume.iloc[i] if not pd.isna(volume.iloc[i]) else 0
                
                # Distribute volume across bins that price touched
                for j in range(bins):
                    bin_low = bin_edges[j]
                    bin_high = bin_edges[j + 1]
                    
                    # Check if price range overlaps with bin
                    if not (price_high < bin_low or price_low > bin_high):
                        overlap = min(price_high, bin_high) - max(price_low, bin_low)
                        price_range_touched = price_high - price_low
                        if price_range_touched > 0:
                            volume_profile[j] += vol * (overlap / price_range_touched)
            
            # Find high volume zones (top 30% of volume)
            volume_threshold = np.percentile(volume_profile, 70)
            high_volume_zones = []
            
            for i in range(bins):
                if volume_profile[i] >= volume_threshold:
                    high_volume_zones.append({
                        'level': float(bin_centers[i]),
                        'volume': float(volume_profile[i]),
                        'strength': min(100, float(volume_profile[i] / volume_profile.max() * 100)),
                        'method': 'volume_profile'
                    })
            
            # Sort by volume (descending)
            high_volume_zones.sort(key=lambda x: x['volume'], reverse=True)
            
            return high_volume_zones[:10]  # Return top 10 levels
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating volume profile levels")
            return []
    
    def calculate_dynamic_levels(
        self,
        data: pd.DataFrame,
        lookback: int = 20
    ) -> Dict[str, List[float]]:
        """
        Calculate dynamic support/resistance levels based on recent price action.
        
        Args:
            data: DataFrame with High, Low, Close columns
            lookback: Number of periods to look back
            
        Returns:
            Dictionary with support and resistance levels
        """
        try:
            normalized_data = self.adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < lookback:
                return {'support': [], 'resistance': []}
            
            high = self.adapter.get_column(normalized_data, 'HIGH')
            low = self.adapter.get_column(normalized_data, 'LOW')
            close = self.adapter.get_column(normalized_data, 'CLOSE')
            
            # Use recent data
            recent_high = high.iloc[-lookback:]
            recent_low = low.iloc[-lookback:]
            
            # Find local highs and lows
            window = max(3, lookback // 5)
            local_highs = recent_high.rolling(window=window, center=True).max() == recent_high
            local_lows = recent_low.rolling(window=window, center=True).min() == recent_low
            
            # Extract resistance levels (local highs)
            resistance_levels = recent_high[local_highs].dropna().tolist()
            
            # Extract support levels (local lows)
            support_levels = recent_low[local_lows].dropna().tolist()
            
            # Remove duplicates and sort
            resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
            support_levels = sorted(list(set(support_levels)))
            
            # Keep only significant levels (top 5)
            return {
                'support': support_levels[:5],
                'resistance': resistance_levels[:5]
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating dynamic levels")
            return {'support': [], 'resistance': []}
    
    def calculate_strength_score(
        self,
        level: float,
        data: pd.DataFrame,
        level_type: str = 'support'
    ) -> float:
        """
        Calculate strength score (0-100) for a support/resistance level.
        
        Factors:
        - Number of touches
        - Volume at level
        - Time since last touch
        - Price distance from level
        
        Args:
            level: Support/resistance level price
            data: Historical price data
            level_type: 'support' or 'resistance'
            
        Returns:
            Strength score (0-100)
        """
        try:
            normalized_data = self.adapter.normalize_dataframe(data)
            
            if normalized_data.empty:
                return 0.0
            
            high = self.adapter.get_column(normalized_data, 'HIGH')
            low = self.adapter.get_column(normalized_data, 'LOW')
            close = self.adapter.get_column(normalized_data, 'CLOSE')
            volume = self.adapter.get_column(normalized_data, 'VOLUME')
            
            # Tolerance for "touching" a level (2% of price)
            tolerance = level * 0.02
            
            # Count touches
            touches = 0
            total_volume = 0.0
            last_touch_idx = -1
            
            for i in range(len(normalized_data)):
                price_high = high.iloc[i]
                price_low = low.iloc[i]
                
                if level_type == 'support':
                    # Support: price low touched the level
                    if abs(price_low - level) <= tolerance or (price_low <= level and price_high >= level):
                        touches += 1
                        total_volume += volume.iloc[i] if not pd.isna(volume.iloc[i]) else 0
                        last_touch_idx = i
                else:
                    # Resistance: price high touched the level
                    if abs(price_high - level) <= tolerance or (price_low <= level and price_high >= level):
                        touches += 1
                        total_volume += volume.iloc[i] if not pd.isna(volume.iloc[i]) else 0
                        last_touch_idx = i
            
            # Calculate score components
            touch_score = min(50, touches * 10)  # Max 50 points for touches
            volume_score = min(30, (total_volume / volume.mean() if volume.mean() > 0 else 0) * 10)  # Max 30 points
            recency_score = 0.0
            
            if last_touch_idx >= 0:
                periods_since_touch = len(normalized_data) - 1 - last_touch_idx
                # More recent = higher score (max 20 points)
                recency_score = max(0, 20 - periods_since_touch * 2)
            
            total_score = touch_score + volume_score + recency_score
            
            return min(100.0, max(0.0, total_score))
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error calculating strength score for level {level}")
            return 0.0
    
    def cluster_levels(
        self,
        levels: List[float],
        threshold: float = 0.02
    ) -> List[Dict[str, Any]]:
        """
        Cluster nearby support/resistance levels to avoid redundancy.
        
        Args:
            levels: List of price levels
            threshold: Percentage threshold for clustering (e.g., 0.02 = 2%)
            
        Returns:
            List of clustered levels with metadata
        """
        if not levels:
            return []
        
        # Sort levels
        sorted_levels = sorted(levels)
        clusters = []
        current_cluster = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            # Check if level is within threshold of cluster center
            cluster_center = np.mean(current_cluster)
            if abs(level - cluster_center) / cluster_center <= threshold:
                current_cluster.append(level)
            else:
                # Save current cluster
                clusters.append({
                    'level': float(np.mean(current_cluster)),
                    'levels': current_cluster.copy(),
                    'count': len(current_cluster),
                    'strength': min(100, len(current_cluster) * 20)  # More levels = stronger
                })
                # Start new cluster
                current_cluster = [level]
        
        # Add last cluster
        if current_cluster:
            clusters.append({
                'level': float(np.mean(current_cluster)),
                'levels': current_cluster.copy(),
                'count': len(current_cluster),
                'strength': min(100, len(current_cluster) * 20)
            })
        
        return clusters
    
    def get_current_support_resistance(
        self,
        data: pd.DataFrame,
        include_pivot_points: bool = True,
        include_volume_profile: bool = True,
        include_dynamic: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive support/resistance levels using all methods.
        
        Args:
            data: DataFrame with OHLCV data
            include_pivot_points: Include pivot point calculations
            include_volume_profile: Include volume profile levels
            include_dynamic: Include dynamic levels
            
        Returns:
            Dictionary with all support/resistance levels
        """
        try:
            normalized_data = self.adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < 20:
                return {
                    'support_levels': [],
                    'resistance_levels': [],
                    'pivot_points': {},
                    'current_price': 0.0
                }
            
            high = self.adapter.get_column(normalized_data, 'HIGH')
            low = self.adapter.get_column(normalized_data, 'LOW')
            close = self.adapter.get_column(normalized_data, 'CLOSE')
            current_price = close.iloc[-1]
            
            result = {
                'support_levels': [],
                'resistance_levels': [],
                'pivot_points': {},
                'current_price': float(current_price)
            }
            
            # Calculate pivot points
            if include_pivot_points:
                try:
                    pivot_points = self.calculate_pivot_points(high, low, close)
                    result['pivot_points'] = pivot_points
                    
                    # Extract support and resistance from classic pivots
                    classic = pivot_points.get('classic', {})
                    if classic:
                        result['resistance_levels'].extend([
                            {'level': classic['r1'], 'method': 'pivot_classic_r1', 'strength': 60},
                            {'level': classic['r2'], 'method': 'pivot_classic_r2', 'strength': 70},
                            {'level': classic['r3'], 'method': 'pivot_classic_r3', 'strength': 80}
                        ])
                        result['support_levels'].extend([
                            {'level': classic['s1'], 'method': 'pivot_classic_s1', 'strength': 60},
                            {'level': classic['s2'], 'method': 'pivot_classic_s2', 'strength': 70},
                            {'level': classic['s3'], 'method': 'pivot_classic_s3', 'strength': 80}
                        ])
                except Exception as e:
                    DebugUtils.log_error(e, "Error calculating pivot points")
            
            # Calculate volume profile levels
            if include_volume_profile:
                try:
                    volume_levels = self.calculate_volume_profile_levels(normalized_data)
                    for level_data in volume_levels:
                        level = level_data['level']
                        if level < current_price:
                            result['support_levels'].append({
                                'level': level,
                                'method': 'volume_profile',
                                'strength': level_data['strength']
                            })
                        else:
                            result['resistance_levels'].append({
                                'level': level,
                                'method': 'volume_profile',
                                'strength': level_data['strength']
                            })
                except Exception as e:
                    DebugUtils.log_error(e, "Error calculating volume profile levels")
            
            # Calculate dynamic levels
            if include_dynamic:
                try:
                    dynamic = self.calculate_dynamic_levels(normalized_data)
                    for level in dynamic.get('support', []):
                        strength = self.calculate_strength_score(level, normalized_data, 'support')
                        result['support_levels'].append({
                            'level': level,
                            'method': 'dynamic',
                            'strength': strength
                        })
                    for level in dynamic.get('resistance', []):
                        strength = self.calculate_strength_score(level, normalized_data, 'resistance')
                        result['resistance_levels'].append({
                            'level': level,
                            'method': 'dynamic',
                            'strength': strength
                        })
                except Exception as e:
                    DebugUtils.log_error(e, "Error calculating dynamic levels")
            
            # Cluster and deduplicate levels
            support_levels = [s['level'] for s in result['support_levels']]
            resistance_levels = [r['level'] for r in result['resistance_levels']]
            
            clustered_support = self.cluster_levels(support_levels)
            clustered_resistance = self.cluster_levels(resistance_levels)
            
            # Rebuild with clustered levels
            result['support_levels'] = [
                {
                    'level': cluster['level'],
                    'method': 'clustered',
                    'strength': cluster['strength'],
                    'touches': cluster['count']
                }
                for cluster in clustered_support
            ]
            
            result['resistance_levels'] = [
                {
                    'level': cluster['level'],
                    'method': 'clustered',
                    'strength': cluster['strength'],
                    'touches': cluster['count']
                }
                for cluster in clustered_resistance
            ]
            
            # Sort by strength (descending)
            result['support_levels'].sort(key=lambda x: x['strength'], reverse=True)
            result['resistance_levels'].sort(key=lambda x: x['strength'], reverse=True)
            
            # Keep top 5 of each
            result['support_levels'] = result['support_levels'][:5]
            result['resistance_levels'] = result['resistance_levels'][:5]
            
            return result
            
        except Exception as e:
            DebugUtils.log_error(e, "Error getting current support/resistance")
            return {
                'support_levels': [],
                'resistance_levels': [],
                'pivot_points': {},
                'current_price': 0.0
            }

