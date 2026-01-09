"""
Terminal zoning layout helpers (Z1–Z5).

This module provides lightweight wrappers that add CSS hooks for consistent
terminal-style layout without changing any backend logic.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Iterator, Optional

import streamlit as st


@dataclass(frozen=True)
class ZoneIds:
    """Canonical zone identifiers for the Trading OS UI."""

    Z1_SYSTEM_BAR: str = "z1"
    Z2_CONTEXT_BAR: str = "z2"
    Z3_PRIMARY_WORK_AREA: str = "z3"
    Z4_SECONDARY_STREAM: str = "z4"
    Z5_DETAIL_PANEL: str = "z5"


ZONES = ZoneIds()


@contextmanager
def sp_zone(zone_id: str, css_class: str, aria_label: Optional[str] = None) -> Iterator[None]:
    """
    Wrap subsequent Streamlit elements in a zone container.

    Args:
        zone_id: Logical zone id (e.g., "z1", "z2"...)
        css_class: Space-separated CSS classes for styling hooks.
        aria_label: Optional aria-label for accessibility.
    """
    aria_attr = f' aria-label="{aria_label}"' if aria_label else ""
    # The `data-zone` attribute gives us stable selectors even if class names change.
    st.markdown(
        f'<div class="sp-zone {css_class}" data-zone="{zone_id}"{aria_attr}>',
        unsafe_allow_html=True,
    )
    try:
        yield
    finally:
        st.markdown("</div>", unsafe_allow_html=True)


def render_terminal_shell(
    *,
    render_z1: Callable[[], None],
    render_z2: Callable[[], None],
    render_z3: Callable[[], None],
    render_z4: Optional[Callable[[], None]] = None,
) -> None:
    """
    Render the common terminal shell for a workspace.

    Notes:
        - Z1 and Z2 are expected to be lightweight and always visible.
        - Z3 and Z4 are laid out as a 70/30 canvas by default.
        - Z5 is intentionally not part of the main flow (implemented as sidebar).
    """
    with sp_zone(ZONES.Z1_SYSTEM_BAR, "sp-z1", aria_label="System bar"):
        render_z1()

    with sp_zone(ZONES.Z2_CONTEXT_BAR, "sp-z2", aria_label="Market context"):
        render_z2()

    canvas_left, canvas_right = st.columns([7, 3], gap="large")
    with canvas_left:
        with sp_zone(ZONES.Z3_PRIMARY_WORK_AREA, "sp-z3", aria_label="Primary work area"):
            render_z3()

    with canvas_right:
        with sp_zone(ZONES.Z4_SECONDARY_STREAM, "sp-z4", aria_label="Secondary stream"):
            if render_z4 is not None:
                render_z4()


