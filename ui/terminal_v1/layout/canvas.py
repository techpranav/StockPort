"""
Canvas

Z4: Main layout wrapper
"""

import streamlit as st
from typing import Callable


def render_canvas(render_content: Callable[[], None]) -> None:
    """
    Render Z4: Main Canvas wrapper.
    
    Args:
        render_content: Function to render canvas content
    """
    st.markdown(
        '<div class="sp-z4">',
        unsafe_allow_html=True
    )
    
    render_content()
    
    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

