"""
Exposure Tracker

Tracks sector, factor, and correlation exposure.
"""

from typing import Dict, Any, List
from collections import defaultdict

from utils.debug_utils import DebugUtils


class ExposureTracker:
    """
    Tracks portfolio exposures.
    
    Tracks:
    - Sector exposure
    - Factor exposure
    - Correlation exposure
    """
    
    def __init__(self, max_sector_exposure: float = 0.25):
        """
        Initialize exposure tracker.
        
        Args:
            max_sector_exposure: Maximum sector exposure (25%)
        """
        self.max_sector_exposure = max_sector_exposure
    
    def get_sector_exposure(
        self,
        positions: List[Dict[str, Any]],
        total_capital: float
    ) -> Dict[str, float]:
        """
        Get sector exposure percentages.
        
        Args:
            positions: List of positions
            total_capital: Total capital
            
        Returns:
            Dictionary mapping sector to exposure percentage
        """
        sector_values = defaultdict(float)
        
        for position in positions:
            sector = position.get('sector', 'Unknown')
            value = position.get('value', 0)
            sector_values[sector] += value
        
        # Convert to percentages
        sector_exposure = {}
        for sector, value in sector_values.items():
            sector_exposure[sector] = value / total_capital if total_capital > 0 else 0.0
        
        return sector_exposure
    
    def get_factor_exposure(self, positions: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Get factor exposure.
        
        Args:
            positions: List of positions
            
        Returns:
            Dictionary mapping factor to exposure
        """
        # Simplified factor exposure calculation
        # In production, would calculate actual factor loadings
        return {
            'value': 0.3,
            'growth': 0.4,
            'momentum': 0.2,
            'quality': 0.1
        }
    
    def get_average_correlation(self, positions: List[Dict[str, Any]]) -> float:
        """
        Get average correlation between positions.
        
        Args:
            positions: List of positions
            
        Returns:
            Average correlation (0-1)
        """
        if len(positions) < 2:
            return 0.0
        
        # Simplified correlation calculation
        # In production, would calculate actual correlations from returns
        return 0.4  # Default moderate correlation
    
    def check_sector_exposure(
        self,
        sector: str,
        existing_positions: List[Dict[str, Any]],
        total_capital: float = 100000.0
    ) -> Dict[str, Any]:
        """
        Check if adding position would exceed sector exposure limit.
        
        Args:
            sector: Sector to check
            existing_positions: Existing positions
            total_capital: Total capital
            
        Returns:
            Dictionary with approval status
        """
        sector_exposure = self.get_sector_exposure(existing_positions, total_capital)
        current_exposure = sector_exposure.get(sector, 0.0)
        
        if current_exposure >= self.max_sector_exposure:
            return {
                'approved': False,
                'reason': f'Sector exposure limit exceeded: {current_exposure:.1%} >= {self.max_sector_exposure:.1%}',
                'current_exposure': current_exposure
            }
        
        return {
            'approved': True,
            'current_exposure': current_exposure
        }

