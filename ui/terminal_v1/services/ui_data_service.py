"""
UI Data Service

Simplified data adapter for terminal_v1 UI.
Wraps legacy service to maintain backend compatibility.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

# Import from services (backend compatibility maintained)
try:
    from ui.services.ui_data_service import UIDataService as LegacyUIDataService
    from ui.services.api_client import get_api_client
except ImportError:
    try:
        # Try alternative import path
        from services.ui_data_service import UIDataService as LegacyUIDataService
        from services.api_client import get_api_client
    except ImportError:
        # Fallback if services not available
        LegacyUIDataService = None
        get_api_client = None


class UIDataService:
    """
    Terminal v1 UI Data Service.
    
    Provides clean interface to backend data.
    """
    
    def __init__(self):
        """Initialize service."""
        if LegacyUIDataService:
            self._legacy_service = LegacyUIDataService()
        else:
            self._legacy_service = None
    
    def get_system_state(self) -> Dict[str, Any]:
        """
        Get system state for Z1.
        
        Returns:
            System state dict with mode, health, etc.
        """
        if not self._legacy_service:
            return {'mode': 'LIVE', 'health': 'UNKNOWN'}
        
        try:
            status = self._legacy_service.get_system_status()
            return {
                'mode': status.get('mode', 'LIVE'),
                'health': status.get('health', 'GREEN'),
                'timestamp': status.get('timestamp', datetime.now().isoformat())
            }
        except:
            return {'mode': 'LIVE', 'health': 'UNKNOWN'}
    
    def get_opportunities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get opportunities for Discover workspace.
        
        Args:
            limit: Maximum number of opportunities
            
        Returns:
            List of opportunity dicts
        """
        if not self._legacy_service:
            return []
        
        try:
            return self._legacy_service.get_opportunities(limit=limit) or []
        except:
            return []
    
    def get_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get signals for Discover workspace.
        
        Args:
            limit: Maximum number of signals
            
        Returns:
            List of signal dicts
        """
        if not self._legacy_service:
            return []
        
        try:
            return self._legacy_service.get_signals(limit=limit) or []
        except:
            return []
    
    def get_algo_confidence(self) -> float:
        """Get algo confidence score (0-100)."""
        if not self._legacy_service:
            return 75.0
        try:
            # Try to get from metric deriver if available
            try:
                from ui.services.metric_deriver import MetricDeriver
            except ImportError:
                from services.metric_deriver import MetricDeriver
            deriver = MetricDeriver(self._legacy_service)
            return deriver.get_algo_confidence()
        except:
            return 75.0
    
    def get_market_readiness(self) -> float:
        """Get market readiness score (0-100)."""
        if not self._legacy_service:
            return 50.0
        try:
            try:
                from ui.services.metric_deriver import MetricDeriver
            except ImportError:
                from services.metric_deriver import MetricDeriver
            deriver = MetricDeriver(self._legacy_service)
            return deriver.get_market_readiness()
        except:
            return 50.0
    
    def get_todays_bias(self) -> str:
        """Get today's market bias."""
        if not self._legacy_service:
            return "NEUTRAL"
        try:
            try:
                from ui.services.metric_deriver import MetricDeriver
            except ImportError:
                from services.metric_deriver import MetricDeriver
            deriver = MetricDeriver(self._legacy_service)
            return deriver.get_todays_bias()
        except:
            return "NEUTRAL"
    
    def get_next_action_eta(self) -> Optional[str]:
        """Get next action ETA."""
        if not self._legacy_service:
            return None
        try:
            try:
                from ui.services.metric_deriver import MetricDeriver
            except ImportError:
                from services.metric_deriver import MetricDeriver
            deriver = MetricDeriver(self._legacy_service)
            return deriver.get_next_action_eta()
        except:
            return None
    
    def get_data_health(self) -> Dict[str, Any]:
        """Get data provider health."""
        if not self._legacy_service:
            return {}
        try:
            return self._legacy_service.get_data_health() or {}
        except:
            return {}
    
    def get_execution_quality(self) -> Dict[str, Any]:
        """Get execution quality metrics."""
        if not self._legacy_service:
            return {}
        try:
            try:
                from ui.services.metric_deriver import MetricDeriver
            except ImportError:
                from services.metric_deriver import MetricDeriver
            deriver = MetricDeriver(self._legacy_service)
            return deriver.get_execution_quality()
        except:
            return {}
    
    def get_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get orders."""
        if not self._legacy_service:
            return []
        try:
            return self._legacy_service.get_orders(limit=limit) or []
        except:
            return []
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get positions."""
        if not self._legacy_service:
            return []
        try:
            return self._legacy_service.get_positions() or []
        except:
            return []
    
    def get_strategy_performance(self) -> List[Dict[str, Any]]:
        """Get strategy performance."""
        if not self._legacy_service:
            return []
        try:
            return self._legacy_service.get_strategy_performance() or []
        except:
            return []
    
    def get_signal_stream(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get signal stream for Decide workspace."""
        if not self._legacy_service:
            return []
        try:
            try:
                from ui.services.metric_deriver import MetricDeriver
            except ImportError:
                from services.metric_deriver import MetricDeriver
            deriver = MetricDeriver(self._legacy_service)
            return deriver.get_signal_stream(limit=limit) or []
        except:
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        if not self._legacy_service:
            return {"is_running": False, "mode": "manual"}
        try:
            return self._legacy_service.get_system_status() or {}
        except:
            return {"is_running": False, "mode": "manual"}
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get current market state."""
        if not self._legacy_service:
            return {"regime": "neutral", "volatility_state": "low", "breadth_state": "mixed", "liquidity_state": "moderate"}
        try:
            return self._legacy_service.get_market_state() or {}
        except:
            return {"regime": "neutral", "volatility_state": "low", "breadth_state": "mixed", "liquidity_state": "moderate"}
    
    def execute_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a system command.
        
        Args:
            command: Command name (start, stop, pause, kill, set_mode)
            params: Command parameters
            
        Returns:
            Command result
        """
        import streamlit as st
        
        if not self._legacy_service:
            # Fallback: update session state for UI-only mode (but don't use widget keys)
            if command == "set_mode" and params:
                mode = params.get('mode', 'live').upper()
                st.session_state['last_mode'] = mode
            elif command in ["start", "pause", "resume"]:
                st.session_state['system_running'] = command in ["start", "resume"]
            elif command == "kill":
                st.session_state['system_running'] = False
            return {"success": True, "message": f"Command {command} executed (UI only - backend not available)"}
        
        try:
            # Try to execute via API client if available
            if hasattr(self._legacy_service, '_api_client'):
                api_client = self._legacy_service._api_client
                if api_client:
                    response = api_client.post("/command", json={
                        "command": command,
                        "parameters": params or {}
                    })
                    if hasattr(response, 'json'):
                        result = response.json()
                        # Update session state for successful commands
                        if result.get("success") and command == "set_mode" and params:
                            st.session_state['last_mode'] = params.get('mode', 'live').upper()
                        return result
                    return {"success": True}
        except Exception as e:
            # Fallback: update session state for UI (but don't use widget keys)
            if command == "set_mode" and params:
                mode = params.get('mode', 'live').upper()
                st.session_state['last_mode'] = mode
            elif command in ["start", "pause", "resume", "kill"]:
                st.session_state['system_running'] = command in ["start", "resume"]
            return {"success": True, "message": f"Command {command} executed (UI only): {str(e)}"}
        
        return {"success": False, "message": "Command execution failed"}


# Singleton instance
_service_instance: Optional[UIDataService] = None


def get_ui_data_service() -> UIDataService:
    """Get singleton UI data service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = UIDataService()
    return _service_instance

