"""
Divider Primitive
"""

import streamlit as st


def render_divider() -> None:
    """Render a divider."""
    st.markdown('<hr class="sp-divider" />', unsafe_allow_html=True)

