"""
Live Indicator Primitive

Operational status indicators for context strip.
"""

import streamlit as st
from typing import Literal

Status = Literal['live', 'idle']


def render_live_indicator(status: Status = 'live', label: str = "LIVE") -> None:
    """
    Render a live/idle indicator.
    
    Args:
        status: 'live' or 'idle'
        label: Label text
    """
    dot_class = "sp-live-dot" if status == 'live' else "sp-live-dot idle"
    st.markdown(
        f'''
        <div class="sp-live-indicator">
            <span class="{dot_class}"></span>
            <span style="color: var(--color-text-2); font-size: var(--font-size-xs);">{label}</span>
        </div>
        ''',
        unsafe_allow_html=True
    )

