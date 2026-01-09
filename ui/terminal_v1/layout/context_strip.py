"""
Context Strip

Z3: Filters / Scope strip
"""

import streamlit as st
from typing import Optional, Dict, Any


def render_context_strip(filters: Optional[Dict[str, Any]] = None) -> None:
    """
    Render Z3: Context Strip (filters / scope).
    
    Args:
        filters: Optional filter configuration
    """
    st.markdown(
        '<div class="sp-z3">',
        unsafe_allow_html=True
    )
    
    # Filters will be rendered here by workspace
    # This is just the container
    
    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

