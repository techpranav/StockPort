"""
Decide Workspace

Strategy reasoning workspace showing why the algo wants a trade.
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime

from ui.terminal_v1.services.ui_data_service import get_ui_data_service
from ui.terminal_v1.components.primitives.section_header import render_section_header
from ui.terminal_v1.components.primitives.metric_inline import render_metric_inline
from ui.terminal_v1.components.primitives.operational_status import render_operational_status
from ui.terminal_v1.components.primitives.divider import render_divider
from ui.terminal_v1.components.stream.stream_row import render_stream_row
from ui.terminal_v1.components.stream.stream_list import render_stream_list
from ui.terminal_v1.layout.context_strip import render_context_strip
from ui.terminal_v1.layout.canvas import render_canvas


def render_decide_context_strip() -> None:
    """Render Z3: Context strip for Decide."""
    render_context_strip()
    
    col1, col2 = st.columns([1, 0.3])
    with col1:
        st.markdown(
            '''
            <div style="display: flex; align-items: center; gap: var(--spacing-sm);">
                <div class="sp-live-indicator">
                    <span class="sp-live-dot"></span>
                    <span style="color: var(--color-text-2); font-size: var(--font-size-xs); font-weight: var(--font-weight-medium);">LIVE</span>
                </div>
                <span style="color: var(--color-muted); font-size: var(--font-size-xs);">|</span>
                <span style="color: var(--color-text-2); font-size: var(--font-size-xs);">Risk-Reward Analysis</span>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with col2:
        render_metric_inline("Updated", datetime.now().strftime("%H:%M:%S"))


def render_decide_canvas() -> None:
    """Render Z4: Main canvas for Decide."""
    data_service = get_ui_data_service()
    
    # Get active signal from session state
    active_symbol = st.session_state.get('decide_active_symbol')
    active_signal = st.session_state.get('decide_active_signal')
    
    # Get signals
    try:
        signals = data_service.get_signal_stream(limit=50)
    except:
        signals = []
    
    # Find active signal data
    active_signal_data = None
    if active_symbol:
        for signal in signals:
            if signal.get('symbol') == active_symbol:
                active_signal_data = signal
                break
    
    # Primary: Risk-Reward Map (hero)
    render_section_header("Risk-Reward Analysis")
    
    st.markdown('<div class="sp-radar-container">', unsafe_allow_html=True)
    
    if not active_signal_data:
        render_operational_status(
            status="NO ACTIVE CANDIDATE",
            opportunities=0,
            last_scan=datetime.now().strftime("%H:%M:%S"),
            show_live=True,
            reason="Select a signal from the stream to see risk/reward and reasoning."
        )
    else:
        strategy_id = active_signal_data.get("strategy_id", "unknown")
        symbol = active_signal_data.get("symbol", "UNKNOWN")
        score = active_signal_data.get("score", 0)
        price = active_signal_data.get("price", 0)
        
        st.caption(f"Strategy: {strategy_id} | Symbol: {symbol}")
        
        # Risk-Reward visualization (simplified)
        risk_amount = price * 10 * 0.05 if price else 0
        reward_amount = price * 10 * 0.10 if price else 0
        risk_reward_ratio = 2.0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Risk", f"₹{risk_amount:.2f}")
        with col2:
            st.metric("Reward", f"₹{reward_amount:.2f}")
        with col3:
            st.metric("R:R Ratio", f"{risk_reward_ratio:.1f}")
        
        # Entry/SL/Target
        entry_price = price
        stop_loss = price * 0.95 if price else 0
        take_profit = price * 1.10 if price else 0
        
        st.markdown('<div style="margin-top: var(--spacing-md);"></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Entry", f"₹{entry_price:.2f}")
        with col2:
            st.metric("Stop Loss", f"₹{stop_loss:.2f}")
        with col3:
            st.metric("Take Profit", f"₹{take_profit:.2f}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Divider
    render_divider()
    
    # Secondary: Candidates
    render_section_header("Candidates")
    
    if not signals:
        render_operational_status(
            status="NO CANDIDATES",
            opportunities=0,
            last_scan=datetime.now().strftime("%H:%M:%S"),
            show_live=True,
            reason="When opportunities are detected, candidates will appear here."
        )
    else:
        def render_candidate_row(signal: Dict[str, Any], idx: int) -> None:
            symbol = signal.get("symbol", "UNKNOWN")
            score = int(signal.get("score", 0))
            strategy = signal.get("strategy_id", "unknown")
            
            pill = "BUY" if score >= 60 else "WATCH" if score >= 40 else "AVOID"
            pill_color = "green" if score >= 80 else "yellow" if score >= 40 else "red"
            
            render_stream_row(
                title=symbol,
                subtitle=strategy,
                right_value=f"{score}",
                status_pill=pill,
                status_color=pill_color,
                key=f"decide_candidate_{symbol}_{idx}"
            )
            
            # Handle selection
            if st.session_state.get(f"decide_candidate_{symbol}_{idx}_clicked", False):
                st.session_state.decide_active_symbol = symbol
                st.session_state.decide_active_signal = signal
                st.rerun()
        
        render_stream_list(
            items=signals[:12],
            render_item=render_candidate_row,
            empty_message=""
        )
        
        # Reasoning section if active signal
        if active_signal_data:
            render_divider()
            render_section_header("Reasoning")
            
            indicators = active_signal_data.get("indicators", {}) or {}
            if not indicators:
                render_operational_status(
                    status="NO BREAKDOWN",
                    opportunities=0,
                    show_live=False,
                    reason="This signal doesn't include indicator contribution in the current feed."
                )
            else:
                for k, v in list(indicators.items())[:10]:
                    st.write(f"- {k}: {v}")


def render_decide() -> None:
    """Render Decide workspace."""
    render_decide_context_strip()
    render_canvas(render_decide_canvas)

