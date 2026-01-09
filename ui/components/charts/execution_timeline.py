"""
Execution Timeline Component

Order lifecycle animation with real-time order status and broker latency display.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd

from ui.components.visual.empty_state import render_empty_state


def render_execution_timeline(
    orders: List[Dict[str, Any]],
    show_latency: bool = True
) -> None:
    """
    Render execution timeline for orders.
    
    Args:
        orders: List of order dictionaries
        show_latency: Whether to show latency information
    """
    if not orders:
        render_empty_state(
            "No orders yet",
            "This timeline will populate as orders are created and filled.",
            icon="◌",
        )
        return
    
    # Order status stages
    status_stages = {
        'pending': 0,
        'submitted': 1,
        'acknowledged': 2,
        'partially_filled': 3,
        'filled': 4,
        'cancelled': 5,
        'rejected': 5
    }
    
    # Prepare timeline data
    timeline_data = []
    for order in orders:
        order_id = order.get('order_id', 'UNKNOWN')
        symbol = order.get('symbol', 'UNKNOWN')
        status = order.get('status', 'pending').lower()
        created_at = order.get('created_at', '')
        filled_at = order.get('filled_at', '')
        
        # Parse timestamps
        try:
            if isinstance(created_at, str):
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_dt = created_at if isinstance(created_at, datetime) else datetime.now()
            
            if filled_at:
                if isinstance(filled_at, str):
                    filled_dt = datetime.fromisoformat(filled_at.replace('Z', '+00:00'))
                else:
                    filled_dt = filled_at if isinstance(filled_at, datetime) else None
            else:
                filled_dt = None
        except:
            created_dt = datetime.now()
            filled_dt = None
        
        stage = status_stages.get(status, 0)
        
        timeline_data.append({
            'order_id': order_id,
            'symbol': symbol,
            'status': status,
            'stage': stage,
            'created_at': created_dt,
            'filled_at': filled_dt,
            'latency_ms': order.get('latency_ms', 0)
        })
    
    df = pd.DataFrame(timeline_data)
    
    # Create timeline visualization
    fig = go.Figure()
    
    # Color mapping for status
    status_colors = {
        'pending': '#9CA3AF',
        # Reserve blue for actions; operational states use neutral tones.
        'submitted': '#94A3B8',
        'acknowledged': '#94A3B8',
        'partially_filled': '#F59E0B',
        'filled': '#22C55E',
        'cancelled': '#EF4444',
        'rejected': '#EF4444'
    }
    
    # Group by status for visualization
    for status, color in status_colors.items():
        status_df = df[df['status'] == status]
        if not status_df.empty:
            fig.add_trace(go.Scatter(
                x=status_df['created_at'],
                y=status_df['stage'],
                mode='markers',
                name=status.title(),
                marker=dict(
                    size=10,
                    color=color,
                    symbol='circle'
                ),
                hovertemplate='<b>%{text}</b><br>' +
                            'Status: ' + status + '<br>' +
                            'Time: %{x}<extra></extra>',
                text=status_df['symbol']
            ))
    
    # Add stage labels
    stage_labels = ['Pending', 'Submitted', 'Acknowledged', 'Partially Filled', 'Filled', 'Cancelled/Rejected']
    fig.update_yaxis(
        tickmode='array',
        tickvals=list(range(len(stage_labels))),
        ticktext=stage_labels
    )
    
    fig.update_layout(
        height=400,
        title="Order Execution Timeline",
        xaxis_title="Time",
        yaxis_title="Status Stage",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#D1D5DB'},
        xaxis=dict(gridcolor='#374151'),
        yaxis=dict(gridcolor='#374151')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
    
    # Show latency if available
    if show_latency and 'latency_ms' in df.columns:
        avg_latency = df['latency_ms'].mean()
        if avg_latency > 0:
            st.metric("Average Latency", f"{avg_latency:.0f}ms")

