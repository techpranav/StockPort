"""
Z5 Detail / Action Panel (on-demand).

Implementation: Streamlit sidebar. Hidden by default (collapsed) and only
populated when there is an active selection in session state.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

from utils.debug_utils import DebugUtils
from ui.components.visual.empty_state import render_empty_state
from ui.components.visual.signal_card import render_signal_card
from ui.services import get_ui_data_service, get_metric_deriver
from ui.workspaces.router import clear_context, get_active_context


def render_detail_panel() -> None:
    """
    Render Z5 panel content into `st.sidebar` only when a selection exists.

    Selection sources:
    - Discover stream rows: symbol/signal
    - Execute stream rows: order
    - Review stream rows: trade/order (best-effort)
    """
    context = get_active_context()
    symbol = context.get("symbol")
    signal_id = context.get("signal")
    order_id = context.get("order")

    # Keep sidebar empty unless something is selected.
    if not symbol and not signal_id and not order_id:
        return

    with st.sidebar:
        st.markdown("### Details")

        # Clear selection (closes Z5 in practice because it becomes empty)
        if st.button("Clear", key="z5_clear_selection"):
            clear_context()
            st.rerun()

        st.markdown('<div class="sp-divider"></div>', unsafe_allow_html=True)

        if order_id:
            _render_order_details(order_id)
            return

        if symbol or signal_id:
            _render_signal_details(symbol or signal_id)
            return

        render_empty_state(
            "No selection",
            "Select a signal or order to inspect details here.",
            icon="◌",
        )


def _render_signal_details(symbol: str) -> None:
    data_service = get_ui_data_service()
    metric_deriver = get_metric_deriver()

    try:
        signals = metric_deriver.get_signal_stream(limit=50)
    except Exception as e:
        DebugUtils.debug(f"Z5: error reading signal stream: {e}")
        signals = []

    selected = next((s for s in signals if s.get("symbol") == symbol), None)
    if not selected:
        render_empty_state(
            "Signal not found",
            "This signal is no longer in the recent stream.",
            icon="◌",
        )
        return

    # Reuse existing component for full details (no new fields).
    render_signal_card(selected, show_expanded=True)


def _render_order_details(order_id: Any) -> None:
    data_service = get_ui_data_service()

    try:
        orders = data_service.get_orders()
    except Exception as e:
        DebugUtils.debug(f"Z5: error loading orders: {e}")
        orders = []

    # Try to match by id; fallback to index-like keys.
    selected = None
    for idx, o in enumerate(orders):
        if str(o.get("id", "")) == str(order_id) or str(o.get("order_id", "")) == str(order_id):
            selected = o
            break
        if str(order_id) == str(idx):
            selected = o
            break

    if not selected:
        render_empty_state(
            "Order not found",
            "This order is no longer in the current list.",
            icon="◌",
        )
        return

    st.markdown(f"**{selected.get('symbol', 'UNKNOWN')}**")
    st.caption(f"Status: {str(selected.get('status', 'unknown')).upper()}")

    st.markdown('<div class="sp-divider"></div>', unsafe_allow_html=True)

    # Display available fields without assuming schema.
    for k in ["side", "quantity", "price", "filled_qty", "avg_fill_price", "slippage", "latency_ms"]:
        if k in selected and selected.get(k) is not None:
            st.write(f"- {k}: {selected.get(k)}")


