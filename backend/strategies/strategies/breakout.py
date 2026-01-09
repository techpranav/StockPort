"""
Breakout Strategy

Trades breakouts above resistance with volume confirmation.
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


class BreakoutStrategy(BaseStrategy):
    """
    Breakout strategy.
    
    Entry conditions:
    - Price breaks above resistance with volume confirmation
    - ATR expansion (volatility increase)
    - Strong momentum indicators
    - Support/resistance breakout confirmation
    
    Exit conditions:
    - Stop-loss below breakout level
    - Take-profit at next resistance
    """
    
    def __init__(self, strategy_id: str, name: str, config: Dict[str, Any]):
        """
        Initialize breakout strategy.
        
        Args:
            strategy_id: Strategy identifier
            name: Strategy name
            config: Strategy configuration dictionary
        """
        super().__init__(strategy_id, name, "breakout")
        self.config = config
        self.entry_config = config.get('strategy', {}).get('entry', {})
        self.exit_config = config.get('strategy', {}).get('exit', {})
        self.min_confirmations = self.entry_config.get('min_confirmations', 3)
        self.min_score = self.entry_config.get('min_score', 70)
        self.min_volume_spike = self.entry_config.get('min_volume_spike', 1.5)  # 50% above average
        self.min_resistance_strength = self.entry_config.get('min_resistance_strength', 50.0)
        
        # Breakout works best in trending markets
        self.market_regimes = ['trending_up', 'bullish', 'uptrend']
        
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
        Evaluate opportunity against breakout strategy.
        
        Args:
            opportunity: Opportunity to evaluate
            market_state: Current market state (optional)
            historical_data: Historical price data (optional)
            
        Returns:
            StrategySignal if opportunity matches, None otherwise
        """
        # Check if strategy is applicable to current regime
        if market_state:
            regime = market_state.get('regime', '')
            if not self.is_applicable(regime):
                return None
        
        # Need historical data for support/resistance
        if historical_data is None:
            DebugUtils.debug(f"No historical data provided for {opportunity.symbol}, skipping breakout strategy")
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
            
            current_price = opportunity.price
            indicators = opportunity.indicators
            
            # Check if price broke above resistance
            near_resistance = validated_levels.get('near_resistance')
            valid_resistance = validated_levels.get('valid_resistance', [])
            
            # Find resistance level that was broken
            broken_resistance = None
            for resistance in valid_resistance:
                resistance_level = resistance.get('level', 0)
                if current_price > resistance_level * 1.01:  # 1% above resistance = breakout
                    if broken_resistance is None or resistance_level > broken_resistance.get('level', 0):
                        broken_resistance = resistance
            
            if not broken_resistance:
                return None
            
            # Build conditions
            conditions = []
            total_score = 0.0
            
            # Resistance breakout condition
            breakout_score = 40.0
            conditions.append(StrategyCondition(
                type="support_resistance",
                name="resistance_breakout",
                operator="above",
                value=broken_resistance.get('level', 0),
                weight=0.4,
                met=True,
                score=breakout_score
            ))
            total_score += breakout_score
            
            # Volume spike confirmation
            volume_ratio = indicators.get('volume_ratio', 1.0)
            if volume_ratio >= self.min_volume_spike:
                volume_score = 30.0
                conditions.append(StrategyCondition(
                    type="indicator",
                    name="volume",
                    operator="above",
                    value=self.min_volume_spike,
                    weight=0.3,
                    met=True,
                    score=volume_score
                ))
                total_score += volume_score
            
            # ATR expansion (volatility increase)
            atr = indicators.get('atr', current_price * 0.02)
            atr_pct = (atr / current_price) * 100 if current_price > 0 else 2.0
            
            # Check if ATR is expanding (would need historical ATR, simplified here)
            if atr_pct > 2.0:  # Higher volatility
                atr_score = 15.0
                conditions.append(StrategyCondition(
                    type="indicator",
                    name="atr",
                    operator="above",
                    value=2.0,
                    weight=0.15,
                    met=True,
                    score=atr_score
                ))
                total_score += atr_score
            
            # Momentum confirmation (RSI, MACD)
            rsi = indicators.get('rsi', 50)
            if 50 <= rsi <= 70:  # Strong but not overbought
                rsi_score = 15.0
                conditions.append(StrategyCondition(
                    type="indicator",
                    name="rsi",
                    operator="between",
                    value=[50, 70],
                    weight=0.15,
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
            
            # Entry price: current price (breakout entry)
            entry_price = current_price
            
            # Stop-loss: below broken resistance level (1% below)
            resistance_level = broken_resistance.get('level', entry_price * 0.98)
            stop_loss = resistance_level * 0.99
            
            # Take-profit: at next resistance or 5% above entry
            if near_resistance and near_resistance.get('level', 0) > entry_price:
                take_profit = near_resistance.get('level', entry_price * 1.05)
            elif valid_resistance:
                # Find next resistance above entry
                next_resistance = None
                for resistance in valid_resistance:
                    res_level = resistance.get('level', 0)
                    if res_level > entry_price:
                        if next_resistance is None or res_level < next_resistance:
                            next_resistance = res_level
                take_profit = next_resistance if next_resistance else entry_price * 1.05
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
            DebugUtils.log_error(e, f"Error evaluating breakout strategy for {opportunity.symbol}")
            return None
    
    def get_entry_conditions(self) -> List[Dict[str, Any]]:
        """Get entry conditions."""
        return self.entry_config.get('conditions', [
            {
                'type': 'support_resistance',
                'name': 'resistance_breakout',
                'operator': 'above',
                'min_strength': self.min_resistance_strength
            },
            {
                'type': 'indicator',
                'name': 'volume',
                'operator': 'above',
                'value': self.min_volume_spike
            },
            {
                'type': 'indicator',
                'name': 'atr',
                'operator': 'above',
                'value': 2.0
            }
        ])
    
    def get_exit_conditions(self) -> Dict[str, Any]:
        """Get exit conditions."""
        return self.exit_config or {
            'take_profit': 'next_resistance',
            'stop_loss': 'below_breakout_level',
            'trailing_stop': False
        }

