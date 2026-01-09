"""
Discover Workspace

Opportunity discovery with radar and signal stream.
"""

import streamlit as st
from typing import List, Dict, Any

from ui.terminal_v1.services.ui_data_service import get_ui_data_service
from ui.terminal_v1.components.primitives.operational_status import render_operational_status
from ui.terminal_v1.components.charts.radar import render_radar
from ui.terminal_v1.components.stream.stream_row import render_stream_row
from ui.terminal_v1.components.stream.stream_list import render_stream_list
from ui.terminal_v1.components.primitives.section_header import render_section_header
from ui.terminal_v1.components.primitives.metric_inline import render_metric_inline
from ui.terminal_v1.layout.context_strip import render_context_strip
from ui.terminal_v1.layout.canvas import render_canvas


def render_discover_context_strip() -> None:
    """Render Z3: Context strip with operational cues and filters."""
    from datetime import datetime
    
    render_context_strip()
    
    # LEFT / CENTER / RIGHT zones
    left_col, center_col, right_col = st.columns([2.5, 1.5, 1], gap="medium")
    
    # LEFT: Operational status
    with left_col:
        st.markdown(
            '''
            <div style="display: flex; align-items: center; gap: var(--spacing-sm); flex-wrap: wrap;">
                <div class="sp-live-indicator">
                    <span class="sp-live-dot"></span>
                    <span style="color: var(--color-text-2); font-size: var(--font-size-xs); font-weight: var(--font-weight-medium);">LIVE</span>
                </div>
                <span style="color: var(--color-muted); font-size: var(--font-size-xs);">|</span>
                <span class="sp-status-pill neutral" style="font-size: var(--font-size-xs); padding: 2px 6px;">Scanning every 5s</span>
                <span style="color: var(--color-muted); font-size: var(--font-size-xs);">|</span>
                <span style="color: var(--color-text-2); font-size: var(--font-size-xs);">512 symbols</span>
                <span style="color: var(--color-muted); font-size: var(--font-size-xs);">|</span>
                <span style="color: var(--color-text-2); font-size: var(--font-size-xs);">Last scan: 0.8s ago</span>
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    # CENTER: Filters
    with center_col:
        filter_col1, filter_col2 = st.columns(2, gap="small")
        
        with filter_col1:
            min_score = st.slider("Min Score", 0, 100, 60, key="discover_min_score", label_visibility="collapsed")
            st.caption("Min Score", help="Minimum confidence score threshold")
        
        with filter_col2:
            strategy_filter = st.selectbox(
                "Strategy",
                ["All", "Mean Reversion", "Momentum", "Breakout"],
                key="discover_strategy",
                label_visibility="collapsed"
            )
            st.caption("Strategy")
    
    # RIGHT: Updated timestamp
    with right_col:
        render_metric_inline("Updated", datetime.now().strftime("%H:%M:%S"))


def render_discover_canvas() -> None:
    """Render Z4: Main canvas with radar and stream."""
    from datetime import datetime
    
    data_service = get_ui_data_service()
    
    # Get data with error handling
    try:
        opportunities = data_service.get_opportunities(limit=100)
        signals = data_service.get_signals(limit=50)
    except RuntimeError as e:
        st.error(f"❌ Backend Error: {str(e)}")
        st.error("Please ensure the backend service is running and accessible.")
        opportunities = []
        signals = []
    except Exception as e:
        st.error(f"❌ Unexpected Error: {str(e)}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())
        opportunities = []
        signals = []
    
    # Filter signals by min score
    min_score = st.session_state.get('discover_min_score', 60)
    filtered_signals = [s for s in signals if s.get('score', 0) >= min_score]
    
    # Primary: Opportunity Radar (dominant, visually isolated)
    render_section_header("Opportunity Radar")
    
    # Radar container for visual dominance
    st.markdown('<div class="sp-radar-container">', unsafe_allow_html=True)
    
    if opportunities:
        render_radar(opportunities)
    else:
        from ui.terminal_v1.components.primitives.operational_status import render_operational_status
        render_operational_status(
            status="SCANNING",
            opportunities=0,
            last_scan=datetime.now().strftime("%H:%M:%S"),
            show_live=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Divider for visual rhythm
    from ui.terminal_v1.components.primitives.divider import render_divider
    render_divider()
    
    # Secondary: Signal Stream (dense, ranked)
    render_section_header("Signal Stream")
    
    # Column headers (always visible for structure)
    st.markdown(
        '''
        <div style="display: grid; grid-template-columns: 2fr 2fr 1fr 1fr 1fr; padding: var(--spacing-xs) var(--spacing-md); 
                    border-bottom: 1px solid var(--color-border); color: var(--color-muted); font-size: var(--font-size-xs); 
                    font-weight: var(--font-weight-medium);">
            <div>Symbol</div>
            <div>Strategy</div>
            <div>Score</div>
            <div>Liquidity</div>
            <div>Time</div>
        </div>
        ''',
        unsafe_allow_html=True
    )
    
    def render_signal_row(signal: Dict[str, Any], idx: int) -> None:
        symbol = signal.get('symbol', 'UNKNOWN')
        score = signal.get('score', 0)
        strategy = signal.get('strategy_id', 'unknown')
        liquidity = signal.get('liquidity', 0)
        signal_time = signal.get('timestamp', datetime.now().isoformat())[:19] if signal.get('timestamp') else '--'
        
        # Determine status
        if score >= 80:
            status_color = 'green'
            status_text = 'STRONG'
        elif score >= 60:
            status_color = 'yellow'
            status_text = 'BUY'
        else:
            status_color = 'neutral'
            status_text = 'WATCH'
        
        render_stream_row(
            title=symbol,
            subtitle=strategy,
            right_value=f"{score}",
            status_pill=status_text,
            status_color=status_color,
            key=f"signal_{symbol}_{idx}"
        )
    
    if filtered_signals:
        render_stream_list(
            items=filtered_signals[:20],
            render_item=render_signal_row,
            empty_message=""
        )
    else:
        # Placeholder row when empty (maintains structure)
        st.markdown(
            '''
            <div style="display: grid; grid-template-columns: 2fr 2fr 1fr 1fr 1fr; padding: var(--spacing-sm) var(--spacing-md); 
                        border-bottom: 1px solid var(--color-border); color: var(--color-muted); font-size: var(--font-size-xs);">
                <div>--</div>
                <div>--</div>
                <div>--</div>
                <div>--</div>
                <div>--</div>
            </div>
            ''',
            unsafe_allow_html=True
        )
        # Operational status below placeholder
        from ui.terminal_v1.components.primitives.operational_status import render_operational_status
        render_operational_status(
            status="NO SIGNALS",
            opportunities=0,
            last_scan=datetime.now().strftime("%H:%M:%S"),
            show_live=True,
            reason="Filters not satisfied or no signals match criteria"
        )


def render_discover() -> None:
    """
    Render Discover workspace.
    
    This is the main entry point, but in terminal_v1,
    we use render_discover_context_strip and render_discover_canvas
    directly from the shell.
    """
    # Z3: Context Strip
    render_discover_context_strip()
    
    # Z4: Main Canvas
    render_canvas(render_discover_canvas)

