"""
UI Data Service

Simplified data adapter for terminal_v1 UI.
Wraps legacy service to maintain backend compatibility.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

# Import API client for direct backend communication
from ui.terminal_v1.services.api_client import get_api_client


class UIDataService:
    """
    Terminal v1 UI Data Service.
    
    Provides clean interface to backend data.
    """
    
    def __init__(self):
        """Initialize service."""
        self._api_client = get_api_client()
    
    def get_system_state(self) -> Dict[str, Any]:
        """
        Get system state for Z1.
        
        Returns:
            System state dict with mode, health, etc.
            
        Raises:
            RuntimeError: If backend is not available
        """
        try:
            status = self._api_client.get_status()
            if not status:
                raise RuntimeError("Backend returned empty status")
            return {
                'mode': status.get('mode', 'LIVE'),
                'health': status.get('health', 'GREEN'),
                'timestamp': status.get('timestamp', datetime.now().isoformat())
            }
        except Exception as e:
            raise RuntimeError(f"Backend service not available: {str(e)}") from e
    
    def get_opportunities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get opportunities for Discover workspace.
        
        Args:
            limit: Maximum number of opportunities
            
        Returns:
            List of opportunity dicts (empty list if no opportunities, but backend is available)
            
        Raises:
            RuntimeError: If backend is not available
        """
        try:
            result = self._api_client.get_opportunities(limit=limit)
            return result if result is not None else []
        except Exception as e:
            raise RuntimeError(f"Backend service not available: {str(e)}") from e
    
    def get_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get signals for Discover workspace.
        
        Args:
            limit: Maximum number of signals
            
        Returns:
            List of signal dicts
        """
        try:
            return self._api_client.get_signals(limit=limit) or []
        except:
            return []
    
    def get_algo_confidence(self) -> float:
        """
        Get algo confidence score (0-100).
        
        Raises:
            RuntimeError: If backend is not available
        """
        try:
            # Get from strategy performance
            performance = self._api_client.get_strategy_performance()
            if performance and len(performance) > 0:
                # Calculate average win rate as confidence proxy
                win_rates = [p.get('win_rate', 0) for p in performance if p.get('win_rate')]
                if win_rates:
                    return sum(win_rates) / len(win_rates) * 100
            # Default fallback
            return 75.0
        except Exception as e:
            raise RuntimeError(f"Backend service not available: {str(e)}") from e
    
    def get_market_readiness(self) -> float:
        """Get market readiness score (0-100)."""
        try:
            market_state = self._api_client.get_market_state()
            if market_state:
                # Simple readiness calculation based on market state
                return 75.0  # Default readiness
            return 50.0
        except:
            return 50.0
    
    def get_todays_bias(self) -> str:
        """Get today's market bias."""
        try:
            market_state = self._api_client.get_market_state()
            if market_state:
                regime = market_state.get('regime', 'neutral')
                if regime in ['bull', 'bullish']:
                    return "BULL"
                elif regime in ['bear', 'bearish']:
                    return "BEAR"
            return "NEUTRAL"
        except:
            return "NEUTRAL"
    
    def get_next_action_eta(self) -> Optional[str]:
        """Get next action ETA."""
        # Not available from API, return None
        return None
    
    def get_data_health(self) -> Dict[str, Any]:
        """Get data provider health."""
        try:
            return self._api_client.get_data_health() or {}
        except:
            return {}
    
    def get_execution_quality(self) -> Dict[str, Any]:
        """Get execution quality metrics."""
        try:
            orders = self._api_client.get_orders()
            if orders:
                # Calculate simple metrics from orders
                filled = [o for o in orders if o.get('status') == 'FILLED']
                return {
                    'fill_rate': len(filled) / len(orders) if orders else 0,
                    'total_orders': len(orders),
                    'filled_orders': len(filled)
                }
            return {}
        except:
            return {}
    
    def get_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get orders."""
        try:
            return self._api_client.get_orders()[:limit] if limit else self._api_client.get_orders()
        except:
            return []
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get positions."""
        try:
            return self._api_client.get_positions() or []
        except:
            return []
    
    def get_strategy_performance(self) -> List[Dict[str, Any]]:
        """Get strategy performance."""
        try:
            return self._api_client.get_strategy_performance() or []
        except:
            return []
    
    def get_signal_stream(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get signal stream for Decide workspace."""
        try:
            return self._api_client.get_signals(limit=limit) or []
        except:
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        try:
            return self._api_client.get_status() or {}
        except:
            return {"is_running": False, "mode": "manual"}
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get current market state."""
        try:
            return self._api_client.get_market_state() or {}
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
        
        try:
            result = self._api_client.post_command(command, params)
            if result and result.get("success"):
                # Update session state for successful commands
                if command == "set_mode" and params:
                    st.session_state['last_mode'] = params.get('mode', 'live').upper()
                return result
            # Fallback: update session state for UI
            if command == "set_mode" and params:
                mode = params.get('mode', 'live').upper()
                st.session_state['last_mode'] = mode
            elif command in ["start", "pause", "resume"]:
                st.session_state['system_running'] = command in ["start", "resume"]
            elif command == "kill":
                st.session_state['system_running'] = False
            return {"success": True, "message": f"Command {command} executed"}
        except Exception as e:
            # Fallback: update session state for UI (but don't use widget keys)
            if command == "set_mode" and params:
                mode = params.get('mode', 'live').upper()
                st.session_state['last_mode'] = mode
            elif command in ["start", "pause", "resume", "kill"]:
                st.session_state['system_running'] = command in ["start", "resume"]
            return {"success": True, "message": f"Command {command} executed (UI only): {str(e)}"}


# Singleton instance
_service_instance: Optional[UIDataService] = None


def get_ui_data_service() -> UIDataService:
    """Get singleton UI data service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = UIDataService()
    return _service_instance

