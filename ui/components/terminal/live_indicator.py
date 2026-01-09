"""
Live indicator components for trader-centric UI.

Provides pulsing dots, timestamps, and refresh indicators to make the UI feel alive.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import streamlit as st


def render_live_dot(color: str = "#22C55E", size: int = 8) -> None:
    """
    Render a pulsing live indicator dot.
    
    Args:
        color: Dot color (default: green for live)
        size: Dot size in pixels
    """
    st.markdown(
        f"""
        <div class="sp-live-dot" style="--sp-dot-color: {color}; --sp-dot-size: {size}px;">
            <span class="sp-live-pulse"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_timestamp(prefix: str = "Updated", show_live: bool = True) -> None:
    """
    Render a live timestamp with optional live indicator.
    
    Args:
        prefix: Text prefix (e.g., "Updated", "Last")
        show_live: Whether to show pulsing live dot
    """
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    
    live_html = '<span class="sp-live-dot-inline"></span>' if show_live else ""
    
    st.markdown(
        f"""
        <div class="sp-timestamp">
            {live_html}
            <span class="sp-timestamp-text">{prefix} {time_str}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_live_badge(text: str = "LIVE", color: str = "#22C55E") -> None:
    """
    Render a live status badge with pulsing animation.
    
    Args:
        text: Badge text
        color: Badge color
    """
    st.markdown(
        f"""
        <div class="sp-live-badge" style="--sp-badge-color: {color};">
            <span class="sp-live-pulse-inline"></span>
            <span>{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

