"""
Breadth Detector

Detects market breadth using advance/decline ratio.
"""

from typing import Dict, Any


class BreadthDetector:
    """
    Detects market breadth.
    
    States:
    - bullish: Advance/decline ratio > 1.5
    - neutral: Advance/decline ratio 0.67-1.5
    - bearish: Advance/decline ratio < 0.67
    """
    
    def detect_breadth(self, market_data: Dict[str, Any]) -> str:
        """
        Detect breadth state.
        
        Args:
            market_data: Dictionary with market data
            
        Returns:
            Breadth state string
        """
        adv_dec_ratio = market_data.get('adv_dec_ratio', 1.0)
        
        if adv_dec_ratio > 1.5:
            return "bullish"
        elif adv_dec_ratio < 0.67:
            return "bearish"
        else:
            return "neutral"

