"""
Latency Tracker

Tracks latency budgets per strategy.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from utils.debug_utils import DebugUtils


@dataclass
class LatencyBudget:
    """Latency budget information."""
    strategy_type: str
    max_total_latency: float  # seconds
    scanner_latency: float
    evaluation_latency: float
    decision_latency: float
    execution_latency: float
    current_total: float
    is_within_budget: bool


class LatencyTracker:
    """
    Tracks latency budgets per strategy.
    
    Budgets:
    - Intraday: 2 seconds
    - Swing: 10 seconds
    - Position: 30 seconds
    """
    
    def __init__(self):
        """Initialize latency tracker."""
        from backend.settings import get_settings
        self.settings = get_settings()
        
        # Subscribe to settings changes
        self.settings.subscribe('timing.latency_budget_intraday_seconds', self._on_intraday_changed)
        self.settings.subscribe('timing.latency_budget_swing_seconds', self._on_swing_changed)
        self.settings.subscribe('timing.latency_budget_position_seconds', self._on_position_changed)
        
        # Initialize budgets from settings
        self._budgets = {}
        self._update_from_settings()
        
        self.latency_records: Dict[str, Dict[str, float]] = {}  # signal_id -> latencies
    
    def _update_from_settings(self):
        """Update latency budgets from settings."""
        self._budgets = {
            'intraday': self.settings.get_latency_budget_intraday_seconds(),
            'swing': self.settings.get_latency_budget_swing_seconds(),
            'position': self.settings.get_latency_budget_position_seconds()
        }
    
    def _on_intraday_changed(self, key: str, old_value: float, new_value: float):
        """Handle intraday latency budget change."""
        self._budgets['intraday'] = new_value
        DebugUtils.info(f"LatencyTracker: Intraday budget updated to {new_value:.1f}s")
    
    def _on_swing_changed(self, key: str, old_value: float, new_value: float):
        """Handle swing latency budget change."""
        self._budgets['swing'] = new_value
        DebugUtils.info(f"LatencyTracker: Swing budget updated to {new_value:.1f}s")
    
    def _on_position_changed(self, key: str, old_value: float, new_value: float):
        """Handle position latency budget change."""
        self._budgets['position'] = new_value
        DebugUtils.info(f"LatencyTracker: Position budget updated to {new_value:.1f}s")
    
    @property
    def budgets(self) -> Dict[str, float]:
        """Get current latency budgets."""
        if not self._budgets:
            self._update_from_settings()
        return self._budgets
    
    def record_latency(
        self,
        signal_id: str,
        stage: str,
        latency: float
    ):
        """
        Record latency for a stage.
        
        Args:
            signal_id: Signal identifier
            stage: Stage name (scanner, evaluation, decision, execution)
            latency: Latency in seconds
        """
        if signal_id not in self.latency_records:
            self.latency_records[signal_id] = {}
        
        self.latency_records[signal_id][stage] = latency
    
    def get_latency_budget(
        self,
        signal_id: str,
        strategy_type: str
    ) -> LatencyBudget:
        """
        Get latency budget for signal.
        
        Args:
            signal_id: Signal identifier
            strategy_type: Strategy type
            
        Returns:
            LatencyBudget object
        """
        max_total = self.budgets.get(strategy_type, 10.0)
        
        latencies = self.latency_records.get(signal_id, {})
        scanner_latency = latencies.get('scanner', 0.0)
        evaluation_latency = latencies.get('evaluation', 0.0)
        decision_latency = latencies.get('decision', 0.0)
        execution_latency = latencies.get('execution', 0.0)
        
        current_total = scanner_latency + evaluation_latency + decision_latency + execution_latency
        is_within_budget = current_total <= max_total
        
        return LatencyBudget(
            strategy_type=strategy_type,
            max_total_latency=max_total,
            scanner_latency=scanner_latency,
            evaluation_latency=evaluation_latency,
            decision_latency=decision_latency,
            execution_latency=execution_latency,
            current_total=current_total,
            is_within_budget=is_within_budget
        )
    
    def is_within_budget(self, signal_id: str, strategy_type: str) -> bool:
        """
        Check if latency is within budget.
        
        Args:
            signal_id: Signal identifier
            strategy_type: Strategy type
            
        Returns:
            True if within budget, False otherwise
        """
        budget = self.get_latency_budget(signal_id, strategy_type)
        return budget.is_within_budget

