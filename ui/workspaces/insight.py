"""
Insight Workspace

Market environment & algo state workspace.
Terminal layout: Z3 (hero) + Z4 (stream). Z1/Z2 are rendered by app shell.
"""

import streamlit as st
from typing import Any, Dict

from utils.debug_utils import DebugUtils
from ui.services import get_ui_data_service, get_metric_deriver
from ui.components.visual import render_confidence_gauge, render_provider_health_tile
from ui.components.charts import render_regime_timeline
from ui.components.layout import sp_surface
from ui.components.visual.empty_state import render_empty_state


def render_insight_workspace() -> None:
    """
    Render the Insight workspace.
    
    Mapping:
    - Z3: Algo confidence (hero)
    - Z4: System health stream (providers/latency)
    """
    from ui.components.terminal.live_indicator import render_timestamp, render_live_badge
    
    # Get data services
    data_service = get_ui_data_service()
    metric_deriver = get_metric_deriver()
    
    # Z3
    with sp_surface("sp-surface sp-hero", aria_label="Insight hero"):
        header_col1, header_col2 = st.columns([1, 0.3], vertical_alignment="center")
        with header_col1:
            st.markdown('<div class="sp-section-title">Insight</div>', unsafe_allow_html=True)
        with header_col2:
            render_live_badge("LIVE", "#22C55E")
            render_timestamp("Updated", show_live=True)
        
        # Z3 content: confidence + compact KPIs
        try:
            confidence = metric_deriver.get_algo_confidence()
            cols = st.columns([1.2, 1.0, 1.0, 1.0], vertical_alignment="center")
            with cols[0]:
                render_confidence_gauge(confidence, size=180, label="Confidence")
            with cols[1]:
                st.metric("Readiness", f"{metric_deriver.get_market_readiness():.0f}")
            with cols[2]:
                st.metric("Bias", metric_deriver.get_todays_bias())
            with cols[3]:
                st.metric("Next", metric_deriver.get_next_action_eta() or "—")
        except Exception as e:
            DebugUtils.debug(f"Insight: error rendering hero: {e}")
            render_empty_state(
                "Insight not ready",
                "Waiting for market + strategy inputs to compute state.",
                icon="◌",
            )

    # Z4 content: health + regime timeline (compact)
    with sp_surface("sp-surface sp-l2", aria_label="Insight stream"):
        from ui.components.terminal.live_indicator import render_timestamp
        header_col1, header_col2 = st.columns([1, 0.4], vertical_alignment="center")
        with header_col1:
            st.markdown('<div class="sp-section-title">System</div>', unsafe_allow_html=True)
        with header_col2:
            render_timestamp("Updated", show_live=True)
        st.caption("Provider health and execution quality.")

        try:
            health_data = data_service.get_data_health()
            if health_data:
                overall_status = health_data.get("overall_status", "UNKNOWN")
                render_provider_health_tile("Angel One", overall_status, latency_ms=180, drop_rate=0.3)
                render_provider_health_tile("NSE", "GREEN", latency_ms=120, drop_rate=0.1)

                exec_quality = metric_deriver.get_execution_quality()
                latency = exec_quality.get("latency_avg", 0)
                if latency:
                    st.caption(f"Execution latency (avg): {latency:.0f}ms")
            else:
                render_empty_state(
                    "Health unavailable",
                    "Provider health will appear here when the backend is reachable.",
                    icon="◌",
                )
        except Exception as e:
            DebugUtils.debug(f"Insight: error rendering health: {e}")
            render_empty_state(
                "Health unavailable",
                "Provider health will appear here when the backend is reachable.",
                icon="◌",
            )

        try:
            regime_timeline = metric_deriver.get_regime_timeline(days=30)
            if regime_timeline:
                st.markdown('<div class="sp-divider"></div>', unsafe_allow_html=True)
                st.caption("Regime timeline")
                render_regime_timeline(regime_timeline)
        except Exception as e:
            DebugUtils.debug(f"Insight: error rendering regime timeline: {e}")

