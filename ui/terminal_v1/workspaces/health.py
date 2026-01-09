"""
Health Workspace

System health monitoring and status dashboard.
"""

import streamlit as st
from typing import Dict, Any
from datetime import datetime

from ui.terminal_v1.services.health_service import get_health_service
from ui.terminal_v1.components.primitives.section_header import render_section_header
from ui.terminal_v1.components.primitives.operational_status import render_operational_status
from ui.terminal_v1.layout.context_strip import render_context_strip
from ui.terminal_v1.layout.canvas import render_canvas


def render_health_context_strip() -> None:
    """Render Z3: Context strip for Health."""
    render_context_strip()
    
    col1, col2 = st.columns([1, 0.3])
    with col1:
        st.markdown(
            '''
            <div style="display: flex; align-items: center; gap: var(--spacing-sm);">
                <div class="sp-live-indicator">
                    <span class="sp-live-dot live"></span>
                    <span style="color: var(--color-text-2); font-size: var(--font-size-xs); font-weight: var(--font-weight-medium);">HEALTH</span>
                </div>
                <span style="color: var(--color-muted); font-size: var(--font-size-xs);">|</span>
                <span style="color: var(--color-text-2); font-size: var(--font-size-xs);">System Status Monitor</span>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div style="text-align: right; color: var(--color-muted); font-size: var(--font-size-xs);">Updated: {datetime.now().strftime("%H:%M:%S")}</div>',
            unsafe_allow_html=True
        )


def get_status_color(status: str) -> str:
    """Get color for status."""
    status_upper = status.upper()
    if status_upper in ["HEALTHY", "ENABLED"]:
        return "var(--color-green)"
    elif status_upper in ["DEGRADED", "UNHEALTHY", "UNAVAILABLE"]:
        return "var(--color-yellow)"
    elif status_upper in ["DOWN", "ERROR", "DISABLED", "CRITICAL"]:
        return "var(--color-red)"
    else:
        return "var(--color-muted)"


def render_health_canvas() -> None:
    """Render Z4: Main canvas for Health workspace."""
    health_service = get_health_service()
    
    render_section_header("System Health Status")
    
    # Auto-refresh every 5 seconds
    if 'health_auto_refresh' not in st.session_state:
        st.session_state.health_auto_refresh = True
    
    col1, col2 = st.columns([1, 0.2])
    with col1:
        st.markdown("**Auto-refresh:** Every 5 seconds")
    with col2:
        if st.button("🔄 Refresh Now", key="health_refresh"):
            st.rerun()
    
    # Get comprehensive health
    try:
        health_data = health_service.get_comprehensive_health()
        
        # Overall status
        overall_status = health_data.get("overall_status", "UNKNOWN")
        overall_color = get_status_color(overall_status)
        
        st.markdown(
            f'''
            <div style="padding: var(--spacing-md); background: var(--color-panel); border-radius: var(--border-radius); margin-bottom: var(--spacing-md);">
                <div style="display: flex; align-items: center; gap: var(--spacing-sm);">
                    <span style="font-size: var(--font-size-lg); font-weight: var(--font-weight-bold);">Overall Status:</span>
                    <span style="font-size: var(--font-size-lg); font-weight: var(--font-weight-bold); color: {overall_color};">{overall_status}</span>
                </div>
                <div style="margin-top: var(--spacing-xs); color: var(--color-text-2); font-size: var(--font-size-sm);">
                    Last checked: {health_data.get("timestamp", "N/A")}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
        
        # Backend health
        st.subheader("Backend API")
        backend_health = health_data.get("backend", {})
        backend_status = backend_health.get("status", "UNKNOWN")
        backend_color = get_status_color(backend_status)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'**Status:** <span style="color: {backend_color};">{backend_status}</span>', unsafe_allow_html=True)
        with col2:
            latency = backend_health.get("latency_ms")
            if latency:
                st.markdown(f"**Latency:** {latency}ms")
            else:
                st.markdown("**Latency:** N/A")
        with col3:
            st.markdown(f"**Message:** {backend_health.get('message', 'N/A')}")
        
        if backend_health.get("error"):
            st.error(f"Error: {backend_health.get('error')}")
        
        st.divider()
        
        # Services health
        st.subheader("Services Status")
        services = health_data.get("services", {})
        
        # Create status grid
        service_names = [
            "Data Fetch for Indian Stocks",
            "Data Fetch for US Stocks",
            "Equity",
            "Historical Data",
            "Options data",
            "Future & Options",
            "Backtesting",
            "Analysis"
        ]
        
        for service_name in service_names:
            service_health = services.get(service_name, {})
            service_status = service_health.get("status", "UNKNOWN")
            service_color = get_status_color(service_status)
            
            col1, col2, col3 = st.columns([2, 1, 3])
            with col1:
                st.markdown(f"**{service_name}**")
            with col2:
                st.markdown(f'<span style="color: {service_color}; font-weight: bold;">{service_status}</span>', unsafe_allow_html=True)
            with col3:
                message = service_health.get("message", "No status available")
                st.markdown(f'<span style="color: var(--color-text-2); font-size: var(--font-size-sm);">{message}</span>', unsafe_allow_html=True)
            
            # Show latency if available
            if service_health.get("latency_ms"):
                st.caption(f"Latency: {service_health.get('latency_ms')}ms")
            
            # Show error if available
            if service_health.get("error"):
                st.error(f"Error: {service_health.get('error')}")
        
        st.divider()
        
        # Providers health
        st.subheader("Data Providers")
        providers = health_data.get("providers", {})
        
        provider_display_names = {
            "indian_stocks": "Indian Stocks Provider",
            "us_stocks": "US Stocks Provider",
            "equity": "Equity Provider",
            "historical": "Historical Data Provider",
            "options": "Options Provider",
            "fno": "Futures & Options Provider"
        }
        
        for provider_key, provider_health in providers.items():
            provider_name = provider_display_names.get(provider_key, provider_key.replace("_", " ").title())
            provider_status = provider_health.get("status", "UNKNOWN")
            provider_color = get_status_color(provider_status)
            
            col1, col2, col3 = st.columns([2, 1, 3])
            with col1:
                st.markdown(f"**{provider_name}**")
            with col2:
                st.markdown(f'<span style="color: {provider_color}; font-weight: bold;">{provider_status}</span>', unsafe_allow_html=True)
            with col3:
                message = provider_health.get("message", "No status available")
                st.markdown(f'<span style="color: var(--color-text-2); font-size: var(--font-size-sm);">{message}</span>', unsafe_allow_html=True)
            
            # Show details if available
            details = provider_health.get("details", {})
            if details:
                with st.expander(f"Details for {provider_name}"):
                    st.json(details)
        
    except Exception as e:
        st.error(f"❌ Error loading health data: {str(e)}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())


# Note: render_health_context_strip and render_health_canvas are used directly from app.py
def render_health() -> None:
    """Render Health workspace."""
    render_health_context_strip()
    from ui.terminal_v1.layout.canvas import render_canvas
    render_canvas(render_health_canvas)

