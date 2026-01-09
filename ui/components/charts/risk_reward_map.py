"""
Risk-Reward Map Component

Risk-reward scatter plot with Entry/SL/Target zones and portfolio impact visualization.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
import pandas as pd

from ui.components.visual.empty_state import render_empty_state


def render_risk_reward_map(
    signals: List[Dict[str, Any]],
    show_portfolio_impact: bool = False
) -> None:
    """
    Render risk-reward map.
    
    Args:
        signals: List of signal dictionaries with risk/reward data
        show_portfolio_impact: Whether to show portfolio impact (basic in v5)
    """
    if not signals:
        render_empty_state(
            "No signal selected",
            "Choose a signal to see its risk–reward profile.",
            icon="◌",
        )
        return
    
    # Prepare data
    data = []
    for signal in signals:
        risk = signal.get('risk_amount', 0.0)
        reward = signal.get('reward_amount', 0.0)
        risk_reward_ratio = signal.get('risk_reward_ratio', 0.0)
        
        if risk > 0 and reward > 0:
            data.append({
                'symbol': signal.get('symbol', 'UNKNOWN'),
                'risk': risk,
                'reward': reward,
                'risk_reward_ratio': risk_reward_ratio,
                'score': signal.get('score', 0),
                'entry_price': signal.get('entry_price', 0.0),
                'stop_loss': signal.get('stop_loss', 0.0),
                'take_profit': signal.get('take_profit', 0.0)
            })
    
    if not data:
        render_empty_state(
            "Risk–reward not available",
            "This signal doesn’t include risk/reward inputs in the current view.",
            icon="◌",
        )
        return
    
    df = pd.DataFrame(data)
    
    # Create scatter plot
    fig = go.Figure()
    
    # Add risk-reward points
    fig.add_trace(go.Scatter(
        x=df['risk'],
        y=df['reward'],
        mode='markers+text',
        text=df['symbol'],
        textposition="top center",
        marker=dict(
            size=df['score'] / 2,
            color=df['risk_reward_ratio'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="R:R Ratio")
        ),
        hovertemplate='<b>%{text}</b><br>' +
                      'Risk: $%{x:,.2f}<br>' +
                      'Reward: $%{y:,.2f}<br>' +
                      'R:R Ratio: %{marker.color:.2f}<extra></extra>'
    ))
    
    # Add ideal zone (1:2 risk-reward line)
    max_risk = df['risk'].max()
    max_reward = df['reward'].max()
    ideal_line_x = [0, max_risk]
    ideal_line_y = [0, max_risk * 2]
    
    fig.add_trace(go.Scatter(
        x=ideal_line_x,
        y=ideal_line_y,
        mode='lines',
        name='1:2 R:R',
        line=dict(color='#22C55E', width=2, dash='dash'),
        hovertemplate='1:2 Risk-Reward Line<extra></extra>'
    ))
    
    # Add entry/SL/Target zones if available
    if 'entry_price' in df.columns and 'stop_loss' in df.columns and 'take_profit' in df.columns:
        # This would show price zones - simplified for v5
        pass
    
    fig.update_layout(
        height=500,
        title="Risk-Reward Map",
        xaxis_title="Risk ($)",
        yaxis_title="Reward ($)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#D1D5DB'},
        xaxis=dict(gridcolor='#374151'),
        yaxis=dict(gridcolor='#374151')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
    
    # Basic portfolio impact (v5)
    if show_portfolio_impact:
        total_risk = df['risk'].sum()
        total_reward = df['reward'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Risk", f"${total_risk:,.2f}")
        with col2:
            st.metric("Total Reward", f"${total_reward:,.2f}")

