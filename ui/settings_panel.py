"""
Settings Panel

UI component for managing system settings with real-time updates.
"""

import streamlit as st
from typing import Dict, Any, Optional
import json

from utils.debug_utils import DebugUtils
from ui.services import get_ui_data_service
from ui.services.api_client import get_api_client


def render_settings_panel():
    """
    Render settings management panel.
    
    Features:
    - View all settings by category
    - Update settings with validation
    - Reset to defaults
    - Real-time updates
    """
    st.header("⚙️ System Settings")
    st.markdown("Configure all system parameters. Changes apply immediately (no restart required).")
    
    api_client = get_api_client()
    
    try:
        # Get all settings and definitions
        all_settings = api_client.get_all_settings()
        definitions = api_client.get_setting_definitions()
        
        if not definitions:
            st.warning("⚠️ Could not load settings definitions. Backend may be unavailable.")
            return
        
        # Group definitions by category
        categories = {}
        for definition in definitions:
            category = definition.get("category", "general")
            if category not in categories:
                categories[category] = []
            categories[category].append(definition)
        
        # Create tabs for each category
        if categories:
            tab_names = list(categories.keys())
            tabs = st.tabs([cat.title() for cat in tab_names])
            
            for tab, category_name in zip(tabs, tab_names):
                with tab:
                    render_category_settings(
                        category_name,
                        categories[category_name],
                        all_settings,
                        api_client
                    )
        else:
            st.info("No settings available")
            
    except Exception as e:
        st.error(f"Error loading settings: {e}")
        DebugUtils.log_error(e, "Error in settings panel")
    
    # Global actions
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reset All to Defaults", use_container_width=True):
            if st.session_state.get('confirm_reset', False):
                try:
                    # This endpoint would need to be added to REST API
                    result = api_client._post("/settings/reset-all")
                    if result.get("success", False):
                        st.success("All settings reset to defaults!")
                        st.session_state.confirm_reset = False
                        st.rerun()
                    else:
                        st.error("Failed to reset settings")
                except Exception as e:
                    st.error(f"Error resetting settings: {e}")
            else:
                st.session_state.confirm_reset = True
                st.warning("Click again to confirm reset all settings")
    
    with col2:
        if st.button("💾 Export Settings", use_container_width=True):
            settings_data = api_client.get_all_settings()
            st.download_button(
                label="Download JSON",
                data=json.dumps(settings_data, indent=2),
                file_name="settings.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📥 Import Settings", use_container_width=True):
            uploaded_file = st.file_uploader("Upload settings JSON", type=['json'])
            if uploaded_file:
                try:
                    imported_settings = json.load(uploaded_file)
                    for key, value in imported_settings.items():
                        api_client.update_setting(key, value)
                    st.success("Settings imported successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error importing settings: {e}")


def render_category_settings(
    category_name: str,
    category_definitions: list,
    all_settings: dict,
    api_client
):
    """Render settings for a specific category."""
    if not category_definitions:
        st.info(f"No settings in {category_name} category")
        return
    
    st.subheader(f"{category_name.title()} Settings")
    
    # Group settings by prefix for better organization
    setting_groups = {}
    for definition in category_definitions:
        key = definition.get("key", "")
        prefix = key.split('.')[0] if '.' in key else 'general'
        if prefix not in setting_groups:
            setting_groups[prefix] = []
        setting_groups[prefix].append((key, definition))
    
    for group_name, group_settings in setting_groups.items():
        if len(setting_groups) > 1:
            st.markdown(f"**{group_name.upper()}**")
        
        for key, definition in group_settings:
            render_setting(key, definition, all_settings, api_client)


def render_setting(
    key: str,
    definition: dict,
    all_settings: dict,
    api_client
):
    """Render a single setting with controls."""
    current_value = all_settings.get(key, definition.get("default_value"))
    
    # Create label with description
    label = key.split('.')[-1].replace('_', ' ').title()
    tooltip = definition.get("description")
    
    value_type = definition.get("value_type", "string")
    min_value = definition.get("min_value")
    max_value = definition.get("max_value")
    allowed_values = definition.get("allowed_values")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # Determine input type based on value type
        if value_type == "bool" or value_type == bool:
            new_value = st.checkbox(
                label,
                value=bool(current_value),
                help=tooltip,
                key=f"setting_{key}"
            )
        elif value_type == "int" or value_type == int:
            min_val = min_value if min_value is not None else 0
            max_val = max_value if max_value is not None else 1000000
            new_value = st.number_input(
                label,
                value=int(current_value) if current_value is not None else 0,
                min_value=int(min_val) if min_val is not None else None,
                max_value=int(max_val) if max_val is not None else None,
                help=tooltip,
                key=f"setting_{key}"
            )
        elif value_type == "float" or value_type == float:
            min_val = min_value if min_value is not None else 0.0
            max_val = max_value if max_value is not None else 1.0
            step = 0.01 if max_val <= 1.0 else 1.0
            new_value = st.number_input(
                label,
                value=float(current_value) if current_value is not None else 0.0,
                min_value=float(min_val) if min_val is not None else None,
                max_value=float(max_val) if max_val is not None else None,
                step=step,
                format="%.4f" if max_val <= 1.0 else "%.2f",
                help=tooltip,
                key=f"setting_{key}"
            )
        elif allowed_values:
            current_idx = 0
            if current_value in allowed_values:
                current_idx = allowed_values.index(current_value)
            new_value = st.selectbox(
                label,
                options=allowed_values,
                index=current_idx,
                help=tooltip,
                key=f"setting_{key}"
            )
        else:
            new_value = st.text_input(
                label,
                value=str(current_value) if current_value is not None else "",
                help=tooltip,
                key=f"setting_{key}"
            )
    
    with col2:
        # Show current value
        if value_type in ("float", float) and isinstance(current_value, (int, float)) and current_value < 1.0:
            st.metric("", f"{current_value:.2%}")
        else:
            st.metric("", str(current_value))
    
    with col3:
        # Update button
        if st.button("Update", key=f"update_{key}", use_container_width=True):
            try:
                result = api_client.update_setting(key, new_value)
                if result.get("success", False):
                    st.success(f"✅ {label} updated!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update {label}. {result.get('error', 'Check value range.')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        # Reset button (would need reset endpoint)
        if st.button("↩️", key=f"reset_{key}", help="Reset to default", use_container_width=True):
            try:
                # This endpoint would need to be added to REST API
                result = api_client._post(f"/settings/reset/{key}")
                if result.get("success", False):
                    st.success(f"✅ {label} reset to default!")
                    st.rerun()
            except Exception as e:
                st.warning(f"Reset not available: {e}")
    
    # Show range/constraints
    if min_value is not None or max_value is not None:
        constraint_text = "Range: "
        if min_value is not None:
            constraint_text += f"{min_value} ≤ "
        constraint_text += "value"
        if max_value is not None:
            constraint_text += f" ≤ {max_value}"
        st.caption(constraint_text)
    
    st.divider()


def render_settings_summary():
    """Render a summary card of key settings."""
    api_client = get_api_client()
    settings = api_client.get_all_settings()
    
    st.subheader("📊 Settings Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        max_pos = settings.get("trading.max_position_size_percent", 0.10)
        st.metric("Max Position Size", f"{max_pos:.1%}")
    
    with col2:
        risk_per_trade = settings.get("risk.default_risk_per_trade", 0.02)
        st.metric("Risk Per Trade", f"{risk_per_trade:.1%}")
    
    with col3:
        max_daily_loss = settings.get("risk.max_daily_loss_percent", 0.05)
        st.metric("Max Daily Loss", f"{max_daily_loss:.1%}")
    
    with col4:
        initial_capital = settings.get("capital.initial_capital", 100000)
        st.metric("Initial Capital", f"${initial_capital:,.0f}")

