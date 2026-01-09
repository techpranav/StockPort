"""
Terminal UI primitives.

Reusable, dense, terminal-style presentation components that standardize
status, metrics, and stream rows across the v5 Trading OS UI.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import streamlit as st


def get_status_color(status: str) -> str:
    """Map a status token to a semantic color (outcomes only)."""
    s = (status or "").strip().upper()
    if s in {"GREEN", "HEALTHY", "OK", "LIVE"}:
        return "#22C55E"
    if s in {"YELLOW", "WARN", "WARNING", "DEGRADED"}:
        return "#F59E0B"
    if s in {"RED", "ERROR", "DOWN", "FAILED"}:
        return "#EF4444"
    return "#94A3B8"


def render_status_pill(text: str, status: str) -> None:
    """Render an inline status pill."""
    color = get_status_color(status)
    st.markdown(
        f'<span class="sp-pill" style="color:{color}; border-color:rgba(148,163,184,0.20)">{text}</span>',
        unsafe_allow_html=True,
    )


def render_metric_badge(label: str, value: str) -> None:
    """Render a compact, muted metric badge for Z2 context."""
    st.markdown(
        f"""
        <span class="sp-badge">
          <span class="sp-badge-label">{label}</span>
          <span class="sp-badge-value">{value}</span>
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_stream_row(
    *,
    title: str,
    subtitle: Optional[str],
    right_kpi_label: str,
    right_kpi_value: str,
    pill_text: str,
    pill_status: str,
    key: str,
    on_select: Optional[Tuple[str, Any]] = None,
) -> bool:
    """
    Render a dense stream row that can be selected.

    Args:
        title: Primary left label (e.g., symbol).
        subtitle: Secondary left label (e.g., strategy or time).
        right_kpi_label: Label on the right (e.g., Score).
        right_kpi_value: Value on the right.
        pill_text: Inline pill text (e.g., BUY/WATCH).
        pill_status: Status for pill color mapping.
        key: Stable Streamlit key.
        on_select: Optional session_state assignment (key, value) when row is selected.

    Returns:
        True if selected.
    """
    left, mid, right = st.columns([4.8, 2.2, 3.0], vertical_alignment="center")
    with left:
        st.markdown(
            f"""
            <div class="sp-card-title">
              <span class="sp-symbol">{title}</span>
              <span class="sp-pill" style="color:{get_status_color(pill_status)}; border-color:rgba(148,163,184,0.22)">
                {pill_text}
              </span>
            </div>
            <div class="sp-meta">{subtitle or ""}</div>
            """,
            unsafe_allow_html=True,
        )

    with mid:
        st.markdown(
            f"""
            <div class="sp-kpi">
              <div class="sp-kpi-label">{right_kpi_label}</div>
              <div class="sp-kpi-value">{right_kpi_value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        selected = st.button("Select", key=key)

    if selected and on_select is not None:
        st.session_state[on_select[0]] = on_select[1]

    st.markdown('<div class="sp-divider"></div>', unsafe_allow_html=True)
    return selected


