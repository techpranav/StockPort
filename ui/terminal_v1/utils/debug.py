"""
Debug Utilities

Simple logging for terminal_v1 UI.
"""

from typing import Any


def log(message: str, level: str = "INFO") -> None:
    """
    Simple log function.
    
    Args:
        message: Log message
        level: Log level (INFO, WARNING, ERROR)
    """
    # In production, this would use proper logging
    # For now, just print (will be replaced with proper logger)
    print(f"[{level}] {message}")

