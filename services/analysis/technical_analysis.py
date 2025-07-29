from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException

# Type aliases
TechnicalIndicators = Dict[str, pd.Series]
TechnicalSignals = Dict[str, List[Dict[str, Any]]]
TrendAnalysis = Dict[str, Union[str, float]]

class TechnicalAnalyzer:
    """Class for performing technical analysis on stock data."""
    
    @staticmethod
    def calculate_indicators(data: pd.DataFrame) -> TechnicalIndicators:
        """
        Calculate technical indicators from price data.
        
        Args:
            data: DataFrame containing price data with columns ['Open', 'High', 'Low', 'Close', 'Volume']
            
        Returns:
            Dictionary containing calculated technical indicators
            
        Raises:
            DataProcessingException: If there's an error processing the data
        """
        try:
            indicators: TechnicalIndicators = {}
            
            # Calculate moving averages
            indicators['sma_20'] = TechnicalAnalyzer._calculate_sma(data['Close'], 20)
            indicators['sma_50'] = TechnicalAnalyzer._calculate_sma(data['Close'], 50)
            indicators['sma_200'] = TechnicalAnalyzer._calculate_sma(data['Close'], 200)
            
            # Calculate RSI
            indicators['rsi'] = TechnicalAnalyzer._calculate_rsi(data['Close'])
            
            # Calculate MACD
            macd_line, signal_line = TechnicalAnalyzer._calculate_macd(data['Close'])
            indicators['macd'] = macd_line
            indicators['macd_signal'] = signal_line
            indicators['macd_histogram'] = macd_line - signal_line
            
            return indicators
            
        except Exception as e:
            raise DataProcessingException(f"Error calculating technical indicators: {str(e)}")
    
    @staticmethod
    def _calculate_sma(prices: pd.Series, window: int) -> pd.Series:
        """
        Calculate Simple Moving Average.
        
        Args:
            prices: Series of price data
            window: Window size for the moving average
            
        Returns:
            Series containing the moving average values
        """
        return prices.rolling(window=window).mean()
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            prices: Series of price data
            window: Window size for RSI calculation
            
        Returns:
            Series containing the RSI values
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def _calculate_macd(prices: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: Series of price data
            
        Returns:
            Tuple containing (MACD line, Signal line)
        """
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd, signal
    
    @staticmethod
    def generate_signals(data: pd.DataFrame) -> TechnicalSignals:
        """
        Generate trading signals based on technical indicators.
        
        Args:
            data: DataFrame containing price data
            
        Returns:
            Dictionary containing trading signals
        """
        signals: TechnicalSignals = {
            'buy': [],
            'sell': []
        }
        
        try:
            # Calculate indicators
            indicators = TechnicalAnalyzer.calculate_indicators(data)
            
            # Generate signals based on moving average crossovers
            for i in range(1, len(data)):
                if indicators['sma_20'].iloc[i] > indicators['sma_50'].iloc[i] and \
                   indicators['sma_20'].iloc[i-1] <= indicators['sma_50'].iloc[i-1]:
                    signals['buy'].append({
                        'date': data.index[i],
                        'price': data['Close'].iloc[i],
                        'type': 'MA_CROSSOVER'
                    })
                
                elif indicators['sma_20'].iloc[i] < indicators['sma_50'].iloc[i] and \
                     indicators['sma_20'].iloc[i-1] >= indicators['sma_50'].iloc[i-1]:
                    signals['sell'].append({
                        'date': data.index[i],
                        'price': data['Close'].iloc[i],
                        'type': 'MA_CROSSOVER'
                    })
            
            return signals
            
        except Exception as e:
            DebugUtils.error(f"Error generating signals: {str(e)}")
            return {'buy': [], 'sell': []}
    
    @staticmethod
    def analyze_trend(data: pd.DataFrame) -> TrendAnalysis:
        """
        Analyze price trend based on technical indicators.
        
        Args:
            data: DataFrame containing price data
            
        Returns:
            Dictionary containing trend analysis
        """
        trend: TrendAnalysis = {}
        
        try:
            # Calculate indicators
            indicators = TechnicalAnalyzer.calculate_indicators(data)
            
            # Get latest values
            last_close = data['Close'].iloc[-1]
            last_sma20 = indicators['sma_20'].iloc[-1]
            last_sma50 = indicators['sma_50'].iloc[-1]
            last_sma200 = indicators['sma_200'].iloc[-1]
            last_rsi = indicators['rsi'].iloc[-1]
            
            # Determine trend
            if last_close > last_sma20 > last_sma50 > last_sma200:
                trend['direction'] = 'bullish'
                trend['strength'] = 'strong'
            elif last_close > last_sma20 > last_sma50:
                trend['direction'] = 'bullish'
                trend['strength'] = 'moderate'
            elif last_close < last_sma20 < last_sma50 < last_sma200:
                trend['direction'] = 'bearish'
                trend['strength'] = 'strong'
            elif last_close < last_sma20 < last_sma50:
                trend['direction'] = 'bearish'
                trend['strength'] = 'moderate'
            else:
                trend['direction'] = 'neutral'
                trend['strength'] = 'weak'
            
            # Add RSI analysis
            if last_rsi > 70:
                trend['rsi_signal'] = 'overbought'
            elif last_rsi < 30:
                trend['rsi_signal'] = 'oversold'
            else:
                trend['rsi_signal'] = 'neutral'
            
            return trend
            
        except Exception as e:
            DebugUtils.error(f"Error analyzing trend: {str(e)}")
            return {'direction': 'unknown', 'strength': 'unknown', 'rsi_signal': 'unknown'} 