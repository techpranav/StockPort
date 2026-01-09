"""
Strategy Implementations Package

Contains concrete strategy implementations.
"""

from backend.strategies.strategies.momentum import MomentumStrategy
from backend.strategies.strategies.trend_following import TrendFollowingStrategy
from backend.strategies.strategies.support_resistance_bounce import SupportResistanceBounceStrategy
from backend.strategies.strategies.mean_reversion import MeanReversionStrategy
from backend.strategies.strategies.breakout import BreakoutStrategy
from backend.strategies.strategies.swing_trading import SwingTradingStrategy

__all__ = [
    'MomentumStrategy',
    'TrendFollowingStrategy',
    'SupportResistanceBounceStrategy',
    'MeanReversionStrategy',
    'BreakoutStrategy',
    'SwingTradingStrategy'
]
