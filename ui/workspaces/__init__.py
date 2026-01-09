"""
Workspaces Module

Core workspaces for Stockport v5 trading operating system.
"""

from ui.workspaces.router import get_active_workspace, set_active_workspace
from ui.workspaces.insight import render_insight_workspace
from ui.workspaces.discover import render_discover_workspace
from ui.workspaces.decide import render_decide_workspace
from ui.workspaces.execute import render_execute_workspace
from ui.workspaces.review import render_review_workspace

__all__ = [
    'get_active_workspace',
    'set_active_workspace',
    'render_insight_workspace',
    'render_discover_workspace',
    'render_decide_workspace',
    'render_execute_workspace',
    'render_review_workspace',
]

