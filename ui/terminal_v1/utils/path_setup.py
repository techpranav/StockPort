"""
Path Setup Utility

Ensures project root is in Python path for imports.
This must be imported FIRST before any other ui.terminal_v1 imports.
"""

import sys
import os
from pathlib import Path


def setup_paths() -> None:
    """Add project root to Python path."""
    # Get project root (3 levels up from this file: ui/terminal_v1/utils/path_setup.py)
    # path_setup.py -> utils/ -> terminal_v1/ -> ui/ -> project_root/
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    project_root_str = str(project_root)
    
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

