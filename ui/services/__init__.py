"""
UI Services Module

Provides data access and integration services for UI components.
"""

from ui.services.ui_data_service import UIDataService, get_ui_data_service, set_ui_data_service
from ui.services.metric_deriver import MetricDeriver, get_metric_deriver
from ui.services.polling_service import PollingService, get_polling_service
from ui.services.websocket_client import WebSocketClient, get_websocket_client

__all__ = [
    'UIDataService',
    'get_ui_data_service',
    'set_ui_data_service',
    'MetricDeriver',
    'get_metric_deriver',
    'PollingService',
    'get_polling_service',
    'WebSocketClient',
    'get_websocket_client',
]

