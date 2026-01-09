"""
Signal Translator

Translates technical signals into simple, actionable language for non-trading users.
"""

from typing import Dict, Any, Optional
from models.signals import EntrySignal

from utils.debug_utils import DebugUtils
from services.analyzers.indicators.support_resistance import SupportResistanceCalculator


class SignalTranslator:
    """
    Translates technical analysis signals into simple language.
    
    Features:
    - Convert technical jargon to plain English
    - Provide actionable recommendations
    - Explain confidence levels
    - Risk assessment in simple terms
    """
    
    def __init__(self):
        """Initialize signal translator."""
        DebugUtils.info("Initialized SignalTranslator")
        self.support_resistance_calc = SupportResistanceCalculator()
    
    def translate_signal(
        self,
        entry_signal: Dict[str, Any],
        support_resistance: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Translate entry signal to simple language with support/resistance context.
        
        Args:
            entry_signal: Entry signal dictionary
            support_resistance: Support/resistance levels (optional)
            
        Returns:
            Dictionary with simple language translations
        """
        signal_type = entry_signal.get('signal_type', '')
        score = entry_signal.get('score', 0)
        confidence = entry_signal.get('confidence', 0)
        
        # Simple recommendation
        recommendation = self._get_recommendation(signal_type, score)
        
        # Simple explanation with support/resistance context
        explanation = self._get_explanation(signal_type, score, confidence, support_resistance)
        
        # Actionable advice with support/resistance context
        advice = self._get_advice(signal_type, entry_signal, support_resistance)
        
        # Risk level in simple terms
        risk_level = self._get_risk_level(entry_signal.get('risk_metrics', {}))
        
        # Educational content
        educational = self._get_educational_content(signal_type, support_resistance)
        
        return {
            'recommendation': recommendation,
            'explanation': explanation,
            'advice': advice,
            'risk_level': risk_level,
            'confidence_text': self._get_confidence_text(confidence),
            'educational': educational,
            'support_resistance_context': self._get_sr_context(support_resistance)
        }
    
    def _get_recommendation(self, signal_type: str, score: float) -> str:
        """Get simple recommendation text."""
        if signal_type == 'STRONG_BUY':
            return "🚀 Excellent Opportunity - Strong Buy"
        elif signal_type == 'BUY':
            return "✅ Good Opportunity - Buy"
        elif signal_type == 'WATCH':
            return "👀 Keep Watching - Wait for Better Entry"
        elif signal_type == 'AVOID':
            return "⚠️ Not Recommended - Avoid"
        else:
            return "❓ No Clear Signal"
    
    def _get_explanation(
        self,
        signal_type: str,
        score: float,
        confidence: float,
        support_resistance: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get simple explanation with support/resistance context."""
        base_explanation = ""
        
        if signal_type == 'STRONG_BUY':
            base_explanation = "This stock shows very strong positive signals. Multiple technical indicators suggest it's a good time to buy."
        elif signal_type == 'BUY':
            base_explanation = "This stock shows positive signals. Technical analysis suggests it may be a good buying opportunity."
        elif signal_type == 'WATCH':
            base_explanation = "This stock shows mixed signals. It's worth monitoring, but wait for clearer signs before buying."
        elif signal_type == 'AVOID':
            base_explanation = "This stock shows negative signals. Technical analysis suggests it's not a good time to buy right now."
        else:
            base_explanation = "The signals for this stock are unclear. More analysis may be needed."
        
        # Add support/resistance context
        if support_resistance:
            near_support = support_resistance.get('near_support')
            near_resistance = support_resistance.get('near_resistance')
            
            if near_support:
                support_level = near_support.get('level', 0)
                bounce_prob = near_support.get('bounce_probability', 0)
                if bounce_prob > 0.6:
                    base_explanation += f" The stock is near a strong support level at ₹{support_level:.2f}, which increases the chance of a price bounce."
            
            if near_resistance:
                resistance_level = near_resistance.get('level', 0)
                base_explanation += f" There's a resistance level at ₹{resistance_level:.2f} that the stock may need to break through."
        
        # Add confidence context
        if confidence > 0.8:
            base_explanation += " The analysis is highly confident in this recommendation."
        elif confidence > 0.6:
            base_explanation += " The analysis is moderately confident in this recommendation."
        else:
            base_explanation += " The analysis has lower confidence, so proceed with caution."
        
        return base_explanation
    
    def _get_advice(
        self,
        signal_type: str,
        entry_signal: Dict[str, Any],
        support_resistance: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get actionable advice with support/resistance context."""
        entry_price = entry_signal.get('entry_price', 0)
        stop_loss = entry_signal.get('stop_loss')
        take_profit = entry_signal.get('take_profit')
        
        advice_parts = []
        
        if signal_type in ['STRONG_BUY', 'BUY']:
            advice_parts.append(f"Consider buying around ₹{entry_price:.2f}")
            
            # Add support/resistance context
            if support_resistance:
                near_support = support_resistance.get('near_support')
                if near_support:
                    support_level = near_support.get('level', 0)
                    advice_parts.append(f"The stock is near support at ₹{support_level:.2f}, which is a good entry point")
            
            if stop_loss:
                advice_parts.append(f"Set a stop-loss at ₹{stop_loss:.2f} to limit potential losses")
            
            if take_profit:
                advice_parts.append(f"Consider taking profits around ₹{take_profit:.2f}")
            
            if support_resistance:
                near_resistance = support_resistance.get('near_resistance')
                if near_resistance:
                    resistance_level = near_resistance.get('level', 0)
                    advice_parts.append(f"Watch for resistance at ₹{resistance_level:.2f} - price may struggle to break above this level")
            
            advice_parts.append("Monitor the stock closely and adjust your position based on market conditions")
        
        elif signal_type == 'WATCH':
            advice_parts.append("Don't buy yet - wait for stronger signals")
            
            if support_resistance:
                near_support = support_resistance.get('near_support')
                if near_support:
                    support_level = near_support.get('level', 0)
                    advice_parts.append(f"Watch for a bounce off support at ₹{support_level:.2f} - that could be a good entry point")
            
            advice_parts.append("Add this stock to your watchlist and check back regularly")
            advice_parts.append("Look for price movements that confirm a buying opportunity")
        
        elif signal_type == 'AVOID':
            advice_parts.append("Avoid buying this stock right now")
            advice_parts.append("If you already own it, consider selling or setting a tight stop-loss")
            advice_parts.append("Wait for better market conditions before considering this stock")
        
        return ". ".join(advice_parts) + "."
    
    def _get_risk_level(self, risk_metrics: Dict[str, Any]) -> str:
        """Get risk level in simple terms."""
        volatility = risk_metrics.get('volatility', 0)
        max_drawdown = risk_metrics.get('max_drawdown', 0)
        
        if volatility > 30 or max_drawdown > 20:
            return "🔴 High Risk - Only invest what you can afford to lose"
        elif volatility > 15 or max_drawdown > 10:
            return "🟡 Medium Risk - Invest cautiously"
        else:
            return "🟢 Low Risk - Relatively safe investment"
    
    def _get_confidence_text(self, confidence: float) -> str:
        """Get confidence level text."""
        if confidence > 0.8:
            return "Very High Confidence"
        elif confidence > 0.6:
            return "High Confidence"
        elif confidence > 0.4:
            return "Moderate Confidence"
        else:
            return "Low Confidence"

