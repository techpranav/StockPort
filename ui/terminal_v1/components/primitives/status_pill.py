"""
Status Pill Primitive
"""

import streamlit as st
from typing import Literal

StatusColor = Literal['green', 'red', 'yellow', 'neutral']


def render_status_pill(text: str, color: StatusColor = 'neutral') -> None:
    """
    Render a status pill.
    
    Args:
        text: Status text
        color: Status color (green, red, yellow, neutral)
    """
    st.markdown(
        f'<span class="sp-status-pill {color}">{text}</span>',
        unsafe_allow_html=True
    )

