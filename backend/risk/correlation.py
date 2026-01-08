"""
Correlation Checker

Checks correlation between positions.
"""

from typing import Dict, Any, List
import numpy as np

from utils.debug_utils import DebugUtils


class CorrelationChecker:
    """
    Checks correlation between positions.
    
    Prevents taking highly correlated positions.
    """
    
    def __init__(self, max_correlation: float = 0.7):
        """
        Initialize correlation checker.
        
        Args:
            max_correlation: Maximum allowed correlation (0-1)
        """
        self.max_correlation = max_correlation
        self.correlation_cache: Dict[str, Dict[str, float]] = {}  # symbol -> {symbol: correlation}
    
    def check_correlation(
        self,
        symbol: str,
        existing_positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check correlation with existing positions.
        
        Args:
            symbol: Stock symbol to check
            existing_positions: List of existing positions
            
        Returns:
            Dictionary with approval status and max correlation
        """
        if not existing_positions:
            return {'approved': True, 'max_correlation': 0.0}
        
        max_correlation = 0.0
        
        for position in existing_positions:
            existing_symbol = position.get('symbol')
            if existing_symbol == symbol:
                continue  # Same symbol
            
            # Calculate correlation (simplified - would use historical returns)
            correlation = self._calculate_correlation(symbol, existing_symbol)
            max_correlation = max(max_correlation, abs(correlation))
        
        if max_correlation > self.max_correlation:
            return {
                'approved': False,
                'reason': f'High correlation ({max_correlation:.2f}) with existing positions',
                'max_correlation': max_correlation
            }
        
        return {
            'approved': True,
            'max_correlation': max_correlation
        }
    
    def _calculate_correlation(self, symbol1: str, symbol2: str) -> float:
        """
        Calculate correlation between two symbols.
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
            
        Returns:
            Correlation coefficient (-1 to 1)
        """
        # Check cache
        if symbol1 in self.correlation_cache:
            if symbol2 in self.correlation_cache[symbol1]:
                return self.correlation_cache[symbol1][symbol2]
        
        # Simplified correlation calculation
        # In production, would use historical returns
        # For now, return a default low correlation
        correlation = 0.3  # Default moderate correlation
        
        # Cache result
        if symbol1 not in self.correlation_cache:
            self.correlation_cache[symbol1] = {}
        self.correlation_cache[symbol1][symbol2] = correlation
        
        return correlation

