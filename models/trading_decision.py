"""
Trading Decision Model

Represents a decision made by the decision engine.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

from models.strategy_signal import StrategySignal


@dataclass
class TradingDecision:
    """
    Represents a trading decision.
    
    Attributes:
        decision_id: Unique decision identifier
        decision: Decision type (APPROVE, REJECT, MODIFY)
        symbol: Stock symbol
        strategy_id: Strategy that generated the signal
        signal: The strategy signal
        risk_amount: Dollar amount at risk
        risk_percent: Percentage of capital at risk
        reward_amount: Potential reward amount
        risk_reward_ratio: Risk-reward ratio
        position_size: Recommended position size
        reasoning: Human-readable reasoning
        timestamp: When decision was made
    """
    decision_id: str
    decision: str  # "APPROVE", "REJECT", "MODIFY"
    symbol: str
    strategy_id: str
    signal: StrategySignal
    risk_amount: float
    risk_percent: float
    reward_amount: float
    risk_reward_ratio: float
    position_size: Dict[str, float]
    reasoning: str
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'decision_id': self.decision_id,
            'decision': self.decision,
            'symbol': self.symbol,
            'strategy_id': self.strategy_id,
            'signal': self.signal.to_dict(),
            'risk_amount': self.risk_amount,
            'risk_percent': self.risk_percent,
            'reward_amount': self.reward_amount,
            'risk_reward_ratio': self.risk_reward_ratio,
            'position_size': self.position_size,
            'reasoning': self.reasoning,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

