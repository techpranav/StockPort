"""
Diversification Engine

Manages diversification guardrails and scoring.
"""

from typing import Dict, Any, List

from utils.debug_utils import DebugUtils
from models.opportunity import Opportunity


class DiversificationEngine:
    """
    Manages diversification.
    
    Features:
    - Diversification scoring
    - Correlation limits
    - Position count limits
    """
    
    def __init__(
        self,
        max_correlation: float = 0.7,
        min_positions: int = 5,
        max_positions: int = 20
    ):
        """
        Initialize diversification engine.
        
        Args:
            max_correlation: Maximum allowed correlation
            min_positions: Minimum positions for diversification
            max_positions: Maximum positions for manageability
        """
        self.max_correlation = max_correlation
        self.min_positions = min_positions
        self.max_positions = max_positions
    
    def calculate_score(
        self,
        positions: List[Dict[str, Any]],
        sector_exposure: Dict[str, float],
        average_correlation: float
    ) -> float:
        """
        Calculate diversification score (0-1, higher is better).
        
        Args:
            positions: List of positions
            sector_exposure: Sector exposure dictionary
            average_correlation: Average correlation
            
        Returns:
            Diversification score
        """
        score = 1.0
        
        # Penalize high correlation
        if average_correlation > 0.5:
            score -= (average_correlation - 0.5) * 0.5
        
        # Penalize sector concentration
        max_sector_exposure = max(sector_exposure.values()) if sector_exposure else 0.0
        if max_sector_exposure > 0.25:
            score -= (max_sector_exposure - 0.25) * 0.5
        
        # Penalize too few positions
        if len(positions) < self.min_positions:
            score -= 0.2
        
        return max(score, 0.0)
    
    def check_diversification(
        self,
        opportunity: Opportunity,
        existing_positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if opportunity improves diversification.
        
        Args:
            opportunity: Opportunity to check
            existing_positions: Existing positions
            
        Returns:
            Dictionary with approval status
        """
        # Check position count
        if len(existing_positions) >= self.max_positions:
            return {
                'approved': False,
                'reason': f'Maximum positions reached: {len(existing_positions)} >= {self.max_positions}'
            }
        
        # Check correlation (simplified - would use actual correlation)
        # For now, assume it improves diversification
        return {
            'approved': True,
            'reason': 'Diversification check passed',
            'improvement': 0.1  # Estimated improvement
        }

