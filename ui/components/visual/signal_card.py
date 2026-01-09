"""
Signal Card Component

Expandable signal cards with sparkline charts, confidence rings, and real-time updates.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from datetime import datetime

from ui.components.visual.empty_state import render_empty_state


def render_signal_card(
    signal: Dict[str, Any],
    show_expanded: bool = False
) -> None:
    """
    Render a signal card with expandable details.
    
    Args:
        signal: Signal dictionary with symbol, score, confidence, etc.
        show_expanded: Whether to show expanded view by default
    """
    symbol = signal.get('symbol', 'UNKNOWN')
    score = signal.get('score', 0)
    confidence = signal.get('confidence', 0.0) * 100 if isinstance(signal.get('confidence'), float) else signal.get('confidence', 0)
    strategy = signal.get('strategy_id', 'unknown')
    price = signal.get('price', 0.0)
    timestamp = signal.get('timestamp', '')
    
    # Determine signal color based on score
    if score >= 80:
        color = '#22C55E'  # Green
        signal_type = 'STRONG BUY'
    elif score >= 60:
        # Keep blue reserved for actions; BUY is informational.
        color = '#E5E7EB'  # Neutral
        signal_type = 'BUY'
    elif score >= 40:
        color = '#F59E0B'  # Amber
        signal_type = 'WATCH'
    else:
        color = '#EF4444'  # Red
        signal_type = 'AVOID'
    
    # Format timestamp
    if timestamp:
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%I:%M %p")
            else:
                time_str = str(timestamp)
        except:
            time_str = "Just now"
    else:
        time_str = "Just now"
    
    # Card header
    st.markdown('<div class="sp-card sp-clickable">', unsafe_allow_html=True)
    try:
        top_left, top_mid, top_right = st.columns([2.2, 1.2, 1.4])
        with top_left:
            st.markdown(
                f"""
                <div class="sp-card-title">
                  <span class="sp-symbol">{symbol}</span>
                  <span class="sp-pill" style="color:{color}; border-color:rgba(148,163,184,0.22)">
                    {signal_type}
                  </span>
                </div>
                <div class="sp-meta">{strategy}</div>
                """,
                unsafe_allow_html=True,
            )

        with top_mid:
            st.markdown(
                f"""
                <div class="sp-kpi">
                  <div class="sp-kpi-label">Score</div>
                  <div class="sp-kpi-value" style="color:{color}">{int(score)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with top_right:
            st.markdown(
                f"""
                <div class="sp-kpi">
                  <div class="sp-kpi-label">Last</div>
                  <div class="sp-kpi-value">${price:.2f}</div>
                  <div class="sp-meta">⏱ {time_str}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sp-divider"></div>', unsafe_allow_html=True)

        # Confidence ring (simplified as progress bar)
        st.progress(confidence / 100)
        st.caption(f"Confidence: {int(confidence)}%")
    finally:
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Sparkline chart (if price history available)
    price_history = signal.get('price_history', [])
    if price_history and len(price_history) > 1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(price_history))),
            y=price_history,
            mode='lines',
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=f'rgba({_hex_to_rgb(color)}, 0.1)'
        ))
        fig.update_layout(
            height=80,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Expandable details
    with st.expander("Details", expanded=show_expanded):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Strategy:**")
            st.write(strategy)
            
            st.markdown("**Indicators:**")
            indicators = signal.get('indicators', {})
            if indicators:
                for ind_name, ind_value in indicators.items():
                    st.write(f"- {ind_name}: {ind_value}")
            else:
                render_empty_state(
                    "No indicator details",
                    "This signal doesn’t include indicator breakdown in the current feed.",
                    icon="◌",
                )
        
        with col2:
            st.markdown("**Risk Metrics:**")
            risk_metrics = signal.get('risk_metrics', {})
            if risk_metrics:
                for metric_name, metric_value in risk_metrics.items():
                    st.write(f"- {metric_name}: {metric_value}")
            else:
                render_empty_state(
                    "No risk metrics",
                    "Risk details are not attached to this signal in the current feed.",
                    icon="◌",
                )
            
            # Entry/Stop/Target if available
            entry_price = signal.get('entry_price')
            stop_loss = signal.get('stop_loss')
            take_profit = signal.get('take_profit')
            
            if entry_price:
                st.markdown("**Entry Levels:**")
                st.write(f"- Entry: ${entry_price:.2f}")
                if stop_loss:
                    st.write(f"- Stop Loss: ${stop_loss:.2f}")
                if take_profit:
                    st.write(f"- Take Profit: ${take_profit:.2f}")


def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB string."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"{r}, {g}, {b}"

