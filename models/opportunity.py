"""
Opportunity Model

Represents a trading opportunity detected by scanners.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class Opportunity:
    """
    Represents a trading opportunity.
    
    Attributes:
        symbol: Stock symbol
        timestamp: When opportunity was detected
        price: Current price
        volume: Trading volume
        market_cap: Market capitalization
        sector: GICS sector
        indicators: Dictionary of indicator values
        pre_filter_score: Pre-filter quality score (0-100)
        source: Which scanner found this opportunity
    """
    symbol: str
    timestamp: datetime
    price: float
    volume: float
    market_cap: float
    sector: str
    indicators: Dict[str, float]
    pre_filter_score: float
    source: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'price': self.price,
            'volume': self.volume,
            'market_cap': self.market_cap,
            'sector': self.sector,
            'indicators': self.indicators,
            'pre_filter_score': self.pre_filter_score,
            'source': self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Opportunity':
        """Create from dictionary."""
        return cls(
            symbol=data['symbol'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            price=data['price'],
            volume=data['volume'],
            market_cap=data['market_cap'],
            sector=data['sector'],
            indicators=data['indicators'],
            pre_filter_score=data['pre_filter_score'],
            source=data['source']
        )

