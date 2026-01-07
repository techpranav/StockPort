"""
Signal Models Module

This module defines data models for trading signals, pattern detections,
and risk metrics.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class EntrySignal:
    """
    Represents a trading entry signal.
    
    Attributes:
        symbol: Stock symbol
        signal_type: Signal type (STRONG_BUY, BUY, WATCH, AVOID)
        score: Signal score (0-100)
        confidence: Confidence level (0-1)
        entry_price: Recommended entry price
        stop_loss: Stop-loss price
        take_profit: Take-profit price
        timestamp: When signal was generated
        indicators: Dictionary of indicator values
        reasoning: Human-readable reasoning
    """
    symbol: str
    signal_type: str
    score: float
    confidence: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timestamp: Optional[datetime] = None
    indicators: Optional[Dict[str, float]] = None
    reasoning: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'score': self.score,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'indicators': self.indicators,
            'reasoning': self.reasoning
        }


@dataclass
class PatternDetection:
    """
    Represents a detected pattern.
    
    Attributes:
        pattern_type: Type of pattern (reversal, continuation, etc.)
        pattern_name: Name of the pattern
        strength: Pattern strength (0-100)
        reliability: Pattern reliability (0-1)
        detected_at: When pattern was detected
        price: Price at detection
        is_bullish: Whether pattern is bullish (True/False/None)
        target_price: Optional target price
    """
    pattern_type: str
    pattern_name: str
    strength: float
    reliability: float
    detected_at: datetime
    price: float
    is_bullish: Optional[bool] = None
    target_price: Optional[float] = None


@dataclass
class RiskMetrics:
    """
    Represents risk metrics for a position.
    
    Attributes:
        stop_loss: Stop-loss price
        take_profit: Take-profit price
        risk_amount: Dollar amount at risk
        reward_amount: Potential reward amount
        risk_reward_ratio: Risk-reward ratio
        position_size: Recommended position size (shares, dollar amount, percentage)
        max_drawdown: Maximum drawdown percentage
        volatility: Volatility percentage
    """
    stop_loss: float
    take_profit: float
    risk_amount: float
    reward_amount: float
    risk_reward_ratio: float
    position_size: Optional[Dict[str, float]] = None
    max_drawdown: Optional[float] = None
    volatility: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_amount': self.risk_amount,
            'reward_amount': self.reward_amount,
            'risk_reward_ratio': self.risk_reward_ratio,
            'position_size': self.position_size,
            'max_drawdown': self.max_drawdown,
            'volatility': self.volatility
        }

