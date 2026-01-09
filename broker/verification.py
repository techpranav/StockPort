"""
SmartAPI Installation Verification

Verifies that SmartApi and pycryptodome are correctly installed and importable.
"""

from typing import Tuple
from utils.debug_utils import DebugUtils


def verify_smartapi_installation() -> Tuple[bool, str]:
    """
    Verify SmartAPI installation and dependencies.
    
    Checks:
    1. pycryptodome (Crypto.Cipher.AES) is available
    2. SmartConnect can be imported from SmartApi.smartConnect
    
    Returns:
        Tuple of (success: bool, message: str)
        
    Raises:
        ImportError: If any required import fails
    """
    errors = []
    
    # Check pycryptodome
    try:
        from Crypto.Cipher import AES
        DebugUtils.info("PyCryptodome OK")
    except ImportError as e:
        error_msg = f"PyCryptodome import failed: {e}"
        errors.append(error_msg)
        DebugUtils.error(error_msg)
        raise ImportError(
            "pycryptodome is required but not available. "
            "Install it with: pip install pycryptodome"
        ) from e
    
    # Check SmartConnect import
    try:
        from SmartApi.smartConnect import SmartConnect
        DebugUtils.info("SmartApi SmartConnect OK")
    except ImportError as e:
        error_msg = f"SmartApi SmartConnect import failed: {e}"
        errors.append(error_msg)
        DebugUtils.error(error_msg)
        raise ImportError(
            "SmartApi SmartConnect is required but not available. "
            "Ensure SmartApi>=1.1.0 is installed. "
            "Install with: pip install SmartApi --no-deps (then install pycryptodome separately)"
        ) from e
    
    if errors:
        return False, "; ".join(errors)
    
    return True, "PyCryptodome OK; SmartApi SmartConnect OK"


def verify_and_log() -> None:
    """
    Verify installation and log results.
    
    This is a convenience function that calls verify_smartapi_installation()
    and logs the results.
    """
    try:
        success, message = verify_smartapi_installation()
        if success:
            DebugUtils.info(f"✅ SmartAPI verification passed: {message}")
        else:
            DebugUtils.error(f"❌ SmartAPI verification failed: {message}")
    except ImportError as e:
        DebugUtils.error(f"❌ SmartAPI verification error: {e}")


if __name__ == "__main__":
    """Run verification when executed directly."""
    import sys
    
    try:
        success, message = verify_smartapi_installation()
        if success:
            print("✅ SmartAPI verification passed")
            print(f"   {message}")
            sys.exit(0)
        else:
            print("❌ SmartAPI verification failed")
            print(f"   {message}")
            sys.exit(1)
    except ImportError as e:
        print(f"❌ SmartAPI verification error: {e}")
        sys.exit(1)

