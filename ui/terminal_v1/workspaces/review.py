"""
Review Workspace

Performance review workspace with performance summary and history.
"""

import streamlit as st
from typing import List, Dict, Any
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


def render_review_context_strip() -> None:
    """Render Z3: Context strip for Review."""
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
                <span style="color: var(--color-text-2); font-size: var(--font-size-xs);">Performance Review</span>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with col2:
        render_metric_inline("Updated", datetime.now().strftime("%H:%M:%S"))


def render_review_canvas() -> None:
    """Render Z4: Main canvas for Review."""
    data_service = get_ui_data_service()
    
    # Primary: Performance Summary (hero)
    render_section_header("Performance Summary")
    
    st.markdown('<div class="sp-radar-container">', unsafe_allow_html=True)
    
    try:
        positions = data_service.get_positions()
        
        if positions:
            total_pnl = sum(pos.get("pnl", 0) for pos in positions)
            total_pnl_pct = (
                sum(pos.get("pnl_percent", 0) for pos in positions) / len(positions)
                if positions
                else 0
            )
            winning_trades = sum(1 for pos in positions if pos.get("pnl", 0) > 0)
            win_rate = (winning_trades / len(positions)) * 100 if positions else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total P&L", f"₹{total_pnl:,.2f}", delta=f"{total_pnl_pct:.2f}%")
            with col2:
                st.metric("Open", f"{len(positions)}")
            with col3:
                st.metric("Win Rate", f"{win_rate:.1f}%")
        else:
            render_operational_status(
                status="NO POSITIONS",
                opportunities=0,
                last_scan=datetime.now().strftime("%H:%M:%S"),
                show_live=True,
                reason="Performance summary will appear once positions exist."
            )
    except:
        render_operational_status(
            status="UNAVAILABLE",
            opportunities=0,
            last_scan=datetime.now().strftime("%H:%M:%S"),
            show_live=True,
            reason="Performance data unavailable."
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Divider
    render_divider()
    
    # Secondary: Order History
    render_section_header("Order History")
    
    try:
        orders = data_service.get_orders(limit=50)
    except:
        orders = []
    
    if not orders:
        render_operational_status(
            status="NO ORDER HISTORY",
            opportunities=0,
            last_scan=datetime.now().strftime("%H:%M:%S"),
            show_live=True,
            reason="Orders will appear here as the system executes."
        )
    else:
        def render_history_row(order: Dict[str, Any], idx: int) -> None:
            symbol = order.get("symbol", "UNKNOWN")
            status = str(order.get("status", "unknown")).upper()
            qty = order.get("quantity", 0)
            order_key = order.get("id") or order.get("order_id") or idx
            
            render_stream_row(
                title=str(symbol),
                subtitle=f"{status}",
                right_value=f"Qty: {qty}",
                status_pill=status,
                status_color="green" if status == "FILLED" else "yellow",
                key=f"review_order_{order_key}_{idx}"
            )
        
        render_stream_list(
            items=orders[:15],
            render_item=render_history_row,
            empty_message=""
        )
    
    # Divider
    render_divider()
    
    # Strategy Performance
    render_section_header("Strategy Performance")
    
    try:
        strategy_perf = data_service.get_strategy_performance()
    except:
        strategy_perf = []
    
    if not strategy_perf:
        render_operational_status(
            status="NO STRATEGY PERFORMANCE",
            opportunities=0,
            show_live=False,
            reason="Strategy health will appear here when the backend exposes performance."
        )
    else:
        for perf in strategy_perf[:6]:
            strategy_id = perf.get("strategy_id", "unknown")
            pnl = perf.get("pnl", 0)
            win_rate = perf.get("win_rate", 0)
            
            st.markdown(
                f'''
                <div class="sp-operational-status" style="margin-bottom: var(--spacing-sm);">
                    <div style="color: var(--color-text); font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); margin-bottom: var(--spacing-xs);">
                        {strategy_id}
                    </div>
                    <div style="display: flex; gap: var(--spacing-lg);">
                        <div style="color: var(--color-text-2); font-size: var(--font-size-xs);">
                            P&L: <span style="color: var(--color-text); font-weight: var(--font-weight-medium);">₹{pnl:,.2f}</span>
                        </div>
                        <div style="color: var(--color-text-2); font-size: var(--font-size-xs);">
                            Win Rate: <span style="color: var(--color-text); font-weight: var(--font-weight-medium);">{win_rate:.1f}%</span>
                        </div>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )


def render_review() -> None:
    """Render Review workspace."""
    render_review_context_strip()
    render_canvas(render_review_canvas)

