"""
Alerts Panel UI Component

Streamlit component for managing alerts and viewing notifications.
"""

import streamlit as st
import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime

from services.alerts.alert_manager import AlertManager
from services.alerts.alert_engine import AlertEngine
from services.alerts.notification_service import NotificationService
from models.alert import Alert, AlertType, AlertStatus
from ui.components.alert_creator import render_alert_creator


def render_alerts_panel(
    alert_manager: AlertManager,
    alert_engine: AlertEngine,
    notification_service: NotificationService,
    available_symbols: List[str]
) -> None:
    """
    Render alerts management panel.
    
    Args:
        alert_manager: Alert manager instance
        alert_engine: Alert engine instance
        notification_service: Notification service instance
        available_symbols: List of available stock symbols
    """
    st.header("🔔 Alerts & Notifications")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Active Alerts", "Create Alert", "Notifications"])
    
    with tab1:
        render_active_alerts(alert_manager, alert_engine)
    
    with tab2:
        render_alert_creator(alert_manager, available_symbols)
    
    with tab3:
        render_notifications(notification_service)


def render_active_alerts(
    alert_manager: AlertManager,
    alert_engine: AlertEngine
) -> None:
    """Render active alerts list."""
    st.subheader("Active Alerts")
    
    # Get active alerts
    active_alerts = alert_manager.get_alerts(status=AlertStatus.ACTIVE)
    
    if not active_alerts:
        st.info("No active alerts. Create one in the 'Create Alert' tab.")
        return
    
    # Display alerts in a table
    alerts_data = []
    for alert in active_alerts:
        alerts_data.append({
            'Symbol': alert.symbol,
            'Type': alert.alert_type.value.replace('_', ' ').title(),
            'Threshold': alert.threshold_value or 'N/A',
            'Created': alert.created_at.strftime('%Y-%m-%d %H:%M'),
            'Triggers': alert.trigger_count,
            'Status': alert.status.value.title()
        })
    
    if alerts_data:
        df = pd.DataFrame(alerts_data)
        st.dataframe(df, use_container_width=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Alerts"):
                st.rerun()
        
        with col2:
            if st.button("▶️ Start Monitoring"):
                alert_engine.start_monitoring()
                st.success("Monitoring started")
        
        with col3:
            if st.button("⏸️ Stop Monitoring"):
                alert_engine.stop_monitoring()
                st.info("Monitoring stopped")
        
        # Delete alert
        st.subheader("Delete Alert")
        alert_ids = {f"{a.symbol} - {a.alert_type.value}": a.id for a in active_alerts}
        selected_alert = st.selectbox("Select alert to delete", options=list(alert_ids.keys()))
        
        if st.button("🗑️ Delete Alert", type="primary"):
            alert_id = alert_ids[selected_alert]
            if alert_manager.delete_alert(alert_id):
                st.success("Alert deleted successfully")
                st.rerun()
            else:
                st.error("Failed to delete alert")


def render_notifications(notification_service: NotificationService) -> None:
    """Render notifications list."""
    st.subheader("Recent Notifications")
    
    notifications = notification_service.get_notifications(limit=50)
    
    if not notifications:
        st.info("No notifications yet.")
        return
    
    # Display notifications
    for notification in notifications[:20]:  # Show last 20
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.write(f"**{notification.get('symbol', 'N/A')}**")
                st.write(notification.get('message', ''))
                timestamp = notification.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        st.caption(f"Triggered: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    except Exception:
                        st.caption(timestamp)
            
            with col2:
                if st.button("✓", key=f"read_{notification.get('alert_id')}"):
                    notification_service.mark_as_read(notification.get('alert_id'))
                    st.rerun()
            
            st.divider()

