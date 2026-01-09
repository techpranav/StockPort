"""
Confidence Gauge Component

Radial confidence meter with animated progress and color-coded thresholds.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Optional


def render_confidence_gauge(
    confidence: float,
    size: int = 200,
    show_label: bool = True,
    label: Optional[str] = None
) -> None:
    """
    Render a radial confidence gauge.
    
    Args:
        confidence: Confidence value (0-100)
        size: Size of the gauge in pixels
        show_label: Whether to show the label
        label: Custom label text
    """
    # Clamp confidence to 0-100
    confidence = max(0, min(100, confidence))
    
    # Determine color based on confidence
    if confidence >= 80:
        color = '#22C55E'  # Green
    elif confidence >= 60:
        # Keep blue reserved for actions; use a neutral tone for mid confidence.
        color = '#CBD5E1'  # Slate
    elif confidence >= 40:
        color = '#F59E0B'  # Amber
    else:
        color = '#EF4444'  # Red
    
    # Create gauge figure
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = confidence,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': label or "Confidence", 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': '#1F2937'},
                {'range': [40, 60], 'color': '#334155'},
                {'range': [60, 80], 'color': '#475569'},
                {'range': [80, 100], 'color': '#64748B'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        },
        number = {'suffix': '%', 'font': {'size': 24, 'color': color}}
    ))
    
    fig.update_layout(
        height=size,
        width=size,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#D1D5DB'},
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False})

