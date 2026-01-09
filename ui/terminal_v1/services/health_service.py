"""
Health Monitoring Service

Monitors health of all system components, data providers, and services.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

from utils.debug_utils import DebugUtils


class HealthService:
    """
    Health monitoring service for all system components.
    
    Checks:
    - Backend API availability
    - Data providers (Indian Stocks, US Stocks, Equity, Historical, Options, F&O)
    - Analysis services
    - Backtesting services
    """
    
    def __init__(self):
        """Initialize health service."""
        self._last_check: Optional[datetime] = None
        self._check_interval = 5  # Check every 5 seconds
        self._health_cache: Dict[str, Any] = {}
        self._cache_ttl = 3  # Cache for 3 seconds
    
    def check_backend_health(self) -> Dict[str, Any]:
        """
        Check backend API health.
        
        Returns:
            Health status dict with status, latency, timestamp
        """
        try:
            from ui.terminal_v1.services.ui_data_service import get_ui_data_service
            data_service = get_ui_data_service()
            
            start_time = time.time()
            status = data_service.get_system_status()
            latency_ms = (time.time() - start_time) * 1000
            
            if status and status.get("status") != "ERROR":
                return {
                    "status": "HEALTHY",
                    "latency_ms": round(latency_ms, 2),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Backend is responding"
                }
            else:
                return {
                    "status": "UNHEALTHY",
                    "latency_ms": round(latency_ms, 2),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Backend returned error status"
                }
        except Exception as e:
            return {
                "status": "DOWN",
                "latency_ms": None,
                "timestamp": datetime.now().isoformat(),
                "message": f"Backend is down: {str(e)}",
                "error": str(e)
            }
    
    def check_data_provider_health(self, provider_type: str) -> Dict[str, Any]:
        """
        Check health of a specific data provider type.
        
        Args:
            provider_type: Type of provider (indian_stocks, us_stocks, equity, historical, options, fno)
            
        Returns:
            Health status dict
        """
        try:
            from ui.terminal_v1.services.ui_data_service import get_ui_data_service
            data_service = get_ui_data_service()
            
            # Get data health from service
            data_health = data_service.get_data_health()
            
            # If no health data from API, try to determine status from backend availability
            if not data_health:
                # Check if backend is available
                backend_health = self.check_backend_health()
                if backend_health.get("status") == "DOWN":
                    return {
                        "status": "UNAVAILABLE",
                        "timestamp": datetime.now().isoformat(),
                        "message": "Backend is down, cannot check provider health"
                    }
                else:
                    # Backend is up but no health data - assume operational
                    return {
                        "status": "OPERATIONAL",
                        "timestamp": datetime.now().isoformat(),
                        "message": f"{provider_type} provider is operational (backend available)"
                    }
            
            # Map provider types to health keys
            provider_map = {
                "indian_stocks": ["indian_equity", "indian_stocks", "nse"],
                "us_stocks": ["us_equity", "us_stocks", "nyse"],
                "equity": ["equity", "stocks"],
                "historical": ["historical", "history"],
                "options": ["options", "option_chain"],
                "fno": ["futures_options", "fno", "futures"]
            }
            
            # Try multiple possible keys
            health_keys = provider_map.get(provider_type, [provider_type])
            provider_health = None
            
            for key in health_keys:
                if key in data_health:
                    provider_health = data_health.get(key)
                    break
            
            if provider_health and isinstance(provider_health, dict):
                status = provider_health.get("status", "OPERATIONAL")
                # Normalize status values
                if status in ["PASS", "ENABLED", "OK"]:
                    status = "HEALTHY"
                elif status in ["FAIL", "DISABLED", "ERROR"]:
                    status = "UNHEALTHY"
                
                return {
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                    "message": provider_health.get("message", f"{provider_type} provider status: {status}"),
                    "details": provider_health
                }
            else:
                # No specific health data, but backend is available
                return {
                    "status": "OPERATIONAL",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"{provider_type} provider is operational"
                }
                
        except Exception as e:
            return {
                "status": "ERROR",
                "timestamp": datetime.now().isoformat(),
                "message": f"Error checking {provider_type}: {str(e)}",
                "error": str(e)
            }
    
    def check_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        Check health of all data providers.
        
        Returns:
            Dict mapping provider type to health status
        """
        providers = [
            "indian_stocks",
            "us_stocks",
            "equity",
            "historical",
            "options",
            "fno"
        ]
        
        results = {}
        for provider in providers:
            results[provider] = self.check_data_provider_health(provider)
        
        return results
    
    def check_analysis_health(self) -> Dict[str, Any]:
        """
        Check analysis service health.
        
        Returns:
            Health status dict
        """
        try:
            from ui.terminal_v1.services.ui_data_service import get_ui_data_service
            data_service = get_ui_data_service()
            
            # Try to get algo confidence as a health check
            start_time = time.time()
            confidence = data_service.get_algo_confidence()
            latency_ms = (time.time() - start_time) * 1000
            
            if confidence is not None and confidence >= 0:
                return {
                    "status": "HEALTHY",
                    "latency_ms": round(latency_ms, 2),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Analysis service is operational",
                    "confidence": confidence
                }
            else:
                return {
                    "status": "UNHEALTHY",
                    "latency_ms": round(latency_ms, 2),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Analysis service returned invalid data"
                }
        except Exception as e:
            return {
                "status": "DOWN",
                "latency_ms": None,
                "timestamp": datetime.now().isoformat(),
                "message": f"Analysis service error: {str(e)}",
                "error": str(e)
            }
    
    def check_backtesting_health(self) -> Dict[str, Any]:
        """
        Check backtesting service health.
        
        Returns:
            Health status dict
        """
        try:
            # Try to import backtest engine
            from services.backtesting.backtest_engine import BacktestEngine
            from services.storage.backtest_storage import BacktestStorage
            
            # Try to initialize (lightweight check)
            storage = BacktestStorage()
            
            return {
                "status": "HEALTHY",
                "timestamp": datetime.now().isoformat(),
                "message": "Backtesting service is available"
            }
        except ImportError as e:
            return {
                "status": "UNAVAILABLE",
                "timestamp": datetime.now().isoformat(),
                "message": f"Backtesting service not available: {str(e)}",
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "timestamp": datetime.now().isoformat(),
                "message": f"Backtesting service error: {str(e)}",
                "error": str(e)
            }
    
    def get_comprehensive_health(self) -> Dict[str, Any]:
        """
        Get comprehensive health status for all services.
        
        Returns:
            Complete health status dict
        """
        # Check if cache is still valid
        now = datetime.now()
        if (self._last_check and 
            (now - self._last_check).total_seconds() < self._cache_ttl and
            self._health_cache):
            return self._health_cache
        
        # Perform all health checks
        backend_health = self.check_backend_health()
        providers_health = self.check_all_providers()
        analysis_health = self.check_analysis_health()
        backtesting_health = self.check_backtesting_health()
        
        # Determine overall system health
        all_statuses = [backend_health.get("status")]
        all_statuses.extend([p.get("status") for p in providers_health.values()])
        all_statuses.append(analysis_health.get("status"))
        all_statuses.append(backtesting_health.get("status"))
        
        if "DOWN" in all_statuses or "ERROR" in all_statuses:
            overall_status = "CRITICAL"
        elif "UNHEALTHY" in all_statuses or "UNAVAILABLE" in all_statuses:
            overall_status = "DEGRADED"
        elif "UNKNOWN" in all_statuses:
            overall_status = "UNKNOWN"
        else:
            overall_status = "HEALTHY"
        
        health_data = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "backend": backend_health,
            "providers": providers_health,
            "analysis": analysis_health,
            "backtesting": backtesting_health,
            "services": {
                "Data Fetch for Indian Stocks": providers_health.get("indian_stocks", {}),
                "Data Fetch for US Stocks": providers_health.get("us_stocks", {}),
                "Equity": providers_health.get("equity", {}),
                "Historical Data": providers_health.get("historical", {}),
                "Options data": providers_health.get("options", {}),
                "Future & Options": providers_health.get("fno", {}),
                "Backtesting": backtesting_health,
                "Analysis": analysis_health
            }
        }
        
        # Cache the result
        self._health_cache = health_data
        self._last_check = now
        
        return health_data
    
    def is_backend_down(self) -> bool:
        """
        Quick check if backend is down.
        
        Returns:
            True if backend is down
        """
        backend_health = self.check_backend_health()
        return backend_health.get("status") == "DOWN"


# Singleton instance
_health_service_instance: Optional[HealthService] = None


def get_health_service() -> HealthService:
    """Get singleton health service instance."""
    global _health_service_instance
    if _health_service_instance is None:
        _health_service_instance = HealthService()
    return _health_service_instance

