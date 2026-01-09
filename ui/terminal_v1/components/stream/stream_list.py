"""
Stream List Component

Container for dense, scrollable stream rows.
"""

import streamlit as st
from typing import List, Dict, Any, Callable, Optional


def render_stream_list(
    items: List[Dict[str, Any]],
    render_item: Callable[[Dict[str, Any], int], None],
    empty_message: Optional[str] = None
) -> None:
    """
    Render a stream list.
    
    Args:
        items: List of items to render
        render_item: Function to render each item (item, index) -> None
        empty_message: Optional empty state message
    """
    if not items:
        if empty_message:
            st.markdown(f'<div style="color: var(--color-muted); padding: var(--spacing-lg); text-align: center;">{empty_message}</div>', unsafe_allow_html=True)
        return
    
    for idx, item in enumerate(items):
        render_item(item, idx)

