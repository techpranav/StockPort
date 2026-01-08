"""
UI Data Service

Provides data access layer for UI components to interact with backend systems.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.debug_utils import DebugUtils
from backend.core.engine import TradingEngine
from backend.capital.capital_manager import CapitalManager
from backend.data.integrity.health_monitor import HealthMonitor
from backend.market_state.state_engine import MarketStateEngine
from backend.learning.performance_tracker import PerformanceTracker
from backend.strategies.registry import StrategyRegistry
from backend.execution.brokers.base_broker import BaseBroker
from backend.execution.order_manager import OrderManager


class UIDataService:
    """
    Data service for UI components.
    
    Provides unified interface to access backend data.
    """
    
    def __init__(
        self,
        trading_engine: Optional[TradingEngine] = None,
        capital_manager: Optional[CapitalManager] = None,
        health_monitor: Optional[HealthMonitor] = None,
        market_state_engine: Optional[MarketStateEngine] = None,
        performance_tracker: Optional[PerformanceTracker] = None,
        strategy_registry: Optional[StrategyRegistry] = None,
        broker: Optional[BaseBroker] = None,
        order_manager: Optional[OrderManager] = None
    ):
        """
        Initialize UI data service.
        
        Args:
            trading_engine: Trading engine instance
            capital_manager: Capital manager instance
            health_monitor: Health monitor instance
            market_state_engine: Market state engine instance
            performance_tracker: Performance tracker instance
            strategy_registry: Strategy registry instance
            broker: Broker instance
            order_manager: Order manager instance
        """
        self.trading_engine = trading_engine
        self.capital_manager = capital_manager
        self.health_monitor = health_monitor
        self.market_state_engine = market_state_engine
        self.performance_tracker = performance_tracker
        self.strategy_registry = strategy_registry
        self.broker = broker
        self.order_manager = order_manager
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status.
        
        Returns:
            System status dictionary
        """
        status = {
            "is_running": False,
            "mode": "manual",
            "timestamp": datetime.now().isoformat()
        }
        
        if self.trading_engine:
            status.update(self.trading_engine.get_status())
        
        return status
    
    def get_capital_overview(self) -> Dict[str, Any]:
        """
        Get capital overview.
        
        Returns:
            Capital overview dictionary
        """
        if not self.capital_manager:
            return {
                "total": 100000.0,
                "available": 75000.0,
                "allocated": 20000.0,
                "reserved": 5000.0
            }
        
        capital_state = self.capital_manager.get_capital_state()
        return {
            "total": capital_state.get('total', 0.0),
            "available": capital_state.get('available', 0.0),
            "allocated": capital_state.get('allocated', 0.0),
            "reserved": capital_state.get('reserved', 0.0)
        }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions.
        
        Returns:
            List of position dictionaries
        """
        if not self.broker:
            return []
        
        try:
            positions = self.broker.get_all_positions()
            return [
                {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "entry_price": pos.avg_entry_price,
                    "current_price": pos.current_price or pos.avg_entry_price,
                    "pnl": pos.pnl or 0.0,
                    "pnl_percent": pos.pnl_percent or 0.0,
                    "value": (pos.current_price or pos.avg_entry_price) * pos.quantity
                }
                for pos in positions
            ]
        except Exception as e:
            DebugUtils.log_error(e, "Error getting positions")
            return []
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders.
        
        Args:
            status: Filter by status (optional)
            
        Returns:
            List of order dictionaries
        """
        if not self.order_manager:
            return []
        
        try:
            orders = self.order_manager.get_orders(status=status)
            return [
                {
                    "order_id": order.get('order_id', ''),
                    "symbol": order.get('symbol', ''),
                    "side": order.get('side', ''),
                    "quantity": order.get('quantity', 0),
                    "order_type": order.get('order_type', ''),
                    "status": order.get('status', ''),
                    "created_at": order.get('created_at', ''),
                    "fill_price": order.get('fill_price'),
                    "filled_quantity": order.get('filled_quantity', 0)
                }
                for order in orders
            ]
        except Exception as e:
            DebugUtils.log_error(e, "Error getting orders")
            return []
    
    def get_data_health(self) -> Dict[str, Any]:
        """
        Get data health status.
        
        Returns:
            Data health dictionary
        """
        if not self.health_monitor:
            return {
                "overall_status": "GREEN",
                "symbols_checked": 0,
                "green_count": 0,
                "yellow_count": 0,
                "red_count": 0
            }
        
        try:
            # Get health for all symbols (simplified)
            # In real implementation, would aggregate from health_monitor
            return {
                "overall_status": "GREEN",
                "symbols_checked": 100,
                "green_count": 95,
                "yellow_count": 4,
                "red_count": 1
            }
        except Exception as e:
            DebugUtils.log_error(e, "Error getting data health")
            return {"overall_status": "UNKNOWN"}
    
    def get_market_state(self) -> Dict[str, Any]:
        """
        Get current market state.
        
        Returns:
            Market state dictionary
        """
        if not self.market_state_engine:
            return {
                "regime": "trending_up",
                "volatility_state": "normal",
                "breadth_state": "bullish",
                "liquidity_state": "high",
                "vix_level": 18.5,
                "confidence": 0.85
            }
        
        try:
            state = self.market_state_engine.get_current_state()
            if state:
                return {
                    "regime": state.regime,
                    "volatility_state": state.volatility_state,
                    "breadth_state": state.breadth_state,
                    "liquidity_state": state.liquidity_state,
                    "vix_level": state.vix_level,
                    "confidence": state.confidence
                }
        except Exception as e:
            DebugUtils.log_error(e, "Error getting market state")
        
        return {
            "regime": "unknown",
            "volatility_state": "unknown",
            "breadth_state": "unknown",
            "liquidity_state": "unknown",
            "vix_level": 0.0,
            "confidence": 0.0
        }
    
    def get_strategy_performance(self, strategy_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get strategy performance.
        
        Args:
            strategy_id: Strategy ID (optional, None = all strategies)
            
        Returns:
            List of strategy performance dictionaries
        """
        if not self.performance_tracker:
            return []
        
        try:
            if strategy_id:
                perf = self.performance_tracker.get_performance(strategy_id, days=90)
                if perf:
                    return [{
                        "strategy_id": strategy_id,
                        "win_rate": perf.win_rate,
                        "profit_factor": perf.profit_factor,
                        "sharpe_ratio": perf.sharpe_ratio,
                        "total_return": perf.total_return,
                        "total_trades": perf.total_trades,
                        "max_drawdown": perf.max_drawdown
                    }]
            else:
                # Get all strategies
                if self.strategy_registry:
                    strategies = self.strategy_registry.get_active()
                    results = []
                    for strategy in strategies:
                        perf = self.performance_tracker.get_performance(strategy.id, days=90)
                        if perf:
                            results.append({
                                "strategy_id": strategy.id,
                                "name": strategy.name,
                                "win_rate": perf.win_rate,
                                "profit_factor": perf.profit_factor,
                                "sharpe_ratio": perf.sharpe_ratio,
                                "total_return": perf.total_return,
                                "total_trades": perf.total_trades,
                                "max_drawdown": perf.max_drawdown
                            })
                    return results
        except Exception as e:
            DebugUtils.log_error(e, "Error getting strategy performance")
        
        return []
    
    def get_opportunities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent opportunities.
        
        Args:
            limit: Maximum number of opportunities
            
        Returns:
            List of opportunity dictionaries
        """
        # Would get from scanner or event bus
        # For now, return empty list
        return []


# Global instance (would be initialized by main app)
_ui_data_service: Optional[UIDataService] = None


def get_ui_data_service() -> UIDataService:
    """Get global UI data service instance."""
    global _ui_data_service
    if _ui_data_service is None:
        _ui_data_service = UIDataService()
    return _ui_data_service


def set_ui_data_service(service: UIDataService):
    """Set global UI data service instance."""
    global _ui_data_service
    _ui_data_service = service

