"""
Trade Attributor

Attributes entry and exit reasons for trades.
"""

from typing import Dict, Any
from datetime import datetime


class TradeAttributor:
    """
    Attributes trades to entry and exit reasons.
    """
    
    def attribute_entry(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attribute entry.
        
        Args:
            trade: Trade dictionary
            
        Returns:
            Entry attribution dictionary
        """
        signal = trade.get('signal', {})
        conditions = signal.get('conditions', [])
        
        # Extract indicators
        indicators = {}
        for condition in conditions:
            if condition.get('type') == 'indicator':
                indicators[condition.get('name', '')] = condition.get('value', 0)
        
        # Extract patterns
        patterns = [
            c.get('name', '') for c in conditions
            if c.get('type') == 'pattern'
        ]
        
        return {
            'reason': f"Entry based on {len(conditions)} conditions",
            'indicators': indicators,
            'patterns': patterns,
            'regime': trade.get('entry_regime', 'unknown')
        }
    
    def attribute_exit(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attribute exit.
        
        Args:
            trade: Trade dictionary
            
        Returns:
            Exit attribution dictionary
        """
        exit_reason = trade.get('exit_reason', 'unknown')
        exit_price = trade.get('exit_price', 0)
        entry_price = trade.get('entry_price', 0)
        
        # Determine exit category
        if 'profit' in exit_reason.lower() or 'target' in exit_reason.lower():
            category = 'profit_target'
        elif 'stop' in exit_reason.lower() or 'loss' in exit_reason.lower():
            category = 'stop_loss'
        elif 'time' in exit_reason.lower():
            category = 'time_based'
        else:
            category = 'manual'
        
        # Determine timing (simplified)
        timing = 'on_time'  # Would compare to optimal exit
        
        return {
            'reason': exit_reason,
            'category': category,
            'timing': timing,
            'indicators': {}  # Would include exit indicators
        }

