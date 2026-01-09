"""
Execute Workspace

Order execution workspace with order timeline and execution quality.
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


def render_execute_context_strip() -> None:
    """Render Z3: Context strip for Execute."""
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
                <span style="color: var(--color-text-2); font-size: var(--font-size-xs);">Execution Performance</span>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with col2:
        render_metric_inline("Updated", datetime.now().strftime("%H:%M:%S"))


def render_execute_canvas() -> None:
    """Render Z4: Main canvas for Execute."""
    data_service = get_ui_data_service()
    
    # Get execution quality
    try:
        exec_quality = data_service.get_execution_quality()
        quality_score = exec_quality.get('score', 0)
        slippage_avg = exec_quality.get('slippage_avg', 0)
        fill_rate = exec_quality.get('fill_rate', 0)
        latency_avg = exec_quality.get('latency_avg', 0)
    except:
        quality_score = 0
        slippage_avg = 0
        fill_rate = 0
        latency_avg = 0
    
    # Primary: Execution Quality (hero)
    render_section_header("Execution Quality")
    
    st.markdown('<div class="sp-radar-container">', unsafe_allow_html=True)
    
    # Quality metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f'''
            <div style="text-align: center; padding: var(--spacing-md);">
                <div style="font-size: 3rem; font-weight: var(--font-weight-bold); color: var(--color-accent);">
                    {quality_score:.0f}%
                </div>
                <div style="color: var(--color-muted); font-size: var(--font-size-sm); margin-top: var(--spacing-xs);">
                    Quality
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    with col2:
        st.metric("Slip", f"{slippage_avg:.4f}%")
    
    with col3:
        st.metric("Fill", f"{fill_rate:.1%}")
    
    with col4:
        st.metric("Lat", f"{latency_avg:.0f}ms")
    
    # Order timeline placeholder
    st.markdown('<div style="margin-top: var(--spacing-lg);"></div>', unsafe_allow_html=True)
    
    try:
        orders = data_service.get_orders(limit=20)
        if orders:
            st.caption("Recent Orders Timeline")
            # Simple order list (timeline would go here)
            for order in orders[:5]:
                symbol = order.get("symbol", "UNKNOWN")
                status = order.get("status", "unknown")
                st.write(f"• {symbol} - {status}")
        else:
            render_operational_status(
                status="NO ORDER FLOW",
                opportunities=0,
                last_scan=datetime.now().strftime("%H:%M:%S"),
                show_live=True,
                reason="Orders and execution timeline will appear once execution begins."
            )
    except:
        render_operational_status(
            status="UNAVAILABLE",
            opportunities=0,
            last_scan=datetime.now().strftime("%H:%M:%S"),
            show_live=True,
            reason="Execution timeline will appear when orders are available."
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Divider
    render_divider()
    
    # Secondary: Active Orders
    render_section_header("Active Orders")
    
    try:
        orders = data_service.get_orders(limit=50)
        active_orders = [
            o for o in orders
            if str(o.get("status", "")).lower() in {"pending", "submitted", "open", "partially_filled"}
        ]
    except:
        active_orders = []
    
    if not active_orders:
        render_operational_status(
            status="NO ACTIVE ORDERS",
            opportunities=0,
            last_scan=datetime.now().strftime("%H:%M:%S"),
            show_live=True,
            reason="Pending and open orders will stream here."
        )
    else:
        def render_order_row(order: Dict[str, Any], idx: int) -> None:
            symbol = order.get("symbol", "UNKNOWN")
            status = str(order.get("status", "unknown")).upper()
            qty = order.get("quantity", 0)
            price = order.get("price", 0.0)
            order_key = order.get("id") or order.get("order_id") or idx
            
            render_stream_row(
                title=str(symbol),
                subtitle=f"{status} · Qty {qty}",
                right_value=f"₹{price:.2f}",
                status_pill=status,
                status_color="green" if status == "FILLED" else "yellow",
                key=f"exec_order_{order_key}_{idx}"
            )
        
        render_stream_list(
            items=active_orders[:20],
            render_item=render_order_row,
            empty_message=""
        )


def render_execute() -> None:
    """Render Execute workspace."""
    render_execute_context_strip()
    render_canvas(render_execute_canvas)

