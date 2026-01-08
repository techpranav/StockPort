"""
Main Orchestrator Engine

This module provides the main orchestrator that coordinates all system components.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from utils.debug_utils import DebugUtils
from backend.core.event_bus import EventBus
from backend.core.state_manager import StateManager


class TradingEngine:
    """
    Main orchestrator for the trading system.
    
    Coordinates between scanners, strategy evaluator, decision engine,
    and execution engine.
    """
    
    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        state_manager: Optional[StateManager] = None
    ):
        """
        Initialize the trading engine.
        
        Args:
            event_bus: Event bus for pub/sub messaging
            state_manager: State manager for persistence
        """
        self.event_bus = event_bus or EventBus()
        self.state_manager = state_manager or StateManager()
        
        self.is_running = False
        self.mode = "manual"  # manual, semi_auto, full_auto
        
        DebugUtils.info("TradingEngine initialized")
    
    def start(self):
        """Start the trading engine."""
        if self.is_running:
            DebugUtils.warning("Trading engine is already running")
            return
        
        self.is_running = True
        self.state_manager.save_system_state({
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "mode": self.mode
        })
        
        DebugUtils.info(f"Trading engine started in {self.mode} mode")
    
    def stop(self):
        """Stop the trading engine."""
        if not self.is_running:
            DebugUtils.warning("Trading engine is not running")
            return
        
        self.is_running = False
        self.state_manager.save_system_state({
            "status": "stopped",
            "stopped_at": datetime.now().isoformat()
        })
        
        DebugUtils.info("Trading engine stopped")
    
    def set_mode(self, mode: str):
        """
        Set the trading mode.
        
        Args:
            mode: "manual", "semi_auto", or "full_auto"
        """
        if mode not in ["manual", "semi_auto", "full_auto"]:
            raise ValueError(f"Invalid mode: {mode}")
        
        self.mode = mode
        self.state_manager.save_system_state({"mode": mode})
        DebugUtils.info(f"Trading mode set to {mode}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current system status.
        
        Returns:
            Dictionary with system status information
        """
        return {
            "is_running": self.is_running,
            "mode": self.mode,
            "timestamp": datetime.now().isoformat()
        }

