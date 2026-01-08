"""
Regime Detector

Detects market regimes (trending, choppy, volatile).
"""

from typing import Dict, Any
import pandas as pd

from utils.debug_utils import DebugUtils


class RegimeDetector:
    """
    Detects market regimes.
    
    Regimes:
    - trending_up: Strong upward trend
    - trending_down: Strong downward trend
    - choppy: Sideways, no clear direction
    - high_volatility: High volatility environment
    - low_volatility: Low volatility environment
    """
    
    def detect_regime(self, market_data: Dict[str, Any]) -> str:
        """
        Detect current market regime.
        
        Args:
            market_data: Dictionary with market data
            
        Returns:
            Regime string
        """
        # Get VIX level
        vix = market_data.get('vix', 20.0)
        
        # Get SPY trend
        spy_data = market_data.get('spy_data')
        if spy_data is not None and isinstance(spy_data, pd.DataFrame):
            if 'Close' in spy_data.columns and len(spy_data) >= 50:
                # Calculate trend (SMA20 vs SMA50)
                sma20 = spy_data['Close'].rolling(20).mean().iloc[-1]
                sma50 = spy_data['Close'].rolling(50).mean().iloc[-1]
                trend = (sma20 - sma50) / sma50 if sma50 > 0 else 0
            else:
                trend = market_data.get('spy_change', 0)
        else:
            trend = market_data.get('spy_change', 0)
        
        # Calculate ATR if available
        atr = market_data.get('atr', 0.02)  # Default 2%
        
        # Determine regime
        if vix > 25 or atr > 0.05:
            return "high_volatility"
        elif vix < 15 and atr < 0.01:
            return "low_volatility"
        elif trend > 0.02:  # 2% uptrend
            return "trending_up"
        elif trend < -0.02:  # 2% downtrend
            return "trending_down"
        elif abs(trend) < 0.005:  # Less than 0.5% movement
            return "choppy"
        else:
            return "normal"

