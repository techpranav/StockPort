"""
UI Data Service

Provides data access layer for UI components to interact with backend systems.
Uses REST API client to communicate with backend.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.debug_utils import DebugUtils
from ui.services.api_client import get_api_client, APIClient


class UIDataService:
    """
    Data service for UI components.
    
    Provides unified interface to access backend data via REST API.
    """
    
    def __init__(self, api_client: Optional[APIClient] = None):
        """
        Initialize UI data service.
        
        Args:
            api_client: API client instance (uses global if None)
        """
        self.api_client = api_client or get_api_client()
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status.
        
        Returns:
            System status dictionary
        """
        try:
            status = self.api_client.get_status()
            if not status:
                # Fallback to default if API unavailable
                return {
                    "is_running": False,
                    "mode": "manual",
                    "timestamp": datetime.now().isoformat()
                }
            return status
        except Exception as e:
            DebugUtils.log_error(e, "Error getting system status")
            return {
                "is_running": False,
                "mode": "manual",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_capital_overview(self) -> Dict[str, Any]:
        """
        Get capital overview.
        
        Returns:
            Capital overview dictionary
        """
        try:
            # This endpoint would need to be added to REST API
            result = self.api_client._get("/capital/overview")
            if result:
                return result
        except Exception as e:
            DebugUtils.log_error(e, "Error getting capital overview")
        
        # Fallback to default if API unavailable
        return {
            "total": 100000.0,
            "available": 75000.0,
            "allocated": 20000.0,
            "reserved": 5000.0
        }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions.
        
        Returns:
            List of position dictionaries
        """
        try:
            return self.api_client.get_positions()
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
        try:
            return self.api_client.get_orders(status=status)
        except Exception as e:
            DebugUtils.log_error(e, "Error getting orders")
            return []
    
    def get_data_health(self) -> Dict[str, Any]:
        """
        Get data health status.
        
        Returns:
            Data health dictionary
        """
        try:
            return self.api_client.get_data_health()
        except Exception as e:
            DebugUtils.log_error(e, "Error getting data health")
            return {
                "overall_status": "UNKNOWN",
                "symbols_checked": 0,
                "green_count": 0,
                "yellow_count": 0,
                "red_count": 0
            }
    
    def get_market_state(self) -> Dict[str, Any]:
        """
        Get current market state.
        
        Returns:
            Market state dictionary
        """
        try:
            state = self.api_client.get_market_state()
            if state:
                return state
        except Exception as e:
            DebugUtils.log_error(e, "Error getting market state")
        
        # Fallback to default if API unavailable
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
        try:
            return self.api_client.get_strategy_performance(strategy_id=strategy_id)
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
        try:
            return self.api_client.get_opportunities(limit=limit)
        except Exception as e:
            DebugUtils.log_error(e, "Error getting opportunities")
            return []
    
    def get_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent signals.
        
        Args:
            limit: Maximum number of signals
            
        Returns:
            List of signal dictionaries
        """
        try:
            return self.api_client.get_signals(limit=limit)
        except Exception as e:
            DebugUtils.log_error(e, "Error getting signals")
            return []


# Global instance (would be initialized by main app)
_ui_data_service: Optional[UIDataService] = None


def get_ui_data_service() -> UIDataService:
    """Get global UI data service instance."""
    global _ui_data_service
    if _ui_data_service is None:
        from ui.services.api_client import get_api_client
        _ui_data_service = UIDataService(api_client=get_api_client())
    return _ui_data_service


def set_ui_data_service(service: UIDataService):
    """Set global UI data service instance."""
    global _ui_data_service
    _ui_data_service = service

