"""
Insight Workspace

Market environment & algo state workspace.
"""

import streamlit as st
from typing import Dict, Any
from datetime import datetime

from ui.terminal_v1.services.ui_data_service import get_ui_data_service
from ui.terminal_v1.components.primitives.section_header import render_section_header
from ui.terminal_v1.components.primitives.metric_inline import render_metric_inline
from ui.terminal_v1.components.primitives.operational_status import render_operational_status
from ui.terminal_v1.components.primitives.divider import render_divider
from ui.terminal_v1.layout.context_strip import render_context_strip
from ui.terminal_v1.layout.canvas import render_canvas


def render_insight_context_strip() -> None:
    """Render Z3: Context strip for Insight."""
    render_context_strip()
    
    col1, col2 = st.columns([1, 0.3])
    with col1:
        st.markdown(
            '''
            <div style="display: flex; align-items: center; gap: var(--spacing-sm);">
                <div class="sp-live-indicator">
                    <span class="sp-live-dot"></span>
                    <span style="color: var(--color-text-2); font-size: var(--font-size-xs); font-weight: var(--font-weight-medium);">LIVE</span>
                </div>
                <span style="color: var(--color-muted); font-size: var(--font-size-xs);">|</span>
                <span style="color: var(--color-text-2); font-size: var(--font-size-xs);">Market Analysis</span>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with col2:
        render_metric_inline("Updated", datetime.now().strftime("%H:%M:%S"))


def render_insight_canvas() -> None:
    """Render Z4: Main canvas for Insight."""
    data_service = get_ui_data_service()
    
    # Primary: Confidence Gauge (hero)
    render_section_header("Algo Confidence")
    
    st.markdown('<div class="sp-radar-container">', unsafe_allow_html=True)
    
    try:
        confidence = data_service.get_algo_confidence()
        readiness = data_service.get_market_readiness()
        bias = data_service.get_todays_bias()
        next_action = data_service.get_next_action_eta()
        
        # Confidence display
        col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
        
        with col1:
            # Simple confidence display (gauge would go here)
            st.markdown(
                f'''
                <div style="text-align: center; padding: var(--spacing-lg);">
                    <div style="font-size: 4rem; font-weight: var(--font-weight-bold); color: var(--color-accent);">
                        {confidence:.0f}%
                    </div>
                    <div style="color: var(--color-muted); font-size: var(--font-size-sm); margin-top: var(--spacing-sm);">
                        Confidence
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
        
        with col2:
            st.metric("Readiness", f"{readiness:.0f}")
        
        with col3:
            st.metric("Bias", bias or "—")
        
        with col4:
            st.metric("Next", next_action or "—")
            
    except Exception as e:
        render_operational_status(
            status="NOT READY",
            opportunities=0,
            last_scan=datetime.now().strftime("%H:%M:%S"),
            show_live=True,
            reason="Waiting for market + strategy inputs to compute state."
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Divider
    render_divider()
    
    # Secondary: System Health
    render_section_header("System Health")
    
    try:
        health_data = data_service.get_data_health()
        exec_quality = data_service.get_execution_quality()
        
        if health_data:
            overall_status = health_data.get("overall_status", "UNKNOWN")
            
            # Provider health tiles
            st.markdown(
                f'''
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-md);">
                    <div class="sp-operational-status">
                        <div style="color: var(--color-text); font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); margin-bottom: var(--spacing-xs);">
                            Angel One
                        </div>
                        <div style="color: var(--color-text-2); font-size: var(--font-size-xs);">
                            Status: <span class="sp-status-pill {'green' if overall_status == 'GREEN' else 'yellow' if overall_status == 'YELLOW' else 'red'}">{overall_status}</span>
                        </div>
                        <div style="color: var(--color-muted); font-size: var(--font-size-xs); margin-top: var(--spacing-xs);">
                            Latency: 180ms | Drop: 0.3%
                        </div>
                    </div>
                    <div class="sp-operational-status">
                        <div style="color: var(--color-text); font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); margin-bottom: var(--spacing-xs);">
                            NSE
                        </div>
                        <div style="color: var(--color-text-2); font-size: var(--font-size-xs);">
                            Status: <span class="sp-status-pill green">GREEN</span>
                        </div>
                        <div style="color: var(--color-muted); font-size: var(--font-size-xs); margin-top: var(--spacing-xs);">
                            Latency: 120ms | Drop: 0.1%
                        </div>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
            if exec_quality:
                latency = exec_quality.get("latency_avg", 0)
                if latency:
                    st.caption(f"Execution latency (avg): {latency:.0f}ms")
        else:
            render_operational_status(
                status="UNAVAILABLE",
                opportunities=0,
                last_scan=datetime.now().strftime("%H:%M:%S"),
                show_live=True,
                reason="Provider health will appear here when the backend is reachable."
            )
    except Exception as e:
        render_operational_status(
            status="UNAVAILABLE",
            opportunities=0,
            last_scan=datetime.now().strftime("%H:%M:%S"),
            show_live=True,
            reason="Health data unavailable."
        )


def render_insight() -> None:
    """Render Insight workspace."""
    render_insight_context_strip()
    render_canvas(render_insight_canvas)

