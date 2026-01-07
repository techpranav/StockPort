"""
Alert Creator UI Component

Streamlit component for creating new alerts.
"""

import streamlit as st
from typing import List
from datetime import datetime, timedelta

from services.alerts.alert_manager import AlertManager
from models.alert import Alert, AlertType, AlertStatus


def render_alert_creator(
    alert_manager: AlertManager,
    available_symbols: List[str]
) -> None:
    """
    Render alert creation form.
    
    Args:
        alert_manager: Alert manager instance
        available_symbols: List of available stock symbols
    """
    st.subheader("Create New Alert")
    
    # Symbol selection
    symbol = st.selectbox(
        "Stock Symbol",
        options=available_symbols,
        help="Select the stock to monitor"
    )
    
    # Alert type selection
    alert_type_options = {
        "Price Above Threshold": AlertType.PRICE_ABOVE,
        "Price Below Threshold": AlertType.PRICE_BELOW,
        "Buy Signal Detected": AlertType.SIGNAL_BUY,
        "Sell Signal Detected": AlertType.SIGNAL_SELL,
        "Pattern Detected": AlertType.PATTERN_DETECTED,
        "Volume Spike": AlertType.VOLUME_SPIKE,
        "High Risk": AlertType.RISK_HIGH
    }
    
    selected_type_label = st.selectbox(
        "Alert Type",
        options=list(alert_type_options.keys()),
        help="Choose the type of alert to create"
    )
    
    alert_type = alert_type_options[selected_type_label]
    
    # Threshold value (for price alerts)
    threshold_value = None
    if alert_type in [AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW]:
        threshold_value = st.number_input(
            "Threshold Price",
            min_value=0.0,
            value=100.0,
            step=0.01,
            help="Price threshold for the alert"
        )
    
    # Expiration (optional)
    expires_in_days = st.number_input(
        "Alert Expires In (days)",
        min_value=0,
        value=0,
        help="0 means alert never expires"
    )
    
    expires_at = None
    if expires_in_days > 0:
        expires_at = datetime.now() + timedelta(days=expires_in_days)
    
    # Notification channels
    st.subheader("Notification Channels")
    in_app = st.checkbox("In-App Notification", value=True)
    email = st.checkbox("Email Notification", value=False)
    push = st.checkbox("Browser Push", value=False)
    
    notification_channels = []
    if in_app:
        notification_channels.append('in_app')
    if email:
        notification_channels.append('email')
    if push:
        notification_channels.append('push')
    
    # Create button
    if st.button("➕ Create Alert", type="primary"):
        if not notification_channels:
            st.error("Please select at least one notification channel")
            return
        
        try:
            alert = alert_manager.create_alert(
                symbol=symbol,
                alert_type=alert_type,
                threshold_value=threshold_value,
                expires_at=expires_at,
                notification_channels=notification_channels
            )
            
            st.success(f"✅ Alert created successfully! Alert ID: {alert.id}")
            st.info(f"Monitoring {symbol} for {selected_type_label.lower()}")
            
        except Exception as e:
            st.error(f"❌ Failed to create alert: {str(e)}")

