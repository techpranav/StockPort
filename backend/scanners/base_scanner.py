"""
Base Scanner

Abstract base class for all scanners.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.opportunity import Opportunity
from backend.data.integrity.truth_layer import TruthLayer


class BaseScanner(ABC):
    """
    Abstract base class for scanners.
    
    All scanners must implement:
    - scan(): Scan for opportunities
    """
    
    def __init__(self, truth_layer: Optional[TruthLayer] = None):
        """
        Initialize scanner.
        
        Args:
            truth_layer: Truth layer for data validation
        """
        self.truth_layer = truth_layer
        self.is_running = False
    
    @abstractmethod
    def scan(self, symbols: Optional[List[str]] = None) -> List[Opportunity]:
        """
        Scan for opportunities.
        
        Args:
            symbols: List of symbols to scan (None = scan all)
            
        Returns:
            List of opportunities
        """
        pass
    
    def start(self):
        """Start scanner."""
        self.is_running = True
    
    def stop(self):
        """Stop scanner."""
        self.is_running = False
    
    def is_data_valid(self, symbol: str) -> bool:
        """
        Check if data is valid for symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            True if valid, False otherwise
        """
        if self.truth_layer:
            return self.truth_layer.is_data_valid(symbol)
        return True  # Assume valid if no truth layer

