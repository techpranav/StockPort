"""
Volatility Detector

Detects volatility state using VIX and ATR.
"""

from typing import Dict, Any


class VolatilityDetector:
    """
    Detects volatility state.
    
    States:
    - low: VIX < 15, ATR < 1%
    - normal: VIX 15-25, ATR 1-3%
    - high: VIX 25-35, ATR 3-5%
    - extreme: VIX > 35, ATR > 5%
    """
    
    def detect_volatility(self, market_data: Dict[str, Any]) -> str:
        """
        Detect volatility state.
        
        Args:
            market_data: Dictionary with market data
            
        Returns:
            Volatility state string
        """
        vix = market_data.get('vix', 20.0)
        atr = market_data.get('atr', 0.02)  # Default 2%
        
        if vix > 35 or atr > 0.05:
            return "extreme"
        elif vix > 25 or atr > 0.03:
            return "high"
        elif vix < 15 and atr < 0.01:
            return "low"
        else:
            return "normal"

