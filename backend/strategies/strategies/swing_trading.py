"""
Swing Trading Strategy

Multi-timeframe trend following with 3-10 day holding periods.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from backend.strategies.base_strategy import BaseStrategy
from models.opportunity import Opportunity
from models.strategy_signal import StrategySignal, StrategyCondition
from utils.debug_utils import DebugUtils


class SwingTradingStrategy(BaseStrategy):
    """
    Swing trading strategy.
    
    Entry conditions:
    - Multi-timeframe alignment (daily + weekly trend)
    - EMA crossovers
    - MACD bullish
    - Support/resistance levels
    - Volume confirmation
    
    Exit conditions:
    - Swing high/low
    - Trailing stop
    - Holding period: 3-10 days
    """
    
    def __init__(self, strategy_id: str, name: str, config: Dict[str, Any]):
        """
        Initialize swing trading strategy.
        
        Args:
            strategy_id: Strategy identifier
            name: Strategy name
            config: Strategy configuration dictionary
        """
        super().__init__(strategy_id, name, "swing_trading")
        self.config = config
        self.entry_config = config.get('strategy', {}).get('entry', {})
        self.exit_config = config.get('strategy', {}).get('exit', {})
        self.min_confirmations = self.entry_config.get('min_confirmations', 4)
        self.min_score = self.entry_config.get('min_score', 75)
        self.holding_period_days = self.entry_config.get('holding_period_days', [3, 10])
        
        # Swing trading works in trending markets
        self.market_regimes = ['trending_up', 'trending_down', 'bullish', 'bearish']
    
    def evaluate(
        self,
        opportunity: Opportunity,
        market_state: Optional[Dict[str, Any]] = None
    ) -> Optional[StrategySignal]:
        """
        Evaluate opportunity against swing trading strategy.
        
        Args:
            opportunity: Opportunity to evaluate
            market_state: Current market state (optional)
            
        Returns:
            StrategySignal if opportunity matches, None otherwise
        """
        # Check if strategy is applicable to current regime
        if market_state:
            regime = market_state.get('regime', '')
            if not self.is_applicable(regime):
                return None
        
        conditions = []
        total_score = 0.0
        
        indicators = opportunity.indicators
        current_price = opportunity.price
        
        # Check EMA alignment (EMA20 > EMA50 > EMA200 for uptrend)
        ema_20 = indicators.get('ema_20', current_price)
        ema_50 = indicators.get('ema_50', current_price)
        sma_200 = indicators.get('sma_200', current_price)
        
        if ema_20 > ema_50 and ema_50 > sma_200 and sma_200 > 0:
            score = 30.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="ema_alignment",
                operator="above",
                value="ema_50",
                weight=0.3,
                met=True,
                score=score
            ))
            total_score += score
        
        # Check MACD bullish
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        if macd > macd_signal:
            score = 25.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="macd",
                operator="cross_above",
                value="signal_line",
                weight=0.25,
                met=True,
                score=score
            ))
            total_score += score
        
        # Check RSI (momentum without overbought)
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
        
        # Volume confirmation
        volume_ratio = indicators.get('volume_ratio', 1.0)
        if volume_ratio > 1.1:  # Above average volume
            score = 15.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="volume",
                operator="above",
                value=1.1,
                weight=0.15,
                met=True,
                score=score
            ))
            total_score += score
        
        # Support/resistance context (if available in indicators)
        support_level = indicators.get('nearest_support', 0)
        if support_level > 0 and current_price > support_level * 1.02:
            # Price is above support (good for swing trade)
            score = 10.0
            conditions.append(StrategyCondition(
                type="support_resistance",
                name="above_support",
                operator="above",
                value=support_level,
                weight=0.1,
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
        
        # Entry price: current price
        entry_price = current_price
        
        # Stop-loss: below EMA20 or 3% below entry
        if ema_20 > 0:
            stop_loss = min(ema_20 * 0.98, entry_price * 0.97)
        else:
            stop_loss = entry_price * 0.97
        
        # Take-profit: 5-8% above entry (swing target)
        take_profit = entry_price * 1.06  # 6% target
        
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
        return self.entry_config.get('conditions', [
            {
                'type': 'indicator',
                'name': 'ema_alignment',
                'operator': 'above',
                'value': 'ema_50'
            },
            {
                'type': 'indicator',
                'name': 'macd',
                'operator': 'cross_above',
                'value': 'signal_line'
            },
            {
                'type': 'indicator',
                'name': 'rsi',
                'operator': 'between',
                'value': [40, 70]
            },
            {
                'type': 'indicator',
                'name': 'volume',
                'operator': 'above',
                'value': 1.1
            }
        ])
    
    def get_exit_conditions(self) -> Dict[str, Any]:
        """Get exit conditions."""
        return self.exit_config or {
            'take_profit': 'percentage',
            'take_profit_pct': 6.0,
            'stop_loss': 'below_ema20',
            'trailing_stop': True,
            'holding_period_days': self.holding_period_days
        }

