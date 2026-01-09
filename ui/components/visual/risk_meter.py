"""
Risk Meter Component

Risk thermometer visualization with multi-level risk indicators and visual risk zones.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Optional


def render_risk_meter(
    risk_level: float,
    max_risk: float = 100.0,
    show_label: bool = True,
    label: Optional[str] = None
) -> None:
    """
    Render a risk thermometer visualization.
    
    Args:
        risk_level: Current risk level (0-max_risk)
        max_risk: Maximum risk threshold
        show_label: Whether to show the label
        label: Custom label text
    """
    # Clamp risk level
    risk_level = max(0, min(max_risk, risk_level))
    risk_percent = (risk_level / max_risk) * 100
    
    # Determine color and zone
    if risk_percent >= 80:
        color = '#EF4444'  # Red - High Risk
        zone = 'HIGH'
    elif risk_percent >= 50:
        color = '#F59E0B'  # Amber - Medium Risk
        zone = 'MEDIUM'
    else:
        color = '#22C55E'  # Green - Low Risk
        zone = 'LOW'
    
    # Create thermometer figure
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_percent,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': label or "Risk Level", 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': '#22C55E'},
                {'range': [50, 80], 'color': '#F59E0B'},
                {'range': [80, 100], 'color': '#EF4444'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        },
        number = {'suffix': '%', 'font': {'size': 24, 'color': color}}
    ))
    
    fig.update_layout(
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#D1D5DB'},
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Show risk zone
    if show_label:
        st.markdown(f"**Risk Zone:** <span style='color: {color}; font-weight: 600;'>{zone}</span>", unsafe_allow_html=True)

