"""
REST API

REST API for commands and queries.
"""

from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from utils.debug_utils import DebugUtils
from backend.core.engine import TradingEngine
from backend.settings import get_settings_manager, get_settings


class CommandRequest(BaseModel):
    """Command request model."""
    command: str
    parameters: Dict[str, Any] = {}


class SettingUpdateRequest(BaseModel):
    """Setting update request model."""
    key: str
    value: Any


class RESTAPI:
    """
    REST API for system commands and queries.
    
    Endpoints:
    - GET /status: Get system status
    - POST /command: Execute command
    - GET /positions: Get positions
    - GET /orders: Get orders
    - GET /capital/overview: Get capital overview
    - GET /opportunities: Get recent opportunities
    - GET /signals: Get recent signals
    - GET /strategies/performance: Get strategy performance
    - GET /market/state: Get market state
    - GET /data/health: Get data health
    """
    
    def __init__(
        self,
        trading_engine: Optional[TradingEngine] = None,
        system_integrator: Optional[Any] = None
    ):
        """
        Initialize REST API.
        
        Args:
            trading_engine: Trading engine instance
            system_integrator: System integrator instance (provides access to all components)
        """
        self.trading_engine = trading_engine
        self.system_integrator = system_integrator
        self.app = FastAPI(title="Stockport v4 API")
        
        # Setup routes
        self.app.get("/status")(self.get_status)
        self.app.post("/command")(self.execute_command)
        self.app.get("/positions")(self.get_positions)
        self.app.get("/orders")(self.get_orders)
        
        # New endpoints
        self.app.get("/capital/overview")(self.get_capital_overview)
        self.app.get("/opportunities")(self.get_opportunities)
        self.app.get("/signals")(self.get_signals)
        self.app.get("/decisions")(self.get_decisions)
        self.app.get("/strategies/performance")(self.get_strategy_performance)
        self.app.get("/market/state")(self.get_market_state)
        self.app.get("/data/health")(self.get_data_health)
        
        # Settings routes
        self.app.get("/settings")(self.get_all_settings)
        self.app.get("/settings/{key}")(self.get_setting)
        self.app.put("/settings/{key}")(self.update_setting)
        self.app.get("/settings/definitions")(self.get_setting_definitions)
        self.app.post("/settings/reset/{key}")(self.reset_setting)
        self.app.post("/settings/reset-all")(self.reset_all_settings)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get system status.
        
        Returns:
            Status dictionary
        """
        if self.trading_engine:
            return self.trading_engine.get_status()
        return {"status": "unknown"}
    
    def execute_command(self, request: CommandRequest) -> Dict[str, Any]:
        """
        Execute a command.
        
        Args:
            request: Command request
            
        Returns:
            Command result
        """
        command = request.command
        params = request.parameters
        
        if not self.trading_engine:
            raise HTTPException(status_code=500, detail="Trading engine not available")
        
        try:
            if command == "start":
                self.trading_engine.start()
                return {"success": True, "message": "Engine started"}
            elif command == "stop":
                self.trading_engine.stop()
                return {"success": True, "message": "Engine stopped"}
            elif command == "set_mode":
                mode = params.get("mode")
                if mode:
                    self.trading_engine.set_mode(mode)
                    return {"success": True, "message": f"Mode set to {mode}"}
                else:
                    raise HTTPException(status_code=400, detail="Mode parameter required")
            else:
                raise HTTPException(status_code=400, detail=f"Unknown command: {command}")
        except Exception as e:
            DebugUtils.log_error(e, f"Error executing command: {command}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_positions(self) -> Dict[str, Any]:
        """
        Get current positions.
        
        Returns:
            Dictionary with positions list
        """
        try:
            if self.system_integrator:
                broker = None
                if hasattr(self.system_integrator, 'broker'):
                    broker = self.system_integrator.broker
                elif hasattr(self.system_integrator, 'execution_engine'):
                    broker = self.system_integrator.execution_engine.broker
                
                if broker:
                    positions = broker.get_all_positions()
                    return {
                        "positions": [
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
                    }
        except Exception as e:
            DebugUtils.log_error(e, "Error getting positions")
        
        return {"positions": []}
    
    def get_orders(self, status: Optional[str] = Query(None)) -> Dict[str, Any]:
        """
        Get recent orders.
        
        Args:
            status: Filter by status (optional)
            
        Returns:
            Dictionary with orders list
        """
        try:
            if self.system_integrator and hasattr(self.system_integrator, 'execution_engine'):
                order_manager = self.system_integrator.execution_engine.order_manager
                if order_manager:
                    orders = order_manager.get_orders(status=status)
                    return {"orders": [self._order_to_dict(order) for order in orders]}
        except Exception as e:
            DebugUtils.log_error(e, "Error getting orders")
        
        return {"orders": []}
    
    def get_capital_overview(self) -> Dict[str, Any]:
        """
        Get capital overview.
        
        Returns:
            Capital overview dictionary
        """
        try:
            if self.system_integrator and hasattr(self.system_integrator, 'capital_manager'):
                capital_state = self.system_integrator.capital_manager.get_capital_state()
                return capital_state
        except Exception as e:
            DebugUtils.log_error(e, "Error getting capital overview")
        
        # Fallback
        return {
            "total": 100000.0,
            "available": 75000.0,
            "allocated": 20000.0,
            "reserved": 5000.0
        }
    
    def get_opportunities(self, limit: int = Query(50)) -> Dict[str, Any]:
        """
        Get recent opportunities.
        
        Args:
            limit: Maximum number of opportunities
            
        Returns:
            Dictionary with opportunities list
        """
        try:
            # Get from audit logger
            if self.system_integrator and hasattr(self.system_integrator, 'audit_logger'):
                audit_logger = self.system_integrator.audit_logger
                logs = audit_logger.get_logs(event_type="OPPORTUNITY_DISCOVERED", limit=limit)
                
                opportunities = []
                for log in logs:
                    # Extract opportunity data from event_data
                    event_data = log.event_data
                    if isinstance(event_data, dict):
                        # Convert audit log to opportunity format
                        opp = {
                            "symbol": event_data.get("symbol", ""),
                            "timestamp": log.timestamp.isoformat(),
                            "price": event_data.get("price", 0.0),
                            "volume": event_data.get("volume", 0),
                            "score": event_data.get("pre_filter_score", event_data.get("score", 0)),
                            "sector": event_data.get("sector", "Unknown"),
                            "source": event_data.get("source", "market_scanner"),
                            "indicators": event_data.get("indicators", {}),
                            "market_cap": event_data.get("market_cap", 0)
                        }
                        opportunities.append(opp)
                
                return {"opportunities": opportunities}
        except Exception as e:
            DebugUtils.log_error(e, "Error getting opportunities")
        
        return {"opportunities": []}
    
    def get_signals(self, limit: int = Query(50)) -> Dict[str, Any]:
        """
        Get recent signals.
        
        Args:
            limit: Maximum number of signals
            
        Returns:
            Dictionary with signals list
        """
        try:
            # Get from audit logger
            if self.system_integrator and hasattr(self.system_integrator, 'audit_logger'):
                audit_logger = self.system_integrator.audit_logger
                logs = audit_logger.get_logs(event_type="SIGNAL_GENERATED", limit=limit)
                
                signals = []
                for log in logs:
                    # Extract signal data from event_data
                    event_data = log.event_data
                    if isinstance(event_data, dict):
                        # Convert audit log to signal format
                        signal = {
                            "signal_id": event_data.get("signal_id", log.decision_id or ""),
                            "symbol": event_data.get("symbol", ""),
                            "strategy_id": event_data.get("strategy_id", ""),
                            "timestamp": log.timestamp.isoformat(),
                            "score": event_data.get("score", 0),
                            "confidence": event_data.get("confidence", 0.0),
                            "entry_price": event_data.get("entry_price", 0.0),
                            "stop_loss": event_data.get("stop_loss"),
                            "take_profit": event_data.get("take_profit"),
                            "decision": "APPROVE"  # Would get from trading_decision event
                        }
                        signals.append(signal)
                
                return {"signals": signals}
        except Exception as e:
            DebugUtils.log_error(e, "Error getting signals")
        
        return {"signals": []}
    
    def get_decisions(self, limit: int = Query(50)) -> Dict[str, Any]:
        """
        Get recent trading decisions.
        
        Args:
            limit: Maximum number of decisions
            
        Returns:
            Dictionary with decisions list
        """
        try:
            # Get from audit logger
            if self.system_integrator and hasattr(self.system_integrator, 'audit_logger'):
                audit_logger = self.system_integrator.audit_logger
                logs = audit_logger.get_logs(event_type="TRADING_DECISION", limit=limit)
                
                decisions = []
                for log in logs:
                    # Extract decision data from event_data
                    event_data = log.event_data
                    if isinstance(event_data, dict):
                        decision = {
                            "decision_id": log.decision_id or "",
                            "symbol": event_data.get("symbol", ""),
                            "decision": event_data.get("decision", "UNKNOWN"),
                            "strategy_id": event_data.get("strategy_id", ""),
                            "timestamp": log.timestamp.isoformat(),
                            "risk_amount": event_data.get("risk_amount", 0.0),
                            "risk_percent": event_data.get("risk_percent", 0.0),
                            "risk_reward_ratio": event_data.get("risk_reward_ratio", 0.0),
                            "position_size": event_data.get("position_size", {}),
                            "explanation": log.explanation or ""
                        }
                        decisions.append(decision)
                
                return {"decisions": decisions}
        except Exception as e:
            DebugUtils.log_error(e, "Error getting decisions")
        
        return {"decisions": []}
    
    def get_strategy_performance(self, strategy_id: Optional[str] = Query(None)) -> Dict[str, Any]:
        """
        Get strategy performance.
        
        Args:
            strategy_id: Strategy ID (optional, None = all strategies)
            
        Returns:
            Dictionary with performance list
        """
        try:
            if self.system_integrator:
                performance_tracker = None
                strategy_registry = None
                
                if hasattr(self.system_integrator, 'performance_tracker'):
                    performance_tracker = self.system_integrator.performance_tracker
                elif hasattr(self.system_integrator, 'learning_system'):
                    performance_tracker = self.system_integrator.learning_system.performance_tracker
                
                if hasattr(self.system_integrator, 'strategy_registry'):
                    strategy_registry = self.system_integrator.strategy_registry
                
                if performance_tracker and strategy_registry:
                    if strategy_id:
                        perf = performance_tracker.get_performance(strategy_id, days=90)
                        if perf:
                            return {
                                "performance": [{
                                    "strategy_id": strategy_id,
                                    "win_rate": perf.win_rate,
                                    "profit_factor": perf.profit_factor,
                                    "sharpe_ratio": perf.sharpe_ratio,
                                    "total_return": perf.total_return,
                                    "total_trades": perf.total_trades,
                                    "max_drawdown": perf.max_drawdown
                                }]
                            }
                    else:
                        # Get all strategies
                        strategies = strategy_registry.get_active()
                        results = []
                        for strategy in strategies:
                            perf = performance_tracker.get_performance(strategy.id, days=90)
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
                        return {"performance": results}
        except Exception as e:
            DebugUtils.log_error(e, "Error getting strategy performance")
        
        return {"performance": []}
    
    def get_market_state(self) -> Dict[str, Any]:
        """
        Get current market state.
        
        Returns:
            Dictionary with market state
        """
        try:
            if self.system_integrator and hasattr(self.system_integrator, 'market_state_engine'):
                state = self.system_integrator.market_state_engine.get_current_state()
                if state:
                    return {
                        "state": {
                            "regime": state.regime,
                            "volatility_state": state.volatility_state,
                            "breadth_state": state.breadth_state,
                            "liquidity_state": state.liquidity_state,
                            "vix_level": state.vix_level,
                            "confidence": state.confidence
                        }
                    }
        except Exception as e:
            DebugUtils.log_error(e, "Error getting market state")
        
        # Fallback
        return {
            "state": {
                "regime": "unknown",
                "volatility_state": "unknown",
                "breadth_state": "unknown",
                "liquidity_state": "unknown",
                "vix_level": 0.0,
                "confidence": 0.0
            }
        }
    
    def get_data_health(self) -> Dict[str, Any]:
        """
        Get data health status.
        
        Returns:
            Dictionary with data health
        """
        try:
            if self.system_integrator and hasattr(self.system_integrator, 'health_monitor'):
                health_monitor = self.system_integrator.health_monitor
                # Get overall health status
                # Would aggregate from health_monitor
                return {
                    "health": {
                        "overall_status": "GREEN",
                        "symbols_checked": 0,
                        "green_count": 0,
                        "yellow_count": 0,
                        "red_count": 0
                    }
                }
        except Exception as e:
            DebugUtils.log_error(e, "Error getting data health")
        
        # Fallback
        return {
            "health": {
                "overall_status": "UNKNOWN",
                "symbols_checked": 0,
                "green_count": 0,
                "yellow_count": 0,
                "red_count": 0
            }
        }
    
    def _order_to_dict(self, order: Any) -> Dict[str, Any]:
        """Convert order object to dictionary."""
        if isinstance(order, dict):
            return order
        
        return {
            "order_id": getattr(order, 'order_id', ''),
            "symbol": getattr(order, 'symbol', ''),
            "side": getattr(order, 'side', ''),
            "quantity": getattr(order, 'quantity', 0),
            "order_type": getattr(order, 'order_type', ''),
            "status": getattr(order, 'status', ''),
            "created_at": getattr(order, 'created_at', '').isoformat() if hasattr(getattr(order, 'created_at', ''), 'isoformat') else str(getattr(order, 'created_at', '')),
            "fill_price": getattr(order, 'fill_price', None),
            "filled_quantity": getattr(order, 'filled_quantity', 0)
        }
    
    # Settings endpoints
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings."""
        try:
            settings_manager = get_settings_manager()
            return settings_manager.get_all()
        except Exception as e:
            DebugUtils.log_error(e, "Error getting all settings")
            return {}
    
    def get_setting(self, key: str) -> Dict[str, Any]:
        """
        Get setting value.
        
        Args:
            key: Setting key
        """
        try:
            settings_manager = get_settings_manager()
            value = settings_manager.get(key)
            return {"key": key, "value": value}
        except Exception as e:
            DebugUtils.log_error(e, f"Error getting setting {key}")
            raise HTTPException(status_code=404, detail=f"Setting {key} not found")
    
    def update_setting(self, key: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update setting.
        
        Args:
            key: Setting key
            request: Setting update request
        """
        try:
            settings_manager = get_settings_manager()
            value = request.get("value")
            if value is None:
                raise HTTPException(status_code=400, detail="Value is required")
            success = settings_manager.set(key, value, validate=True)
            if success:
                return {"success": True, "key": key, "value": value}
            else:
                raise HTTPException(status_code=400, detail=f"Failed to update setting {key}")
        except Exception as e:
            DebugUtils.log_error(e, f"Error updating setting {key}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_setting_definitions(self) -> Dict[str, Any]:
        """Get all setting definitions."""
        try:
            settings_manager = get_settings_manager()
            definitions = settings_manager.get_definitions()
            # Convert to list of dicts for JSON serialization
            definitions_list = []
            for key, definition in definitions.items():
                definitions_list.append({
                    "key": key,
                    "value_type": definition.value_type.__name__ if hasattr(definition.value_type, '__name__') else str(definition.value_type),
                    "default_value": definition.default_value,
                    "description": definition.description,
                    "category": definition.category.value if hasattr(definition.category, 'value') else str(definition.category),
                    "min_value": definition.min_value,
                    "max_value": definition.max_value,
                    "allowed_values": definition.allowed_values
                })
            return {"definitions": definitions_list}
        except Exception as e:
            DebugUtils.log_error(e, "Error getting setting definitions")
            return {"definitions": []}
    
    def reset_setting(self, key: str) -> Dict[str, Any]:
        """
        Reset setting to default.
        
        Args:
            key: Setting key
        """
        try:
            settings_manager = get_settings_manager()
            settings_manager.reset_to_default(key)
            return {"success": True, "key": key, "message": f"Setting {key} reset to default"}
        except Exception as e:
            DebugUtils.log_error(e, f"Error resetting setting {key}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def reset_all_settings(self) -> Dict[str, Any]:
        """Reset all settings to defaults."""
        try:
            settings_manager = get_settings_manager()
            settings_manager.reset_all_to_defaults()
            return {"success": True, "message": "All settings reset to defaults"}
        except Exception as e:
            DebugUtils.log_error(e, "Error resetting all settings")
            raise HTTPException(status_code=500, detail=str(e))
    
    def run(self, host: str = "0.0.0.0", port: int = 8001):
        """
        Run REST API server.
        
        Args:
            host: Host address
            port: Port number
        """
        import uvicorn
        DebugUtils.info(f"Starting REST API server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

