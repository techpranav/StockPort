"""
Discover Workspace

Opportunity discovery workspace with opportunity radar, signal stream,
and filter sliders.
"""

import streamlit as st
from typing import List, Dict, Any

from utils.debug_utils import DebugUtils
from ui.services import get_ui_data_service, get_metric_deriver
from ui.components.charts import render_opportunity_radar
from ui.components.layout import sp_surface
from ui.components.terminal.primitives import render_stream_row
from ui.components.visual import render_empty_state
from ui.workspaces.router import set_active_context


def render_discover_workspace() -> None:
    """
    Render the Discover workspace.
    
    Features:
    - Opportunity radar (circular/heatmap)
    - Signal stream (dense rows; details in Z5)
    - Auto-updating with filters
    - Sorted by confidence × freshness
    """
    st.markdown('<div class="sp-section-title">Discover</div>', unsafe_allow_html=True)
    st.caption("Opportunity radar + ranked stream. Select to inspect (Z5).")
    
    # Get data services
    data_service = get_ui_data_service()
    metric_deriver = get_metric_deriver()
    
    from ui.components.terminal.live_indicator import render_live_badge, render_timestamp
    
    # Local filters (moved into stream rail for terminal layout)
    with sp_surface("sp-surface sp-hero", aria_label="Opportunity Radar"):
        header_col1, header_col2 = st.columns([1, 0.3], vertical_alignment="center")
        with header_col1:
            st.markdown('<div class="sp-section-title">Opportunity Radar</div>', unsafe_allow_html=True)
        with header_col2:
            render_live_badge("LIVE", "#22C55E")
            render_timestamp("Updated", show_live=True)
        st.caption("Primary canvas: score × liquidity × volatility.")

        try:
            opportunities = data_service.get_opportunities(limit=100)
            if opportunities:
                render_opportunity_radar(opportunities, chart_type="scatter")
            else:
                render_empty_state(
                    "No opportunities yet",
                    "When the scanner detects setups, they’ll appear here.",
                    icon="◌",
                )
        except Exception as e:
            DebugUtils.debug(f"Discover: error rendering radar: {e}")
            render_empty_state(
                "Radar unavailable",
                "Opportunity radar will populate when opportunities are available.",
                icon="◌",
            )

    # Dense stream + filters (Z4 container is provided by shell; we render in-flow)
    with sp_surface("sp-surface sp-rail", aria_label="Discover stream"):
        st.markdown('<div class="sp-section-title">Stream</div>', unsafe_allow_html=True)
        st.caption("Ranked by confidence × recency. Select to inspect.")

        st.caption("Min confidence")
        min_confidence = st.slider(
            "Min Confidence",
            0,
            100,
            60,
            key="discover_min_confidence",
            label_visibility="collapsed",
        )

        try:
            signals = metric_deriver.get_signal_stream(limit=50)
        except Exception as e:
            DebugUtils.debug(f"Discover: error reading signal stream: {e}")
            signals = []

        if not signals:
            render_empty_state(
                "No signals yet",
                "Signals will appear here as opportunities are scored.",
                icon="◌",
            )
            return

        filtered = [s for s in signals if s.get("score", 0) >= min_confidence]
        if not filtered:
            render_empty_state(
                "No matches",
                "Lower the confidence threshold to widen the stream.",
                icon="◌",
            )
            return

        # Already sorted by MetricDeriver; keep stable ordering.
        for idx, signal in enumerate(filtered[:20]):
            symbol = signal.get("symbol", "UNKNOWN")
            score = int(signal.get("score", 0))
            strategy = signal.get("strategy_id", "unknown")
            pill = "BUY" if score >= 60 else "WATCH" if score >= 40 else "AVOID"
            pill_status = "GREEN" if score >= 80 else "YELLOW" if score >= 40 else "RED"

            selected = render_stream_row(
                title=symbol,
                subtitle=strategy,
                right_kpi_label="Score",
                right_kpi_value=str(score),
                pill_text=pill,
                pill_status=pill_status,
                key=f"discover_row_{symbol}_{idx}",
            )
            if selected:
                set_active_context(symbol=symbol, signal=symbol)
                st.rerun()

