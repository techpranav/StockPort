"""
Universal Stock Monitor

Monitors all stocks in real-time and generates signals.
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import threading
import time

from utils.debug_utils import DebugUtils
from backend.scanners.market_scanner import MarketScanner
from backend.strategies.evaluator import StrategyEvaluator
from backend.core.event_bus import EventBus
from models.opportunity import Opportunity
from models.strategy_signal import StrategySignal


class UniversalMonitor:
    """
    Universal stock monitor.
    
    Features:
    - Monitor all stocks in universe (configurable list)
    - Real-time price updates
    - Signal generation for all stocks
    - Performance tracking
    - Alert generation
    """
    
    def __init__(
        self,
        market_scanner: MarketScanner,
        strategy_evaluator: StrategyEvaluator,
        event_bus: Optional[EventBus] = None,
        monitor_interval: int = 60,  # seconds
        stock_universe: Optional[List[str]] = None
    ):
        """
        Initialize universal monitor.
        
        Args:
            market_scanner: Market scanner instance
            strategy_evaluator: Strategy evaluator instance
            event_bus: Event bus for publishing events (optional)
            monitor_interval: Monitoring interval in seconds
            stock_universe: List of stocks to monitor (None = use scanner default)
        """
        self.market_scanner = market_scanner
        self.strategy_evaluator = strategy_evaluator
        self.event_bus = event_bus
        self.monitor_interval = monitor_interval
        self.stock_universe = stock_universe or []
        
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Track signals and performance
        self.current_signals: Dict[str, List[StrategySignal]] = {}
        self.signal_history: List[Dict[str, Any]] = []
        self.last_scan_time: Optional[datetime] = None
        
        DebugUtils.info("Initialized UniversalMonitor")
    
    def start(self):
        """Start monitoring."""
        if self.is_running:
            DebugUtils.warning("UniversalMonitor is already running")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        DebugUtils.info("UniversalMonitor started")
    
    def stop(self):
        """Stop monitoring."""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        DebugUtils.info("UniversalMonitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                # Scan for opportunities
                opportunities = self.market_scanner.scan(self.stock_universe)
                
                # Evaluate each opportunity
                all_signals = {}
                for opportunity in opportunities:
                    try:
                        signals = self.strategy_evaluator.evaluate_opportunity(opportunity)
                        if signals:
                            all_signals[opportunity.symbol] = signals
                    except Exception as e:
                        DebugUtils.log_error(e, f"Error evaluating {opportunity.symbol}")
                
                # Update current signals
                self.current_signals = all_signals
                self.last_scan_time = datetime.now()
                
                # Store in history
                self.signal_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'signals': {
                        symbol: [s.signal_id for s in signals]
                        for symbol, signals in all_signals.items()
                    }
                })
                
                # Keep only last 100 scans in history
                if len(self.signal_history) > 100:
                    self.signal_history = self.signal_history[-100:]
                
                # Publish events if event bus available
                if self.event_bus:
                    self._publish_signals(all_signals)
                
                DebugUtils.debug(
                    f"UniversalMonitor scan completed: {len(opportunities)} opportunities, "
                    f"{len(all_signals)} symbols with signals"
                )
                
                # Sleep until next scan
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                DebugUtils.log_error(e, "Error in UniversalMonitor loop")
                time.sleep(self.monitor_interval)
    
    def _publish_signals(self, signals: Dict[str, List[StrategySignal]]):
        """Publish signals to event bus."""
        try:
            if not self.event_bus:
                return
            
            for symbol, signal_list in signals.items():
                for signal in signal_list:
                    self.event_bus.publish(
                        'signal.generated',
                        {
                            'symbol': symbol,
                            'signal_id': signal.signal_id,
                            'strategy_id': signal.strategy_id,
                            'score': signal.score,
                            'confidence': signal.confidence,
                            'entry_price': signal.entry_price,
                            'timestamp': signal.timestamp.isoformat()
                        }
                    )
        except Exception as e:
            DebugUtils.log_error(e, "Error publishing signals to event bus")
    
    def get_current_signals(
        self,
        min_score: float = 0.0,
        min_confidence: float = 0.0
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get current signals filtered by score and confidence.
        
        Args:
            min_score: Minimum signal score
            min_confidence: Minimum confidence
            
        Returns:
            Dictionary of filtered signals
        """
        filtered = {}
        
        for symbol, signals in self.current_signals.items():
            filtered_signals = [
                {
                    'signal_id': s.signal_id,
                    'strategy_id': s.strategy_id,
                    'score': s.score,
                    'confidence': s.confidence,
                    'entry_price': s.entry_price,
                    'stop_loss': s.stop_loss,
                    'take_profit': s.take_profit,
                    'timestamp': s.timestamp.isoformat()
                }
                for s in signals
                if s.score >= min_score and s.confidence >= min_confidence
            ]
            
            if filtered_signals:
                filtered[symbol] = filtered_signals
        
        return filtered
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitor status."""
        return {
            'is_running': self.is_running,
            'last_scan_time': self.last_scan_time.isoformat() if self.last_scan_time else None,
            'monitor_interval': self.monitor_interval,
            'stock_universe_size': len(self.stock_universe),
            'current_signals_count': sum(len(s) for s in self.current_signals.values()),
            'symbols_with_signals': len(self.current_signals)
        }

