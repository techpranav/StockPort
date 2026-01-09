"""
Support/Resistance Validator

Validates support/resistance levels and predicts bounce/breakout probability.
"""

from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from services.data_providers.adapters.adapter_factory import AdapterFactory
from config.constants.DataConstants import DEFAULT_PROVIDER


class SupportResistanceValidator:
    """
    Validates support/resistance levels and predicts bounce/breakout probability.
    
    Features:
    - Check if price is near support/resistance
    - Validate if level is still valid (not broken)
    - Predict probability of bounce/breakout
    - Historical accuracy tracking
    """
    
    def __init__(self, provider_name: str = DEFAULT_PROVIDER):
        """
        Initialize validator.
        
        Args:
            provider_name: Data provider name for adapter
        """
        self.provider_name = provider_name
        self.adapter = AdapterFactory.get_adapter(provider_name)
        self.historical_accuracy: Dict[str, Dict[str, float]] = {}  # level -> {bounces: int, breaks: int}
    
    def is_near_level(
        self,
        current_price: float,
        level: float,
        tolerance_pct: float = 0.02
    ) -> bool:
        """
        Check if current price is near a support/resistance level.
        
        Args:
            current_price: Current stock price
            level: Support/resistance level
            tolerance_pct: Percentage tolerance (default 2%)
            
        Returns:
            True if price is within tolerance of level
        """
        if level == 0:
            return False
        
        tolerance = level * tolerance_pct
        return abs(current_price - level) <= tolerance
    
    def is_level_valid(
        self,
        level: float,
        level_type: str,
        data: pd.DataFrame
    ) -> bool:
        """
        Check if a support/resistance level is still valid (not broken).
        
        Args:
            level: Support/resistance level
            level_type: 'support' or 'resistance'
            data: Historical price data
            
        Returns:
            True if level is still valid, False if broken
        """
        try:
            normalized_data = self.adapter.normalize_dataframe(data)
            
            if normalized_data.empty:
                return False
            
            high = self.adapter.get_column(normalized_data, 'HIGH')
            low = self.adapter.get_column(normalized_data, 'LOW')
            
            # Check recent price action (last 5 periods)
            recent_high = high.iloc[-5:].max()
            recent_low = low.iloc[-5:].min()
            
            if level_type == 'support':
                # Support is broken if price went significantly below it
                return recent_low >= (level * 0.98)  # 2% buffer
            else:
                # Resistance is broken if price went significantly above it
                return recent_high <= (level * 1.02)  # 2% buffer
                
        except Exception as e:
            DebugUtils.log_error(e, f"Error validating level {level}")
            return False
    
    def predict_bounce_probability(
        self,
        level: float,
        level_type: str,
        data: pd.DataFrame,
        strength: float = 50.0
    ) -> float:
        """
        Predict probability of bounce/breakout at a support/resistance level.
        
        Args:
            level: Support/resistance level
            level_type: 'support' or 'resistance'
            data: Historical price data
            strength: Level strength score (0-100)
            
        Returns:
            Probability (0-1) of bounce (for support) or breakout (for resistance)
        """
        try:
            normalized_data = self.adapter.normalize_dataframe(data)
            
            if normalized_data.empty:
                return 0.5  # Default probability
            
            high = self.adapter.get_column(normalized_data, 'HIGH')
            low = self.adapter.get_column(normalized_data, 'LOW')
            close = self.adapter.get_column(normalized_data, 'CLOSE')
            volume = self.adapter.get_column(normalized_data, 'VOLUME')
            
            current_price = close.iloc[-1]
            current_volume = volume.iloc[-1] if not pd.isna(volume.iloc[-1]) else 0
            avg_volume = volume.mean() if volume.mean() > 0 else 1
            
            # Base probability from strength
            base_prob = strength / 100.0
            
            # Adjust based on distance from level
            distance_pct = abs(current_price - level) / level if level > 0 else 1.0
            if distance_pct < 0.01:  # Very close
                distance_factor = 1.2
            elif distance_pct < 0.02:  # Close
                distance_factor = 1.1
            elif distance_pct < 0.05:  # Moderate
                distance_factor = 1.0
            else:  # Far
                distance_factor = 0.8
            
            # Adjust based on volume
            volume_ratio = current_volume / avg_volume
            if volume_ratio > 1.5:  # High volume
                volume_factor = 1.1
            elif volume_ratio > 1.2:  # Above average
                volume_factor = 1.05
            else:  # Low volume
                volume_factor = 0.95
            
            # Adjust based on momentum
            if len(close) >= 5:
                momentum = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]
                if level_type == 'support':
                    # For support: negative momentum (falling) increases bounce probability
                    momentum_factor = 1.0 + abs(min(0, momentum)) * 0.5
                else:
                    # For resistance: positive momentum (rising) increases breakout probability
                    momentum_factor = 1.0 + abs(max(0, momentum)) * 0.5
            else:
                momentum_factor = 1.0
            
            # Calculate final probability
            probability = base_prob * distance_factor * volume_factor * momentum_factor
            
            # Clamp to [0, 1]
            return max(0.0, min(1.0, probability))
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error predicting bounce probability for level {level}")
            return 0.5
    
    def track_level_accuracy(
        self,
        level: float,
        level_type: str,
        outcome: str  # 'bounce', 'break', 'none'
    ) -> None:
        """
        Track historical accuracy of a support/resistance level.
        
        Args:
            level: Support/resistance level
            level_type: 'support' or 'resistance'
            outcome: 'bounce', 'break', or 'none'
        """
        level_key = f"{level_type}_{level:.2f}"
        
        if level_key not in self.historical_accuracy:
            self.historical_accuracy[level_key] = {
                'bounces': 0,
                'breaks': 0,
                'total': 0
            }
        
        if outcome == 'bounce':
            self.historical_accuracy[level_key]['bounces'] += 1
        elif outcome == 'break':
            self.historical_accuracy[level_key]['breaks'] += 1
        
        self.historical_accuracy[level_key]['total'] += 1
    
    def get_level_accuracy(
        self,
        level: float,
        level_type: str
    ) -> Dict[str, float]:
        """
        Get historical accuracy for a support/resistance level.
        
        Args:
            level: Support/resistance level
            level_type: 'support' or 'resistance'
            
        Returns:
            Dictionary with accuracy metrics
        """
        level_key = f"{level_type}_{level:.2f}"
        
        if level_key not in self.historical_accuracy:
            return {
                'bounce_rate': 0.0,
                'break_rate': 0.0,
                'total_events': 0
            }
        
        stats = self.historical_accuracy[level_key]
        total = stats['total']
        
        if total == 0:
            return {
                'bounce_rate': 0.0,
                'break_rate': 0.0,
                'total_events': 0
            }
        
        return {
            'bounce_rate': stats['bounces'] / total,
            'break_rate': stats['breaks'] / total,
            'total_events': total
        }
    
    def validate_levels(
        self,
        support_levels: List[Dict[str, Any]],
        resistance_levels: List[Dict[str, Any]],
        data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Validate all support/resistance levels and predict probabilities.
        
        Args:
            support_levels: List of support level dictionaries
            resistance_levels: List of resistance level dictionaries
            data: Historical price data
            
        Returns:
            Dictionary with validated levels and probabilities
        """
        try:
            normalized_data = self.adapter.normalize_dataframe(data)
            
            if normalized_data.empty:
                return {
                    'valid_support': [],
                    'valid_resistance': [],
                    'near_support': None,
                    'near_resistance': None
                }
            
            close = self.adapter.get_column(normalized_data, 'CLOSE')
            current_price = close.iloc[-1]
            
            # Validate support levels
            valid_support = []
            near_support = None
            min_support_distance = float('inf')
            
            for support in support_levels:
                level = support.get('level', 0)
                strength = support.get('strength', 50.0)
                
                if self.is_level_valid(level, 'support', normalized_data):
                    bounce_prob = self.predict_bounce_probability(
                        level, 'support', normalized_data, strength
                    )
                    
                    validated = support.copy()
                    validated['valid'] = True
                    validated['bounce_probability'] = bounce_prob
                    validated['distance_pct'] = abs(current_price - level) / level if level > 0 else 1.0
                    
                    valid_support.append(validated)
                    
                    # Track nearest support
                    if self.is_near_level(current_price, level):
                        distance = abs(current_price - level)
                        if distance < min_support_distance:
                            min_support_distance = distance
                            near_support = validated
            
            # Validate resistance levels
            valid_resistance = []
            near_resistance = None
            min_resistance_distance = float('inf')
            
            for resistance in resistance_levels:
                level = resistance.get('level', 0)
                strength = resistance.get('strength', 50.0)
                
                if self.is_level_valid(level, 'resistance', normalized_data):
                    breakout_prob = self.predict_bounce_probability(
                        level, 'resistance', normalized_data, strength
                    )
                    
                    validated = resistance.copy()
                    validated['valid'] = True
                    validated['breakout_probability'] = breakout_prob
                    validated['distance_pct'] = abs(current_price - level) / level if level > 0 else 1.0
                    
                    valid_resistance.append(validated)
                    
                    # Track nearest resistance
                    if self.is_near_level(current_price, level):
                        distance = abs(current_price - level)
                        if distance < min_resistance_distance:
                            min_resistance_distance = distance
                            near_resistance = validated
            
            return {
                'valid_support': sorted(valid_support, key=lambda x: x.get('strength', 0), reverse=True),
                'valid_resistance': sorted(valid_resistance, key=lambda x: x.get('strength', 0), reverse=True),
                'near_support': near_support,
                'near_resistance': near_resistance,
                'current_price': float(current_price)
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error validating support/resistance levels")
            return {
                'valid_support': [],
                'valid_resistance': [],
                'near_support': None,
                'near_resistance': None
            }

