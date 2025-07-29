from typing import Dict, Any
import pandas as pd
from utils.debug_utils import DebugUtils
from .base_analyzer import BaseAnalyzer

class GrowthAnalyzer(BaseAnalyzer):
    """Class for analyzing growth metrics."""
    
    @staticmethod
    def analyze_growth(data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze growth metrics from historical data.
        
        Args:
            data: Dictionary containing historical data
            
        Returns:
            Dictionary containing growth metrics
        """
        growth_metrics = {}
        
        try:
            # Validate required data
            BaseAnalyzer._validate_data(data, ['history'])
            
            # Get historical data
            history = data['history']
            if history.empty:
                DebugUtils.warning("No historical data available for growth analysis")
                return growth_metrics
            
            # Calculate price growth
            growth_metrics['price_growth'] = GrowthAnalyzer._calculate_price_growth(history)
            
            # Calculate volume growth
            growth_metrics['volume_growth'] = GrowthAnalyzer._calculate_volume_growth(history)
            
            # Calculate volatility
            growth_metrics['volatility'] = GrowthAnalyzer._calculate_volatility(history)
            
        except Exception as e:
            DebugUtils.error(f"Error analyzing growth: {str(e)}")
        
        return growth_metrics
    
    @staticmethod
    def _calculate_price_growth(history: pd.DataFrame) -> float:
        """Calculate price growth rate."""
        try:
            if len(history) >= 2:
                current_price = history['Close'].iloc[-1]
                previous_price = history['Close'].iloc[-2]
                return BaseAnalyzer._calculate_growth_rate(current_price, previous_price)
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating price growth: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_volume_growth(history: pd.DataFrame) -> float:
        """Calculate volume growth rate."""
        try:
            if len(history) >= 2:
                current_volume = history['Volume'].iloc[-1]
                previous_volume = history['Volume'].iloc[-2]
                return BaseAnalyzer._calculate_growth_rate(current_volume, previous_volume)
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating volume growth: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_volatility(history: pd.DataFrame) -> float:
        """Calculate price volatility."""
        try:
            if len(history) >= 2:
                returns = history['Close'].pct_change().dropna()
                return returns.std() * 100  # Convert to percentage
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating volatility: {str(e)}")
            return 0.0 