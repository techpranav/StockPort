"""
Intraday Technical Indicators Module

This module provides intraday-specific technical indicators optimized for
short-term and intraday trading analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from config.constants.NumericConstants import RSI_PERIOD
from services.data_providers.adapters.adapter_factory import AdapterFactory
from config.constants.DataConstants import DEFAULT_PROVIDER


class IntradayIndicators:
    """
    Class for calculating intraday technical indicators.
    
    Provides indicators optimized for intraday and short-term trading:
    - Stochastic Oscillator
    - Average Directional Index (ADX)
    - Average True Range (ATR)
    - Commodity Channel Index (CCI)
    - Williams %R
    - Money Flow Index (MFI)
    - On-Balance Volume (OBV)
    - Volume Weighted Average Price (VWAP)
    - Ichimoku Cloud
    - Parabolic SAR
    - Fibonacci Retracement Levels
    """
    
    @staticmethod
    def calculate_stochastic(
        data: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3,
        provider_name: str = DEFAULT_PROVIDER
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator (K% and D%).
        
        Stochastic measures the position of closing price relative to
        the high-low range over a given period.
        
        Args:
            data: DataFrame with High, Low, Close columns (will be normalized)
            k_period: Period for %K calculation (default: 14)
            d_period: Period for %D smoothing (default: 3)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Tuple of (K%, D%) Series
            
        Raises:
            DataProcessingException: If data is invalid
        """
        try:
            # Get adapter and normalize data
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < k_period:
                raise DataProcessingException(
                    f"Insufficient data for Stochastic: need at least {k_period} periods"
                )
            
            high = adapter.get_column(normalized_data, 'HIGH')
            low = adapter.get_column(normalized_data, 'LOW')
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Calculate %K
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            
            # Calculate %D (smoothed %K)
            d_percent = k_percent.rolling(window=d_period).mean()
            
            return k_percent, d_percent
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating Stochastic: {str(e)}") from e
    
    @staticmethod
    def calculate_adx(
        data: pd.DataFrame,
        period: int = 14,
        provider_name: str = DEFAULT_PROVIDER
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Average Directional Index (ADX) with +DI and -DI.
        
        ADX measures trend strength regardless of direction.
        +DI and -DI indicate bullish and bearish momentum.
        
        Args:
            data: DataFrame with High, Low, Close columns (will be normalized)
            period: Period for ADX calculation (default: 14)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Tuple of (ADX, +DI, -DI) Series
        """
        try:
            # Get adapter and normalize data
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period * 2:
                raise DataProcessingException(
                    f"Insufficient data for ADX: need at least {period * 2} periods"
                )
            
            high = adapter.get_column(normalized_data, 'HIGH')
            low = adapter.get_column(normalized_data, 'LOW')
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Calculate True Range
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Calculate Directional Movement
            plus_dm = high.diff()
            minus_dm = -low.diff()
            
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm < 0] = 0
            
            # Calculate smoothed values
            atr = tr.rolling(window=period).mean()
            plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
            
            # Calculate ADX
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=period).mean()
            
            return adx, plus_di, minus_di
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating ADX: {str(e)}") from e
    
    @staticmethod
    def _get_ohlcv_data(
        data: pd.DataFrame,
        provider_name: str = DEFAULT_PROVIDER
    ) -> Dict[str, pd.Series]:
        """
        Helper method to get normalized OHLCV data using adapter.
        
        Args:
            data: Raw DataFrame
            provider_name: Name of the data provider
            
        Returns:
            Dictionary with 'high', 'low', 'close', 'open', 'volume' keys
        """
        adapter = AdapterFactory.get_adapter(provider_name)
        normalized_data = adapter.normalize_dataframe(data)
        return adapter.get_ohlcv_data(normalized_data)
    
    @staticmethod
    def calculate_atr(
        data: pd.DataFrame,
        period: int = 14,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        ATR measures market volatility by calculating the average
        of true ranges over a specified period.
        
        Args:
            data: DataFrame with High, Low, Close columns
            period: Period for ATR calculation (default: 14)
            
        Returns:
            Series containing ATR values
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period:
                raise DataProcessingException(
                    f"Insufficient data for ATR: need at least {period} periods"
                )
            
            high = adapter.get_column(normalized_data, 'HIGH')
            low = adapter.get_column(normalized_data, 'LOW')
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Calculate True Range
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Calculate ATR (using Wilder's smoothing)
            atr = tr.ewm(alpha=1/period, adjust=False).mean()
            
            return atr
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating ATR: {str(e)}") from e
    
    @staticmethod
    def calculate_cci(
        data: pd.DataFrame,
        period: int = 20,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Commodity Channel Index (CCI).
        
        CCI identifies cyclical trends by measuring the deviation of price
        from its statistical mean.
        
        Args:
            data: DataFrame with High, Low, Close columns (will be normalized)
            period: Period for CCI calculation (default: 20)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Series containing CCI values
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period:
                raise DataProcessingException(
                    f"Insufficient data for CCI: need at least {period} periods"
                )
            
            high = adapter.get_column(normalized_data, 'HIGH')
            low = adapter.get_column(normalized_data, 'LOW')
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Typical Price
            tp = (high + low + close) / 3
            
            # Simple Moving Average of TP
            sma_tp = tp.rolling(window=period).mean()
            
            # Mean Deviation
            mean_dev = tp.rolling(window=period).apply(
                lambda x: np.mean(np.abs(x - x.mean()))
            )
            
            # CCI
            cci = (tp - sma_tp) / (0.015 * mean_dev)
            
            return cci
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating CCI: {str(e)}") from e
    
    @staticmethod
    def calculate_williams_r(
        data: pd.DataFrame,
        period: int = 14,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Williams %R.
        
        Williams %R is a momentum indicator that measures overbought/oversold
        levels, similar to Stochastic but inverted.
        
        Args:
            data: DataFrame with High, Low, Close columns
            period: Period for calculation (default: 14)
            
        Returns:
            Series containing Williams %R values (-100 to 0)
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < period:
                raise DataProcessingException(
                    f"Insufficient data for Williams %R: need at least {period} periods"
                )
            
            high = adapter.get_column(normalized_data, 'HIGH')
            low = adapter.get_column(normalized_data, 'LOW')
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            
            williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
            
            return williams_r
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating Williams %R: {str(e)}") from e
    
    @staticmethod
    def calculate_mfi(
        data: pd.DataFrame,
        period: int = 14,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Money Flow Index (MFI).
        
        MFI combines price and volume to identify overbought/oversold conditions.
        It's similar to RSI but includes volume.
        
        Args:
            data: DataFrame with High, Low, Close, Volume columns
            period: Period for calculation (default: 14)
            
        Returns:
            Series containing MFI values (0-100)
        """
        try:
            if data.empty or len(data) < period:
                raise DataProcessingException(
                    f"Insufficient data for MFI: need at least {period} periods"
                )
            
            if 'Volume' not in data.columns:
                raise DataProcessingException("Volume column required for MFI")
            
            high = data['High']
            low = data['Low']
            close = data['Close']
            volume = data['Volume']
            
            # Typical Price
            tp = (high + low + close) / 3
            
            # Raw Money Flow
            rmf = tp * volume
            
            # Positive and Negative Money Flow
            positive_flow = rmf.where(tp > tp.shift(), 0).rolling(window=period).sum()
            negative_flow = rmf.where(tp < tp.shift(), 0).rolling(window=period).sum()
            
            # Money Flow Ratio
            mfr = positive_flow / negative_flow
            
            # Money Flow Index
            mfi = 100 - (100 / (1 + mfr))
            
            return mfi
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating MFI: {str(e)}") from e
    
    @staticmethod
    def calculate_obv(
        data: pd.DataFrame,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV).
        
        OBV is a cumulative volume indicator that relates volume to price change.
        
        Args:
            data: DataFrame with Close and Volume columns
            
        Returns:
            Series containing OBV values
        """
        try:
            if data.empty:
                raise DataProcessingException("Data cannot be empty for OBV")
            
            if 'Volume' not in data.columns:
                raise DataProcessingException("Volume column required for OBV")
            
            close = data['Close']
            volume = data['Volume']
            
            # Calculate OBV
            obv = (volume * np.sign(close.diff())).fillna(0).cumsum()
            
            return obv
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating OBV: {str(e)}") from e
    
    @staticmethod
    def calculate_vwap(
        data: pd.DataFrame,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP).
        
        VWAP is the average price a security has traded at throughout the day,
        based on both volume and price.
        
        Args:
            data: DataFrame with High, Low, Close, Volume columns
            
        Returns:
            Series containing VWAP values
        """
        try:
            if data.empty:
                raise DataProcessingException("Data cannot be empty for VWAP")
            
            if 'Volume' not in data.columns:
                raise DataProcessingException("Volume column required for VWAP")
            
            high = data['High']
            low = data['Low']
            close = data['Close']
            volume = data['Volume']
            
            # Typical Price
            tp = (high + low + close) / 3
            
            # VWAP = Cumulative(TP * Volume) / Cumulative(Volume)
            cumulative_tpv = (tp * volume).cumsum()
            cumulative_volume = volume.cumsum()
            
            vwap = cumulative_tpv / cumulative_volume
            
            return vwap
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating VWAP: {str(e)}") from e
    
    @staticmethod
    def calculate_ichimoku(
        data: pd.DataFrame,
        tenkan_period: int = 9,
        kijun_period: int = 26,
        senkou_b_period: int = 52,
        provider_name: str = DEFAULT_PROVIDER
    ) -> Dict[str, pd.Series]:
        """
        Calculate Ichimoku Cloud components.
        
        Ichimoku Cloud is a comprehensive indicator that provides support/resistance
        levels and trend direction.
        
        Args:
            data: DataFrame with High, Low, Close columns
            tenkan_period: Period for Tenkan-sen (default: 9)
            kijun_period: Period for Kijun-sen (default: 26)
            senkou_b_period: Period for Senkou Span B (default: 52)
            
        Returns:
            Dictionary with Ichimoku components:
            - tenkan_sen: Conversion line
            - kijun_sen: Base line
            - senkou_span_a: Leading span A
            - senkou_span_b: Leading span B
            - chikou_span: Lagging span
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < senkou_b_period:
                raise DataProcessingException(
                    f"Insufficient data for Ichimoku: need at least {senkou_b_period} periods"
                )
            
            high = adapter.get_column(normalized_data, 'HIGH')
            low = adapter.get_column(normalized_data, 'LOW')
            close = adapter.get_column(normalized_data, 'CLOSE')
            
            # Tenkan-sen (Conversion Line)
            tenkan_high = high.rolling(window=tenkan_period).max()
            tenkan_low = low.rolling(window=tenkan_period).min()
            tenkan_sen = (tenkan_high + tenkan_low) / 2
            
            # Kijun-sen (Base Line)
            kijun_high = high.rolling(window=kijun_period).max()
            kijun_low = low.rolling(window=kijun_period).min()
            kijun_sen = (kijun_high + kijun_low) / 2
            
            # Senkou Span A (Leading Span A)
            senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun_period)
            
            # Senkou Span B (Leading Span B)
            senkou_b_high = high.rolling(window=senkou_b_period).max()
            senkou_b_low = low.rolling(window=senkou_b_period).min()
            senkou_span_b = ((senkou_b_high + senkou_b_low) / 2).shift(kijun_period)
            
            # Chikou Span (Lagging Span)
            chikou_span = close.shift(-kijun_period)
            
            return {
                'tenkan_sen': tenkan_sen,
                'kijun_sen': kijun_sen,
                'senkou_span_a': senkou_span_a,
                'senkou_span_b': senkou_span_b,
                'chikou_span': chikou_span
            }
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating Ichimoku: {str(e)}") from e
    
    @staticmethod
    def calculate_parabolic_sar(
        data: pd.DataFrame,
        af_start: float = 0.02,
        af_increment: float = 0.02,
        af_max: float = 0.2,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.Series:
        """
        Calculate Parabolic SAR.
        
        Parabolic SAR provides potential reversal points in price direction.
        
        Args:
            data: DataFrame with High, Low, Close columns
            af_start: Acceleration factor start (default: 0.02)
            af_increment: Acceleration factor increment (default: 0.02)
            af_max: Maximum acceleration factor (default: 0.2)
            
        Returns:
            Series containing Parabolic SAR values
        """
        try:
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty or len(normalized_data) < 2:
                raise DataProcessingException("Insufficient data for Parabolic SAR")
            
            high = adapter.get_column(normalized_data, 'HIGH').values
            low = adapter.get_column(normalized_data, 'LOW').values
            close = adapter.get_column(normalized_data, 'CLOSE').values
            
            sar = np.zeros(len(data))
            trend = np.zeros(len(data), dtype=int)
            ep = np.zeros(len(data))
            af = np.zeros(len(data))
            
            # Initialize
            sar[0] = low[0]
            trend[0] = 1  # 1 for uptrend, -1 for downtrend
            ep[0] = high[0]
            af[0] = af_start
            
            for i in range(1, len(data)):
                # Previous values
                prev_sar = sar[i-1]
                prev_trend = trend[i-1]
                prev_ep = ep[i-1]
                prev_af = af[i-1]
                
                # Calculate SAR
                if prev_trend == 1:  # Uptrend
                    sar[i] = prev_sar + prev_af * (prev_ep - prev_sar)
                    sar[i] = min(sar[i], low[i-1], low[i])
                    
                    if high[i] > prev_ep:
                        ep[i] = high[i]
                        af[i] = min(prev_af + af_increment, af_max)
                    else:
                        ep[i] = prev_ep
                        af[i] = prev_af
                    
                    if low[i] < sar[i]:
                        trend[i] = -1
                        sar[i] = prev_ep
                        ep[i] = low[i]
                        af[i] = af_start
                    else:
                        trend[i] = 1
                        
                else:  # Downtrend
                    sar[i] = prev_sar + prev_af * (prev_ep - prev_sar)
                    sar[i] = max(sar[i], high[i-1], high[i])
                    
                    if low[i] < prev_ep:
                        ep[i] = low[i]
                        af[i] = min(prev_af + af_increment, af_max)
                    else:
                        ep[i] = prev_ep
                        af[i] = prev_af
                    
                    if high[i] > sar[i]:
                        trend[i] = 1
                        sar[i] = prev_ep
                        ep[i] = high[i]
                        af[i] = af_start
                    else:
                        trend[i] = -1
            
            return pd.Series(sar, index=normalized_data.index)
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating Parabolic SAR: {str(e)}") from e
    
    @staticmethod
    def calculate_fibonacci_retracement(
        data: pd.DataFrame,
        lookback_period: int = 20
    ) -> Dict[str, pd.Series]:
        """
        Calculate Fibonacci Retracement Levels.
        
        Fibonacci retracements are horizontal lines indicating potential
        support/resistance levels based on Fibonacci ratios.
        
        Args:
            data: DataFrame with High, Low columns
            lookback_period: Period to find swing high/low (default: 20)
            
        Returns:
            Dictionary with Fibonacci levels:
            - level_0: 0% (swing high)
            - level_236: 23.6%
            - level_382: 38.2%
            - level_500: 50%
            - level_618: 61.8%
            - level_786: 78.6%
            - level_100: 100% (swing low)
        """
        try:
            if data.empty or len(data) < lookback_period:
                raise DataProcessingException(
                    f"Insufficient data for Fibonacci: need at least {lookback_period} periods"
                )
            
            high = data['High']
            low = data['Low']
            
            # Find swing high and low
            swing_high = high.rolling(window=lookback_period).max()
            swing_low = low.rolling(window=lookback_period).min()
            
            # Calculate range
            price_range = swing_high - swing_low
            
            # Fibonacci ratios
            fib_ratios = {
                'level_0': 0.0,
                'level_236': 0.236,
                'level_382': 0.382,
                'level_500': 0.500,
                'level_618': 0.618,
                'level_786': 0.786,
                'level_100': 1.0
            }
            
            # Calculate levels
            levels = {}
            for level_name, ratio in fib_ratios.items():
                if ratio == 0.0:
                    levels[level_name] = swing_high
                elif ratio == 1.0:
                    levels[level_name] = swing_low
                else:
                    levels[level_name] = swing_high - (price_range * ratio)
            
            return levels
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating Fibonacci: {str(e)}") from e

