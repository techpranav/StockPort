"""
Terminal v1 Application Entry Point

Clean, professional trading terminal UI.
"""

import sys
from pathlib import Path

# Setup paths FIRST - before any other imports
# Get project root (2 levels up: ui/terminal_v1/app.py -> ui/ -> project_root/)
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from ui.terminal_v1.layout.shell import render_shell
from ui.terminal_v1.workspaces.discover import (
    render_discover_context_strip,
    render_discover_canvas
)
from ui.terminal_v1.workspaces.insight import (
    render_insight_context_strip,
    render_insight_canvas
)
from ui.terminal_v1.workspaces.decide import (
    render_decide_context_strip,
    render_decide_canvas
)
from ui.terminal_v1.workspaces.execute import (
    render_execute_context_strip,
    render_execute_canvas
)
from ui.terminal_v1.workspaces.review import (
    render_review_context_strip,
    render_review_canvas
)
from ui.terminal_v1.workspaces.backtest import (
    render_backtest_context_strip,
    render_backtest_canvas
)
from ui.terminal_v1.workspaces.health import (
    render_health_context_strip,
    render_health_canvas
)
from ui.terminal_v1.workspaces.export import (
    render_export_context_strip,
    render_export_canvas
)
from ui.terminal_v1.layout.canvas import render_canvas


def main() -> None:
    """Main application entry point."""
    # Check URL parameters for workspace
    query_params = st.query_params
    if 'active_workspace' in query_params:
        workspace_from_url = query_params['active_workspace']
        if workspace_from_url in ['discover', 'insight', 'decide', 'execute', 'review', 'backtest', 'health', 'export']:
            st.session_state.active_workspace = workspace_from_url
    
    # Initialize session state
    if 'active_workspace' not in st.session_state:
        st.session_state.active_workspace = 'discover'
    
    if 'ui_theme' not in st.session_state:
        st.session_state.ui_theme = 'dark'

    # Handle workspace changes
    def on_workspace_change(new_workspace: str) -> None:
        """Handle workspace change and update session state."""
        # Update session state immediately
        st.session_state.active_workspace = new_workspace

    # Apply theme via CSS class injection
    theme = st.session_state.ui_theme
    if theme == 'light':
        st.markdown(
            '''
            <style>
            :root {
                --color-bg: #FFFFFF;
                --color-bg-2: #F9FAFB;
                --color-panel: rgba(243, 244, 246, 0.8);
                --color-border: rgba(209, 213, 219, 0.5);
                --color-text: #111827;
                --color-text-2: #374151;
                --color-muted: rgba(107, 114, 128, 0.7);
                --color-accent: #2563EB;
                --color-profit: #16A34A;
                --color-loss: #DC2626;
                --color-warn: #D97706;
            }
            </style>
            ''',
            unsafe_allow_html=True
        )

    # Render shell with workspace
    active_workspace = st.session_state.active_workspace

    # Route to appropriate workspace
    if active_workspace == 'discover':
        render_shell(
            active_workspace=active_workspace,
            on_workspace_change=on_workspace_change,
            render_z3=render_discover_context_strip,
            render_z4=lambda: render_canvas(render_discover_canvas)
        )
    elif active_workspace == 'insight':
        render_shell(
            active_workspace=active_workspace,
            on_workspace_change=on_workspace_change,
            render_z3=render_insight_context_strip,
            render_z4=lambda: render_canvas(render_insight_canvas)
        )
    elif active_workspace == 'decide':
        render_shell(
            active_workspace=active_workspace,
            on_workspace_change=on_workspace_change,
            render_z3=render_decide_context_strip,
            render_z4=lambda: render_canvas(render_decide_canvas)
        )
    elif active_workspace == 'execute':
        render_shell(
            active_workspace=active_workspace,
            on_workspace_change=on_workspace_change,
            render_z3=render_execute_context_strip,
            render_z4=lambda: render_canvas(render_execute_canvas)
        )
    elif active_workspace == 'review':
        render_shell(
            active_workspace=active_workspace,
            on_workspace_change=on_workspace_change,
            render_z3=render_review_context_strip,
            render_z4=lambda: render_canvas(render_review_canvas)
        )
    elif active_workspace == 'backtest':
        render_shell(
            active_workspace=active_workspace,
            on_workspace_change=on_workspace_change,
            render_z3=render_backtest_context_strip,
            render_z4=lambda: render_canvas(render_backtest_canvas)
        )
    elif active_workspace == 'health':
        render_shell(
            active_workspace=active_workspace,
            on_workspace_change=on_workspace_change,
            render_z3=render_health_context_strip,
            render_z4=lambda: render_canvas(render_health_canvas)
        )
    elif active_workspace == 'export':
        render_shell(
            active_workspace=active_workspace,
            on_workspace_change=on_workspace_change,
            render_z3=render_export_context_strip,
            render_z4=lambda: render_canvas(render_export_canvas)
        )
    else:
        render_shell(
            active_workspace=active_workspace,
            on_workspace_change=on_workspace_change,
            render_z4=lambda: st.error(f"Workspace '{active_workspace}' not found.")
        )


if __name__ == "__main__":
    main()

