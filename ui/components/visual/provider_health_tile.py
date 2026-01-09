"""
Provider Health Tile Component

Provider status tiles (Angel/NSE/Backup) with Green/Amber/Red glow,
latency display, and drop rate metrics.
"""

import streamlit as st
from typing import Dict, Any, Optional

from ui.components.visual.empty_state import render_empty_state


def render_provider_health_tile(
    provider_name: str,
    status: str,
    latency_ms: Optional[float] = None,
    drop_rate: Optional[float] = None,
    error_message: Optional[str] = None
) -> None:
    """
    Render a provider health tile.
    
    Args:
        provider_name: Name of the data provider (e.g., "Angel One", "NSE")
        status: Health status ("GREEN", "YELLOW", "RED")
        latency_ms: Latency in milliseconds
        drop_rate: Drop rate percentage (0-100)
        error_message: Error message if status is RED
    """
    # Determine status color
    if status == "GREEN":
        color = '#22C55E'
        status_text = "HEALTHY"
    elif status == "YELLOW":
        color = '#F59E0B'
        status_text = "WARNING"
    elif status == "RED":
        color = '#EF4444'
        status_text = "ERROR"
    else:
        render_empty_state(
            "Provider status unavailable",
            "Health details aren’t available for this provider right now.",
            icon="◌",
        )
        return
    
    rgb_color = _hex_to_rgb(color)

    # Escape HTML in error message to prevent injection
    error_escaped = ""
    if error_message and status == "RED":
        error_escaped = (
            error_message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

    latency_html = (
        f'<div class="sp-provider-metric"><span>Latency</span><strong>{latency_ms:.0f}ms</strong></div>'
        if latency_ms is not None
        else ""
    )
    drop_html = (
        f'<div class="sp-provider-metric"><span>Drop rate</span><strong>{drop_rate:.2f}%</strong></div>'
        if drop_rate is not None
        else ""
    )
    err_html = (
        f'<div class="sp-provider-metric"><span>Last error</span>'
        f'<strong style="color:#EF4444">{error_escaped}</strong></div>'
        if error_escaped
        else ""
    )

    st.markdown(
        f"""
        <div class="sp-provider-tile" data-glow="true"
             style="--sp-status: {color}; --sp-status-rgb: {rgb_color};">
          <div class="sp-provider-name">{provider_name}</div>
          <div class="sp-provider-status">{status_text}</div>
          {latency_html}
          {drop_html}
          {err_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB string."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"{r}, {g}, {b}"

