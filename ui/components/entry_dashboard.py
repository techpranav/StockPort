"""
Entry Point Dashboard Component

This module provides UI components for displaying entry point opportunities
with signal strength visualization and risk metrics.
"""

import streamlit as st
from typing import Dict, Any, List
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from services.analyzers.signals.entry_detector import EntryDetector
from services.analyzers.signals.signal_scorer import SignalScorer
from config.constants.SignalConstants import (
    SIGNAL_TYPE_STRONG_BUY,
    SIGNAL_TYPE_BUY,
    SIGNAL_TYPE_WATCH,
    SIGNAL_TYPE_AVOID
)


def render_entry_dashboard(
    entry_signals: List[Dict[str, Any]]
) -> None:
    """
    Render entry point dashboard with ranked opportunities.
    
    Args:
        entry_signals: List of entry signal dictionaries
    """
    if not entry_signals:
        st.info("No entry signals available. Run analysis to generate signals.")
        return
    
    st.header("🎯 Entry Point Dashboard")
    
    # Filter and sort signals
    strong_buy = [s for s in entry_signals if s.get('signal_type') == SIGNAL_TYPE_STRONG_BUY]
    buy = [s for s in entry_signals if s.get('signal_type') == SIGNAL_TYPE_BUY]
    watch = [s for s in entry_signals if s.get('signal_type') == SIGNAL_TYPE_WATCH]
    avoid = [s for s in entry_signals if s.get('signal_type') == SIGNAL_TYPE_AVOID]
    
    # Display by category
    if strong_buy:
        st.subheader("🔥 Strong Buy Opportunities")
        _display_signal_list(strong_buy)
    
    if buy:
        st.subheader("📈 Buy Opportunities")
        _display_signal_list(buy)
    
    if watch:
        st.subheader("👀 Watch List")
        _display_signal_list(watch)
    
    if avoid:
        with st.expander("⚠️ Avoid (Low Score)", expanded=False):
            _display_signal_list(avoid)
    
    # Summary chart
    _render_signal_summary_chart(entry_signals)


def _display_signal_list(signals: List[Dict[str, Any]]) -> None:
    """Display list of signals in a table."""
    # Sort by score descending
    signals_sorted = sorted(signals, key=lambda x: x.get('score', 0), reverse=True)
    
    # Create DataFrame for display
    display_data = []
    for sig in signals_sorted:
        display_data.append({
            'Symbol': sig.get('symbol', ''),
            'Score': f"{sig.get('score', 0):.1f}",
            'Confidence': f"{sig.get('confidence', 0)*100:.1f}%",
            'Entry Price': f"${sig.get('entry_price', 0):.2f}",
            'Stop Loss': f"${sig.get('stop_loss', 0):.2f}" if sig.get('stop_loss') else 'N/A',
            'Take Profit': f"${sig.get('take_profit', 0):.2f}" if sig.get('take_profit') else 'N/A',
            'Risk/Reward': f"{sig.get('risk_reward_ratio', 0):.2f}" if sig.get('risk_reward_ratio') else 'N/A'
        })
    
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True)


def _render_signal_summary_chart(signals: List[Dict[str, Any]]) -> None:
    """Render summary chart of signal distribution."""
    if not signals:
        return
    
    # Count by signal type
    signal_counts = {}
    for sig in signals:
        signal_type = sig.get('signal_type', 'UNKNOWN')
        signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=list(signal_counts.keys()),
            y=list(signal_counts.values()),
            marker_color=['green' if 'BUY' in k else 'orange' if 'WATCH' in k else 'red' for k in signal_counts.keys()]
        )
    ])
    
    fig.update_layout(
        title="Signal Distribution",
        xaxis_title="Signal Type",
        yaxis_title="Count",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

