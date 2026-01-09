"""
Section Header Primitive
"""

import streamlit as st
from typing import Optional


def render_section_header(text: str, subtitle: Optional[str] = None) -> None:
    """
    Render a section header with optional subtitle.
    
    Args:
        text: Header text
        subtitle: Optional subtitle text
    """
    subtitle_html = f'<div class="sp-section-subtitle">{subtitle}</div>' if subtitle else ''
    st.markdown(
        f'<h3 class="sp-section-header">{text}</h3>{subtitle_html}',
        unsafe_allow_html=True
    )

