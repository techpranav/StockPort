"""
Opportunity Radar Chart

Primary visualization for Discover workspace.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Any

from ui.terminal_v1.components.primitives.empty_state import render_empty_state


def render_radar(opportunities: List[Dict[str, Any]]) -> None:
    """
    Render opportunity radar chart.
    
    Args:
        opportunities: List of opportunity dicts with symbol, score, etc.
    """
    if not opportunities:
        render_empty_state(
            "No opportunities",
            "Opportunities will appear here when detected.",
            icon="◌"
        )
        return
    
    # Prepare data
    symbols = [o.get('symbol', 'UNKNOWN') for o in opportunities]
    scores = [o.get('score', 0) for o in opportunities]
    prices = [o.get('price', 0) for o in opportunities]
    
    # Create scatter plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=scores,
        y=prices,
        mode='markers+text',
        text=symbols,
        textposition="top center",
        marker=dict(
            size=[max(s / 5, 5) for s in scores],
            color=scores,
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Score")
        ),
        hovertemplate='<b>%{text}</b><br>Score: %{x}<br>Price: ₹%{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        height=500,
        title="Opportunity Radar",
        xaxis_title="Score",
        yaxis_title="Price (₹)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#D1D5DB'},
        xaxis=dict(gridcolor='#374151'),
        yaxis=dict(gridcolor='#374151')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

