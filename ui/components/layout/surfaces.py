"""
Surface helpers.

Streamlit does not provide first-class CSS class hooks for containers.
We use a small HTML wrapper to apply visual hierarchy and spacing.

Note: This is layout/styling only. No new features or data.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

import streamlit as st


@contextmanager
def sp_surface(css_class: str, aria_label: Optional[str] = None) -> Iterator[None]:
    """
    Wrap subsequent Streamlit elements in a styled surface.

    This relies on Streamlit rendering order; the wrapper is used throughout the UI
    to create consistent L1/L2/L3 hierarchy without adding extra components.

    Args:
        css_class: Space-separated CSS classes to apply to the wrapper.
        aria_label: Optional aria-label for accessibility.
    """
    aria_attr = f' aria-label="{aria_label}"' if aria_label else ""
    st.markdown(f'<div class="{css_class}"{aria_attr}>', unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown("</div>", unsafe_allow_html=True)


