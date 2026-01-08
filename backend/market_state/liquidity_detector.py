"""
Liquidity Detector

Detects liquidity conditions.
"""

from typing import Dict, Any


class LiquidityDetector:
    """
    Detects liquidity state.
    
    States:
    - high: High volume, tight spreads
    - normal: Average volume and spreads
    - low: Low volume, wide spreads
    """
    
    def detect_liquidity(self, market_data: Dict[str, Any]) -> str:
        """
        Detect liquidity state.
        
        Args:
            market_data: Dictionary with market data
            
        Returns:
            Liquidity state string
        """
        volume_ratio = market_data.get('volume_ratio', 1.0)  # Current vs average
        spread = market_data.get('spread', 0.001)  # Bid-ask spread
        
        if volume_ratio > 1.2 and spread < 0.001:
            return "high"
        elif volume_ratio < 0.8 or spread > 0.005:
            return "low"
        else:
            return "normal"

