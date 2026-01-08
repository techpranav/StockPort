"""
Shadow Trading Module

Provides shadow trading capabilities for testing strategies without risking capital:
- Shadow engine for executing shadow trades
- Shadow broker for paper trading
- Isolation layer to prevent shadow leakage
- Comparison engine for shadow vs live performance
"""

from backend.shadow.shadow_engine import ShadowEngine
from backend.shadow.shadow_broker import ShadowBroker
from backend.shadow.isolation_layer import IsolationLayer, IsolationError
from backend.shadow.comparison_engine import ComparisonEngine, ShadowComparison

__all__ = [
    'ShadowEngine',
    'ShadowBroker',
    'IsolationLayer',
    'IsolationError',
    'ComparisonEngine',
    'ShadowComparison'
]
