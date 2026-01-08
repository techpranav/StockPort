"""
Duplicate Prevention

Prevents duplicate orders using idempotency keys.
"""

from typing import Dict, Any, Optional
import hashlib
import json

from utils.debug_utils import DebugUtils


class DuplicatePrevention:
    """
    Prevents duplicate orders using idempotency keys.
    
    Features:
    - Idempotency key generation
    - Order deduplication
    - State machine enforcement
    """
    
    def __init__(self):
        """Initialize duplicate prevention."""
        self.processed_keys: set = set()  # Set of processed idempotency keys
    
    def generate_idempotency_key(self, order: Dict[str, Any]) -> str:
        """
        Generate idempotency key for order.
        
        Args:
            order: Order dictionary
            
        Returns:
            Idempotency key string
        """
        # Create unique key from order attributes
        key_data = {
            'symbol': order.get('symbol'),
            'side': order.get('side'),
            'quantity': order.get('quantity'),
            'strategy_id': order.get('strategy_id'),
            'signal_id': order.get('signal_id'),
            'timestamp': order.get('timestamp', '').isoformat() if hasattr(order.get('timestamp', ''), 'isoformat') else str(order.get('timestamp', ''))
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        return key_hash
    
    def is_duplicate(self, idempotency_key: str) -> bool:
        """
        Check if order is duplicate.
        
        Args:
            idempotency_key: Idempotency key
            
        Returns:
            True if duplicate, False otherwise
        """
        return idempotency_key in self.processed_keys
    
    def mark_processed(self, idempotency_key: str):
        """
        Mark idempotency key as processed.
        
        Args:
            idempotency_key: Idempotency key
        """
        self.processed_keys.add(idempotency_key)
        
        # Keep only last 10000 keys to prevent memory issues
        if len(self.processed_keys) > 10000:
            # Remove oldest (simplified - would use LRU)
            self.processed_keys = set(list(self.processed_keys)[-5000:])

