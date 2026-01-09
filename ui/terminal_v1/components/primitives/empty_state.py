"""
Empty State Primitive

Reassuring empty states with operational cues.
"""

import streamlit as st
from typing import Optional
from datetime import datetime

from ui.terminal_v1.components.primitives.live_indicator import render_live_indicator


def render_empty_state(
    title: str,
    description: str,
    icon: str = "◌",
    show_live: bool = True,
    timestamp: Optional[str] = None
) -> None:
    """
    Render a reassuring empty state with operational cues.
    
    Args:
        title: Empty state title
        description: Empty state description
        icon: Optional icon character
        show_live: Show LIVE indicator
        timestamp: Optional timestamp text
    """
    live_html = ''
    if show_live:
        live_html = '<div class="sp-empty-state-meta"><span class="sp-live-dot"></span><span>LIVE</span></div>'
    
    timestamp_html = ''
    if timestamp:
        timestamp_html = f'<div class="sp-empty-state-meta" style="margin-top: var(--spacing-xs);">{timestamp}</div>'
    
    st.markdown(
        f'''
        <div class="sp-empty-state">
            <div class="sp-empty-state-icon">{icon}</div>
            <div class="sp-empty-state-title">{title}</div>
            <div class="sp-empty-state-desc">{description}</div>
            {live_html}
            {timestamp_html}
        </div>
        ''',
        unsafe_allow_html=True
    )

