"""
Decide Workspace

Strategy reasoning workspace showing why the algo wants a trade.
"""

import streamlit as st
from typing import Dict, Any, Optional

from utils.debug_utils import DebugUtils
from ui.services import get_ui_data_service, get_metric_deriver
from ui.components.charts import render_risk_reward_map
from ui.components.layout import sp_surface
from ui.components.terminal.primitives import render_stream_row
from ui.components.visual import render_empty_state, render_signal_card
from ui.workspaces.router import get_active_context, set_active_context


def render_decide_workspace() -> None:
    """
    Render the Decide workspace.
    
    For each signal shows:
    - Strategy reasoning
    - Indicator contribution
    - Risk-reward map
    - Portfolio impact simulation (basic in v5)
    - Confidence decay timer
    """
    st.markdown('<div class="sp-section-title">Decide</div>', unsafe_allow_html=True)
    st.caption("Reasoning + risk/reward. Select a candidate to inspect.")
    
    # Get active context
    context = get_active_context()
    active_symbol = context.get('symbol')
    active_signal = context.get('signal')
    
    # Get data services
    data_service = get_ui_data_service()
    metric_deriver = get_metric_deriver()
    
    # Load recent signals (for selection and details)
    try:
        signals = metric_deriver.get_signal_stream(limit=50)
    except Exception as e:
        DebugUtils.debug(f"Decide: error loading signals: {e}")
        signals = []
    
    # Get signal data
    try:
        # Find active signal
        active_signal_data = None
        if active_symbol:
            for signal in signals:
                if signal.get('symbol') == active_symbol:
                    active_signal_data = signal
                    break
        
        # Z3 hero: either selected signal RR map, or intentional empty state
        with sp_surface("sp-surface sp-hero", aria_label="Decide hero"):
            if not active_signal_data:
                render_empty_state(
                    "No active candidate",
                    "Select a signal from the stream to see risk/reward and reasoning.",
                    icon="◌",
                )
            else:
                strategy_id = active_signal_data.get("strategy_id", "unknown")
                st.caption(f"Strategy: {strategy_id}")

                # Risk-Reward Map (hero)
                risk_reward_signals = [{
                    "symbol": active_signal_data.get("symbol"),
                    "score": active_signal_data.get("score", 0),
                    "risk_amount": active_signal_data.get("price", 0) * 10 * 0.05,
                    "reward_amount": active_signal_data.get("price", 0) * 10 * 0.10,
                    "risk_reward_ratio": 2.0,
                    "entry_price": active_signal_data.get("price", 0),
                    "stop_loss": active_signal_data.get("price", 0) * 0.95,
                    "take_profit": active_signal_data.get("price", 0) * 1.10,
                }]
                render_risk_reward_map(risk_reward_signals, show_portfolio_impact=True)

        # Z4 support: candidates + indicator breakdown (compact)
        with sp_surface("sp-surface sp-l2", aria_label="Decide support"):
            st.markdown('<div class="sp-section-title">Candidates</div>', unsafe_allow_html=True)
            st.caption("Select to load risk/reward into the hero canvas.")

            if not signals:
                render_empty_state(
                    "No candidates",
                    "When opportunities are detected, candidates will appear here.",
                    icon="◌",
                )
                return

            for idx, s in enumerate(signals[:12]):
                symbol = s.get("symbol", "UNKNOWN")
                score = int(s.get("score", 0))
                strategy = s.get("strategy_id", "unknown")
                pill = "BUY" if score >= 60 else "WATCH" if score >= 40 else "AVOID"
                pill_status = "GREEN" if score >= 80 else "YELLOW" if score >= 40 else "RED"

                selected = render_stream_row(
                    title=symbol,
                    subtitle=strategy,
                    right_kpi_label="Score",
                    right_kpi_value=str(score),
                    pill_text=pill,
                    pill_status=pill_status,
                    key=f"decide_row_{symbol}_{idx}",
                )
                if selected:
                    set_active_context(symbol=symbol, signal=symbol)
                    st.rerun()

            if active_signal_data:
                st.markdown('<div class="sp-divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="sp-section-title">Reasoning</div>', unsafe_allow_html=True)
                st.caption("Indicator contributions (as provided in the feed).")

                indicators = active_signal_data.get("indicators", {}) or {}
                if not indicators:
                    render_empty_state(
                        "No breakdown available",
                        "This signal doesn’t include indicator contribution in the current feed.",
                        icon="◌",
                    )
                else:
                    # Compact list; avoid heavy progress UI.
                    for k, v in list(indicators.items())[:10]:
                        st.write(f"- {k}: {v}")
        
    except Exception as e:
        DebugUtils.debug(f"Error rendering decide workspace: {e}")
        render_empty_state(
            "Decide unavailable",
            "Decision view will populate when signal data is available.",
            icon="◌",
        )

