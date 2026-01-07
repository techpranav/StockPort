"""
Volume Analysis Indicators Module

This module provides volume-based technical indicators for analyzing
trading volume patterns and unusual volume detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from config.constants.NumericConstants import (
    HIGH_VOLUME_MULTIPLIER,
    LOW_VOLUME_MULTIPLIER,
    SMA_SHORT_PERIOD
)
from services.data_providers.adapters.adapter_factory import AdapterFactory
from config.constants.DataConstants import DEFAULT_PROVIDER


class VolumeIndicators:
    """
    Class for calculating volume-based technical indicators.
    
    Provides indicators for volume analysis:
    - Volume Profile
    - Volume Rate of Change (VROC)
    - Accumulation/Distribution Line
    - Chaikin Money Flow (CMF)
    - Volume-weighted indicators
    - Unusual volume detection
    """
    
    @staticmethod
    def calculate_volume_profile(
        data: pd.DataFrame,
        bins: int = 20,
        provider_name: str = DEFAULT_PROVIDER
    ) -> Dict[str, Any]:
        """
        Calculate Volume Profile.
        
        Volume Profile shows the distribution of volume at different price levels,
        helping identify support and resistance zones.
        
        Args:
            data: DataFrame with High, Low, Close, Volume columns (will be normalized)
            bins: Number of price bins for profile (default: 20)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Dictionary with:
            - price_levels: Array of price levels
            - volume_at_level: Array of volume at each level
            - poc: Point of Control (price level with highest volume)
            - value_area_high: Upper bound of value area (70% volume)
            - value_area_low: Lower bound of value area (70% volume)
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty:
                raise DataProcessingException("Data cannot be empty for Volume Profile")
            
            try:
                volume = adapter.get_column(normalized_data, 'VOLUME')
            except DataProcessingException:
                raise DataProcessingException("Volume column required for Volume Profile")
            
            high = adapter.get_column(normalized_data, 'HIGH')
            low = adapter.get_column(normalized_data, 'LOW')
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Create price bins
            price_min = low.min()
            price_max = high.max()
            price_levels = np.linspace(price_min, price_max, bins)
            
            # Calculate volume at each price level
            volume_at_level = np.zeros(bins)
            
            for idx, row in normalized_data.iterrows():
                # Determine which bins this candle contributes to
                candle_low = row['low']
                candle_high = row['high']
                candle_volume = row['volume']
                
                # Find bins within candle range
                valid_bins = (price_levels >= candle_low) & (price_levels <= candle_high)
                
                if valid_bins.any():
                    # Distribute volume evenly across valid bins
                    volume_per_bin = candle_volume / valid_bins.sum()
                    volume_at_level[valid_bins] += volume_per_bin
            
            # Point of Control (POC) - price level with highest volume
            poc_idx = np.argmax(volume_at_level)
            poc = price_levels[poc_idx]
            
            # Value Area (70% of volume)
            total_volume = volume_at_level.sum()
            target_volume = total_volume * 0.70
            
            # Find value area bounds
            sorted_indices = np.argsort(volume_at_level)[::-1]
            cumulative_volume = 0
            value_area_indices = []
            
            for idx in sorted_indices:
                cumulative_volume += volume_at_level[idx]
                value_area_indices.append(idx)
                if cumulative_volume >= target_volume:
                    break
            
            value_area_prices = price_levels[value_area_indices]
            value_area_high = value_area_prices.max()
            value_area_low = value_area_prices.min()
            
            return {
                'price_levels': price_levels,
                'volume_at_level': volume_at_level,
                'poc': poc,
                'value_area_high': value_area_high,
                'value_area_low': value_area_low,
                'total_volume': total_volume
            }
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating Volume Profile: {str(e)}") from e
    
    @staticmethod
    def calculate_vroc(
        data: pd.DataFrame,
        period: int = 12
    ) -> pd.Series:
        """
        Calculate Volume Rate of Change (VROC).
        
        VROC measures the rate of change in volume over a specified period.
        
        Args:
            data: DataFrame with Volume column
            period: Period for calculation (default: 12)
            
        Returns:
            Series containing VROC values (percentage)
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period:
                raise DataProcessingException(
                    f"Insufficient data for VROC: need at least {period} periods"
                )
            
            try:
                volume = adapter.get_column(normalized_data, 'VOLUME')
            except DataProcessingException:
                raise DataProcessingException("Volume column required for VROC")
            
            # VROC = ((Current Volume - Volume N periods ago) / Volume N periods ago) * 100
            vroc = ((volume - volume.shift(period)) / volume.shift(period)) * 100
            
            return vroc
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating VROC: {str(e)}") from e
    
    @staticmethod
    def calculate_accumulation_distribution(
        data: pd.DataFrame,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Accumulation/Distribution Line.
        
        A/D Line uses price and volume to determine if a stock is being
        accumulated or distributed.
        
        Args:
            data: DataFrame with High, Low, Close, Volume columns
            
        Returns:
            Series containing A/D Line values
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty:
                raise DataProcessingException("Data cannot be empty for A/D Line")
            
            try:
                volume = adapter.get_column(normalized_data, 'VOLUME')
            except DataProcessingException:
                raise DataProcessingException("Volume column required for A/D Line")
            
            high = adapter.get_column(normalized_data, 'HIGH')
            low = adapter.get_column(normalized_data, 'LOW')
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Money Flow Multiplier
            mfm = ((close - low) - (high - close)) / (high - low)
            mfm = mfm.fillna(0)  # Handle division by zero
            
            # Money Flow Volume
            mfv = mfm * volume
            
            # Accumulation/Distribution Line (cumulative)
            ad_line = mfv.cumsum()
            
            return ad_line
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating A/D Line: {str(e)}") from e
    
    @staticmethod
    def calculate_cmf(
        data: pd.DataFrame,
        period: int = 20,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Chaikin Money Flow (CMF).
        
        CMF measures the amount of Money Flow Volume over a specific period.
        Positive values indicate buying pressure, negative values indicate selling pressure.
        
        Args:
            data: DataFrame with High, Low, Close, Volume columns
            period: Period for calculation (default: 20)
            
        Returns:
            Series containing CMF values (-1 to 1)
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period:
                raise DataProcessingException(
                    f"Insufficient data for CMF: need at least {period} periods"
                )
            
            try:
                volume = adapter.get_column(normalized_data, 'VOLUME')
            except DataProcessingException:
                raise DataProcessingException("Volume column required for CMF")
            
            high = adapter.get_column(normalized_data, 'HIGH')
            low = adapter.get_column(normalized_data, 'LOW')
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Money Flow Multiplier
            mfm = ((close - low) - (high - close)) / (high - low)
            mfm = mfm.fillna(0)
            
            # Money Flow Volume
            mfv = mfm * volume
            
            # CMF = Sum of MFV / Sum of Volume over period
            cmf = mfv.rolling(window=period).sum() / volume.rolling(window=period).sum()
            
            return cmf
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating CMF: {str(e)}") from e
    
    @staticmethod
    def detect_unusual_volume(
        data: pd.DataFrame,
        multiplier: float = HIGH_VOLUME_MULTIPLIER,
        period: int = SMA_SHORT_PERIOD,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Detect unusual volume spikes.
        
        Identifies periods where volume is significantly higher or lower
        than the average volume.
        
        Args:
            data: DataFrame with Volume column
            multiplier: Multiplier for unusual volume detection (default: 1.5)
            period: Period for average volume calculation (default: 20)
            
        Returns:
            Series with boolean values (True for unusual volume)
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period:
                raise DataProcessingException(
                    f"Insufficient data for unusual volume detection: need at least {period} periods"
                )
            
            try:
                volume = adapter.get_column(normalized_data, 'VOLUME')
            except DataProcessingException:
                raise DataProcessingException("Volume column required for unusual volume detection")
            avg_volume = volume.rolling(window=period).mean()
            
            # Detect unusual volume (above multiplier * average)
            unusual_volume = volume > (avg_volume * multiplier)
            
            return unusual_volume
            
        except Exception as e:
            raise DataProcessingException(f"Error detecting unusual volume: {str(e)}") from e
    
    @staticmethod
    def calculate_volume_weighted_sma(
        data: pd.DataFrame,
        period: int = SMA_SHORT_PERIOD
    ) -> pd.Series:
        """
        Calculate Volume Weighted Simple Moving Average.
        
        VW-SMA gives more weight to periods with higher volume.
        
        Args:
            data: DataFrame with Close and Volume columns
            period: Period for calculation (default: 20)
            
        Returns:
            Series containing VW-SMA values
        """
        try:
            if data.empty or len(data) < period:
                raise DataProcessingException(
                    f"Insufficient data for VW-SMA: need at least {period} periods"
                )
            
            if 'Volume' not in data.columns:
                raise DataProcessingException("Volume column required for VW-SMA")
            
            close = data['Close']
            volume = data['Volume']
            
            # Volume Weighted SMA = Sum(Price * Volume) / Sum(Volume)
            vw_sma = (close * volume).rolling(window=period).sum() / volume.rolling(window=period).sum()
            
            return vw_sma
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating VW-SMA: {str(e)}") from e
    
    @staticmethod
    def calculate_volume_oscillator(
        data: pd.DataFrame,
        short_period: int = 5,
        long_period: int = 10,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Volume Oscillator.
        
        Volume Oscillator shows the relationship between two volume moving averages.
        
        Args:
            data: DataFrame with Volume column
            short_period: Short period MA (default: 5)
            long_period: Long period MA (default: 10)
            
        Returns:
            Series containing Volume Oscillator values (percentage)
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < long_period:
                raise DataProcessingException(
                    f"Insufficient data for Volume Oscillator: need at least {long_period} periods"
                )
            
            try:
                volume = adapter.get_column(normalized_data, 'VOLUME')
            except DataProcessingException:
                raise DataProcessingException("Volume column required for Volume Oscillator")
            
            # Calculate moving averages
            short_ma = volume.rolling(window=short_period).mean()
            long_ma = volume.rolling(window=long_period).mean()
            
            # Volume Oscillator = ((Short MA - Long MA) / Long MA) * 100
            volume_oscillator = ((short_ma - long_ma) / long_ma) * 100
            
            return volume_oscillator
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating Volume Oscillator: {str(e)}") from e

