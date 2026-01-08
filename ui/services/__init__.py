"""
UI Services Module

Provides data access and integration services for UI components.
"""

from ui.services.ui_data_service import UIDataService, get_ui_data_service, set_ui_data_service

__all__ = [
    'UIDataService',
    'get_ui_data_service',
    'set_ui_data_service'
]

