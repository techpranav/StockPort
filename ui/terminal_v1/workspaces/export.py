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
    
    # Provider selection
    try:
        from services.stock_data_factory import StockDataFactory
        available_providers = StockDataFactory.list_providers()
    except:
        available_providers = ["yahoo_finance"]
    
    col1, col2 = st.columns(2)
    with col1:
        export_type = st.selectbox(
            "Export Type",
            options=["Equity", "Future & Options", "Fundamentals", "Historical Data"],
            key="export_type"
        )
    with col2:
        provider_name = st.selectbox(
            "Data Provider",
            options=available_providers,
            index=0 if "yahoo_finance" in available_providers else 0,
            key="export_provider"
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
                
                if export_type == "Equity" or export_type == "Historical Data":
                    # Fetch historical/equity data using provider
                    try:
                        from services.stock_data_factory import StockDataFactory
                        provider = StockDataFactory.get_provider(provider_name)
                        
                        # Convert timeframe to period and interval
                        period_map = {
                            "1min": ("5d", "1m"),
                            "5min": ("5d", "5m"),
                            "15min": ("5d", "15m"),
                            "30min": ("1mo", "30m"),
                            "1hour": ("3mo", "1h"),
                            "1day": ("1y", "1d"),
                            "1week": ("2y", "1wk"),
                            "1month": ("5y", "1mo")
                        }
                        period, interval = period_map.get(timeframe, ("1y", "1d"))
                        
                        # Fetch historical data
                        data = provider.fetch_historical_data(symbol, period=period, interval=interval)
                        
                        # Filter by date range if data has DatetimeIndex
                        if not data.empty and isinstance(data.index, pd.DatetimeIndex):
                            data = data[(data.index.date >= start_date) & (data.index.date <= end_date)]
                        
                    except Exception as e:
                        st.error(f"Error fetching {export_type.lower()} data: {str(e)}")
                        DebugUtils.log_error(e, f"Error exporting {export_type} data for {symbol}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        return
                
                elif export_type == "Fundamentals":
                    # Fetch fundamentals data using provider
                    try:
                        from services.stock_data_factory import StockDataFactory
                        # Try to use selected provider, fallback to yahoo_finance (best fundamentals support)
                        try:
                            provider = StockDataFactory.get_provider(provider_name)
                        except Exception as e:
                            DebugUtils.warning(f"Provider {provider_name} failed, using yahoo_finance: {e}")
                            provider = StockDataFactory.get_provider("yahoo_finance")
                        
                        # Fetch financials
                        financials = provider.fetch_financials(symbol)
                        
                        if not financials:
                            st.error("No fundamentals data available for the selected symbol.")
                            st.markdown('</div>', unsafe_allow_html=True)
                            return
                        
                        # Convert financials to DataFrame format for export
                        # Combine all financial statements into a structured format
                        export_data = {}
                        
                        # Yearly financials
                        yearly = financials.get("yearly", {})
                        if yearly:
                            for statement_type, statement_df in yearly.items():
                                if isinstance(statement_df, pd.DataFrame) and not statement_df.empty:
                                    export_data[f"yearly_{statement_type}"] = statement_df
                        
                        # Quarterly financials
                        quarterly = financials.get("quarterly", {})
                        if quarterly:
                            for statement_type, statement_df in quarterly.items():
                                if isinstance(statement_df, pd.DataFrame) and not statement_df.empty:
                                    export_data[f"quarterly_{statement_type}"] = statement_df
                        
                        # If only one statement, use it directly
                        if len(export_data) == 1:
                            data = list(export_data.values())[0]
                        else:
                            # Combine multiple statements (for Excel multi-sheet export)
                            data = export_data
                        
                    except Exception as e:
                        st.error(f"Error fetching fundamentals data: {str(e)}")
                        DebugUtils.log_error(e, f"Error exporting fundamentals data for {symbol}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        return
                
                elif export_type == "Future & Options":
                    st.warning("F&O data export not yet implemented. Please use Equity or Historical Data.")
                    st.markdown('</div>', unsafe_allow_html=True)
                    return
                
                # Handle fundamentals data (dict of DataFrames) vs single DataFrame
                if export_type == "Fundamentals" and isinstance(data, dict):
                    # Multiple DataFrames - export as Excel with multiple sheets or JSON
                    if export_format == "Excel":
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            for sheet_name, df in data.items():
                                if isinstance(df, pd.DataFrame) and not df.empty:
                                    df.to_excel(writer, sheet_name=sheet_name[:31], index=True)  # Excel sheet name limit
                        buffer.seek(0)
                        st.download_button(
                            label="📥 Download Excel",
                            data=buffer,
                            file_name=f"{symbol}_{export_type}_{start_date}_{end_date}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_excel"
                        )
                        st.success(f"✅ Fundamentals exported successfully! ({len(data)} statements)")
                        # Show preview of first statement
                        first_df = next(iter(data.values()))
                        if isinstance(first_df, pd.DataFrame):
                            st.subheader("Data Preview (First Statement)")
                            st.dataframe(first_df.head(50), use_container_width=True)
                    elif export_format == "JSON":
                        # Convert all DataFrames to dict format
                        json_data = {}
                        for key, df in data.items():
                            if isinstance(df, pd.DataFrame):
                                json_data[key] = df.to_dict(orient='index')
                        json_str = json.dumps(json_data, indent=2, default=str)
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_str,
                            file_name=f"{symbol}_{export_type}_{start_date}_{end_date}.json",
                            mime="application/json",
                            key="download_json"
                        )
                        st.success(f"✅ Fundamentals exported successfully! ({len(data)} statements)")
                    else:
                        st.warning("Fundamentals export supports Excel (multi-sheet) and JSON formats. Please select one of these.")
                else:
                    # Single DataFrame export
                    if data is None or (isinstance(data, pd.DataFrame) and data.empty):
                        st.error("No data available for the selected symbol and date range.")
                        st.markdown('</div>', unsafe_allow_html=True)
                        return
                    
                    if not isinstance(data, pd.DataFrame):
                        st.error(f"Unexpected data type: {type(data)}")
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

