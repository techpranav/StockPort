"""
Layout Shell

Z1: System Bar
Z2: Workspace Tabs
"""

import streamlit as st
from typing import Callable, Optional

from ui.terminal_v1.services.ui_data_service import get_ui_data_service
from ui.terminal_v1.services.health_service import get_health_service


def render_system_bar() -> None:
    """Render Z1: System Bar with mode selector, controls, and metrics."""
    data_service = get_ui_data_service()
    
    try:
        system_state = data_service.get_system_state() or {}
    except:
        system_state = {}
    
    mode_raw = system_state.get('mode', 'LIVE')
    health = system_state.get('health', 'UNKNOWN')
    
    # Get algo metrics
    try:
        algo_confidence = data_service.get_algo_confidence()
        bias = data_service.get_todays_bias()
    except:
        algo_confidence = 75.0
        bias = "NEUTRAL"
    
    # Check if system is running
    try:
        status = data_service.get_system_status()
        is_running = status.get("is_running", False)
    except:
        is_running = False
    
    # Theme toggle state
    if 'ui_theme' not in st.session_state:
        st.session_state.ui_theme = 'dark'
    
    # System bar layout: Left | Middle | Right
    col_left, col_mid, col_right = st.columns([3, 4, 2])
    
    # Left: Brand + Health
    with col_left:
        # Check backend health
        health_service = get_health_service()
        backend_down = health_service.is_backend_down()
        
        health_class = 'green' if health == 'GREEN' else 'yellow' if health == 'YELLOW' else 'red' if health == 'RED' else 'neutral'
        if backend_down:
            health_class = 'red'
            health = 'DOWN'
        
        # Add blinking class if backend is down
        blink_class = 'sp-health-blink' if backend_down else ''
        
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: var(--spacing-md);">
                <div style="font-weight: var(--font-weight-bold); color: var(--color-text);">
                    STOCKPORT
                </div>
                <span class="sp-status-pill {health_class} {blink_class}">
                    {health}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Middle: Mode + Metrics + Controls
    with col_mid:
        mid_col1, mid_col2, mid_col3, mid_col4, mid_col5 = st.columns([1.5, 1, 1, 1, 1.5])
        
        with mid_col1:
            # Mode selector
            mode_options = ["LIVE", "PAPER", "BACKTEST", "REPLAY"]
            normalized_mode = mode_raw.strip().upper()
            if normalized_mode not in mode_options:
                normalized_mode = "PAPER" if "paper" in mode_raw.lower() else "LIVE" if "live" in mode_raw.lower() else "BACKTEST" if "backtest" in mode_raw.lower() else "REPLAY" if "replay" in mode_raw.lower() else "LIVE"
            
            # Get current mode from session state or use normalized
            current_mode_key = f"system_mode_{normalized_mode}"
            if current_mode_key not in st.session_state:
                st.session_state[current_mode_key] = normalized_mode
            
            # Find index for selectbox
            try:
                current_index = mode_options.index(normalized_mode)
            except ValueError:
                current_index = 0
            
            selected_mode = st.selectbox(
                "Mode",
                mode_options,
                index=current_index,
                key="system_mode_selector",
                label_visibility="collapsed"
            )
            
            # Handle mode change - only if different from current
            if selected_mode != normalized_mode:
                try:
                    result = data_service.execute_command("set_mode", {"mode": selected_mode.lower()})
                    if result.get("success"):
                        # Update session state before rerun
                        st.session_state['last_mode'] = selected_mode
                        st.rerun()
                    else:
                        st.warning(f"Mode change failed: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    # If command fails, still update UI state for visual feedback
                    st.warning(f"Mode change may not have been applied: {str(e)}")
                    st.rerun()
        
        with mid_col2:
            # Algo Confidence
            if algo_confidence is not None:
                conf_color = "#22C55E" if algo_confidence >= 80 else "#CBD5E1" if algo_confidence >= 60 else "#F59E0B" if algo_confidence >= 40 else "#EF4444"
                st.markdown(
                    f'<div style="text-align: center;"><span style="color: var(--color-muted); font-size: var(--font-size-xs);">Algo</span><br><strong style="color: {conf_color};">{int(algo_confidence)}</strong></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div style="text-align: center;"><span style="color: var(--color-muted); font-size: var(--font-size-xs);">Algo</span><br><strong style="color: var(--color-red);">--</strong></div>',
                    unsafe_allow_html=True
                )
        
        with mid_col3:
            # Bias
            bias_color = "#22C55E" if "bull" in bias.lower() or "up" in bias.lower() else "#EF4444" if "bear" in bias.lower() or "down" in bias.lower() else "#F59E0B"
            st.markdown(
                f'<div style="text-align: center;"><span style="color: var(--color-muted); font-size: var(--font-size-xs);">Bias</span><br><strong style="color: {bias_color};">{bias.upper()}</strong></div>',
                unsafe_allow_html=True
            )
        
        with mid_col4:
            # Start/Pause button
            button_label = "⏸" if is_running else "▶"
            button_help = "Pause system" if is_running else "Start system"
            if st.button(button_label, key="system_pause_resume", help=button_help):
                try:
                    if is_running:
                        result = data_service.execute_command("pause", {})
                    else:
                        result = data_service.execute_command("start", {})
                    if result.get("success"):
                        st.rerun()
                    else:
                        st.warning(f"Command failed: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    st.warning(f"Command execution failed: {str(e)}")
        
        with mid_col5:
            # Kill button
            if st.button("⛔", key="system_kill", help="Emergency stop"):
                try:
                    result = data_service.execute_command("kill", {})
                    if result.get("success"):
                        st.error("System stopped")
                        st.rerun()
                    else:
                        st.warning(f"Kill command failed: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    st.warning(f"Kill command failed: {str(e)}")
    
    # Right: Live indicator + Theme toggle
    with col_right:
        right_col1, right_col2 = st.columns([1, 1])
        
        with right_col1:
            # Live indicator
            live_color = "#22C55E" if is_running else "#94A3B8"
            st.markdown(
                f'<div style="display: flex; align-items: center; gap: var(--spacing-xs);"><span class="sp-live-dot" style="background: {live_color};"></span><span style="color: var(--color-text-2); font-size: var(--font-size-xs);">{"LIVE" if is_running else "IDLE"}</span></div>',
                unsafe_allow_html=True
            )
        
        with right_col2:
            # Theme toggle
            theme_icon = '☀️' if st.session_state.ui_theme == 'dark' else '🌙'
            if st.button(theme_icon, key="theme_toggle", help="Toggle light/dark theme", use_container_width=False):
                st.session_state.ui_theme = 'light' if st.session_state.ui_theme == 'dark' else 'dark'
                st.rerun()
    
    # Wrap in system bar container
    st.markdown('<div class="sp-z1"></div>', unsafe_allow_html=True)


def render_workspace_tabs(active_workspace: str, on_workspace_change: Callable[[str], None]) -> None:
    """Render Z2: Workspace Tabs (horizontal only, subtle mode indicators)."""
    workspaces = ['discover', 'insight', 'decide', 'execute', 'review', 'backtest', 'health', 'export']
    
    # Use Streamlit columns with styled buttons
    cols = st.columns(len(workspaces), gap="small")
    
    for idx, ws in enumerate(workspaces):
        with cols[idx]:
            is_active = ws == active_workspace
            # Use consistent key for each workspace
            button_key = f"tab_{ws}"
            clicked = st.button(ws.upper(), key=button_key, use_container_width=True)
            if clicked:
                # Update state immediately before callback
                st.session_state.active_workspace = ws
                on_workspace_change(ws)
                # Force rerun to reflect changes
                st.rerun()
    
    # Style tabs to be subtle and mode-like
    st.markdown(
        f'''
        <style>
        .sp-z2 button {{
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid transparent !important;
            color: var(--color-muted) !important;
            font-weight: var(--font-weight-normal) !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: var(--spacing-xs) 0 !important;
        }}
        .sp-z2 button:hover {{
            color: var(--color-text-2) !important;
        }}
        .sp-z2 button[key="tab_{active_workspace}"] {{
            color: var(--color-text) !important;
            border-bottom: 1px solid var(--color-accent) !important;
            font-weight: var(--font-weight-medium) !important;
        }}
        </style>
        ''',
        unsafe_allow_html=True
    )


def render_shell(
    active_workspace: str,
    on_workspace_change: Callable[[str], None],
    render_z3: Optional[Callable[[], None]] = None,
    render_z4: Optional[Callable[[], None]] = None
) -> None:
    """
    Render complete shell: Z1 + Z2 + Z3 + Z4.
    
    Args:
        active_workspace: Current workspace name
        on_workspace_change: Callback for workspace changes
        render_z3: Optional function to render Z3 context strip
        render_z4: Function to render Z4 main canvas
    """
    # Inject CSS
    from pathlib import Path
    css_path = Path(__file__).parent.parent / 'styles' / 'main.css'
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError as e:
        # Fallback if CSS not found - use minimal styles
        st.markdown('''
        <style>
        :root {
            --color-bg: #0B1220;
            --color-text: #F9FAFB;
            --color-muted: rgba(209, 213, 219, 0.62);
        }
        body { background: var(--color-bg); color: var(--color-text); }
        </style>
        ''', unsafe_allow_html=True)
    
    # Z1: System Bar
    render_system_bar()
    
    # Z2: Workspace Tabs
    render_workspace_tabs(active_workspace, on_workspace_change)
    
    # Z3: Context Strip (if provided)
    if render_z3:
        render_z3()
    
    # Z4: Main Canvas
    if render_z4:
        render_z4()

