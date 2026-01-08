"""
Strategy Evaluator

Evaluates opportunities against active strategies.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from utils.debug_utils import DebugUtils
from models.opportunity import Opportunity
from models.strategy_signal import StrategySignal
from backend.strategies.registry import StrategyRegistry
from backend.market_state.state_engine import MarketStateEngine
from backend.governance.audit_logger import AuditLogger


class StrategyEvaluator:
    """
    Evaluates opportunities against active strategies.
    
    Responsibilities:
    - Evaluate opportunities against all active strategies
    - Score and rank opportunities
    - Filter by market regime
    """
    
    def __init__(
        self,
        strategy_registry: StrategyRegistry,
        market_state_engine: Optional[MarketStateEngine] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize strategy evaluator.
        
        Args:
            strategy_registry: Strategy registry instance
            market_state_engine: Market state engine (optional)
            audit_logger: Audit logger instance (optional)
        """
        self.strategy_registry = strategy_registry
        self.market_state_engine = market_state_engine
        self.audit_logger = audit_logger
    
    def evaluate_opportunity(
        self,
        opportunity: Opportunity,
        market_state: Optional[Dict[str, Any]] = None
    ) -> List[StrategySignal]:
        """
        Evaluate opportunity against all active strategies.
        
        Args:
            opportunity: Opportunity to evaluate
            market_state: Current market state (optional)
            
        Returns:
            List of strategy signals (one per matching strategy)
        """
        signals = []
        
        # Get active strategies
        active_strategies = self.strategy_registry.get_active()
        
        # Get current market state if not provided
        if market_state is None and self.market_state_engine:
            current_state = self.market_state_engine.get_current_state()
            if current_state:
                market_state = {
                    'regime': current_state.regime,
                    'volatility_state': current_state.volatility_state,
                    'breadth_state': current_state.breadth_state
                }
        
        # Evaluate against each strategy
        for strategy in active_strategies:
            try:
                # Check if strategy is applicable to current regime
                if market_state:
                    regime = market_state.get('regime')
                    if not strategy.is_applicable(regime):
                        continue
                
                # Evaluate opportunity
                signal = strategy.evaluate(opportunity, market_state)
                
                if signal:
                    signals.append(signal)
                    DebugUtils.debug(
                        f"Strategy {strategy.get_id()} generated signal for {opportunity.symbol} "
                        f"(score: {signal.score:.1f})"
                    )
                    
                    # Audit log signal generation
                    if self.audit_logger:
                        self.audit_logger.log(
                            event_type="SIGNAL_GENERATED",
                            event_data={
                                'symbol': opportunity.symbol,
                                'strategy_id': strategy.get_id(),
                                'signal_id': signal.signal_id,
                                'score': signal.score,
                                'confidence': signal.confidence
                            },
                            decision_id=signal.signal_id,
                            explanation=f"Strategy {strategy.get_id()} generated signal for {opportunity.symbol} (score: {signal.score:.1f})"
                        )
            except Exception as e:
                DebugUtils.log_error(e, f"Error evaluating {opportunity.symbol} with strategy {strategy.get_id()}")
        
        # Sort by score (highest first)
        signals.sort(key=lambda s: s.score, reverse=True)
        
        return signals
    
    def evaluate_batch(
        self,
        opportunities: List[Opportunity],
        market_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[StrategySignal]]:
        """
        Evaluate multiple opportunities.
        
        Args:
            opportunities: List of opportunities
            market_state: Current market state (optional)
            
        Returns:
            Dictionary mapping symbol to list of signals
        """
        results = {}
        
        for opportunity in opportunities:
            signals = self.evaluate_opportunity(opportunity, market_state)
            if signals:
                results[opportunity.symbol] = signals
        
        return results

