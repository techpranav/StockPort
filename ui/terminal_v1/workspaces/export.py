"""
Data Export Workspace

Export market data in various formats.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import io

from ui.terminal_v1.services.ui_data_service import get_ui_data_service
from ui.terminal_v1.components.primitives.section_header import render_section_header
from ui.terminal_v1.components.primitives.operational_status import render_operational_status
from ui.terminal_v1.layout.context_strip import render_context_strip
from ui.terminal_v1.layout.canvas import render_canvas
from utils.debug_utils import DebugUtils


def render_export_context_strip() -> None:
    """Render Z3: Context strip for Export."""
    render_context_strip()
    
    col1, col2 = st.columns([1, 0.3])
    with col1:
        st.markdown(
            '''
            <div style="display: flex; align-items: center; gap: var(--spacing-sm);">
                <div class="sp-live-indicator">
                    <span class="sp-live-dot idle"></span>
                    <span style="color: var(--color-text-2); font-size: var(--font-size-xs); font-weight: var(--font-weight-medium);">EXPORT</span>
                </div>
                <span style="color: var(--color-muted); font-size: var(--font-size-xs);">|</span>
                <span style="color: var(--color-text-2); font-size: var(--font-size-xs);">Data Export & Download</span>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div style="text-align: right; color: var(--color-muted); font-size: var(--font-size-xs);">Updated: {datetime.now().strftime("%H:%M:%S")}</div>',
            unsafe_allow_html=True
        )


def render_export_canvas() -> None:
    """Render Z4: Main canvas for Export workspace."""
    data_service = get_ui_data_service()
    
    render_section_header("Data Export")
    
    # Export type selection
    export_type = st.selectbox(
        "Export Type",
        options=["Equity", "Future & Options", "Fundamentals", "Historical Data"],
        key="export_type"
    )
    
    st.markdown('<div class="sp-radar-container">', unsafe_allow_html=True)
    
    # Common fields
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.text_input(
            "Symbol",
            placeholder="e.g., RELIANCE, AAPL",
            key="export_symbol"
        )
    
    with col2:
        timeframe = st.selectbox(
            "Timeframe",
            options=["1min", "5min", "15min", "30min", "1hour", "1day", "1week", "1month"],
            index=5,  # Default to 1day
            key="export_timeframe"
        )
    
    # Date range
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now(),
            key="export_start_date"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now(),
            key="export_end_date"
        )
    
    if start_date >= end_date:
        st.error("Start date must be before end date")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Format selection
    export_format = st.selectbox(
        "Export Format",
        options=["CSV", "Excel", "JSON", "Parquet"],
        key="export_format"
    )
    
    # Additional options based on export type
    if export_type == "Future & Options":
        col1, col2 = st.columns(2)
        with col1:
            expiry_date = st.date_input(
                "Expiry Date (Optional)",
                value=None,
                key="export_expiry_date"
            )
        with col2:
            option_type = st.selectbox(
                "Option Type",
                options=["All", "Call", "Put"],
                key="export_option_type"
            )
    
    elif export_type == "Fundamentals":
        include_ratios = st.checkbox("Include Financial Ratios", value=True, key="export_include_ratios")
        include_statements = st.checkbox("Include Financial Statements", value=False, key="export_include_statements")
    
    # Export button
    if st.button("📥 Export Data", type="primary", key="export_button", use_container_width=True):
        if not symbol:
            st.error("Please enter a symbol")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        with st.spinner(f"Exporting {export_type} data for {symbol}..."):
            try:
                # Fetch data based on export type
                data = None
                
                if export_type == "Equity":
                    # Fetch equity data
                    try:
                        from services.data_providers.adapters.adapter_factory import AdapterFactory
                        adapter = AdapterFactory.get_adapter("yahoo_finance")
                        
                        # Convert timeframe to period
                        period_map = {
                            "1min": "1d",
                            "5min": "5d",
                            "15min": "15d",
                            "30min": "1mo",
                            "1hour": "3mo",
                            "1day": "1y",
                            "1week": "2y",
                            "1month": "5y"
                        }
                        period = period_map.get(timeframe, "1y")
                        
                        data = adapter.get_historical_data(
                            symbol=symbol,
                            start_date=start_date,
                            end_date=end_date,
                            interval=timeframe
                        )
                    except Exception as e:
                        st.error(f"Error fetching equity data: {str(e)}")
                        DebugUtils.log_error(e, f"Error exporting equity data for {symbol}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        return
                
                elif export_type == "Historical Data":
                    # Similar to equity but with more options
                    try:
                        from services.data_providers.adapters.adapter_factory import AdapterFactory
                        adapter = AdapterFactory.get_adapter("yahoo_finance")
                        
                        data = adapter.get_historical_data(
                            symbol=symbol,
                            start_date=start_date,
                            end_date=end_date,
                            interval=timeframe
                        )
                    except Exception as e:
                        st.error(f"Error fetching historical data: {str(e)}")
                        DebugUtils.log_error(e, f"Error exporting historical data for {symbol}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        return
                
                elif export_type == "Future & Options":
                    st.warning("F&O data export not yet implemented. Please use Equity or Historical Data.")
                    st.markdown('</div>', unsafe_allow_html=True)
                    return
                
                elif export_type == "Fundamentals":
                    st.warning("Fundamentals data export not yet implemented. Please use Equity or Historical Data.")
                    st.markdown('</div>', unsafe_allow_html=True)
                    return
                
                if data is None or data.empty:
                    st.error("No data available for the selected symbol and date range.")
                    st.markdown('</div>', unsafe_allow_html=True)
                    return
                
                # Convert to requested format
                if export_format == "CSV":
                    csv = data.to_csv(index=True)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"{symbol}_{export_type}_{start_date}_{end_date}.csv",
                        mime="text/csv",
                        key="download_csv"
                    )
                
                elif export_format == "Excel":
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        data.to_excel(writer, sheet_name='Data', index=True)
                    buffer.seek(0)
                    st.download_button(
                        label="📥 Download Excel",
                        data=buffer,
                        file_name=f"{symbol}_{export_type}_{start_date}_{end_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel"
                    )
                
                elif export_format == "JSON":
                    json_str = data.to_json(orient='index', date_format='iso')
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"{symbol}_{export_type}_{start_date}_{end_date}.json",
                        mime="application/json",
                        key="download_json"
                    )
                
                elif export_format == "Parquet":
                    buffer = io.BytesIO()
                    data.to_parquet(buffer, index=True)
                    buffer.seek(0)
                    st.download_button(
                        label="📥 Download Parquet",
                        data=buffer,
                        file_name=f"{symbol}_{export_type}_{start_date}_{end_date}.parquet",
                        mime="application/octet-stream",
                        key="download_parquet"
                    )
                
                # Show preview
                st.success(f"✅ Data exported successfully! ({len(data)} rows)")
                st.subheader("Data Preview")
                st.dataframe(data.head(100), use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")
                DebugUtils.log_error(e, f"Error exporting {export_type} data")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())
    
    st.markdown('</div>', unsafe_allow_html=True)


# Note: render_export_context_strip and render_export_canvas are used directly from app.py
def render_export() -> None:
    """Render Export workspace."""
    render_export_context_strip()
    from ui.terminal_v1.layout.canvas import render_canvas
    render_canvas(render_export_canvas)

