"""
Z2 Context Bar (passive, glanceable).

Purpose: market environment awareness in a muted strip below Z1.
"""

from __future__ import annotations

import streamlit as st

from utils.debug_utils import DebugUtils
from ui.components.terminal.primitives import render_metric_badge
from ui.services import get_ui_data_service


def render_context_bar() -> None:
    """Render the Z2 market context bar using existing market state fields."""
    from ui.components.terminal.live_indicator import render_live_dot
    
    data_service = get_ui_data_service()

    try:
        market_state = data_service.get_market_state() or {}
    except Exception as e:
        DebugUtils.debug(f"Z2: error getting market state: {e}")
        market_state = {}

    regime = str(market_state.get("regime", "unknown") or "unknown").replace("_", " ").title()
    volatility = str(market_state.get("volatility_state", "unknown") or "unknown").title()
    breadth = str(market_state.get("breadth_state", "unknown") or "unknown").title()
    liquidity = str(market_state.get("liquidity_state", "unknown") or "unknown").title()

    # Live indicator for market data
    render_live_dot("#22C55E" if market_state else "#94A3B8", size=5)
    
    render_metric_badge("Regime", regime)
    render_metric_badge("Vol", volatility)
    render_metric_badge("Breadth", breadth)
    render_metric_badge("Liq", liquidity)

    # Optional: tiny hint if state is unknown (still passive, no error box).
    if (regime.lower() == "unknown") and not market_state:
        st.markdown('<span class="sp-sys-meta">Waiting for market state…</span>', unsafe_allow_html=True)


