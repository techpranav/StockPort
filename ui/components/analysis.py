import streamlit as st
from typing import Dict, Any, List
import pandas as pd
from pathlib import Path
from config.settings import (
    ENABLE_AI_FEATURES,
    ENABLE_TECHNICAL_ANALYSIS,
    ENABLE_FUNDAMENTAL_ANALYSIS,
    ENABLE_PORTFOLIO_ANALYSIS
)
import plotly.graph_objects as go
from services.analyzers.technical_analysis import TechnicalAnalysisService
from services.analyzers.fundamental_analysis import FundamentalAnalysisService
from services.analyzers.portfolio_service import PortfolioService
from utils.debug_utils import DebugUtils
from config.constants import *
from config.constants.Messages import (
    # Headers and titles
    HEADER_SINGLE_STOCK_ANALYSIS,
    HEADER_MASS_STOCK_ANALYSIS,
    # Section headers
    SECTION_FINANCIAL_METRICS,
    SECTION_COMPANY_INFO,
    SECTION_TECHNICAL_ANALYSIS,
    SECTION_BALANCE_SHEET,
    SECTION_CASH_FLOW,
    SECTION_AI_ANALYSIS,
    # Status messages
    MSG_NO_FINANCIAL_METRICS,
    MSG_NO_COMPANY_INFO,
    MSG_NO_TECHNICAL_DATA,
    MSG_NO_FUNDAMENTAL_DATA,
    MSG_NO_PORTFOLIO_DATA,
    MSG_NO_HISTORICAL_DATA,
    MSG_INSUFFICIENT_DATA,
    MSG_PROCESSING_COMPLETE,
    MSG_ANALYSIS_COMPLETE,
    # Error messages
    ERROR_PROCESSING_STOCK,
    ERROR_ANALYZING_SYMBOL,
    ERROR_MASS_ANALYSIS,
    # Button labels
    BUTTON_ANALYZE,
    BUTTON_DOWNLOAD_EXCEL,
    BUTTON_DOWNLOAD_WORD,
    # Input placeholders
    PLACEHOLDER_STOCK_SYMBOL,
    PLACEHOLDER_UPLOAD_FILE
)
import numpy as np
import zipfile
import tempfile

@st.cache_data
def get_file_download_data(file_path: str) -> bytes:
    """Get file data for download, with caching to prevent repeated reads."""
    try:
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        DebugUtils.log_error(e, f"Error reading file for download: {file_path}")
        return None

def create_reports_zip_data(successful_analyses: List[Dict[str, Any]], report_type: str):
    """Create ZIP data containing all reports of the specified type."""
    try:
        # Create ZIP data in memory
        import io
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            files_added = 0
            
            for result in successful_analyses:
                symbol = result.get('symbol', 'Unknown')
                
                # Get the appropriate report path
                if report_type == "excel":
                    report_path = result.get('excel_report_path')
                    file_extension = '.xlsx'
                else:  # word
                    report_path = result.get('word_report_path')
                    file_extension = '.docx'
                
                if report_path and os.path.exists(report_path):
                    # Add file to ZIP with a clean name
                    archive_name = f"{symbol}_{report_type}_report{file_extension}"
                    zipf.write(report_path, archive_name)
                    files_added += 1
            
            if files_added == 0:
                return None, 0
        
        # Get ZIP data
        zip_data = zip_buffer.getvalue()
        zip_buffer.close()
        
        return zip_data, files_added
        
    except Exception as e:
        DebugUtils.log_error(e, f"Error creating ZIP data for {report_type} reports")
        return None, 0

def display_single_stock_analysis():
    """Display single stock analysis interface."""
    st.header(HEADER_SINGLE_STOCK_ANALYSIS)
    
    # Stock symbol input
    symbol = st.text_input(
        "Enter Stock Symbol:",
        placeholder=PLACEHOLDER_STOCK_SYMBOL,
        key="single_stock_symbol"
    ).upper().strip()
    
    # Analysis button
    if st.button(BUTTON_ANALYZE, key="analyze_single_stock"):
        if symbol:
            # Clear any existing results for this symbol before starting new analysis
            if f'analysis_result_{symbol}' in st.session_state:
                del st.session_state[f'analysis_result_{symbol}']
            # Set flag to indicate analysis is running (hide any existing results)
            st.session_state[f'analysis_running_{symbol}'] = True
            with st.spinner(f"Analyzing {symbol}..."):
                try:
                    # Import here to avoid circular imports
                    from core.stock_analyzer import StockAnalyzer
                    from config.constants.StringConstants import input_dir, output_dir

                    # Get configuration from session state
                    config = st.session_state.get('config', {})

                    # Initialize analyzer with configuration
                    analyzer = StockAnalyzer(
                        input_dir=input_dir,
                        output_dir=output_dir,
                        ai_mode=config.get('ai_model'),
                        days_back=config.get('days_back', 365),
                        delay_between_calls=config.get('delay_between_calls', 60)
                    )

                    # Process the stock
                    result = analyzer.process_stock(symbol)

                    if result['status'] == 'success':
                        st.success(MSG_ANALYSIS_COMPLETE)
                        display_analysis_results(result)
                        # Store result after display to persist across download interactions
                        st.session_state[f'analysis_result_{symbol}'] = result
                    else:
                        st.error(f"{ERROR_ANALYZING_SYMBOL} {symbol}: {result.get('error', 'Unknown error')}")
                    
                    # Clear the analysis running flag
                    if f'analysis_running_{symbol}' in st.session_state:
                        del st.session_state[f'analysis_running_{symbol}']

                except Exception as e:
                    DebugUtils.log_error(e, f"Error in single stock analysis for {symbol}")
                    st.error(f"{ERROR_ANALYZING_SYMBOL} {symbol}: {str(e)}")
                    # Clear the analysis running flag even on error
                    if f'analysis_running_{symbol}' in st.session_state:
                        del st.session_state[f'analysis_running_{symbol}']
        else:
            st.warning("Please enter a stock symbol.")

    # Show stored results if available (for download interactions, not during analysis)
    elif symbol and f'analysis_result_{symbol}' in st.session_state and not st.session_state.get(f'analysis_running_{symbol}', False):
        # Show stored results for download interactions
        stored_result = st.session_state[f'analysis_result_{symbol}']
        display_analysis_results(stored_result)

        # Add Clear Results button
        if st.button("🗑️ Clear Results", key="clear_single_analysis"):
            del st.session_state[f'analysis_result_{symbol}']
            # Clear all related flags
            if f'analysis_running_{symbol}' in st.session_state:
                del st.session_state[f'analysis_running_{symbol}']
            st.rerun()


def display_mass_stock_analysis():
    """Display mass stock analysis interface."""
    st.header(HEADER_MASS_STOCK_ANALYSIS)

    # Add Clear Results button if there are stored results
    if 'mass_analysis_successful' in st.session_state or 'mass_analysis_failed' in st.session_state:
        if st.button("🗑️ Clear Mass Analysis Results", key="clear_mass_analysis"):
            # Clear all mass analysis results from session state
            keys_to_remove = ['mass_analysis_successful', 'mass_analysis_failed', 'mass_analysis_symbols']
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # File upload with custom styling
    st.markdown("""
    <style>
    .uploadedFile {
        background-color: #f0f2f6;
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
    }
    .uploadedFile:hover {
        border-color: #1f77b4;
        background-color: #e8f4fd;
    }
    .results-container {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a text file with stock symbols (one per line):",
        type=['txt'],
        help="Upload a .txt file containing stock symbols, one symbol per line",
        key="mass_analysis_file_uploader"
    )

    if uploaded_file is not None:
        # Display file preview
        try:
            content = uploaded_file.read().decode('utf-8')
            symbols = [line.strip().upper() for line in content.splitlines() if line.strip()]

            st.success(f"✅ File uploaded successfully! Found {len(symbols)} symbols.")

            # Show preview of symbols
            with st.expander("📋 Preview symbols", expanded=False):
                st.write(", ".join(symbols[:10]) + ("..." if len(symbols) > 10 else ""))

            # Analysis button
            if st.button(BUTTON_ANALYZE, key="analyze_mass_stocks"):
                if symbols:
                    # Clear any existing mass analysis results before starting new analysis
                    keys_to_remove = ['mass_analysis_successful', 'mass_analysis_failed', 'mass_analysis_symbols']
                    for key in keys_to_remove:
                        if key in st.session_state:
                            del st.session_state[key]
                    # Set flag to indicate mass analysis is running
                    st.session_state['mass_analysis_running'] = True
                    process_mass_analysis(symbols)
                else:
                    st.warning("No valid symbols found in the uploaded file.")

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    
    # Display stored mass analysis results if available (for download interactions, not during analysis)
    if ('mass_analysis_successful' in st.session_state or 'mass_analysis_failed' in st.session_state) and not st.session_state.get('mass_analysis_running', False):
        successful_analyses = st.session_state.get('mass_analysis_successful', [])
        failed_analyses = st.session_state.get('mass_analysis_failed', [])
        symbols = st.session_state.get('mass_analysis_symbols', [])
        
        if successful_analyses or failed_analyses:
            st.markdown("---")
            st.subheader("📊 Analysis Summary")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("✅ Successful", len(successful_analyses))
            with col2:
                st.metric("❌ Failed", len(failed_analyses))
            
            # Display results for successful analyses
            if successful_analyses:
                st.subheader("✅ Successful Analyses")
                
                # Add "Download All Reports" section
                st.markdown("---")
                st.subheader("📥 Download All Reports")
                
                # Create ZIP files for download
                excel_zip_data, excel_count = create_reports_zip_data(successful_analyses, "excel")
                word_zip_data, word_count = create_reports_zip_data(successful_analyses, "word")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if excel_zip_data:
                        st.download_button(
                            label=f"📊 Download All Excel Reports ({excel_count} files)",
                            data=excel_zip_data,
                            file_name="mass_analysis_excel_reports.zip",
                            mime="application/zip",
                            key="download_all_excel_zip_stored"
                        )
                    else:
                        st.info("No Excel reports available")
                
                with col2:
                    if word_zip_data:
                        st.download_button(
                            label=f"📄 Download All Word Reports ({word_count} files)",
                            data=word_zip_data,
                            file_name="mass_analysis_word_reports.zip",
                            mime="application/zip",
                            key="download_all_word_zip_stored"
                        )
                    else:
                        st.info("No Word reports available")
                
                st.markdown("---")
                
                for result in successful_analyses:
                    with st.expander(f"📈 {result['symbol']} - View Details"):
                        display_analysis_results(result)
            
            # Display failed analyses
            if failed_analyses:
                st.subheader("❌ Failed Analyses")
                for failed in failed_analyses:
                    st.error(f"**{failed['symbol']}**: {failed['error']}")

def process_mass_analysis(symbols: List[str]):
    """Process multiple stock symbols for analysis."""
    try:
        # Import here to avoid circular imports
        from core.stock_analyzer import StockAnalyzer
        from config.constants.StringConstants import input_dir, output_dir

        # Get configuration from session state
        config = st.session_state.get('config', {})

        # Initialize analyzer with configuration
        analyzer = StockAnalyzer(
            input_dir=input_dir,
            output_dir=output_dir,
            ai_mode=config.get('ai_model'),
            days_back=config.get('days_back', 365),
            delay_between_calls=config.get('delay_between_calls', 60)
        )

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()

        successful_analyses = []
        failed_analyses = []

        # Process each symbol
        for i, symbol in enumerate(symbols):
            try:
                status_text.text(f"Processing {symbol} ({i+1}/{len(symbols)})...")
                progress_bar.progress((i + 1) / len(symbols))

                # Process the stock
                result = analyzer.process_stock(symbol)

                if result['status'] == 'success':
                    successful_analyses.append(result)
                    with results_container:
                        st.success(f"✅ {symbol}: Analysis completed")
                else:
                    failed_analyses.append({'symbol': symbol, 'error': result.get('error', 'Unknown error')})
                    with results_container:
                        st.error(f"❌ {symbol}: {result.get('error', 'Analysis failed')}")

            except Exception as e:
                DebugUtils.log_error(e, f"Error processing {symbol} in mass analysis")
                failed_analyses.append({'symbol': symbol, 'error': str(e)})
                with results_container:
                    st.error(f"❌ {symbol}: {str(e)}")

        # Final summary
        status_text.text(MSG_PROCESSING_COMPLETE)

        # Store results in session state for persistence
        st.session_state['mass_analysis_successful'] = successful_analyses
        st.session_state['mass_analysis_failed'] = failed_analyses
        st.session_state['mass_analysis_symbols'] = symbols
        
        # Clear the mass analysis running flag
        if 'mass_analysis_running' in st.session_state:
            del st.session_state['mass_analysis_running']

        # Results are now stored in session state and will be displayed by display_mass_stock_analysis

    except Exception as e:
        DebugUtils.log_error(e, "Error in mass stock analysis")
        st.error(f"{ERROR_MASS_ANALYSIS}: {str(e)}")
        # Clear the mass analysis running flag even on error
        if 'mass_analysis_running' in st.session_state:
            del st.session_state['mass_analysis_running']



def display_analysis_results(result: Dict[str, Any]):
    """Display comprehensive analysis results."""
    if not result or result.get('status') != 'success':
        st.error("No valid analysis results to display.")
        return

    symbol = result.get('symbol', 'Unknown')

    # Create tabs for different analysis types
    tabs = st.tabs([
        TAB_OVERVIEW,
        TAB_TECHNICAL_ANALYSIS,
        TAB_FUNDAMENTAL_ANALYSIS,
        TAB_PORTFOLIO
    ])

    # Overview Tab
    with tabs[0]:
        display_overview(result)

    # Technical Analysis Tab
    with tabs[1]:
        if ENABLE_TECHNICAL_ANALYSIS:
            display_technical_analysis(result)
        else:
            st.info("Technical analysis is disabled in configuration.")

    # Fundamental Analysis Tab
    with tabs[2]:
        if ENABLE_FUNDAMENTAL_ANALYSIS:
            display_fundamental_analysis(result)
        else:
            st.info("Fundamental analysis is disabled in configuration.")

    # Portfolio Analysis Tab
    with tabs[3]:
        if ENABLE_PORTFOLIO_ANALYSIS:
            display_portfolio_analysis(result)
        else:
            st.info("Portfolio analysis is disabled in configuration.")

    # Download buttons
    st.markdown("---")
    st.subheader("📥 Download Reports")

    col1, col2 = st.columns(2)

    with col1:
        if result.get('excel_report_path') and os.path.exists(result['excel_report_path']):
            try:
                # Read file data only when creating the download button
                excel_data = get_file_download_data(result['excel_report_path'])
                if excel_data:
                    st.download_button(
                        label=f"📊 {BUTTON_DOWNLOAD_EXCEL}",
                        data=excel_data,
                        file_name=f"{symbol}_analysis.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_excel_{symbol}_{hash(result['excel_report_path'])}"
                    )
                else:
                    st.error("Excel report file not found or empty")
            except Exception as e:
                st.error(f"Error preparing Excel download: {str(e)}")
        else:
            st.info("Excel report not available")

    with col2:
        if result.get('word_report_path') and os.path.exists(result['word_report_path']):
            try:
                # Read file data only when creating the download button
                word_data = get_file_download_data(result['word_report_path'])
                if word_data:
                    st.download_button(
                        label=f"📄 {BUTTON_DOWNLOAD_WORD}",
                        data=word_data,
                        file_name=f"{symbol}_analysis.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"download_word_{symbol}_{hash(result['word_report_path'])}"
                    )
                else:
                    st.error("Word report file not found or empty")
            except Exception as e:
                st.error(f"Error preparing Word download: {str(e)}")
        else:
            st.info("Word report not available")

def display_overview(result: Dict[str, Any]):
    """Display comprehensive overview of stock analysis."""
    try:
        symbol = result.get('symbol', 'Unknown')
        
        # Company Information Section
        st.subheader(SECTION_COMPANY_INFO)
        company_info = result.get('company_info', {})
        
        if company_info:
            # Create columns for better layout
            col1, col2 = st.columns(2)
            
            with col1:
                # Basic company info
                basic_info_data = []
                for key in COMPANY_INFO_KEYS:
                    if key in company_info:
                        value = company_info[key]
                        if value is not None and str(value).strip():
                            # Format the display name
                            display_name = key.replace('_', ' ').title()
                            # Format the value
                            if isinstance(value, (int, float)) and key in ['market_cap', 'enterprise_value']:
                                formatted_value = f"{CURRENCY_SYMBOL}{value:,.0f}" if value != 0 else NOT_AVAILABLE
                            elif isinstance(value, float) and 'ratio' in key.lower():
                                formatted_value = f"{value:.2f}" if value != 0 else NOT_AVAILABLE
                            else:
                                formatted_value = str(value) if value != 0 else NOT_AVAILABLE
                            
                            basic_info_data.append({COLUMN_ATTRIBUTE: display_name, COLUMN_VALUE: formatted_value})
                
                if basic_info_data:
                    df_basic = pd.DataFrame(basic_info_data)
                    st.dataframe(df_basic, use_container_width=True, hide_index=True)
                else:
                    st.info(MSG_NO_COMPANY_INFO)
            
            with col2:
                # Additional metrics if available
                if 'previous_close' in company_info and company_info['previous_close']:
                    st.metric("Previous Close", f"{CURRENCY_SYMBOL}{company_info['previous_close']:.2f}")
                if 'day_high' in company_info and company_info['day_high']:
                    st.metric("Day High", f"{CURRENCY_SYMBOL}{company_info['day_high']:.2f}")
                if 'day_low' in company_info and company_info['day_low']:
                    st.metric("Day Low", f"{CURRENCY_SYMBOL}{company_info['day_low']:.2f}")
        else:
            st.info(MSG_NO_COMPANY_INFO)
        
        # Financial Metrics Section
        st.subheader(SECTION_FINANCIAL_METRICS)
        metrics = result.get('metrics', {})
        
        if metrics:
            # Create financial metrics display
            metrics_data = []
            for key, display_name in FINANCIAL_METRICS_DISPLAY.items():
                if key in metrics:
                    value = metrics[key]
                    if value is not None and value != 0:
                        # Format based on metric type
                        if 'ratio' in key.lower() or 'margin' in key.lower():
                            formatted_value = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
                        elif 'revenue' in key.lower() or 'income' in key.lower() or 'assets' in key.lower():
                            formatted_value = f"{CURRENCY_SYMBOL}{value:,.0f}" if isinstance(value, (int, float)) else str(value)
                        else:
                            formatted_value = str(value)
                        
                        metrics_data.append({COLUMN_METRIC: display_name, COLUMN_VALUE: formatted_value})
            
            if metrics_data:
                df_metrics = pd.DataFrame(metrics_data)
                st.dataframe(df_metrics, use_container_width=True, hide_index=True)
            else:
                st.info(MSG_NO_FINANCIAL_METRICS)
        else:
            st.info(MSG_NO_FINANCIAL_METRICS)
        
        # Technical Analysis Summary
        st.subheader(SECTION_TECHNICAL_ANALYSIS)
        technical_signals = result.get('technical_signals', {})
        
        if technical_signals:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                trend = technical_signals.get('trend', NOT_AVAILABLE)
                st.metric(LABEL_TREND, trend)
            
            with col2:
                momentum = technical_signals.get('momentum', NOT_AVAILABLE)
                st.metric(LABEL_MOMENTUM, momentum)
            
            with col3:
                volatility = technical_signals.get('volatility', NOT_AVAILABLE)
                st.metric(LABEL_VOLATILITY, volatility)
            
            with col4:
                volume = technical_signals.get('volume', NOT_AVAILABLE)
                st.metric(LABEL_VOLUME, volume)
        else:
            st.info(MSG_NO_TECHNICAL_DATA)
        
        # Balance Sheet Summary
        financials = result.get('financials', {})
        if financials and 'balance_sheet' in financials:
            st.subheader(SECTION_BALANCE_SHEET)
            balance_sheet = financials['balance_sheet']
            
            if isinstance(balance_sheet, dict) and 'yearly' in balance_sheet:
                yearly_bs = balance_sheet['yearly']
                if isinstance(yearly_bs, pd.DataFrame) and not yearly_bs.empty:
                    # Show key balance sheet items
                    key_items = ['Total Assets', 'Total Debt', 'Total Equity', 'Cash And Cash Equivalents']
                    bs_data = []
                    
                    latest_col = yearly_bs.columns[0] if len(yearly_bs.columns) > 0 else None
                    if latest_col is not None:
                        for item in key_items:
                            if item in yearly_bs.index:
                                value = yearly_bs.loc[item, latest_col]
                                if pd.notna(value) and value != 0:
                                    formatted_value = f"{CURRENCY_SYMBOL}{value:,.0f}" if isinstance(value, (int, float)) else str(value)
                                    bs_data.append({COLUMN_METRIC: item, COLUMN_VALUE: formatted_value})
                    
                    if bs_data:
                        df_bs = pd.DataFrame(bs_data)
                        st.dataframe(df_bs, use_container_width=True, hide_index=True)
                    else:
                        st.info("No balance sheet data available.")
                else:
                    st.info("No balance sheet data available.")
            else:
                st.info("No balance sheet data available.")
        
        # Cash Flow Summary
        if financials and 'cashflow' in financials:
            st.subheader(SECTION_CASH_FLOW)
            cashflow = financials['cashflow']
            
            if isinstance(cashflow, dict) and 'yearly' in cashflow:
                yearly_cf = cashflow['yearly']
                if isinstance(yearly_cf, pd.DataFrame) and not yearly_cf.empty:
                    # Show key cash flow items
                    key_items = ['Operating Cash Flow', 'Free Cash Flow', 'Capital Expenditure']
                    cf_data = []
                    
                    latest_col = yearly_cf.columns[0] if len(yearly_cf.columns) > 0 else None
                    if latest_col is not None:
                        for item in key_items:
                            if item in yearly_cf.index:
                                value = yearly_cf.loc[item, latest_col]
                                if pd.notna(value) and value != 0:
                                    formatted_value = f"{CURRENCY_SYMBOL}{value:,.0f}" if isinstance(value, (int, float)) else str(value)
                                    cf_data.append({COLUMN_METRIC: item, COLUMN_VALUE: formatted_value})
                    
                    if cf_data:
                        df_cf = pd.DataFrame(cf_data)
                        st.dataframe(df_cf, use_container_width=True, hide_index=True)
                    else:
                        st.info("No cash flow data available.")
                else:
                    st.info("No cash flow data available.")
            else:
                st.info("No cash flow data available.")
        
        # AI Analysis Section (if enabled and available)
        if ENABLE_AI_FEATURES and result.get('summary'):
            st.subheader(SECTION_AI_ANALYSIS)
            st.write(result['summary'])
            
    except Exception as e:
        DebugUtils.log_error(e, f"Error displaying overview for {result.get('symbol', 'Unknown')}")
        st.error(f"Error displaying overview: {str(e)}")

def display_technical_analysis(result: Dict[str, Any]):
    """Display technical analysis results."""
    try:
        symbol = result.get('symbol', 'Unknown')
        history = result.get('history', pd.DataFrame())
        
        # Check if we have historical data
        if history.empty:
            st.warning(MSG_NO_HISTORICAL_DATA)
            return
        
        # Check if we have required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in history.columns]
        
        if missing_columns:
            st.warning(f"{MSG_INSUFFICIENT_DATA} Missing columns: {', '.join(missing_columns)}")
            return
        
        # Perform technical analysis
        try:
            tech_service = TechnicalAnalysisService()
            
            # Calculate technical indicators
            history_with_indicators = tech_service.calculate_technical_indicators(history.copy())
            
            # Get technical signals
            technical_signals = tech_service.get_technical_signals(history_with_indicators)
            
            if not history_with_indicators.empty:
                # Display technical indicators
                st.subheader("📊 Technical Indicators")
                
                # Create columns for metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if 'SMA_20' in history_with_indicators.columns:
                        latest_sma_20 = history_with_indicators['SMA_20'].iloc[-1]
                        if not pd.isna(latest_sma_20):
                            st.metric("SMA (20)", f"{latest_sma_20:.2f}")
                    if 'RSI' in history_with_indicators.columns:
                        latest_rsi = history_with_indicators['RSI'].iloc[-1]
                        if not pd.isna(latest_rsi):
                            st.metric("RSI", f"{latest_rsi:.2f}")
                
                with col2:
                    if 'SMA_50' in history_with_indicators.columns:
                        latest_sma_50 = history_with_indicators['SMA_50'].iloc[-1]
                        if not pd.isna(latest_sma_50):
                            st.metric("SMA (50)", f"{latest_sma_50:.2f}")
                    if 'MACD' in history_with_indicators.columns:
                        latest_macd = history_with_indicators['MACD'].iloc[-1]
                        if not pd.isna(latest_macd):
                            st.metric("MACD", f"{latest_macd:.4f}")
                
                with col3:
                    if 'BB_Upper' in history_with_indicators.columns and 'BB_Lower' in history_with_indicators.columns:
                        latest_bb_upper = history_with_indicators['BB_Upper'].iloc[-1]
                        latest_bb_lower = history_with_indicators['BB_Lower'].iloc[-1]
                        if not pd.isna(latest_bb_upper) and not pd.isna(latest_bb_lower):
                            st.metric("Bollinger Range", 
                                    f"{latest_bb_lower:.2f} - {latest_bb_upper:.2f}")
                
                # Display technical signals
                if technical_signals:
                    st.subheader("🎯 Technical Signals")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        trend = technical_signals.get('trend', NOT_AVAILABLE)
                        st.metric(LABEL_TREND, trend)
                    
                    with col2:
                        momentum = technical_signals.get('momentum', NOT_AVAILABLE)
                        st.metric(LABEL_MOMENTUM, momentum)
                    
                    with col3:
                        volatility = technical_signals.get('volatility', NOT_AVAILABLE)
                        st.metric(LABEL_VOLATILITY, volatility)
                    
                    with col4:
                        volume = technical_signals.get('volume', NOT_AVAILABLE)
                        st.metric(LABEL_VOLUME, volume)
                
                # Price chart
                st.subheader("📈 Price Chart")
                
                fig = go.Figure()
                
                # Add candlestick chart
                fig.add_trace(go.Candlestick(
                    x=history.index,
                    open=history['Open'],
                    high=history['High'],
                    low=history['Low'],
                    close=history['Close'],
                    name=symbol
                ))
                
                # Add moving averages if available
                if 'SMA_20' in history_with_indicators.columns:
                    fig.add_trace(go.Scatter(
                        x=history_with_indicators.index,
                        y=history_with_indicators['SMA_20'],
                        mode='lines',
                        name='SMA 20',
                        line=dict(color='orange')
                    ))
                
                if 'SMA_50' in history_with_indicators.columns:
                    fig.add_trace(go.Scatter(
                        x=history_with_indicators.index,
                        y=history_with_indicators['SMA_50'],
                        mode='lines',
                        name='SMA 50',
                        line=dict(color='red')
                    ))
                
                fig.update_layout(
                    title=f"{symbol} Price Chart",
                    xaxis_title=LABEL_DATE,
                    yaxis_title="Price ($)",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info(MSG_NO_TECHNICAL_DATA)
                
        except Exception as e:
            DebugUtils.log_error(e, f"Error performing technical analysis for {symbol}")
            st.error(f"Error performing technical analysis: {str(e)}")
            
    except Exception as e:
        DebugUtils.log_error(e, f"Error in technical analysis display for {result.get('symbol', 'Unknown')}")
        st.error(f"Error displaying technical analysis: {str(e)}")

def display_fundamental_analysis(result: Dict[str, Any]):
    """Display fundamental analysis results."""
    try:
        symbol = result.get('symbol', 'Unknown')
        
        # Get fundamental analysis data
        fundamental_service = FundamentalAnalysisService()
        
        # Use the stock data object if available
        stock_data = result.get('stock_data_object')
        if stock_data:
            # Convert StockData object to dictionary format expected by the service
            data_dict = stock_data.to_dict()
            ratios = fundamental_service.calculate_financial_ratios(data_dict)
        else:
            # Fallback to legacy format
            ratios = result.get('ratios', {})
        
        if ratios:
            st.subheader("📊 Financial Ratios")
            
            # Profitability Ratios
            st.subheader("💰 Profitability Ratios")
            prof_col1, prof_col2 = st.columns(2)
            
            with prof_col1:
                if 'gross_margin' in ratios:
                    st.metric("Gross Margin", f"{ratios['gross_margin']:.2f}%")
                if 'operating_margin' in ratios:
                    st.metric("Operating Margin", f"{ratios['operating_margin']:.2f}%")
                if 'net_margin' in ratios:
                    st.metric("Net Margin", f"{ratios['net_margin']:.2f}%")
            
            with prof_col2:
                if 'roa' in ratios:
                    st.metric("ROA", f"{ratios['roa']:.2f}%")
                if 'roe' in ratios:
                    st.metric("ROE", f"{ratios['roe']:.2f}%")
                if 'roic' in ratios:
                    st.metric("ROIC", f"{ratios['roic']:.2f}%")
            
            # Liquidity Ratios
            st.subheader("💧 Liquidity Ratios")
            liq_col1, liq_col2 = st.columns(2)
            
            with liq_col1:
                if 'current_ratio' in ratios:
                    st.metric("Current Ratio", f"{ratios['current_ratio']:.2f}")
                if 'quick_ratio' in ratios:
                    st.metric("Quick Ratio", f"{ratios['quick_ratio']:.2f}")
            
            with liq_col2:
                if 'cash_ratio' in ratios:
                    st.metric("Cash Ratio", f"{ratios['cash_ratio']:.2f}")
                if 'working_capital' in ratios:
                    st.metric("Working Capital", f"${ratios['working_capital']:,.0f}")
            
            # Leverage Ratios
            st.subheader("⚖️ Leverage Ratios")
            lev_col1, lev_col2 = st.columns(2)
            
            with lev_col1:
                if 'debt_to_equity' in ratios:
                    st.metric("Debt-to-Equity", f"{ratios['debt_to_equity']:.2f}")
                if 'debt_to_assets' in ratios:
                    st.metric("Debt-to-Assets", f"{ratios['debt_to_assets']:.2f}")
            
            with lev_col2:
                if 'interest_coverage' in ratios:
                    st.metric("Interest Coverage", f"{ratios['interest_coverage']:.2f}")
                if 'equity_multiplier' in ratios:
                    st.metric("Equity Multiplier", f"{ratios['equity_multiplier']:.2f}")
            
            # Efficiency Ratios
            st.subheader("⚡ Efficiency Ratios")
            eff_col1, eff_col2 = st.columns(2)
            
            with eff_col1:
                if 'asset_turnover' in ratios:
                    st.metric("Asset Turnover", f"{ratios['asset_turnover']:.2f}")
                if 'inventory_turnover' in ratios:
                    st.metric("Inventory Turnover", f"{ratios['inventory_turnover']:.2f}")
            
            with eff_col2:
                if 'receivables_turnover' in ratios:
                    st.metric("Receivables Turnover", f"{ratios['receivables_turnover']:.2f}")
                if 'payables_turnover' in ratios:
                    st.metric("Payables Turnover", f"{ratios['payables_turnover']:.2f}")
            
        else:
            st.info(MSG_NO_FUNDAMENTAL_DATA)
            
    except Exception as e:
        DebugUtils.log_error(e, f"Error in fundamental analysis display for {result.get('symbol', 'Unknown')}")
        st.error(f"Error displaying fundamental analysis: {str(e)}")

def display_portfolio_analysis(result: Dict[str, Any]):
    """Display portfolio analysis results."""
    try:
        symbol = result.get('symbol', 'Unknown')
        history = result.get('history', pd.DataFrame())
        
        # Check if we have historical data with Close column
        if history.empty or 'Close' not in history.columns:
            st.warning(MSG_NO_PORTFOLIO_DATA)
            return
        
        try:
            # Calculate single stock risk metrics
            returns = history['Close'].pct_change().dropna()
            
            if len(returns) > 0:
                # Calculate basic risk metrics
                daily_return = returns.mean() * 100
                volatility = returns.std() * np.sqrt(252)  # Annualized volatility
                
                # Calculate Sharpe ratio (assuming risk-free rate of 2%)
                risk_free_rate = 0.02
                excess_returns = returns.mean() * 252 - risk_free_rate
                sharpe_ratio = excess_returns / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
                
                # Calculate maximum drawdown
                cumulative_returns = (1 + returns).cumprod()
                rolling_max = cumulative_returns.expanding().max()
                drawdown = (cumulative_returns - rolling_max) / rolling_max
                max_drawdown = drawdown.min() * 100
                
                # Calculate VaR (95%)
                var_95 = np.percentile(returns, 5)
                
                portfolio_data = {
                    'daily_return': daily_return,
                    'volatility': volatility,
                    'sharpe_ratio': sharpe_ratio,
                    'max_drawdown': max_drawdown,
                    'var_95': var_95
                }
            else:
                portfolio_data = {}
            
            if portfolio_data:
                st.subheader("📊 Risk & Return Metrics")
                
                # Risk and Return Metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if 'daily_return' in portfolio_data:
                        st.metric("Avg Daily Return", f"{portfolio_data['daily_return']:.4f}%")
                    if 'volatility' in portfolio_data:
                        st.metric("Volatility (σ)", f"{portfolio_data['volatility']:.4f}")
                
                with col2:
                    if 'sharpe_ratio' in portfolio_data:
                        st.metric("Sharpe Ratio", f"{portfolio_data['sharpe_ratio']:.4f}")
                    if 'max_drawdown' in portfolio_data:
                        st.metric("Max Drawdown", f"{portfolio_data['max_drawdown']:.2f}%")
                
                with col3:
                    if 'var_95' in portfolio_data:
                        st.metric("VaR (95%)", f"{portfolio_data['var_95']:.4f}")
                    # Beta calculation requires market data, so removed for single stock analysis
                
                # Returns Distribution
                if 'returns' in portfolio_data:
                    st.subheader("📈 Returns Distribution")
                    
                    returns = portfolio_data['returns']
                    
                    # Create histogram
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(
                        x=returns,
                        nbinsx=50,
                        name="Daily Returns",
                        opacity=0.7
                    ))
                    
                    fig.update_layout(
                        title=f"{symbol} Daily Returns Distribution",
                        xaxis_title="Daily Return (%)",
                        yaxis_title=LABEL_FREQUENCY,
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Cumulative Returns
                if 'cumulative_returns' in portfolio_data:
                    st.subheader("📊 Cumulative Returns")
                    
                    cum_returns = portfolio_data['cumulative_returns']
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=cum_returns.index,
                        y=cum_returns.values,
                        mode='lines',
                        name="Cumulative Returns",
                        line=dict(color='green')
                    ))
                    
                    fig.update_layout(
                        title=f"{symbol} Cumulative Returns",
                        xaxis_title=LABEL_DATE,
                        yaxis_title="Cumulative Return (%)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info(MSG_NO_PORTFOLIO_DATA)
                
        except Exception as e:
            DebugUtils.log_error(e, f"Error performing portfolio analysis for {symbol}")
            st.error(f"Error performing portfolio analysis: {str(e)}")
            
    except Exception as e:
        DebugUtils.log_error(e, f"Error in portfolio analysis display for {result.get('symbol', 'Unknown')}")
        st.error(f"Error displaying portfolio analysis: {str(e)}") 