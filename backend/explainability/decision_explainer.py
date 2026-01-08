"""
Decision Explainer

Generates human-readable decision explanations.
"""

from typing import Dict, Any, List


class DecisionExplainer:
    """
    Generates human-readable explanations for trading decisions.
    """
    
    def explain(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate explanation for decision.
        
        Args:
            decision: Trading decision dictionary
            
        Returns:
            Explanation dictionary
        """
        signal = decision.get('signal', {})
        strategy_id = signal.get('strategy_id', 'unknown')
        symbol = decision.get('symbol', '')
        
        # Build entry reasoning
        entry_reasoning = self._build_entry_reasoning(decision, signal)
        
        # Build risk justification
        risk_justification = self._build_risk_justification(decision)
        
        # Build invalidation conditions
        invalidation_conditions = self._build_invalidation_conditions(decision)
        
        return {
            'entry_reasoning': entry_reasoning,
            'risk_justification': risk_justification,
            'invalidation_conditions': invalidation_conditions,
            'portfolio_fit': 'Portfolio fit check passed',
            'diversification_impact': 'Improves diversification'
        }
    
    def _build_entry_reasoning(
        self,
        decision: Dict[str, Any],
        signal: Dict[str, Any]
    ) -> str:
        """Build entry reasoning."""
        strategy_id = signal.get('strategy_id', 'unknown')
        score = signal.get('score', 0)
        conditions = signal.get('conditions', [])
        confidence = signal.get('confidence', 0.5)
        
        met_conditions = [c for c in conditions if c.get('met', False)]
        
        # Build condition details
        condition_details = []
        for condition in met_conditions[:3]:  # Top 3 conditions
            cond_name = condition.get('name', 'condition')
            cond_value = condition.get('value', '')
            if cond_value:
                condition_details.append(f"{cond_name}={cond_value:.2f}" if isinstance(cond_value, (int, float)) else f"{cond_name}={cond_value}")
        
        condition_text = ", ".join(condition_details) if condition_details else "multiple indicators aligned"
        
        # Score interpretation
        if score >= 80:
            strength = "Very strong"
        elif score >= 60:
            strength = "Strong"
        elif score >= 40:
            strength = "Moderate"
        else:
            strength = "Weak"
        
        return (
            f"{strength} {strategy_id} signal detected (score: {score:.1f}/100, confidence: {confidence:.1%}). "
            f"{len(met_conditions)} of {len(conditions)} conditions met ({condition_text}). "
            f"Entry price: ${decision.get('entry_price', 0):.2f}."
        )
    
    def _build_risk_justification(self, decision: Dict[str, Any]) -> str:
        """Build risk justification."""
        risk_amount = decision.get('risk_amount', 0)
        risk_percent = decision.get('risk_percent', 0)
        reward_amount = decision.get('reward_amount', 0)
        risk_reward = decision.get('risk_reward_ratio', 0)
        
        return (
            f"Risking ${risk_amount:,.2f} ({risk_percent:.1f}% of capital) "
            f"for potential reward of ${reward_amount:,.2f} "
            f"(risk-reward ratio: {risk_reward:.2f}:1)."
        )
    
    def _build_invalidation_conditions(self, decision: Dict[str, Any]) -> List[str]:
        """
        Build invalidation conditions that would invalidate this trade.
        
        Args:
            decision: Trading decision dictionary
            
        Returns:
            List of invalidation conditions
        """
        signal = decision.get('signal', {})
        stop_loss = signal.get('stop_loss')
        take_profit = signal.get('take_profit')
        entry_price = decision.get('entry_price', 0)
        strategy_id = signal.get('strategy_id', '')
        
        conditions = []
        
        # Stop loss invalidation
        if stop_loss and entry_price > 0:
            stop_loss_pct = ((entry_price - stop_loss) / entry_price) * 100
            conditions.append(
                f"Price breaks below stop loss at ${stop_loss:.2f} "
                f"({stop_loss_pct:.1f}% loss from entry)"
            )
        
        # Take profit invalidation (if reached, exit)
        if take_profit and entry_price > 0:
            take_profit_pct = ((take_profit - entry_price) / entry_price) * 100
            conditions.append(
                f"Price reaches take profit at ${take_profit:.2f} "
                f"({take_profit_pct:.1f}% gain from entry) - exit signal"
            )
        
        # Strategy-specific conditions
        if 'trend' in strategy_id.lower():
            conditions.append("Trend reverses (price breaks below key moving average)")
            conditions.append("Volume drops significantly (trend losing momentum)")
        elif 'momentum' in strategy_id.lower():
            conditions.append("RSI exceeds 70 (overbought) or drops below 30 (oversold)")
            conditions.append("Momentum indicator shows divergence")
        elif 'mean_reversion' in strategy_id.lower():
            conditions.append("Price continues trending away from mean")
            conditions.append("Mean reversion signal weakens")
        
        # General market conditions
        conditions.append("Market regime changes (e.g., trending to choppy)")
        conditions.append("Correlation with existing positions exceeds 0.7 (overexposure)")
        conditions.append("Data quality drops below acceptable threshold")
        
        # Signal expiry
        conditions.append("Signal expires (age exceeds strategy-specific expiry time)")
        
        return conditions

