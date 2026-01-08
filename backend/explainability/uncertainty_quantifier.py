"""
Uncertainty Quantifier

Quantifies uncertainty in decisions.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class Uncertainty:
    """Uncertainty representation."""
    total_uncertainty: float  # 0-1
    data_uncertainty: float
    model_uncertainty: float
    market_uncertainty: float
    execution_uncertainty: float
    uncertainty_sources: List[str]


class UncertaintyQuantifier:
    """
    Quantifies uncertainty in trading decisions.
    
    Sources:
    - Data uncertainty
    - Model uncertainty
    - Market uncertainty
    - Execution uncertainty
    """
    
    def quantify(self, decision: Dict[str, Any]) -> Uncertainty:
        """
        Quantify uncertainty.
        
        Args:
            decision: Trading decision dictionary
            
        Returns:
            Uncertainty object
        """
        signal = decision.get('signal', {})
        confidence = decision.get('confidence', 0.7)
        
        # Data uncertainty (inverse of data quality)
        data_quality = decision.get('data_quality_score', 1.0)
        data_uncertainty = 1.0 - data_quality
        
        # Model uncertainty (inverse of confidence)
        model_uncertainty = 1.0 - confidence
        
        # Market uncertainty (based on volatility and regime)
        volatility = decision.get('volatility', 0.2)
        regime = decision.get('market_regime', 'normal')
        
        if regime in ['high_volatility', 'extreme']:
            market_uncertainty = min(volatility * 1.5, 0.5)
        elif regime == 'choppy':
            market_uncertainty = 0.3
        else:
            market_uncertainty = volatility
        
        # Execution uncertainty (slippage, fills, liquidity)
        liquidity = decision.get('liquidity_score', 1.0)
        execution_uncertainty = (1.0 - liquidity) * 0.2 + 0.05  # Base 5% + liquidity impact
        
        # Total uncertainty
        total_uncertainty = (
            data_uncertainty * 0.3 +
            model_uncertainty * 0.4 +
            market_uncertainty * 0.2 +
            execution_uncertainty * 0.1
        )
        
        # Uncertainty sources
        sources = []
        if data_uncertainty > 0.3:
            sources.append("Low data quality")
        if model_uncertainty > 0.3:
            sources.append("Low model confidence")
        if market_uncertainty > 0.3:
            sources.append("High market volatility")
        
        return Uncertainty(
            total_uncertainty=total_uncertainty,
            data_uncertainty=data_uncertainty,
            model_uncertainty=model_uncertainty,
            market_uncertainty=market_uncertainty,
            execution_uncertainty=execution_uncertainty,
            uncertainty_sources=sources
        )

