import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import os
import zipfile
import tempfile

from services.exporters.report_manager import ReportManager
from utils.debug_utils import DebugUtils
from config.constants.Messages import (
    HEADER_REPORT_HISTORY,
    LABEL_FILTER_BY_SYMBOL,
    LABEL_FILTER_BY_TYPE,
    LABEL_FILTER_BY_DAYS,
    MSG_NO_REPORTS_AVAILABLE,
    SUCCESS_REPORT_DELETED,
    BUTTON_DELETE_REPORT,
    BUTTON_CLEANUP_REPORTS
)

def render_report_manager():
    """Render the report management interface."""
    try:
        st.header(HEADER_REPORT_HISTORY)
        
        # Initialize report manager
        report_manager = ReportManager()
        
        # Get all available reports
        reports = report_manager.get_reports()
        
        if not reports:
            st.info(MSG_NO_REPORTS_AVAILABLE)
            return
        
        # Show summary of available reports
        unique_symbols = sorted(list(set([report['symbol'] for report in reports])))
        unique_types = sorted(list(set([report['report_type'] for report in reports])))
        
        st.success(f"📊 **{len(reports)} reports available** for {len(unique_symbols)} symbols: {', '.join(unique_symbols)}")
        st.write(f"Report types: {', '.join(unique_types)}")
        
        # Filters
        st.subheader("🔍 Filter Reports")
        
        # Add clear filters button and download all button
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Clear All Filters", help="Reset all filters to show all reports"):
                st.rerun()
        
        with col2:
            # Show download options directly
            if st.button("📦 Show Download Options", help="Show download options for all reports"):
                st.session_state['show_download_options'] = True
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Symbol filter
            all_symbols = sorted(list(set([report['symbol'] for report in reports])))
            selected_symbols = st.multiselect(
                LABEL_FILTER_BY_SYMBOL,
                options=all_symbols,
                default=all_symbols,  # Show ALL symbols by default
                help="Select specific symbols to filter, or leave all selected to see everything"
            )
        
        with col2:
            # Report type filter
            all_types = sorted(list(set([report['report_type'] for report in reports])))
            selected_types = st.multiselect(
                LABEL_FILTER_BY_TYPE,
                options=all_types,
                default=all_types,  # Show ALL types by default
                help="Select specific report types to filter (Excel/Word)"
            )
        
        with col3:
            # Date range filter
            max_days = st.number_input(
                LABEL_FILTER_BY_DAYS,
                min_value=1,
                max_value=365,
                value=30,
                help="Show reports from the last N days"
            )
        
        # Filter reports based on criteria
        filtered_reports = filter_reports(
            reports, 
            selected_symbols, 
            selected_types, 
            max_days
        )
        
        # Show download options if requested
        if st.session_state.get('show_download_options', False):
            st.markdown("---")
            st.subheader("📦 Download All Reports")
            
            # Group reports by type
            excel_reports = [r for r in reports if r['report_type'] == 'excel']
            word_reports = [r for r in reports if r['report_type'] == 'word']
            
            col1, col2, col3 = st.columns(3)
            
            # Excel reports ZIP
            if excel_reports:
                with col1:
                    excel_zip_data, excel_count = create_historical_zip_data(excel_reports, "excel")
                    if excel_zip_data:
                        st.download_button(
                            label=f"📊 Download Excel Reports ({excel_count} files)",
                            data=excel_zip_data,
                            file_name="historical_excel_reports.zip",
                            mime="application/zip",
                            key="download_excel_historical_zip"
                        )
            
            # Word reports ZIP  
            if word_reports:
                with col2:
                    word_zip_data, word_count = create_historical_zip_data(word_reports, "word")
                    if word_zip_data:
                        st.download_button(
                            label=f"📄 Download Word Reports ({word_count} files)",
                            data=word_zip_data,
                            file_name="historical_word_reports.zip",
                            mime="application/zip",
                            key="download_word_historical_zip"
                        )
            
            # Combined ZIP
            with col3:
                combined_zip_data, combined_count = create_combined_historical_zip_data(reports)
                if combined_zip_data:
                    st.download_button(
                        label=f"📦 Download All Reports ({combined_count} files)",
                        data=combined_zip_data,
                        file_name="all_historical_reports.zip",
                        mime="application/zip",
                        key="download_combined_historical_zip"
                    )
            
            # Hide download options button
            if st.button("❌ Hide Download Options"):
                st.session_state['show_download_options'] = False
                st.rerun()
            
            st.markdown("---")
        
        # Show filter summary
        st.info(f"Showing {len(filtered_reports)} of {len(reports)} reports")
        
        if not filtered_reports:
            st.warning("No reports match the selected filters. Try adjusting your filter criteria:")
            st.write("- Increase the number of days")
            st.write("- Select more symbols or report types")
            st.write("- Clear some filters to see more results")
            return
        
        # Display reports
        st.subheader(f"📊 Reports ({len(filtered_reports)} found)")
        
        # Convert to DataFrame for better display
        df_data = []
        for report in filtered_reports:
            df_data.append({
                'Symbol': report['symbol'],
                'Type': report['report_type'],
                'Created': report['created_date'].strftime('%Y-%m-%d %H:%M'),
                'Size': format_file_size(report['size']),
                'Days Back': report.get('days_back', 'N/A'),
                'Path': report['path']
            })
        
        df = pd.DataFrame(df_data)
        
        # Display the table
        st.dataframe(
            df[['Symbol', 'Type', 'Created', 'Size', 'Days Back']], 
            use_container_width=True,
            hide_index=True
        )
        
        # Download and delete actions
        st.subheader("📥 Actions")
        
        # Group reports by symbol for easier management
        reports_by_symbol = {}
        for report in filtered_reports:
            symbol = report['symbol']
            if symbol not in reports_by_symbol:
                reports_by_symbol[symbol] = []
            reports_by_symbol[symbol].append(report)
        
        # Display reports grouped by symbol
        for symbol, symbol_reports in reports_by_symbol.items():
            with st.expander(f"📈 {symbol} ({len(symbol_reports)} reports)"):
                
                for report in symbol_reports:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.write(f"**{report['report_type']}** - {report['created_date'].strftime('%Y-%m-%d %H:%M')}")
                    
                    with col2:
                        st.write(f"Size: {format_file_size(report['size'])}")
                    
                    with col3:
                        # Download button
                        if os.path.exists(report['path']):
                            try:
                                with open(report['path'], 'rb') as f:
                                    file_data = f.read()
                                
                                file_name = os.path.basename(report['path'])
                                mime_type = get_mime_type(report['report_type'])
                                
                                st.download_button(
                                    label="📥 Download",
                                    data=file_data,
                                    file_name=file_name,
                                    mime=mime_type,
                                    key=f"download_{report['symbol']}_{report['report_type']}_{report['created_date'].timestamp()}"
                                )
                            except Exception as e:
                                st.error(f"Error loading file: {str(e)}")
                        else:
                            st.error("File not found")
                    
                    with col4:
                        # Delete button
                        if st.button(
                            BUTTON_DELETE_REPORT,
                            key=f"delete_{report['symbol']}_{report['report_type']}_{report['created_date'].timestamp()}"
                        ):
                            try:
                                report_manager.delete_report(report['path'])
                                st.success(SUCCESS_REPORT_DELETED)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting report: {str(e)}")
        
        # Bulk cleanup section
        st.markdown("---")
        st.subheader("🧹 Bulk Cleanup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cleanup_days = st.number_input(
                "Delete reports older than (days):",
                min_value=1,
                max_value=365,
                value=30
            )
        
        with col2:
            if st.button(BUTTON_CLEANUP_REPORTS):
                try:
                    deleted_count = report_manager.cleanup_old_reports(cleanup_days)
                    if deleted_count > 0:
                        st.success(f"Successfully deleted {deleted_count} old reports.")
                        st.rerun()
                    else:
                        st.info("No old reports found to delete.")
                except Exception as e:
                    st.error(f"Error during cleanup: {str(e)}")
        
        # Statistics
        st.markdown("---")
        st.subheader("📈 Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Reports", len(reports))
        
        with col2:
            total_size = sum([report['size'] for report in reports])
            st.metric("Total Size", format_file_size(total_size))
        
        with col3:
            unique_symbols = len(set([report['symbol'] for report in reports]))
            st.metric("Unique Symbols", unique_symbols)
        
        with col4:
            if reports:
                oldest_report = min(reports, key=lambda x: x['created_date'])
                days_old = (datetime.now() - oldest_report['created_date']).days
                st.metric("Oldest Report", f"{days_old} days")
        
    except Exception as e:
        DebugUtils.log_error(e, "Error in report manager UI")
        st.error(f"Error loading report manager: {str(e)}")

def filter_reports(reports: List[Dict[str, Any]], 
                  symbols: List[str], 
                  types: List[str], 
                  max_days: int) -> List[Dict[str, Any]]:
    """Filter reports based on criteria."""
    filtered = []
    cutoff_date = datetime.now() - timedelta(days=max_days)
    
    for report in reports:
        # Check symbol filter
        if symbols and report['symbol'] not in symbols:
            continue
        
        # Check type filter
        if types and report['report_type'] not in types:
            continue
        
        # Check date filter
        if report['created_date'] < cutoff_date:
            continue
        
        filtered.append(report)
    
    return filtered

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def get_mime_type(report_type: str) -> str:
    """Get MIME type based on report type."""
    mime_types = {
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'word': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'json': 'application/json',
        'csv': 'text/csv'
    }
    
    return mime_types.get(report_type.lower(), 'application/octet-stream')

def create_historical_zip_data(reports: List[Dict[str, Any]], report_type: str):
    """Create ZIP data for historical reports of a specific type."""
    try:
        import io
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            files_added = 0
            
            for report in reports:
                if os.path.exists(report['path']):
                    # Create a clean filename with symbol and date
                    symbol = report['symbol']
                    date_str = report['created_date'].strftime('%Y%m%d_%H%M%S')
                    file_ext = '.xlsx' if report_type == 'excel' else '.docx'
                    archive_name = f"{symbol}_{report_type}_{date_str}{file_ext}"
                    
                    zipf.write(report['path'], archive_name)
                    files_added += 1
            
            if files_added == 0:
                return None, 0
        
        # Get ZIP data
        zip_data = zip_buffer.getvalue()
        zip_buffer.close()
        
        return zip_data, files_added
        
    except Exception as e:
        DebugUtils.log_error(e, f"Error creating historical {report_type} ZIP data")
        return None, 0

def create_combined_historical_zip_data(reports: List[Dict[str, Any]]):
    """Create ZIP data containing all historical reports with organized structure."""
    try:
        import io
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            files_added = 0
            
            for report in reports:
                if os.path.exists(report['path']):
                    # Create organized folder structure in ZIP
                    symbol = report['symbol']
                    report_type = report['report_type']
                    date_str = report['created_date'].strftime('%Y%m%d_%H%M%S')
                    file_ext = '.xlsx' if report_type == 'excel' else '.docx'
                    
                    # Organize by symbol, then by type
                    archive_name = f"{symbol}/{report_type}/{symbol}_{report_type}_{date_str}{file_ext}"
                    
                    zipf.write(report['path'], archive_name)
                    files_added += 1
            
            if files_added == 0:
                return None, 0
        
        # Get ZIP data
        zip_data = zip_buffer.getvalue()
        zip_buffer.close()
        
        return zip_data, files_added
        
    except Exception as e:
        DebugUtils.log_error(e, "Error creating combined historical ZIP data")
        return None, 0 