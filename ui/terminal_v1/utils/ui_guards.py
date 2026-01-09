"""
UI Guards

Validation and safety checks for UI layer.
"""

from typing import Any, Dict, List


def validate_workspace_name(name: str) -> bool:
    """
    Validate workspace name.
    
    Args:
        name: Workspace name
        
    Returns:
        True if valid
    """
    valid_workspaces = ['discover', 'insight', 'decide', 'execute', 'review']
    return name in valid_workspaces


def sanitize_data(data: Any) -> Any:
    """
    Sanitize data for UI display.
    
    Args:
        data: Data to sanitize
        
    Returns:
        Sanitized data
    """
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    elif isinstance(data, str):
        # Basic XSS prevention
        return data.replace('<', '&lt;').replace('>', '&gt;')
    return data

