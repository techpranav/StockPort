"""
Momentum Strategy

Captures strong price movements with momentum confirmation.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from backend.strategies.base_strategy import BaseStrategy
from models.opportunity import Opportunity
from models.strategy_signal import StrategySignal, StrategyCondition
from utils.debug_utils import DebugUtils


class MomentumStrategy(BaseStrategy):
    """
    Momentum strategy.
    
    Entry conditions:
    - Strong price momentum (ROC > threshold)
    - Volume confirmation
    - RSI in momentum zone
    """
    
    def __init__(self, strategy_id: str, name: str, config: Dict[str, Any]):
        """
        Initialize momentum strategy.
        
        Args:
            strategy_id: Strategy identifier
            name: Strategy name
            config: Strategy configuration dictionary
        """
        super().__init__(strategy_id, name, "momentum")
        self.config = config
        self.entry_config = config['strategy']['entry']
        self.exit_config = config['strategy']['exit']
        self.min_confirmations = self.entry_config.get('min_confirmations', 2)
        self.min_score = self.entry_config.get('min_score', 60)
    
    def evaluate(
        self,
        opportunity: Opportunity,
        market_state: Optional[Dict[str, Any]] = None
    ) -> Optional[StrategySignal]:
        """
        Evaluate opportunity against momentum strategy.
        
        Args:
            opportunity: Opportunity to evaluate
            market_state: Current market state (optional)
            
        Returns:
            StrategySignal if opportunity matches, None otherwise
        """
        # Check if strategy is applicable to current regime
        if market_state:
            regime = market_state.get('regime')
            if not self.is_applicable(regime):
                return None
        
        conditions = []
        total_score = 0.0
        
        indicators = opportunity.indicators
        
        # Check ROC (Rate of Change)
        roc = indicators.get('roc', 0)
        if roc > 0.05:  # 5% momentum
            score = 40.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="roc",
                operator="above",
                value=0.05,
                weight=0.4,
                met=True,
                score=score
            ))
            total_score += score
        
        # Check volume
        volume_ratio = indicators.get('volume_ratio', 1.0)
        if volume_ratio > 1.2:  # 20% above average
            score = 30.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="volume",
                operator="above",
                value=1.2,
                weight=0.3,
                met=True,
                score=score
            ))
            total_score += score
        
        # Check RSI
        rsi = indicators.get('rsi', 50)
        if 50 <= rsi <= 70:  # Momentum zone
            score = 30.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="rsi",
                operator="between",
                value=[50, 70],
                weight=0.3,
                met=True,
                score=score
            ))
            total_score += score
        
        # Check if we have enough confirmations
        met_conditions = [c for c in conditions if c.met]
        if len(met_conditions) < self.min_confirmations:
            return None
        
        # Check if score meets minimum
        if total_score < self.min_score:
            return None
        
        # Calculate confidence
        confidence = min(total_score / 100.0, 1.0)
        
        # Calculate entry price
        entry_price = opportunity.price
        
        # Calculate stop loss and take profit
        atr = indicators.get('atr', opportunity.price * 0.02)
        stop_loss = entry_price - (atr * 1.5)
        take_profit = entry_price + (atr * 2.5)
        
        signal_id = str(uuid.uuid4())
        
        return StrategySignal(
            signal_id=signal_id,
            strategy_id=self.strategy_id,
            opportunity=opportunity,
            score=total_score,
            confidence=confidence,
            conditions=conditions,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            timestamp=datetime.now()
        )
    
    def get_entry_conditions(self) -> List[Dict[str, Any]]:
        """Get entry conditions."""
        return self.entry_config.get('conditions', [])
    
    def get_exit_conditions(self) -> Dict[str, Any]:
        """Get exit conditions."""
        return self.exit_config

