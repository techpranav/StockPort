"""
Regime Timeline Component

Market regime timeline (last 30 days) with confidence bands and regime transitions.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from ui.components.visual.empty_state import render_empty_state


def render_regime_timeline(
    regime_data: List[Dict[str, Any]],
    days: int = 30
) -> None:
    """
    Render market regime timeline.
    
    Args:
        regime_data: List of regime data points with timestamp and regime info
        days: Number of days to display
    """
    if not regime_data:
        render_empty_state(
            "No regime history",
            "Regime history isn’t available in this session yet.",
            icon="◌",
        )
        return
    
    # Prepare data
    dates = []
    regimes = []
    confidence = []
    
    for point in regime_data:
        timestamp = point.get('timestamp', '')
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                dt = datetime.now()
        else:
            dt = timestamp if isinstance(timestamp, datetime) else datetime.now()
        
        dates.append(dt)
        regimes.append(point.get('regime', 'unknown'))
        confidence.append(point.get('confidence', 0.0) * 100 if isinstance(point.get('confidence'), float) else point.get('confidence', 0))
    
    # Create regime color mapping
    regime_colors = {
        'bullish': '#22C55E',
        'bearish': '#EF4444',
        'neutral': '#F59E0B',
        'trending_up': '#22C55E',
        'trending_down': '#EF4444',
        'sideways': '#9CA3AF',
        'unknown': '#6B7280'
    }
    
    # Create figure
    fig = go.Figure()
    
    # Add confidence bands
    fig.add_trace(go.Scatter(
        x=dates,
        y=confidence,
        mode='lines',
        name='Confidence',
        line=dict(color='#CBD5E1', width=2),
        fill='tozeroy',
        fillcolor='rgba(203, 213, 225, 0.08)'
    ))
    
    # Add regime markers
    for i, (date, regime, conf) in enumerate(zip(dates, regimes, confidence)):
        color = regime_colors.get(regime.lower(), '#6B7280')
        fig.add_trace(go.Scatter(
            x=[date],
            y=[conf],
            mode='markers',
            name=regime,
            marker=dict(
                size=10,
                color=color,
                symbol='circle'
            ),
            showlegend=False,
            hovertemplate=f'<b>{regime}</b><br>Confidence: {conf:.1f}%<extra></extra>'
        ))
    
    # Add regime transition lines
    prev_regime = None
    for i, regime in enumerate(regimes):
        if prev_regime and regime != prev_regime:
            fig.add_vline(
                x=dates[i],
                line_dash="dash",
                line_color="#9CA3AF",
                opacity=0.5,
                annotation_text=f"{prev_regime} → {regime}"
            )
        prev_regime = regime
    
    fig.update_layout(
        height=400,
        title="Market Regime Timeline",
        xaxis_title="Date",
        yaxis_title="Confidence (%)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#D1D5DB'},
        xaxis=dict(gridcolor='#374151'),
        yaxis=dict(gridcolor='#374151', range=[0, 100])
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

