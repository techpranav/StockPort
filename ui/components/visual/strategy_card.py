"""
Strategy Card Component

Strategy status indicators with edge score visualization, regime compatibility,
and decay warnings.
"""

import streamlit as st
from typing import Dict, Any, Optional


def render_strategy_card(
    strategy: Dict[str, Any],
    show_details: bool = False
) -> None:
    """
    Render a strategy card.
    
    Args:
        strategy: Strategy dictionary with id, name, status, performance, etc.
        show_details: Whether to show detailed information
    """
    strategy_id = strategy.get('strategy_id', 'unknown')
    name = strategy.get('name', strategy_id)
    status = strategy.get('status', 'unknown')
    win_rate = strategy.get('win_rate', 0.0) * 100 if isinstance(strategy.get('win_rate'), float) else strategy.get('win_rate', 0)
    profit_factor = strategy.get('profit_factor', 0.0)
    sharpe = strategy.get('sharpe_ratio', 0.0)
    total_return = strategy.get('total_return', 0.0) * 100 if isinstance(strategy.get('total_return'), float) else strategy.get('total_return', 0)
    
    # Determine status color
    if status == 'active' or status == 'live':
        status_color = '#22C55E'
        status_text = '🟢 LIVE'
    elif status == 'shadow':
        status_color = '#F59E0B'
        status_text = '🟡 SHADOW'
    else:
        status_color = '#EF4444'
        status_text = '🔴 DISABLED'
    
    # Calculate edge score (simplified)
    edge_score = min(100, max(0, (win_rate * 0.5) + (profit_factor * 20) + (sharpe * 10)))
    
    # Card header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### {name}")
        st.markdown(f"**ID:** {strategy_id}")
    
    with col2:
        st.markdown(f"<div style='color: {status_color}; font-weight: 600;'>{status_text}</div>", unsafe_allow_html=True)
    
    # Edge score visualization
    st.markdown("**Edge Score:**")
    st.progress(edge_score / 100)
    st.caption(f"{edge_score:.0f}%")
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    with col2:
        st.metric("Profit Factor", f"{profit_factor:.2f}")
    
    with col3:
        st.metric("Sharpe Ratio", f"{sharpe:.2f}")
    
    with col4:
        st.metric("Total Return", f"{total_return:.2f}%")
    
    # Regime compatibility
    regime_fit = strategy.get('regime_fit', 'unknown')
    if regime_fit != 'unknown':
        st.markdown(f"**Regime Fit:** {regime_fit.title()}")
    
    # Decay warning
    decay_risk = strategy.get('decay_risk', 'low')
    if decay_risk != 'low':
        decay_color = '#F59E0B' if decay_risk == 'medium' else '#EF4444'
        st.markdown(f"<div style='color: {decay_color}; font-weight: 600;'>⚠️ Decay Risk: {decay_risk.upper()}</div>", unsafe_allow_html=True)
    
    # Expandable details
    if show_details:
        with st.expander("Strategy Details", expanded=True):
            st.json(strategy)

