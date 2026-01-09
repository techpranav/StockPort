"""
Mean Reversion Strategy

Trades price deviations from mean in ranging markets.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from backend.strategies.base_strategy import BaseStrategy
from models.opportunity import Opportunity
from models.strategy_signal import StrategySignal, StrategyCondition
from utils.debug_utils import DebugUtils


class MeanReversionStrategy(BaseStrategy):
    """
    Mean reversion strategy.
    
    Entry conditions:
    - Price deviates significantly from mean (Bollinger Bands, Z-score)
    - RSI oversold/overbought
    - Low volatility (ranging market)
    - Volume confirmation
    
    Exit conditions:
    - Price returns to mean
    - Stop-loss if mean breaks
    """
    
    def __init__(self, strategy_id: str, name: str, config: Dict[str, Any]):
        """
        Initialize mean reversion strategy.
        
        Args:
            strategy_id: Strategy identifier
            name: Strategy name
            config: Strategy configuration dictionary
        """
        super().__init__(strategy_id, name, "mean_reversion")
        self.config = config
        self.entry_config = config.get('strategy', {}).get('entry', {})
        self.exit_config = config.get('strategy', {}).get('exit', {})
        self.min_confirmations = self.entry_config.get('min_confirmations', 3)
        self.min_score = self.entry_config.get('min_score', 65)
        self.z_score_threshold = self.entry_config.get('z_score_threshold', 2.0)
        self.rsi_oversold = self.entry_config.get('rsi_oversold', 30)
        self.rsi_overbought = self.entry_config.get('rsi_overbought', 70)
        
        # Mean reversion works best in ranging markets
        self.market_regimes = ['ranging', 'sideways', 'consolidation']
    
    def evaluate(
        self,
        opportunity: Opportunity,
        market_state: Optional[Dict[str, Any]] = None
    ) -> Optional[StrategySignal]:
        """
        Evaluate opportunity against mean reversion strategy.
        
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
        
        # Check Bollinger Bands position (Z-score)
        bb_upper = indicators.get('bb_upper', current_price * 1.02)
        bb_lower = indicators.get('bb_lower', current_price * 0.98)
        bb_middle = indicators.get('bb_middle', current_price)
        
        if bb_upper > bb_lower and bb_middle > 0:
            # Calculate Z-score (distance from mean in standard deviations)
            bb_width = bb_upper - bb_lower
            if bb_width > 0:
                z_score = (current_price - bb_middle) / (bb_width / 4)  # Approximate std dev
                
                # Look for oversold condition (price below lower band)
                if z_score < -self.z_score_threshold:
                    score = 40.0
                    conditions.append(StrategyCondition(
                        type="indicator",
                        name="bollinger_oversold",
                        operator="below",
                        value=bb_lower,
                        weight=0.4,
                        met=True,
                        score=score
                    ))
                    total_score += score
                # Look for overbought condition (price above upper band) - for shorting
                elif z_score > self.z_score_threshold:
                    # Mean reversion strategy can also short overbought conditions
                    # But for now, we focus on long entries (oversold)
                    pass
        
        # Check RSI
        rsi = indicators.get('rsi', 50)
        if rsi < self.rsi_oversold:  # Oversold
            score = 30.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="rsi",
                operator="below",
                value=self.rsi_oversold,
                weight=0.3,
                met=True,
                score=score
            ))
            total_score += score
        elif rsi > self.rsi_overbought:  # Overbought (for shorting, but we focus on longs)
            pass
        
        # Check volatility (ATR or Bollinger Band width)
        atr = indicators.get('atr', current_price * 0.02)
        atr_pct = (atr / current_price) * 100 if current_price > 0 else 2.0
        
        # Low volatility is good for mean reversion
        if atr_pct < 3.0:  # Low volatility
            score = 20.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="volatility",
                operator="below",
                value=3.0,
                weight=0.2,
                met=True,
                score=score
            ))
            total_score += score
        
        # Volume confirmation (not too high, not too low)
        volume_ratio = indicators.get('volume_ratio', 1.0)
        if 0.8 <= volume_ratio <= 1.5:  # Normal volume
            score = 10.0
            conditions.append(StrategyCondition(
                type="indicator",
                name="volume",
                operator="between",
                value=[0.8, 1.5],
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
        
        # Entry price: current price (mean reversion entry)
        entry_price = current_price
        
        # Stop-loss: below lower Bollinger Band or 2% below entry
        if 'bb_lower' in indicators:
            stop_loss = indicators['bb_lower'] * 0.99
        else:
            stop_loss = entry_price * 0.98
        
        # Take-profit: at middle Bollinger Band (mean) or 2% above entry
        if 'bb_middle' in indicators:
            take_profit = indicators['bb_middle']
        else:
            take_profit = entry_price * 1.02
        
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
                'name': 'bollinger_oversold',
                'operator': 'below',
                'value': 'bb_lower'
            },
            {
                'type': 'indicator',
                'name': 'rsi',
                'operator': 'below',
                'value': self.rsi_oversold
            },
            {
                'type': 'indicator',
                'name': 'volatility',
                'operator': 'below',
                'value': 3.0
            }
        ])
    
    def get_exit_conditions(self) -> Dict[str, Any]:
        """Get exit conditions."""
        return self.exit_config or {
            'take_profit': 'bb_middle',
            'stop_loss': 'below_bb_lower',
            'trailing_stop': False
        }

