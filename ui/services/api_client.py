"""
REST API Client

Client for connecting to Stockport v4 backend REST API.
"""

import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from utils.debug_utils import DebugUtils


class APIClient:
    """
    REST API client for backend communication.
    
    Connects to backend REST API for data fetching and commands.
    """
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of REST API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 5.0  # 5 second timeout
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response JSON as dictionary
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            DebugUtils.warning(f"API request failed: {e}")
            return {}
    
    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make POST request.
        
        Args:
            endpoint: API endpoint
            data: Request body
            
        Returns:
            Response JSON as dictionary
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            DebugUtils.warning(f"API request failed: {e}")
            return {}
    
    def _put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make PUT request.
        
        Args:
            endpoint: API endpoint
            data: Request body
            
        Returns:
            Response JSON as dictionary
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            DebugUtils.warning(f"API request failed: {e}")
            return {}
    
    # System Status
    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return self._get("/status")
    
    def execute_command(self, command: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute system command.
        
        Args:
            command: Command name
            params: Command parameters
            
        Returns:
            Command result
        """
        return self._post("/command", data={"command": command, "params": params or {}})
    
    # Positions & Orders
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions."""
        result = self._get("/positions")
        return result.get("positions", [])
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders.
        
        Args:
            status: Filter by status (optional)
        """
        params = {}
        if status:
            params["status"] = status
        result = self._get("/orders", params=params)
        return result.get("orders", [])
    
    # Settings
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings."""
        return self._get("/settings")
    
    def get_setting(self, key: str) -> Any:
        """
        Get setting value.
        
        Args:
            key: Setting key
        """
        result = self._get(f"/settings/{key}")
        return result.get("value")
    
    def update_setting(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Update setting.
        
        Args:
            key: Setting key
            value: Setting value
        """
        return self._put(f"/settings/{key}", data={"value": value})
    
    def get_setting_definitions(self) -> List[Dict[str, Any]]:
        """Get all setting definitions."""
        result = self._get("/settings/definitions")
        return result.get("definitions", [])
    
    # Opportunities & Signals (would need to be added to REST API)
    def get_opportunities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent opportunities.
        
        Args:
            limit: Maximum number of opportunities
        """
        # This endpoint would need to be added to REST API
        result = self._get("/opportunities", params={"limit": limit})
        return result.get("opportunities", [])
    
    def get_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent signals.
        
        Args:
            limit: Maximum number of signals
        """
        # This endpoint would need to be added to REST API
        result = self._get("/signals", params={"limit": limit})
        return result.get("signals", [])
    
    # Strategy Performance
    def get_strategy_performance(self, strategy_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get strategy performance.
        
        Args:
            strategy_id: Strategy ID (optional, None = all strategies)
        """
        # This endpoint would need to be added to REST API
        params = {}
        if strategy_id:
            params["strategy_id"] = strategy_id
        result = self._get("/strategies/performance", params=params)
        return result.get("performance", [])
    
    # Market State
    def get_market_state(self) -> Dict[str, Any]:
        """Get current market state."""
        # This endpoint would need to be added to REST API
        result = self._get("/market/state")
        return result.get("state", {})
    
    # Data Health
    def get_data_health(self) -> Dict[str, Any]:
        """Get data health status."""
        # This endpoint would need to be added to REST API
        result = self._get("/data/health")
        return result.get("health", {})


# Global instance
_api_client: Optional[APIClient] = None


def get_api_client() -> APIClient:
    """Get global API client instance."""
    global _api_client
    if _api_client is None:
        import os
        base_url = os.getenv("STOCKPORT_API_URL", "http://localhost:8001")
        _api_client = APIClient(base_url=base_url)
    return _api_client


def set_api_client(client: APIClient):
    """Set global API client instance."""
    global _api_client
    _api_client = client

