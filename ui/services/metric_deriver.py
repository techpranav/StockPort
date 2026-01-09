"""
Metric Deriver Service

Derives UI metrics from existing backend APIs without requiring new endpoints.
UI v5 is a "new lens, not a new brain" - all metrics computed from existing data.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from utils.debug_utils import DebugUtils
from ui.services import get_ui_data_service


class MetricDeriver:
    """
    Derives UI metrics from existing backend APIs.
    
    All metrics are computed in the UI layer from existing API responses.
    No new backend endpoints required.
    """
    
    def __init__(self):
        """Initialize metric deriver."""
        self.data_service = get_ui_data_service()
    
    def get_algo_confidence(self) -> float:
        """
        Derive algo confidence from strategy performance.
        
        Returns:
            Confidence score (0-100)
        """
        try:
            strategy_perf = self.data_service.get_strategy_performance()
            
            if not strategy_perf:
                return 75.0  # Default confidence
            
            # Aggregate confidence from strategies
            # Use win_rate as proxy for confidence
            total_confidence = 0.0
            count = 0
            
            for perf in strategy_perf:
                win_rate = perf.get('win_rate', 0.0)
                if isinstance(win_rate, float) and 0 <= win_rate <= 1:
                    total_confidence += win_rate * 100
                    count += 1
                elif isinstance(win_rate, (int, float)) and 0 <= win_rate <= 100:
                    total_confidence += win_rate
                    count += 1
            
            if count > 0:
                return total_confidence / count
            else:
                return 75.0
                
        except Exception as e:
            DebugUtils.debug(f"Error deriving algo confidence: {e}")
            return 75.0
    
    def get_market_readiness(self) -> float:
        """
        Derive market readiness score from market state.
        
        Returns:
            Readiness score (0-100)
        """
        try:
            market_state = self.data_service.get_market_state()
            
            if not market_state:
                return 50.0  # Default readiness
            
            # Combine regime + volatility + breadth + liquidity
            regime = market_state.get('regime', 'unknown')
            volatility = market_state.get('volatility_state', 'normal')
            breadth = market_state.get('breadth_state', 'neutral')
            liquidity = market_state.get('liquidity_state', 'normal')
            
            score = 50.0  # Base score
            
            # Regime contribution
            if 'bull' in regime.lower() or 'up' in regime.lower():
                score += 20
            elif 'bear' in regime.lower() or 'down' in regime.lower():
                score -= 10
            
            # Volatility contribution
            if volatility == 'low':
                score += 15
            elif volatility == 'high':
                score -= 15
            
            # Breadth contribution
            if breadth == 'bullish':
                score += 10
            elif breadth == 'bearish':
                score -= 10
            
            # Liquidity contribution
            if liquidity == 'high':
                score += 5
            elif liquidity == 'low':
                score -= 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            DebugUtils.debug(f"Error deriving market readiness: {e}")
            return 50.0
    
    def get_todays_bias(self) -> str:
        """
        Derive today's bias from market state.
        
        Returns:
            Bias string: "Bullish", "Neutral", or "Bearish"
        """
        try:
            market_state = self.data_service.get_market_state()
            
            if not market_state:
                return "Neutral"
            
            regime = market_state.get('regime', 'unknown')
            breadth = market_state.get('breadth_state', 'neutral')
            
            # Determine bias
            if 'bull' in regime.lower() or breadth == 'bullish':
                return "Bullish"
            elif 'bear' in regime.lower() or breadth == 'bearish':
                return "Bearish"
            else:
                return "Neutral"
                
        except Exception as e:
            DebugUtils.debug(f"Error deriving today's bias: {e}")
            return "Neutral"
    
    def get_next_action_eta(self) -> Optional[str]:
        """
        Calculate next action ETA from scanner frequency settings.
        
        Returns:
            ETA string (e.g., "02:14") or None
        """
        try:
            # This would typically come from settings
            # For now, return a default
            # In real implementation, would read from settings API
            return "02:14"  # Default
            
        except Exception as e:
            DebugUtils.debug(f"Error calculating next action ETA: {e}")
            return None
    
    def get_signal_stream(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get signal stream from opportunities endpoint.
        
        Args:
            limit: Maximum number of signals to return
            
        Returns:
            List of signal dictionaries
        """
        try:
            opportunities = self.data_service.get_opportunities(limit=limit)
            
            # Convert opportunities to signals
            signals = []
            for opp in opportunities:
                signal = {
                    'symbol': opp.get('symbol', ''),
                    'score': opp.get('score', 0),
                    'confidence': opp.get('score', 0) / 100.0,  # Normalize to 0-1
                    'price': opp.get('price', 0.0),
                    'timestamp': opp.get('timestamp', ''),
                    'strategy_id': opp.get('source', 'unknown'),
                    'indicators': opp.get('indicators', {})
                }
                signals.append(signal)
            
            # Sort by confidence × freshness
            signals.sort(key=lambda x: (
                x.get('score', 0),
                x.get('timestamp', '')
            ), reverse=True)
            
            return signals[:limit]
            
        except Exception as e:
            DebugUtils.debug(f"Error getting signal stream: {e}")
            return []
    
    def get_execution_quality(self) -> Dict[str, Any]:
        """
        Calculate execution quality from order history.
        
        Returns:
            Dictionary with quality metrics
        """
        try:
            orders = self.data_service.get_orders()
            
            if not orders:
                return {
                    'score': 0.0,
                    'slippage_avg': 0.0,
                    'fill_rate': 0.0,
                    'latency_avg': 0.0
                }
            
            # Calculate metrics
            filled_orders = [o for o in orders if o.get('status', '').lower() == 'filled']
            total_orders = len(orders)
            
            fill_rate = len(filled_orders) / total_orders if total_orders > 0 else 0.0
            
            # Average slippage (if available)
            slippages = [o.get('slippage', 0.0) for o in filled_orders if o.get('slippage')]
            slippage_avg = sum(slippages) / len(slippages) if slippages else 0.0
            
            # Average latency (if available)
            latencies = [o.get('latency_ms', 0) for o in filled_orders if o.get('latency_ms')]
            latency_avg = sum(latencies) / len(latencies) if latencies else 0.0
            
            # Calculate quality score (0-100)
            score = (
                fill_rate * 40 +  # Fill rate contributes 40%
                (1 - min(slippage_avg / 0.1, 1.0)) * 30 +  # Low slippage contributes 30%
                (1 - min(latency_avg / 2000, 1.0)) * 30  # Low latency contributes 30%
            )
            
            return {
                'score': score,
                'slippage_avg': slippage_avg,
                'fill_rate': fill_rate,
                'latency_avg': latency_avg
            }
            
        except Exception as e:
            DebugUtils.debug(f"Error calculating execution quality: {e}")
            return {
                'score': 0.0,
                'slippage_avg': 0.0,
                'fill_rate': 0.0,
                'latency_avg': 0.0
            }
    
    def get_regime_timeline(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Aggregate regime timeline from historical market state data.
        
        Args:
            days: Number of days to include
            
        Returns:
            List of regime data points
        """
        try:
            # In real implementation, would fetch historical market state
            # For now, return current market state as single point
            market_state = self.data_service.get_market_state()
            
            if not market_state:
                return []
            
            return [{
                'timestamp': market_state.get('timestamp', datetime.now().isoformat()),
                'regime': market_state.get('regime', 'unknown'),
                'confidence': market_state.get('confidence', 0.75)
            }]
            
        except Exception as e:
            DebugUtils.debug(f"Error getting regime timeline: {e}")
            return []


def get_metric_deriver() -> MetricDeriver:
    """
    Get metric deriver instance.
    
    Returns:
        MetricDeriver instance
    """
    return MetricDeriver()

