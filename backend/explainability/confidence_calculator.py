"""
Confidence Calculator

Calculates confidence scores for decisions.
"""

from typing import Dict, Any


class ConfidenceCalculator:
    """
    Calculates confidence scores for trading decisions.
    
    Factors:
    - Strategy score
    - Indicator confirmations
    - Pattern strength
    - Regime alignment
    - Data quality
    """
    
    def calculate(self, decision: Dict[str, Any]) -> float:
        """
        Calculate confidence score (0-1).
        
        Args:
            decision: Trading decision dictionary
            
        Returns:
            Confidence score
        """
        signal = decision.get('signal', {})
        score = signal.get('score', 0)
        conditions = signal.get('conditions', [])
        
        # Strategy score factor (0-0.3)
        strategy_factor = (score / 100) * 0.3
        
        # Indicator confirmations (0-0.2)
        met_conditions = [c for c in conditions if c.get('met', False)]
        confirmations_factor = min(len(met_conditions) / 5, 1.0) * 0.2
        
        # Pattern strength (0-0.2)
        patterns = [c for c in conditions if c.get('type') == 'pattern']
        pattern_factor = 0.1 if patterns else 0.0
        
        # Regime alignment (0-0.15)
        regime = decision.get('market_regime', 'unknown')
        strategy_regimes = signal.get('market_regimes', [])
        if regime in strategy_regimes:
            regime_factor = 0.15
        elif regime == 'unknown':
            regime_factor = 0.10  # Unknown regime = moderate confidence
        else:
            regime_factor = 0.05  # Mismatch = low confidence
        
        # Data quality (0-0.15)
        data_quality = decision.get('data_quality_score', 1.0)
        data_factor = data_quality * 0.15
        
        # Risk-reward factor (0-0.1)
        risk_reward = decision.get('risk_reward_ratio', 0)
        if risk_reward >= 2.0:
            risk_reward_factor = 0.1
        elif risk_reward >= 1.5:
            risk_reward_factor = 0.08
        elif risk_reward >= 1.0:
            risk_reward_factor = 0.05
        else:
            risk_reward_factor = 0.0
        
        confidence = (
            strategy_factor +
            confirmations_factor +
            pattern_factor +
            regime_factor +
            data_factor +
            risk_reward_factor
        )
        
        # Normalize to 0-1 range
        return min(max(confidence, 0.0), 1.0)

