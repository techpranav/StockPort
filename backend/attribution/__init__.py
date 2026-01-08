"""
Attribution Module

Provides trade attribution and failure analysis:
- Trade attribution engine
- Entry/exit attribution
- Indicator contribution analysis
- Failure classification
"""

from backend.attribution.attribution_engine import AttributionEngine, TradeAttribution
from backend.attribution.trade_attributor import TradeAttributor
from backend.attribution.indicator_contributor import IndicatorContributor
from backend.attribution.failure_classifier import FailureClassifier, FailureCategory

__all__ = [
    'AttributionEngine',
    'TradeAttribution',
    'TradeAttributor',
    'IndicatorContributor',
    'FailureClassifier',
    'FailureCategory'
]
