"""
Explainer Engine

Main explainability engine.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from utils.debug_utils import DebugUtils
from backend.explainability.decision_explainer import DecisionExplainer
from backend.explainability.confidence_calculator import ConfidenceCalculator
from backend.explainability.uncertainty_quantifier import UncertaintyQuantifier


class ExplainerEngine:
    """
    Main explainability engine.
    
    Provides:
    - Decision explanations
    - Confidence scores
    - Uncertainty quantification
    """
    
    def __init__(self):
        """Initialize explainer engine."""
        self.decision_explainer = DecisionExplainer()
        self.confidence_calculator = ConfidenceCalculator()
        self.uncertainty_quantifier = UncertaintyQuantifier()
    
    def explain_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate explanation for decision.
        
        Args:
            decision: Trading decision dictionary
            
        Returns:
            Explanation dictionary
        """
        # Generate explanation
        explanation = self.decision_explainer.explain(decision)
        
        # Calculate confidence
        confidence = self.confidence_calculator.calculate(decision)
        
        # Quantify uncertainty
        uncertainty = self.uncertainty_quantifier.quantify(decision)
        
        return {
            'explanation': explanation,
            'confidence': confidence,
            'uncertainty': uncertainty
        }

