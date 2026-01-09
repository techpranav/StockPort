"""
Empty State Component

Intentional, calm empty states used across the Trading OS UI.
This is presentation-only and does not change behavior or data.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st


def render_empty_state(
    title: str,
    description: str,
    icon: str = "◌",
    hint: Optional[str] = None,
) -> None:
    """
    Render a consistent empty state.

    Args:
        title: Short headline (calm tone)
        description: One-sentence description
        icon: Subtle icon glyph (keep minimal)
        hint: Optional secondary hint (one short phrase)
    """
    hint_html = f'<div class="sp-empty-hint">{hint}</div>' if hint else ""
    st.markdown(
        f"""
        <div class="sp-empty">
          <div class="sp-empty-icon">{icon}</div>
          <div class="sp-empty-body">
            <div class="sp-empty-title">{title}</div>
            <div class="sp-empty-desc">{description}</div>
            {hint_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


