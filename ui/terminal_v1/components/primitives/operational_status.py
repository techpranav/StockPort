"""
Operational Status Block

System-oriented status displays for empty states.
"""

import streamlit as st
from typing import Optional
from datetime import datetime


def render_operational_status(
    status: str,
    opportunities: int = 0,
    last_scan: Optional[str] = None,
    show_live: bool = True,
    reason: Optional[str] = None
) -> None:
    """
    Render an operational status block (for empty states).
    
    Args:
        status: Status text (e.g., "SCANNING", "NO SIGNALS")
        opportunities: Number of opportunities/signals
        last_scan: Last scan timestamp
        show_live: Show LIVE indicator
        reason: Optional reason text
    """
    # Build HTML safely
    live_section = ''
    if show_live:
        live_section = '<div style="display: flex; align-items: center; gap: var(--spacing-xs);"><span class="sp-live-dot"></span><span style="color: var(--color-text-2); font-size: var(--font-size-xs);">LIVE</span></div>'
    
    last_scan_section = ''
    if last_scan:
        last_scan_section = f'<div style="color: var(--color-muted); font-size: var(--font-size-xs); margin-top: var(--spacing-xs);">Last Scan: {last_scan}</div>'
    
    reason_section = ''
    if reason:
        # Escape HTML in reason text
        reason_escaped = reason.replace('<', '&lt;').replace('>', '&gt;')
        reason_section = f'<div style="color: var(--color-muted); font-size: var(--font-size-xs); margin-top: var(--spacing-xs);">{reason_escaped}</div>'
    
    html_content = f'''<div class="sp-operational-status">
<div style="display: flex; align-items: center; gap: var(--spacing-md); margin-bottom: var(--spacing-sm);">
<div style="color: var(--color-text); font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold);">Status: {status}</div>
{live_section}
</div>
<div style="display: flex; align-items: center; gap: var(--spacing-lg);">
<div style="color: var(--color-text-2); font-size: var(--font-size-xs);">Opportunities: <span style="color: var(--color-text); font-weight: var(--font-weight-medium);">{opportunities}</span></div>
{last_scan_section}
</div>
{reason_section}
</div>'''
    
    st.markdown(html_content, unsafe_allow_html=True)

