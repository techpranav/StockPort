"""
Settings Panel

UI component for managing system settings with real-time updates.
"""

import streamlit as st
from typing import Dict, Any, Optional
import json

from utils.debug_utils import DebugUtils
from backend.settings import get_settings_manager, get_settings, SettingCategory


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
    
    settings_manager = get_settings_manager()
    settings = get_settings()
    
    # Category tabs
    categories = [
        ("Trading", SettingCategory.TRADING),
        ("Risk", SettingCategory.RISK),
        ("Capital", SettingCategory.CAPITAL),
        ("Timing", SettingCategory.TIMING),
        ("Data", SettingCategory.DATA),
        ("Performance", SettingCategory.PERFORMANCE)
    ]
    
    tab_names = [cat[0] for cat in categories]
    tabs = st.tabs(tab_names)
    
    for idx, (tab, (category_name, category)) in enumerate(zip(tabs, categories)):
        with tab:
            render_category_settings(
                category_name,
                category,
                settings_manager,
                settings
            )
    
    # Global actions
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reset All to Defaults", use_container_width=True):
            if st.session_state.get('confirm_reset', False):
                settings_manager.reset_all_to_defaults()
                st.success("All settings reset to defaults!")
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("Click again to confirm reset all settings")
    
    with col2:
        if st.button("💾 Export Settings", use_container_width=True):
            settings_data = settings_manager.get_all()
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
                        settings_manager.set(key, value, validate=True)
                    st.success("Settings imported successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error importing settings: {e}")


def render_category_settings(
    category_name: str,
    category: SettingCategory,
    settings_manager,
    settings
):
    """Render settings for a specific category."""
    definitions = settings_manager.get_definitions()
    category_settings = {
        k: v for k, v in definitions.items()
        if v.category == category
    }
    
    if not category_settings:
        st.info(f"No settings in {category_name} category")
        return
    
    st.subheader(f"{category_name} Settings")
    
    # Group settings by prefix for better organization
    setting_groups = {}
    for key, definition in category_settings.items():
        prefix = key.split('.')[0] if '.' in key else 'general'
        if prefix not in setting_groups:
            setting_groups[prefix] = []
        setting_groups[prefix].append((key, definition))
    
    for group_name, group_settings in setting_groups.items():
        if len(setting_groups) > 1:
            st.markdown(f"**{group_name.upper()}**")
        
        for key, definition in group_settings:
            render_setting(key, definition, settings_manager, settings)


def render_setting(
    key: str,
    definition,
    settings_manager,
    settings
):
    """Render a single setting with controls."""
    current_value = settings_manager.get(key)
    
    # Create label with description
    label = key.split('.')[-1].replace('_', ' ').title()
    if definition.description:
        tooltip = definition.description
    else:
        tooltip = None
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # Determine input type based on value type
        if definition.value_type == bool:
            new_value = st.checkbox(
                label,
                value=current_value,
                help=tooltip,
                key=f"setting_{key}"
            )
        elif definition.value_type == int:
            min_val = definition.min_value if definition.min_value is not None else 0
            max_val = definition.max_value if definition.max_value is not None else 1000000
            new_value = st.number_input(
                label,
                value=int(current_value),
                min_value=int(min_val) if min_val is not None else None,
                max_value=int(max_val) if max_val is not None else None,
                help=tooltip,
                key=f"setting_{key}"
            )
        elif definition.value_type == float:
            min_val = definition.min_value if definition.min_value is not None else 0.0
            max_val = definition.max_value if definition.max_value is not None else 1.0
            step = 0.01 if max_val <= 1.0 else 1.0
            new_value = st.number_input(
                label,
                value=float(current_value),
                min_value=float(min_val) if min_val is not None else None,
                max_value=float(max_val) if max_val is not None else None,
                step=step,
                format="%.4f" if max_val <= 1.0 else "%.2f",
                help=tooltip,
                key=f"setting_{key}"
            )
        elif definition.allowed_values:
            new_value = st.selectbox(
                label,
                options=definition.allowed_values,
                index=definition.allowed_values.index(current_value) if current_value in definition.allowed_values else 0,
                help=tooltip,
                key=f"setting_{key}"
            )
        else:
            new_value = st.text_input(
                label,
                value=str(current_value),
                help=tooltip,
                key=f"setting_{key}"
            )
    
    with col2:
        # Show current value
        if definition.value_type == float and current_value < 1.0:
            st.metric("", f"{current_value:.2%}")
        else:
            st.metric("", str(current_value))
    
    with col3:
        # Update button
        if st.button("Update", key=f"update_{key}", use_container_width=True):
            try:
                # Convert to correct type
                if definition.value_type == bool:
                    value_to_set = bool(new_value)
                elif definition.value_type == int:
                    value_to_set = int(new_value)
                elif definition.value_type == float:
                    value_to_set = float(new_value)
                else:
                    value_to_set = new_value
                
                success = settings_manager.set(key, value_to_set, validate=True)
                
                if success:
                    st.success(f"✅ {label} updated!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update {label}. Check value range.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        # Reset button
        if st.button("↩️", key=f"reset_{key}", help="Reset to default", use_container_width=True):
            settings_manager.reset_to_default(key)
            st.success(f"✅ {label} reset to default!")
            st.rerun()
    
    # Show range/constraints
    if definition.min_value is not None or definition.max_value is not None:
        constraint_text = "Range: "
        if definition.min_value is not None:
            constraint_text += f"{definition.min_value} ≤ "
        constraint_text += "value"
        if definition.max_value is not None:
            constraint_text += f" ≤ {definition.max_value}"
        st.caption(constraint_text)
    
    st.divider()


def render_settings_summary():
    """Render a summary card of key settings."""
    settings = get_settings()
    
    st.subheader("📊 Settings Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Max Position Size",
            f"{settings.get_max_position_size_percent():.1%}"
        )
    
    with col2:
        st.metric(
            "Risk Per Trade",
            f"{settings.get_default_risk_per_trade():.1%}"
        )
    
    with col3:
        st.metric(
            "Max Daily Loss",
            f"{settings.get_max_daily_loss_percent():.1%}"
        )
    
    with col4:
        st.metric(
            "Initial Capital",
            f"${settings.get_initial_capital():,.0f}"
        )

