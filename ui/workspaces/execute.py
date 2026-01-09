"""
Execute Workspace

Order execution workspace with order timeline, execution quality,
and real-time feedback.
"""

import streamlit as st
from typing import List, Dict, Any

from utils.debug_utils import DebugUtils
from ui.services import get_ui_data_service, get_metric_deriver
from ui.components.charts import render_execution_timeline
from ui.components.visual import render_confidence_gauge
from ui.components.layout import sp_surface
from ui.components.terminal.primitives import render_stream_row
from ui.components.visual.empty_state import render_empty_state
from ui.workspaces.router import set_active_context


def render_execute_workspace() -> None:
    """
    Render the Execute workspace.
    
    Design goals:
    - Zero clutter
    - Real-time feedback
    - Calm under pressure
    
    Components:
    - Order timeline animation
    - Broker latency live counter
    - Execution quality score
    - Slippage vs expected
    """
    st.markdown('<div class="sp-section-title">Execute</div>', unsafe_allow_html=True)
    st.caption("Execution performance + active orders. Select to inspect (Z5).")
    
    # Get data services
    data_service = get_ui_data_service()
    metric_deriver = get_metric_deriver()
    
    try:
        exec_quality = metric_deriver.get_execution_quality()
        
        quality_score = exec_quality.get('score', 0)
        slippage_avg = exec_quality.get('slippage_avg', 0)
        fill_rate = exec_quality.get('fill_rate', 0)
        latency_avg = exec_quality.get('latency_avg', 0)
    except Exception as e:
        DebugUtils.debug(f"Error rendering execution quality: {e}")

    # Z3 hero: timeline + execution KPIs
    with sp_surface("sp-surface sp-hero", aria_label="Execute hero"):
        cols = st.columns(4, vertical_alignment="center")
        with cols[0]:
            render_confidence_gauge(quality_score, size=150, label="Quality")
        with cols[1]:
            st.metric("Slip", f"{slippage_avg:.4f}%")
        with cols[2]:
            st.metric("Fill", f"{fill_rate:.1%}")
        with cols[3]:
            st.metric("Lat", f"{latency_avg:.0f}ms")

        try:
            orders = data_service.get_orders()
            if orders:
                render_execution_timeline(orders[:20], show_latency=True)
            else:
                render_empty_state(
                    "No order flow yet",
                    "Orders and execution timeline will appear once execution begins.",
                    icon="◌",
                )
        except Exception as e:
            DebugUtils.debug(f"Execute: error rendering timeline: {e}")
            render_empty_state(
                "Timeline unavailable",
                "Execution timeline will appear when orders are available.",
                icon="◌",
            )

    # Z4: active orders stream (dense rows)
    with sp_surface("sp-surface sp-rail", aria_label="Active orders"):
        st.markdown('<div class="sp-section-title">Active Orders</div>', unsafe_allow_html=True)
        st.caption("Select an order to inspect (Z5).")

        try:
            orders = data_service.get_orders()
        except Exception as e:
            DebugUtils.debug(f"Execute: error loading orders: {e}")
            orders = []

        active_orders = [
            o for o in orders
            if str(o.get("status", "")).lower() in {"pending", "submitted", "open", "partially_filled"}
        ]

        if not active_orders:
            render_empty_state(
                "No active orders",
                "Pending and open orders will stream here.",
                icon="◌",
            )
            return

        for idx, order in enumerate(active_orders[:20]):
            symbol = order.get("symbol", "UNKNOWN")
            status = str(order.get("status", "unknown")).upper()
            qty = order.get("quantity", 0)
            price = order.get("price", 0.0)
            order_key = order.get("id") or order.get("order_id") or idx

            selected = render_stream_row(
                title=str(symbol),
                subtitle=f"{status} · Qty {qty}",
                right_kpi_label="Px",
                right_kpi_value=f"{price}",
                pill_text=status,
                pill_status=status,
                key=f"exec_order_{order_key}",
            )
            if selected:
                set_active_context(order=str(order_key), symbol=str(symbol))
                st.rerun()

