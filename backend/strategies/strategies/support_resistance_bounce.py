"""
Support/Resistance Bounce Strategy

Trades bounces off strong support levels with confirmation.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from backend.strategies.base_strategy import BaseStrategy
from models.opportunity import Opportunity
from models.strategy_signal import StrategySignal, StrategyCondition
from services.analyzers.indicators.support_resistance import SupportResistanceCalculator
from services.analyzers.indicators.support_resistance_validator import SupportResistanceValidator
from services.data_providers.adapters.adapter_factory import AdapterFactory
from config.constants.DataConstants import DEFAULT_PROVIDER
from utils.debug_utils import DebugUtils


class SupportResistanceBounceStrategy(BaseStrategy):
    """
    Support/Resistance Bounce strategy.
    
    Entry conditions:
    - Price is near a strong support level
    - Support level is valid (not broken)
    - High bounce probability (>60%)
    - Volume confirmation
    - Bullish candlestick pattern (optional but preferred)
    
    Exit conditions:
    - Target next resistance level
    - Stop-loss below support level
    """
    
    def __init__(self, strategy_id: str, name: str, config: Dict[str, Any]):
        """
        Initialize support/resistance bounce strategy.
        
        Args:
            strategy_id: Strategy identifier
            name: Strategy name
            config: Strategy configuration dictionary
        """
        super().__init__(strategy_id, name, "support_resistance_bounce")
        self.config = config
        self.entry_config = config.get('strategy', {}).get('entry', {})
        self.exit_config = config.get('strategy', {}).get('exit', {})
        self.min_confirmations = self.entry_config.get('min_confirmations', 3)
        self.min_score = self.entry_config.get('min_score', 65)
        self.min_support_strength = self.entry_config.get('min_support_strength', 60.0)
        self.min_bounce_probability = self.entry_config.get('min_bounce_probability', 0.6)
        
        # Initialize support/resistance calculator
        provider_name = config.get('provider_name', DEFAULT_PROVIDER)
        self.support_resistance_calc = SupportResistanceCalculator(provider_name)
        self.support_resistance_validator = SupportResistanceValidator(provider_name)
        self.adapter = AdapterFactory.get_adapter(provider_name)
    
    def evaluate(
        self,
        opportunity: Opportunity,
        market_state: Optional[Dict[str, Any]] = None,
        historical_data: Optional[Any] = None  # pd.DataFrame if available
    ) -> Optional[StrategySignal]:
        """
        Evaluate opportunity against support/resistance bounce strategy.
        
        Args:
            opportunity: Opportunity to evaluate
            market_state: Current market state (optional)
            historical_data: Historical price data (optional, for support/resistance calculation)
            
        Returns:
            StrategySignal if opportunity matches, None otherwise
        """
        # Check if strategy is applicable to current regime
        if market_state:
            regime = market_state.get('regime', '')
            if not self.is_applicable(regime):
                return None
        
        # Need historical data for support/resistance calculation
        if historical_data is None:
            DebugUtils.debug(f"No historical data provided for {opportunity.symbol}, skipping S/R bounce strategy")
            return None
        
        try:
            # Calculate support/resistance levels
            support_resistance = self.support_resistance_calc.get_current_support_resistance(
                historical_data,
                include_pivot_points=True,
                include_volume_profile=True,
                include_dynamic=True
            )
            
            # Validate levels
            validated_levels = self.support_resistance_validator.validate_levels(
                support_resistance.get('support_levels', []),
                support_resistance.get('resistance_levels', []),
                historical_data
            )
            
            # Check if price is near support
            near_support = validated_levels.get('near_support')
            if not near_support:
                return None
            
            # Check support strength
            support_strength = near_support.get('strength', 0)
            if support_strength < self.min_support_strength:
                return None
            
            # Check bounce probability
            bounce_prob = near_support.get('bounce_probability', 0)
            if bounce_prob < self.min_bounce_probability:
                return None
            
            # Build conditions
            conditions = []
            total_score = 0.0
            
            # Support level condition
            support_score = min(40, support_strength * 0.4)
            conditions.append(StrategyCondition(
                type="support_resistance",
                name="near_strong_support",
                operator="near",
                value=near_support.get('level', 0),
                weight=0.4,
                met=True,
                score=support_score
            ))
            total_score += support_score
            
            # Bounce probability condition
            bounce_score = min(30, bounce_prob * 30)
            conditions.append(StrategyCondition(
                type="support_resistance",
                name="high_bounce_probability",
                operator="above",
                value=self.min_bounce_probability,
                weight=0.3,
                met=True,
                score=bounce_score
            ))
            total_score += bounce_score
            
            # Volume confirmation
            indicators = opportunity.indicators
            volume_ratio = indicators.get('volume_ratio', 1.0)
            if volume_ratio > 1.2:  # 20% above average
                volume_score = 20.0
                conditions.append(StrategyCondition(
                    type="indicator",
                    name="volume",
                    operator="above",
                    value=1.2,
                    weight=0.2,
                    met=True,
                    score=volume_score
                ))
                total_score += volume_score
            
            # RSI confirmation (oversold is good for bounce)
            rsi = indicators.get('rsi', 50)
            if rsi < 40:  # Oversold
                rsi_score = 10.0
                conditions.append(StrategyCondition(
                    type="indicator",
                    name="rsi",
                    operator="below",
                    value=40,
                    weight=0.1,
                    met=True,
                    score=rsi_score
                ))
                total_score += rsi_score
            
            # Check if we have enough confirmations
            met_conditions = [c for c in conditions if c.met]
            if len(met_conditions) < self.min_confirmations:
                return None
            
            # Check if score meets minimum
            if total_score < self.min_score:
                return None
            
            # Calculate confidence
            confidence = min(total_score / 100.0, 1.0)
            
            # Entry price: slightly above support (0.5% buffer)
            support_level = near_support.get('level', opportunity.price)
            entry_price = support_level * 1.005
            
            # Stop-loss: below support (1% below)
            stop_loss = support_level * 0.99
            
            # Take-profit: at nearest resistance
            near_resistance = validated_levels.get('near_resistance')
            if near_resistance:
                take_profit = near_resistance.get('level', entry_price * 1.05)
            else:
                # Use strongest resistance or default 5% target
                valid_resistance = validated_levels.get('valid_resistance', [])
                if valid_resistance:
                    take_profit = valid_resistance[0].get('level', entry_price * 1.05)
                else:
                    take_profit = entry_price * 1.05  # Default 5% target
            
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
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error evaluating S/R bounce strategy for {opportunity.symbol}")
            return None
    
    def get_entry_conditions(self) -> List[Dict[str, Any]]:
        """Get entry conditions."""
        return self.entry_config.get('conditions', [
            {
                'type': 'support_resistance',
                'name': 'near_strong_support',
                'operator': 'near',
                'min_strength': self.min_support_strength
            },
            {
                'type': 'support_resistance',
                'name': 'high_bounce_probability',
                'operator': 'above',
                'value': self.min_bounce_probability
            },
            {
                'type': 'indicator',
                'name': 'volume',
                'operator': 'above',
                'value': 1.2
            }
        ])
    
    def get_exit_conditions(self) -> Dict[str, Any]:
        """Get exit conditions."""
        return self.exit_config or {
            'take_profit': 'nearest_resistance',
            'stop_loss': 'below_support',
            'trailing_stop': False
        }

