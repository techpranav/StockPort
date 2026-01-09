"""
Z1 System Bar (always visible).

Purpose: trust + control in an ultra-compact strip.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from utils.debug_utils import DebugUtils
from ui.services import get_metric_deriver, get_ui_data_service
from ui.workspaces.router import get_active_workspace, set_active_workspace


def render_system_bar() -> None:
    """
    Render the Z1 system bar.

    Contains:
    - Workspace selector (compact)
    - Mode (LIVE/PAPER/BACKTEST/REPLAY)
    - Algo confidence (number + color)
    - Market bias
    - Health indicator
    - Pause/Resume/Kill actions (UI only; existing placeholders preserved)
    """
    data_service = get_ui_data_service()
    metric_deriver = get_metric_deriver()

    active_ws = get_active_workspace()

    # Derive status / metrics using existing UI services only.
    try:
        status = data_service.get_system_status()
        is_running = bool(status.get("is_running", False))
        mode_raw = str(status.get("mode", "manual") or "manual")
    except Exception as e:
        DebugUtils.debug(f"Z1: error getting system status: {e}")
        is_running = False
        mode_raw = "manual"

    try:
        algo_conf = float(metric_deriver.get_algo_confidence())
    except Exception as e:
        DebugUtils.debug(f"Z1: error deriving algo confidence: {e}")
        algo_conf = 0.0

    try:
        bias = str(metric_deriver.get_todays_bias() or "Neutral")
    except Exception as e:
        DebugUtils.debug(f"Z1: error deriving bias: {e}")
        bias = "Neutral"

    try:
        health = data_service.get_data_health()
        overall = str(health.get("overall_status", "UNKNOWN") or "UNKNOWN").upper()
    except Exception as e:
        DebugUtils.debug(f"Z1: error getting data health: {e}")
        overall = "UNKNOWN"

    # Left side: brand + workspace nav
    left, mid, right = st.columns([4.2, 3.4, 2.4], vertical_alignment="center")

    with left:
        b1, b2, b3, b4, b5, b6 = st.columns([1.4, 1, 1, 1, 1, 1], vertical_alignment="center")
        with b1:
            st.markdown('<span class="sp-sys-brand">Stockport</span>', unsafe_allow_html=True)
        _ws_button(b2, "Insight", "insight", active_ws)
        _ws_button(b3, "Discover", "discover", active_ws)
        _ws_button(b4, "Decide", "decide", active_ws)
        _ws_button(b5, "Execute", "execute", active_ws)
        _ws_button(b6, "Review", "review", active_ws)

    with mid:
        c1, c2, c3, c4 = st.columns([1.1, 1.1, 1.2, 1.0], vertical_alignment="center")

        with c1:
            _mode_selector(mode_raw)

        with c2:
            _kpi("Algo", _format_confidence(algo_conf), _confidence_color(algo_conf))

        with c3:
            _kpi("Bias", bias.upper(), _bias_color(bias))

        with c4:
            _kpi("Health", overall, _health_color(overall))

    with right:
        r1, r2, r3, r4 = st.columns([1, 1, 1, 1.2], vertical_alignment="center")
        with r1:
            with st.container():
                st.markdown('<div class="sp-sys-actions">', unsafe_allow_html=True)
                if st.button("⏸" if is_running else "▶", key="z1_pause_resume"):
                    st.info("Pause/Resume functionality to be implemented")
                st.markdown("</div>", unsafe_allow_html=True)
        with r2:
            with st.container():
                st.markdown('<div class="sp-sys-actions">', unsafe_allow_html=True)
                if st.button("⛔", key="z1_kill"):
                    st.info("Kill-switch functionality to be implemented")
                st.markdown("</div>", unsafe_allow_html=True)
        with r3:
            from ui.components.terminal.live_indicator import render_live_dot
            render_live_dot("#22C55E" if is_running else "#94A3B8", size=6)
        with r4:
            st.markdown('<span class="sp-sys-meta">Alt+I/D/E/X/R</span>', unsafe_allow_html=True)


def _ws_button(container: st.delta_generator.DeltaGenerator, label: str, ws_id: str, active_ws: str) -> None:
    with container:
        pressed = st.button(
            label,
            key=f"z1_ws_{ws_id}",
            type="secondary" if ws_id != active_ws else "primary",
            use_container_width=True,
        )
        if pressed:
            set_active_workspace(ws_id)
            try:
                st.query_params["workspace"] = ws_id
            except Exception:
                pass
            st.rerun()


def _mode_selector(mode_raw: str) -> None:
    mode_options = ["LIVE", "PAPER", "BACKTEST", "REPLAY"]
    normalized = mode_raw.strip().upper()
    if normalized not in mode_options:
        normalized = "PAPER" if "paper" in mode_raw.lower() else "LIVE" if "live" in mode_raw.lower() else "BACKTEST" if "backtest" in mode_raw.lower() else "REPLAY" if "replay" in mode_raw.lower() else "LIVE"

    st.selectbox(
        "Mode",
        mode_options,
        index=mode_options.index(normalized),
        key="z1_mode_select",
        label_visibility="collapsed",
    )


def _kpi(label: str, value: str, color: str) -> None:
    st.markdown(
        f"""
        <div class="sp-sys-kpi">
          <span class="sp-sys-meta">{label}</span>
          <strong style="color:{color}">{value}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_confidence(conf: float) -> str:
    try:
        return f"{int(round(conf))}"
    except Exception:
        return "—"


def _confidence_color(conf: float) -> str:
    if conf >= 80:
        return "#22C55E"
    if conf >= 60:
        return "#CBD5E1"
    if conf >= 40:
        return "#F59E0B"
    return "#EF4444"


def _bias_color(bias: str) -> str:
    b = (bias or "").lower()
    if "bull" in b or "up" in b:
        return "#22C55E"
    if "bear" in b or "down" in b:
        return "#EF4444"
    return "#F59E0B"


def _health_color(overall: str) -> str:
    o = (overall or "").upper()
    if o == "GREEN":
        return "#22C55E"
    if o == "YELLOW":
        return "#F59E0B"
    if o == "RED":
        return "#EF4444"
    return "#94A3B8"


