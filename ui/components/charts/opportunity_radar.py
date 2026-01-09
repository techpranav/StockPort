"""
Opportunity Radar Component

Circular/heatmap opportunity visualization with Score × Volume × Volatility mapping
and interactive filtering.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import pandas as pd

from ui.components.visual.empty_state import render_empty_state


def render_opportunity_radar(
    opportunities: List[Dict[str, Any]],
    chart_type: str = "scatter"
) -> None:
    """
    Render opportunity radar visualization.
    
    Args:
        opportunities: List of opportunity dictionaries
        chart_type: Type of chart ("scatter" or "heatmap")
    """
    if not opportunities:
        render_empty_state(
            "No opportunities yet",
            "When the scanner detects setups, they’ll appear here.",
            icon="◌",
        )
        return
    
    # Prepare data
    data = []
    for opp in opportunities:
        data.append({
            'symbol': opp.get('symbol', 'UNKNOWN'),
            'score': opp.get('score', 0),
            'volume': opp.get('volume', 0),
            'volatility': opp.get('volatility', 0),
            'price': opp.get('price', 0.0)
        })
    
    df = pd.DataFrame(data)
    
    if chart_type == "scatter":
        # Scatter plot: Score (x) × Volume (y), bubble size = Volatility
        fig = px.scatter(
            df,
            x='score',
            y='volume',
            size='volatility',
            color='score',
            hover_data=['symbol', 'price'],
            labels={
                'score': 'Score',
                'volume': 'Volume',
                'volatility': 'Volatility'
            },
            color_continuous_scale='Viridis',
            size_max=50
        )
        
        fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>' +
                          'Score: %{x}<br>' +
                          'Volume: %{y:,.0f}<br>' +
                          'Price: $%{customdata[0]:.2f}<extra></extra>',
            hovertext=df['symbol']
        )
        
    else:  # heatmap
        # Create heatmap data
        score_bins = pd.cut(df['score'], bins=10, labels=False)
        volume_bins = pd.cut(df['volume'], bins=10, labels=False)
        
        heatmap_data = pd.crosstab(score_bins, volume_bins, values=df['volatility'], aggfunc='mean')
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Viridis',
            hoverongaps=False
        ))
        
        fig.update_layout(
            xaxis_title='Volume (binned)',
            yaxis_title='Score (binned)',
            title='Opportunity Heatmap'
        )
    
    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#D1D5DB'},
        xaxis=dict(gridcolor='#374151'),
        yaxis=dict(gridcolor='#374151')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

