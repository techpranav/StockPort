"""
Stream Row Component

Dense row for signal/opportunity streams.
"""

import streamlit as st
from typing import Optional, Callable


def render_stream_row(
    title: str,
    subtitle: Optional[str] = None,
    right_value: Optional[str] = None,
    status_pill: Optional[str] = None,
    status_color: str = 'neutral',
    on_click: Optional[Callable[[], None]] = None,
    key: Optional[str] = None
) -> None:
    """
    Render a stream row.
    
    Args:
        title: Primary text
        subtitle: Secondary text
        right_value: Value to show on right
        status_pill: Optional status pill text
        status_color: Status pill color
        on_click: Optional click handler
        key: Unique key for Streamlit
    """
    subtitle_html = f'<div class="sp-stream-row-subtitle">{subtitle}</div>' if subtitle else ''
    right_html = f'<div style="color: var(--color-text); font-weight: var(--font-weight-semibold);">{right_value}</div>' if right_value else ''
    pill_html = f'<span class="sp-status-pill {status_color}">{status_pill}</span>' if status_pill else ''
    
    st.markdown(
        f'''
        <div class="sp-stream-row" data-key="{key or ''}">
            <div class="sp-stream-row-left">
                <div class="sp-stream-row-title">{title} {pill_html}</div>
                {subtitle_html}
            </div>
            <div class="sp-stream-row-right">
                {right_html}
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

