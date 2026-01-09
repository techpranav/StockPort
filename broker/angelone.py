"""
Angel One SmartAPI Integration Wrapper

This module provides the ONLY direct import point for SmartApi in the codebase.
All other modules should import SmartConnect from broker.angelone (or broker).

IMPORTANT:
- DO NOT import SmartConnect using `from SmartApi import SmartConnect` - this fails
- Always use: `from SmartApi.smartConnect import SmartConnect`
- PyCrypto is NOT used - we use pycryptodome as a drop-in replacement
- Ignore pip warnings about PyCrypto dependency conflicts - runtime imports are correct
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # For type checking only
    from SmartApi.smartConnect import SmartConnect
else:
    # Runtime import - this is the ONLY place where SmartApi is directly imported
    try:
        from SmartApi.smartConnect import SmartConnect
    except ImportError as e:
        raise ImportError(
            "Failed to import SmartConnect from SmartApi.smartConnect. "
            "Ensure SmartApi>=1.1.0 is installed and pycryptodome is available. "
            f"Original error: {e}"
        ) from e

__all__ = ['SmartConnect']

