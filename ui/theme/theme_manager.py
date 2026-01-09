"""
Theme Manager

Manages dark theme colors, CSS injection, and theme configuration.
"""

import streamlit as st
from typing import Dict, Any
from pathlib import Path


# Color Palette Constants
COLORS = {
    'background': '#0B1220',
    'background_alt': '#111827',
    'surface': '#121A2A',
    'surface_alt': '#161B22',
    'accent': '#3B82F6',
    'accent_hover': '#2563EB',
    'profit': '#22C55E',
    'loss': '#EF4444',
    'warning': '#F59E0B',
    'text_primary': '#F9FAFB',
    'text_secondary': '#D1D5DB',
    'text_muted': '#9CA3AF',
    'border': '#374151',
    'border_light': '#4B5563',
}


def get_theme_colors() -> Dict[str, str]:
    """
    Get theme color palette.
    
    Returns:
        Dictionary of color constants
    """
    return COLORS.copy()


def inject_theme() -> None:
    """
    Inject dark theme CSS into Streamlit app.
    
    This function should be called at the start of the main app
    to apply dark theme styling globally.
    """
    css_file = Path(__file__).parent / 'styles.css'
    
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Inject CSS
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    else:
        # Fallback: inject inline CSS if file doesn't exist
        _inject_fallback_css()


def _inject_fallback_css() -> None:
    """Inject fallback CSS if styles.css is not found."""
    fallback_css = f"""
    <style>
    /* Dark Theme Base Styles */
    .stApp {{
        background-color: {COLORS['background']};
        color: {COLORS['text_primary']};
    }}
    
    /* Main container */
    .main .block-container {{
        background-color: {COLORS['background']};
        padding-top: 2rem;
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['text_primary']};
    }}
    
    /* Text */
    p, span, div {{
        color: {COLORS['text_secondary']};
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {COLORS['text_primary']};
    }}
    
    /* Cards/Surfaces */
    .element-container {{
        background-color: {COLORS['surface']};
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid {COLORS['border']};
    }}
    </style>
    """
    st.markdown(fallback_css, unsafe_allow_html=True)

