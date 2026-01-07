"""
Live Analysis Service Module

This module provides continuous monitoring mode with alert system for
new entry points and real-time signal updates.
"""

from typing import Dict, Any, List, Optional, Callable
import time
from datetime import datetime

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataAnalysisException
from services.data_providers.intraday_fetcher import IntradayFetcher
from services.analyzers.signals.entry_detector import EntryDetector
from services.data_providers.stock_data_provider import StockDataProvider


class LiveAnalyzer:
    """
    Live analysis service for continuous monitoring.
    
    Features:
    - Continuous monitoring mode
    - Alert system for new entry points
    - Real-time signal updates
    - Market session awareness
    """
    
    def __init__(
        self,
        provider: StockDataProvider,
        update_interval: int = 60  # seconds
    ):
        """
        Initialize live analyzer.
        
        Args:
            provider: Stock data provider
            update_interval: Update interval in seconds
        """
        self.provider = provider
        self.intraday_fetcher = IntradayFetcher(provider)
        self.entry_detector = EntryDetector()
        self.update_interval = update_interval
        self.monitoring_symbols: List[str] = []
        self.last_signals: Dict[str, Any] = {}
        self.alert_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
    
    def add_symbol(self, symbol: str) -> None:
        """Add symbol to monitoring list."""
        if symbol not in self.monitoring_symbols:
            self.monitoring_symbols.append(symbol)
            DebugUtils.info(f"Added {symbol} to live monitoring")
    
    def remove_symbol(self, symbol: str) -> None:
        """Remove symbol from monitoring list."""
        if symbol in self.monitoring_symbols:
            self.monitoring_symbols.remove(symbol)
            DebugUtils.info(f"Removed {symbol} from live monitoring")
    
    def register_alert_callback(
        self,
        callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """
        Register callback for entry point alerts.
        
        Args:
            callback: Function that takes (symbol, signal_dict) as arguments
        """
        self.alert_callbacks.append(callback)
    
    def analyze_symbol(
        self,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a single symbol for entry points.
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            Entry signal dictionary or None
        """
        try:
            # Fetch intraday data
            data = self.intraday_fetcher.fetch_intraday_data(symbol, interval="5m", period="1d")
            
            if data.empty:
                return None
            
            # Calculate indicators (simplified - would use full indicator calculation)
            # For now, return basic analysis
            current_price = data['Close'].iloc[-1]
            
            # Check if market is open
            is_open = self.intraday_fetcher.is_market_open()
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'market_open': is_open,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error in live analysis for {symbol}")
            return None
    
    def check_for_new_signals(
        self,
        symbol: str,
        current_signal: Dict[str, Any]
    ) -> bool:
        """
        Check if new signal is different from last signal.
        
        Args:
            symbol: Stock symbol
            current_signal: Current signal data
            
        Returns:
            True if signal changed
        """
        last_signal = self.last_signals.get(symbol)
        
        if last_signal is None:
            return True
        
        # Compare signal types
        if current_signal.get('signal_type') != last_signal.get('signal_type'):
            return True
        
        # Compare scores (significant change)
        current_score = current_signal.get('score', 0)
        last_score = last_signal.get('score', 0)
        
        if abs(current_score - last_score) > 10:  # 10 point change
            return True
        
        return False
    
    def trigger_alert(
        self,
        symbol: str,
        signal: Dict[str, Any]
    ) -> None:
        """Trigger alert callbacks for new signal."""
        for callback in self.alert_callbacks:
            try:
                callback(symbol, signal)
            except Exception as e:
                DebugUtils.log_error(e, f"Error in alert callback for {symbol}")

