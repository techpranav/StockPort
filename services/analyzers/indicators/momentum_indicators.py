"""
Momentum Indicators Module

This module provides momentum-based technical indicators for analyzing
price momentum and rate of change.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from services.data_providers.adapters.adapter_factory import AdapterFactory
from config.constants.DataConstants import DEFAULT_PROVIDER


class MomentumIndicators:
    """
    Class for calculating momentum-based technical indicators.
    
    Provides indicators for momentum analysis:
    - Rate of Change (ROC)
    - Momentum Oscillator
    - Price Rate of Change (PROC)
    - Relative Momentum Index (RMI)
    - True Strength Index (TSI)
    """
    
    @staticmethod
    def calculate_roc(
        data: pd.DataFrame,
        period: int = 12,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Rate of Change (ROC).
        
        ROC measures the percentage change in price over a specified period.
        
        Args:
            data: DataFrame with Close column (will be normalized)
            period: Period for calculation (default: 12)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Series containing ROC values (percentage)
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period:
                raise DataProcessingException(
                    f"Insufficient data for ROC: need at least {period} periods"
                )
            
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # ROC = ((Current Price - Price N periods ago) / Price N periods ago) * 100
            roc = ((close - close.shift(period)) / close.shift(period)) * 100
            
            return roc
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating ROC: {str(e)}") from e
    
    @staticmethod
    def calculate_momentum(
        data: pd.DataFrame,
        period: int = 10,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Momentum Oscillator.
        
        Momentum measures the rate of change in price, showing the speed
        of price movement.
        
        Args:
            data: DataFrame with Close column (will be normalized)
            period: Period for calculation (default: 10)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Series containing Momentum values
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period:
                raise DataProcessingException(
                    f"Insufficient data for Momentum: need at least {period} periods"
                )
            
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Momentum = Current Price - Price N periods ago
            momentum = close - close.shift(period)
            
            return momentum
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating Momentum: {str(e)}") from e
    
    @staticmethod
    def calculate_proc(
        data: pd.DataFrame,
        period: int = 12,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Price Rate of Change (PROC).
        
        PROC is similar to ROC but uses a different calculation method.
        
        Args:
            data: DataFrame with Close column (will be normalized)
            period: Period for calculation (default: 12)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Series containing PROC values (percentage)
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period:
                raise DataProcessingException(
                    f"Insufficient data for PROC: need at least {period} periods"
                )
            
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # PROC = (Current Price / Price N periods ago - 1) * 100
            proc = ((close / close.shift(period)) - 1) * 100
            
            return proc
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating PROC: {str(e)}") from e
    
    @staticmethod
    def calculate_rmi(
        data: pd.DataFrame,
        period: int = 14,
        momentum_period: int = 5,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Relative Momentum Index (RMI).
        
        RMI is similar to RSI but uses momentum instead of price changes.
        
        Args:
            data: DataFrame with Close column (will be normalized)
            period: Period for calculation (default: 14)
            momentum_period: Period for momentum calculation (default: 5)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Series containing RMI values (0-100)
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period + momentum_period:
                raise DataProcessingException(
                    f"Insufficient data for RMI: need at least {period + momentum_period} periods"
                )
            
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Calculate momentum
            momentum = close - close.shift(momentum_period)
            
            # Separate gains and losses
            gains = momentum.where(momentum > 0, 0)
            losses = -momentum.where(momentum < 0, 0)
            
            # Calculate average gains and losses
            avg_gains = gains.rolling(window=period).mean()
            avg_losses = losses.rolling(window=period).mean()
            
            # Calculate RMI
            rs = avg_gains / avg_losses.replace(0, np.nan)
            rmi = 100 - (100 / (1 + rs))
            
            return rmi.fillna(50)  # Neutral value when no losses
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating RMI: {str(e)}") from e
    
    @staticmethod
    def calculate_tsi(
        data: pd.DataFrame,
        long_period: int = 25,
        short_period: int = 13,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate True Strength Index (TSI).
        
        TSI uses double smoothing of price momentum to identify trend direction
        and strength while filtering out market noise.
        
        Args:
            data: DataFrame with Close column (will be normalized)
            long_period: Long smoothing period (default: 25)
            short_period: Short smoothing period (default: 13)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Series containing TSI values
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < long_period + short_period:
                raise DataProcessingException(
                    f"Insufficient data for TSI: need at least {long_period + short_period} periods"
                )
            
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Calculate price change
            price_change = close.diff()
            
            # Double smoothing of price change
            first_smooth = price_change.ewm(span=long_period, adjust=False).mean()
            second_smooth = first_smooth.ewm(span=short_period, adjust=False).mean()
            
            # Double smoothing of absolute price change
            abs_price_change = price_change.abs()
            first_smooth_abs = abs_price_change.ewm(span=long_period, adjust=False).mean()
            second_smooth_abs = first_smooth_abs.ewm(span=short_period, adjust=False).mean()
            
            # Calculate TSI
            tsi = 100 * (second_smooth / second_smooth_abs.replace(0, np.nan))
            
            return tsi.fillna(0)
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating TSI: {str(e)}") from e
    
    @staticmethod
    def calculate_momentum_divergence(
        data: pd.DataFrame,
        indicator: pd.Series,
        period: int = 14,
        provider_name: str = DEFAULT_PROVIDER
    ) -> Dict[str, pd.Series]:
        """
        Calculate momentum divergence between price and indicator.
        
        Divergence occurs when price and indicator move in opposite directions,
        potentially signaling trend reversal.
        
        Args:
            data: DataFrame with Close column (will be normalized)
            indicator: Series of indicator values (e.g., RSI, MACD)
            period: Period for divergence detection (default: 14)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Dictionary with:
            - bullish_divergence: Boolean series (True when bullish divergence detected)
            - bearish_divergence: Boolean series (True when bearish divergence detected)
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period * 2:
                raise DataProcessingException(
                    f"Insufficient data for divergence: need at least {period * 2} periods"
                )
            
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Find local highs and lows
            price_highs = close.rolling(window=period, center=True).max() == close
            price_lows = close.rolling(window=period, center=True).min() == close
            
            indicator_highs = indicator.rolling(window=period, center=True).max() == indicator
            indicator_lows = indicator.rolling(window=period, center=True).min() == indicator
            
            # Detect divergences
            bullish_divergence = pd.Series(False, index=normalized_data.index)
            bearish_divergence = pd.Series(False, index=normalized_data.index)
            
            # Look for divergences in recent periods
            lookback = min(period * 2, len(normalized_data))
            
            for i in range(lookback, len(normalized_data)):
                # Check for bullish divergence (price makes lower low, indicator makes higher low)
                recent_price_lows = price_lows.iloc[i-lookback:i]
                recent_indicator_lows = indicator_lows.iloc[i-lookback:i]
                
                if recent_price_lows.any() and recent_indicator_lows.any():
                    price_low_idx = recent_price_lows[recent_price_lows].index[-1]
                    indicator_low_idx = recent_indicator_lows[recent_indicator_lows].index[-1]
                    
                    if price_low_idx < indicator_low_idx:
                        if close.iloc[i] > close.loc[price_low_idx] and indicator.iloc[i] > indicator.loc[indicator_low_idx]:
                            bullish_divergence.iloc[i] = True
                
                # Check for bearish divergence (price makes higher high, indicator makes lower high)
                recent_price_highs = price_highs.iloc[i-lookback:i]
                recent_indicator_highs = indicator_highs.iloc[i-lookback:i]
                
                if recent_price_highs.any() and recent_indicator_highs.any():
                    price_high_idx = recent_price_highs[recent_price_highs].index[-1]
                    indicator_high_idx = recent_indicator_highs[recent_indicator_highs].index[-1]
                    
                    if price_high_idx < indicator_high_idx:
                        if close.iloc[i] < close.loc[price_high_idx] and indicator.iloc[i] < indicator.loc[indicator_high_idx]:
                            bearish_divergence.iloc[i] = True
            
            return {
                'bullish_divergence': bullish_divergence,
                'bearish_divergence': bearish_divergence
            }
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating momentum divergence: {str(e)}") from e

