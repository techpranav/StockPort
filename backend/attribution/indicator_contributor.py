"""
Indicator Contributor

Calculates indicator contributions to signals.
"""

from typing import Dict, Any


class IndicatorContributor:
    """
    Calculates how much each indicator contributed to a signal.
    """
    
    def calculate_contributions(self, trade: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate indicator contributions.
        
        Args:
            trade: Trade dictionary
            
        Returns:
            Dictionary mapping indicator to contribution percentage
        """
        signal = trade.get('signal', {})
        conditions = signal.get('conditions', [])
        
        contributions = {}
        total_score = 0.0
        
        for condition in conditions:
            indicator_name = condition.get('name', 'unknown')
            condition_score = condition.get('score', 0) * condition.get('weight', 1.0)
            contributions[indicator_name] = condition_score
            total_score += condition_score
        
        # Normalize to percentages
        if total_score > 0:
            for indicator in contributions:
                contributions[indicator] = (contributions[indicator] / total_score) * 100
        
        return contributions

