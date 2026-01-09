"""
Simple REST API Client for Terminal v1 UI.

Connects directly to backend REST API.
"""

import os
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime


class APIClient:
    """
    Simple REST API client for backend communication.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            base_url: Backend API base URL (default: http://localhost:8001)
        """
        self.base_url = base_url or os.getenv("STOCKPORT_API_URL", "http://localhost:8001")
        self.timeout = 5  # 5 second timeout
    
    def _get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make GET request."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def _post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make POST request."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.post(url, json=json, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get system status."""
        return self._get("/status")
    
    def get_opportunities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get opportunities."""
        result = self._get(f"/opportunities?limit={limit}")
        return result if isinstance(result, list) else []
    
    def get_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get signals."""
        result = self._get(f"/signals?limit={limit}")
        return result if isinstance(result, list) else []
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get positions."""
        result = self._get("/positions")
        return result if isinstance(result, list) else []
    
    def get_orders(self) -> List[Dict[str, Any]]:
        """Get orders."""
        result = self._get("/orders")
        return result if isinstance(result, list) else []
    
    def get_market_state(self) -> Optional[Dict[str, Any]]:
        """Get market state."""
        return self._get("/market/state")
    
    def get_data_health(self) -> Optional[Dict[str, Any]]:
        """Get data health."""
        return self._get("/data/health")
    
    def get_strategy_performance(self) -> List[Dict[str, Any]]:
        """Get strategy performance."""
        result = self._get("/strategies/performance")
        return result if isinstance(result, list) else []
    
    def post_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute a command."""
        return self._post("/command", json={
            "command": command,
            "parameters": params or {}
        })


# Singleton instance
_api_client: Optional[APIClient] = None


def get_api_client() -> APIClient:
    """Get singleton API client instance."""
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client

