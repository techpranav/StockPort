"""
Trend Following Strategy

Follows strong trends with momentum confirmation.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from backend.strategies.base_strategy import BaseStrategy
from models.opportunity import Opportunity
from models.strategy_signal import StrategySignal, StrategyCondition
from utils.debug_utils import DebugUtils


class TrendFollowingStrategy(BaseStrategy):
    """
    Trend following strategy.
    
    Entry conditions:
    - SMA20 > SMA50 (uptrend)
    - RSI between 40-70 (momentum without overbought)
    - MACD bullish crossover
    - Optional: Bullish pattern
    """
    
    def __init__(self, strategy_id: str, name: str, config: Dict[str, Any]):
        """
        Initialize trend following strategy.
        
        Args:
            strategy_id: Strategy identifier
            name: Strategy name
            config: Strategy configuration dictionary
        """
        super().__init__(strategy_id, name, "trend_following")
        self.config = config
        self.entry_config = config['strategy']['entry']
        self.exit_config = config['strategy']['exit']
        self.min_confirmations = self.entry_config.get('min_confirmations', 3)
        self.min_score = self.entry_config.get('min_score', 70)
    
    def evaluate(
        self,
        opportunity: Opportunity,
        market_state: Optional[Dict[str, Any]] = None
    ) -> Optional[StrategySignal]:
        """
        Evaluate opportunity against trend following strategy.
        
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
        
        # Check SMA20 > SMA50
        sma20 = indicators.get('sma_20', 0)
        sma50 = indicators.get('sma_50', 0)
        if sma20 > sma50 and sma50 > 0:
            score = 30.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="sma_20",
                operator="above",
                value="sma_50",
                weight=0.3,
                met=True,
                score=score
            ))
            total_score += score
        
        # Check RSI
        rsi = indicators.get('rsi', 50)
        if 40 <= rsi <= 70:
            score = 20.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="rsi",
                operator="between",
                value=[40, 70],
                weight=0.2,
                met=True,
                score=score
            ))
            total_score += score
        
        # Check MACD
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        if macd > macd_signal:
            score = 30.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="macd",
                operator="cross_above",
                value="signal_line",
                weight=0.3,
                met=True,
                score=score
            ))
            total_score += score
        
        # Check for bullish pattern
        pattern = indicators.get('pattern', '')
        if 'bullish' in pattern.lower() or 'engulfing' in pattern.lower():
            score = 20.0
            conditions.append(StrategyCondition(
                type="pattern",
                name="bullish_pattern",
                operator="detected",
                value=pattern,
                weight=0.2,
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
        
        # Calculate stop loss and take profit from ATR
        atr = indicators.get('atr', opportunity.price * 0.02)
        stop_loss = entry_price - (atr * 2.0)
        take_profit = entry_price + (atr * 3.0)
        
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

