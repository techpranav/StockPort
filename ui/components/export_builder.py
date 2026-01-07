"""
Export Builder UI Component

Streamlit component for building export criteria and exporting data.
"""

import streamlit as st
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

from models.export_config import ExportCriteria, ExportFormat, DataType
from services.exporters.advanced_exporter import AdvancedExporter
from utils.debug_utils import DebugUtils


def render_export_builder(
    available_symbols: List[str],
    available_data: Optional[Dict[str, Any]] = None
) -> Optional[ExportCriteria]:
    """
    Render export builder UI component.
    
    Args:
        available_symbols: List of available stock symbols
        available_data: Optional pre-loaded data to export
        
    Returns:
        ExportCriteria if user wants to export, None otherwise
    """
    st.header("📊 Advanced Data Export")
    
    # Symbol selection
    st.subheader("Select Stocks")
    selected_symbols = st.multiselect(
        "Choose stocks to export",
        options=available_symbols,
        default=available_symbols[:5] if len(available_symbols) > 5 else available_symbols,
        help="Select one or more stocks to include in the export"
    )
    
    if not selected_symbols:
        st.warning("Please select at least one stock to export")
        return None
    
    # Date range selection
    st.subheader("Date Range")
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            help="Start date for data export"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            help="End date for data export"
        )
    
    if start_date > end_date:
        st.error("Start date must be before end date")
        return None
    
    # Data type selection
    st.subheader("Data Types")
    data_type_options = {
        "All Data": DataType.ALL,
        "Technical Indicators": DataType.TECHNICAL,
        "Fundamental Data": DataType.FUNDAMENTAL,
        "Trading Signals": DataType.SIGNALS,
        "Pattern Detections": DataType.PATTERNS,
        "Risk Metrics": DataType.RISK_METRICS
    }
    
    selected_data_types = st.multiselect(
        "Select data types to export",
        options=list(data_type_options.keys()),
        default=["All Data"],
        help="Choose which types of data to include"
    )
    
    data_types = [data_type_options[dt] for dt in selected_data_types]
    
    # Export format
    st.subheader("Export Format")
    format_options = {
        "Excel (.xlsx)": ExportFormat.EXCEL,
        "CSV (.csv)": ExportFormat.CSV,
        "JSON (.json)": ExportFormat.JSON,
        "PDF (.pdf)": ExportFormat.PDF,
        "Word (.docx)": ExportFormat.WORD
    }
    
    selected_format = st.selectbox(
        "Choose export format",
        options=list(format_options.keys()),
        index=0,
        help="Select the file format for export"
    )
    
    export_format = format_options[selected_format]
    
    # Advanced options (collapsible)
    with st.expander("Advanced Options"):
        # Indicator filtering
        st.write("**Indicator Filtering**")
        include_indicators = st.text_input(
            "Include specific indicators (comma-separated)",
            help="e.g., rsi, macd, sma_20"
        )
        exclude_indicators = st.text_input(
            "Exclude specific indicators (comma-separated)",
            help="e.g., obv, vwap"
        )
        
        include_list = [i.strip() for i in include_indicators.split(',') if i.strip()] if include_indicators else []
        exclude_list = [i.strip() for i in exclude_indicators.split(',') if i.strip()] if exclude_indicators else []
        
        # Custom filters
        st.write("**Custom Filters**")
        min_score = st.number_input(
            "Minimum Signal Score",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            help="Only export stocks with signal score above this value"
        )
    
    # Build criteria
    criteria = ExportCriteria(
        stock_symbols=selected_symbols,
        start_date=datetime.combine(start_date, datetime.min.time()),
        end_date=datetime.combine(end_date, datetime.max.time()),
        data_types=data_types,
        export_format=export_format,
        include_indicators=include_list,
        exclude_indicators=exclude_list,
        custom_filters={'min_score': min_score} if min_score > 0 else {}
    )
    
    # Export button
    if st.button("📥 Export Data", type="primary"):
        return criteria
    
    return None


def handle_export(
    criteria: ExportCriteria,
    data: Dict[str, Any]
) -> Optional[str]:
    """
    Handle the export process.
    
    Args:
        criteria: Export criteria
        data: Data to export
        
    Returns:
        Path to exported file or None if export failed
    """
    try:
        exporter = AdvancedExporter()
        output_path = exporter.export_data(data, criteria)
        
        st.success(f"✅ Data exported successfully to: {output_path}")
        
        # Provide download button
        with open(output_path, 'rb') as f:
            st.download_button(
                label="📥 Download Export",
                data=f.read(),
                file_name=output_path.split('/')[-1],
                mime="application/octet-stream"
            )
        
        return output_path
        
    except Exception as e:
        st.error(f"❌ Export failed: {str(e)}")
        DebugUtils.log_error(e, "Export failed")
        return None

