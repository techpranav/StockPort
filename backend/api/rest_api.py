"""
REST API

REST API for commands and queries.
"""

from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
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
    """
    
    def __init__(self, trading_engine: Optional[TradingEngine] = None):
        """
        Initialize REST API.
        
        Args:
            trading_engine: Trading engine instance
        """
        self.trading_engine = trading_engine
        self.app = FastAPI(title="Stockport v4 API")
        
        # Setup routes
        self.app.get("/status")(self.get_status)
        self.app.post("/command")(self.execute_command)
        self.app.get("/positions")(self.get_positions)
        self.app.get("/orders")(self.get_orders)
        
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
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions.
        
        Returns:
            List of positions
        """
        # Would get from broker or position manager
        return []
    
    def get_orders(self) -> List[Dict[str, Any]]:
        """
        Get recent orders.
        
        Returns:
            List of orders
        """
        # Would get from order manager
        return []
    
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

