"""
Market State Engine

Main engine for market state detection and management.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from utils.debug_utils import DebugUtils
from backend.market_state.regime_detector import RegimeDetector
from backend.market_state.volatility_detector import VolatilityDetector
from backend.market_state.breadth_detector import BreadthDetector
from backend.market_state.liquidity_detector import LiquidityDetector


@dataclass
class MarketState:
    """Authoritative market state object."""
    timestamp: datetime
    regime: str  # trending_up, trending_down, choppy, high_volatility, low_volatility
    volatility_state: str  # low, normal, high, extreme
    breadth_state: str  # bullish, neutral, bearish
    liquidity_state: str  # high, normal, low
    vix_level: float
    market_direction: str  # up, down, sideways
    confidence: float  # 0-1
    indicators: Dict[str, float]
    transitions: List[Dict[str, Any]]


class MarketStateEngine:
    """
    Main market state engine.
    
    Detects and publishes market state for consumption by strategies,
    risk engine, and capital manager.
    """
    
    def __init__(self):
        """Initialize market state engine."""
        self.regime_detector = RegimeDetector()
        self.volatility_detector = VolatilityDetector()
        self.breadth_detector = BreadthDetector()
        self.liquidity_detector = LiquidityDetector()
        self.current_state: Optional[MarketState] = None
        self.state_history: List[MarketState] = []
    
    def detect_state(self, market_data: Dict[str, Any]) -> MarketState:
        """
        Detect current market state.
        
        Args:
            market_data: Dictionary with market data (SPY, VIX, etc.)
            
        Returns:
            MarketState object
        """
        # Detect regime
        regime = self.regime_detector.detect_regime(market_data)
        
        # Detect volatility
        volatility_state = self.volatility_detector.detect_volatility(market_data)
        vix_level = market_data.get('vix', 20.0)
        
        # Detect breadth
        breadth_state = self.breadth_detector.detect_breadth(market_data)
        
        # Detect liquidity
        liquidity_state = self.liquidity_detector.detect_liquidity(market_data)
        
        # Determine market direction
        market_direction = self._determine_direction(market_data)
        
        # Calculate confidence
        confidence = self._calculate_confidence(regime, volatility_state, breadth_state)
        
        # Build indicators dict
        indicators = {
            'vix': vix_level,
            'spy_price': market_data.get('spy_price', 0),
            'spy_change': market_data.get('spy_change', 0)
        }
        
        # Detect transitions
        transitions = self._detect_transitions()
        
        state = MarketState(
            timestamp=datetime.now(),
            regime=regime,
            volatility_state=volatility_state,
            breadth_state=breadth_state,
            liquidity_state=liquidity_state,
            vix_level=vix_level,
            market_direction=market_direction,
            confidence=confidence,
            indicators=indicators,
            transitions=transitions
        )
        
        # Update state history
        if self.current_state and self.current_state.regime != state.regime:
            transitions.append({
                'from': self.current_state.regime,
                'to': state.regime,
                'timestamp': state.timestamp
            })
        
        self.current_state = state
        self.state_history.append(state)
        
        # Keep only last 100 states
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
        
        DebugUtils.debug(f"Market state detected: {regime}, volatility={volatility_state}, breadth={breadth_state}")
        
        return state
    
    def get_current_state(self) -> Optional[MarketState]:
        """Get current market state."""
        return self.current_state
    
    def _determine_direction(self, market_data: Dict[str, Any]) -> str:
        """Determine market direction."""
        change = market_data.get('spy_change', 0)
        if change > 0.01:  # > 1%
            return "up"
        elif change < -0.01:  # < -1%
            return "down"
        else:
            return "sideways"
    
    def _calculate_confidence(
        self,
        regime: str,
        volatility_state: str,
        breadth_state: str
    ) -> float:
        """Calculate confidence in state classification."""
        # Simplified confidence calculation
        confidence = 0.7  # Base confidence
        
        # Increase confidence if multiple indicators agree
        if volatility_state in ["low", "normal"]:
            confidence += 0.1
        if breadth_state in ["bullish", "bearish"]:  # Clear direction
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _detect_transitions(self) -> List[Dict[str, Any]]:
        """Detect recent state transitions."""
        if len(self.state_history) < 2:
            return []
        
        transitions = []
        for i in range(1, len(self.state_history)):
            prev_state = self.state_history[i-1]
            curr_state = self.state_history[i]
            
            if prev_state.regime != curr_state.regime:
                transitions.append({
                    'from': prev_state.regime,
                    'to': curr_state.regime,
                    'timestamp': curr_state.timestamp
                })
        
        return transitions[-5:]  # Return last 5 transitions

