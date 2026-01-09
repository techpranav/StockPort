"""
Review Workspace

Performance review workspace with performance tabs, strategy health,
and trade replay feature.
"""

import streamlit as st
from typing import List, Dict, Any

from utils.debug_utils import DebugUtils
from ui.services import get_ui_data_service
from ui.components.layout import sp_surface
from ui.components.terminal.primitives import render_stream_row
from ui.components.visual import render_strategy_card
from ui.components.visual.empty_state import render_empty_state
from ui.workspaces.router import set_active_context


def render_review_workspace() -> None:
    """
    Render the Review workspace.
    
    Terminal mapping:
    - Z3: performance hero (summary + placeholder chart container)
    - Z4: trade/order stream + strategy health stream
    - Z5: inspection on selection
    """
    st.markdown('<div class="sp-section-title">Review</div>', unsafe_allow_html=True)
    st.caption("Performance + history. Select items to inspect (Z5).")
    
    # Get data service
    data_service = get_ui_data_service()

    # Z3 hero: performance summary
    with sp_surface("sp-surface sp-hero", aria_label="Review hero"):
        try:
            positions = data_service.get_positions()
        except Exception as e:
            DebugUtils.debug(f"Review: error loading positions: {e}")
            positions = []

        if positions:
            total_pnl = sum(pos.get("pnl", 0) for pos in positions)
            total_pnl_pct = (
                sum(pos.get("pnl_percent", 0) for pos in positions) / len(positions)
                if positions
                else 0
            )
            winning_trades = sum(1 for pos in positions if pos.get("pnl", 0) > 0)
            win_rate = (winning_trades / len(positions)) * 100 if positions else 0

            c1, c2, c3 = st.columns(3, vertical_alignment="center")
            with c1:
                st.metric("Total P&L", f"{total_pnl:,.2f}", delta=f"{total_pnl_pct:.2f}%")
            with c2:
                st.metric("Open", f"{len(positions)}")
            with c3:
                st.metric("Win", f"{win_rate:.1f}%")
        else:
            render_empty_state(
                "No positions yet",
                "Performance summary will appear once positions exist.",
                icon="◌",
            )

        st.markdown('<div class="sp-divider"></div>', unsafe_allow_html=True)
        st.caption("Performance / drawdown / replay charts stay placeholder (layout only).")
        render_empty_state(
            "No performance chart attached",
            "Charts will render here once the underlying data is available.",
            icon="◌",
        )

    # Z4 stream: recent orders + strategy health
    with sp_surface("sp-surface sp-rail", aria_label="Review stream"):
        st.markdown('<div class="sp-section-title">History</div>', unsafe_allow_html=True)
        st.caption("Recent orders and strategy health.")

        try:
            orders = data_service.get_orders()
        except Exception as e:
            DebugUtils.debug(f"Review: error loading orders: {e}")
            orders = []

        if orders:
            for idx, o in enumerate(orders[:15]):
                symbol = o.get("symbol", "UNKNOWN")
                status = str(o.get("status", "unknown")).upper()
                order_key = o.get("id") or o.get("order_id") or idx
                selected = render_stream_row(
                    title=str(symbol),
                    subtitle=f"{status}",
                    right_kpi_label="Qty",
                    right_kpi_value=str(o.get("quantity", "—")),
                    pill_text=status,
                    pill_status=status,
                    key=f"review_order_{order_key}",
                )
                if selected:
                    set_active_context(order=str(order_key), symbol=str(symbol))
                    st.rerun()
        else:
            render_empty_state(
                "No order history yet",
                "Orders will appear here as the system executes.",
                icon="◌",
            )

        st.markdown('<div class="sp-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sp-section-title">Strategies</div>', unsafe_allow_html=True)
        try:
            strategy_perf = data_service.get_strategy_performance()
        except Exception as e:
            DebugUtils.debug(f"Review: error loading strategy performance: {e}")
            strategy_perf = []

        if strategy_perf:
            for perf in strategy_perf[:6]:
                render_strategy_card(perf, show_details=False)
        else:
            render_empty_state(
                "No strategy performance",
                "Strategy health will appear here when the backend exposes performance.",
                icon="◌",
            )

