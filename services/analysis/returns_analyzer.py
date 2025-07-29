from typing import Dict, Any
import pandas as pd
import numpy as np
from utils.debug_utils import DebugUtils
from .base_analyzer import BaseAnalyzer

class ReturnsAnalyzer(BaseAnalyzer):
    """Class for calculating return metrics."""
    
    @staticmethod
    def calculate_returns(data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate return metrics from historical data.
        
        Args:
            data: Dictionary containing historical data
            
        Returns:
            Dictionary containing return metrics
        """
        return_metrics = {}
        
        try:
            # Validate required data
            BaseAnalyzer._validate_data(data, ['history'])
            
            # Get historical data
            history = data['history']
            if history.empty:
                DebugUtils.warning("No historical data available for returns analysis")
                return return_metrics
            
            # Calculate daily returns
            returns = ReturnsAnalyzer._calculate_daily_returns(history)
            
            # Calculate return metrics
            return_metrics['daily_return_mean'] = returns.mean() * 100  # Convert to percentage
            return_metrics['daily_return_std'] = returns.std() * 100  # Convert to percentage
            return_metrics['sharpe_ratio'] = ReturnsAnalyzer._calculate_sharpe_ratio(returns)
            
        except Exception as e:
            DebugUtils.error(f"Error calculating returns: {str(e)}")
        
        return return_metrics
    
    @staticmethod
    def _calculate_daily_returns(history: pd.DataFrame) -> pd.Series:
        """Calculate daily returns."""
        try:
            if len(history) >= 2:
                return history['Close'].pct_change().dropna()
            return pd.Series()
        except Exception as e:
            DebugUtils.error(f"Error calculating daily returns: {str(e)}")
            return pd.Series()
    
    @staticmethod
    def _calculate_sharpe_ratio(returns: pd.Series) -> float:
        """Calculate Sharpe ratio."""
        try:
            if len(returns) >= 2:
                # Assuming risk-free rate of 0 for simplicity
                excess_returns = returns - 0
                if excess_returns.std() != 0:
                    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)  # Annualized
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating Sharpe ratio: {str(e)}")
            return 0.0 