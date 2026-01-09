"""
Layout helpers for Stockport UI.

These utilities are purely presentational and are used to apply consistent
visual hierarchy (L1/L2/L3 surfaces) without changing any data or behavior.
"""

from ui.components.layout.surfaces import sp_surface
from ui.components.layout.zones import ZONES, ZoneIds, render_terminal_shell, sp_zone

__all__ = [
    "sp_surface",
    "sp_zone",
    "render_terminal_shell",
    "ZoneIds",
    "ZONES",
]


