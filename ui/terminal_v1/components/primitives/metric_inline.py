"""
Metric Inline Primitive
"""

import streamlit as st


def render_metric_inline(label: str, value: str) -> None:
    """
    Render an inline metric (label: value).
    
    Args:
        label: Metric label
        value: Metric value
    """
    st.markdown(
        f'''
        <div class="sp-metric-inline">
            <span class="sp-metric-inline-label">{label}:</span>
            <span class="sp-metric-inline-value">{value}</span>
        </div>
        ''',
        unsafe_allow_html=True
    )

