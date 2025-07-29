import traceback

import streamlit as st
from pathlib import Path
import os
import json
from typing import Dict, Any, List, Optional
import pandas as pd
from services.stock_service import StockService
from services.report_service import ReportService
from datetime import datetime
import plotly.graph_objects as go
import plotly.subplots as sp
from constants.Constants import (
    FINANCIAL_STATEMENT_TYPES,
    FINANCIAL_SHEET_NAMES,
    FINANCIAL_STATEMENT_FILTER_KEYS,
    FINANCIAL_METRICS_KEYS
)

from core.config import (
    INPUT_DIR, OUTPUT_DIR, ENABLE_AI_FEATURES, ENABLE_GOOGLE_DRIVE
)
from core.stock_analyzer import StockAnalyzer
from app.components.sidebar import render_sidebar
from app.components.analysis import (
    render_single_stock_analysis,
    render_mass_analysis,
    display_analysis_results,
    display_error,
    display_success,
    display_progress
)

def initialize_session_state():
    """Initialize session state variables."""
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'error' not in st.session_state:
        st.session_state.error = None

def setup_google_drive(settings: Dict[str, Any]) -> None:
    """Setup Google Drive integration if enabled."""
    if not ENABLE_GOOGLE_DRIVE:
        return
        
    if settings['upload_to_drive']:
        if not settings['client_secrets']:
            display_error("Please upload a client secrets file for Google Drive integration.")
            return
        
        # Save the uploaded client secrets file
        client_secrets_path = Path("client_secrets.json")
        with open(client_secrets_path, "wb") as f:
            f.write(settings['client_secrets'].getvalue())
        
        # Set environment variable for Google Drive
        os.environ['GOOGLE_DRIVE_CLIENT_SECRETS'] = str(client_secrets_path)

def process_stock(analyzer: StockAnalyzer, symbol: str) -> None:
    """Process a single stock with progress tracking."""
    try:
        display_progress(0.0, f"Analyzing {symbol}...")
        result = analyzer.process_stock(symbol)
        print("process_stock result ::: ",result)
        st.session_state.results.append(result)
        display_success(f"Analysis completed for {symbol}")
    except Exception as e:
        display_error(f"Error analyzing {symbol}: {str(e)}")

def process_multiple_stocks(analyzer: StockAnalyzer, symbols: List[str]) -> None:
    """Process multiple stocks with progress tracking."""
    total_stocks = len(symbols)
    for i, symbol in enumerate(symbols, 1):
        try:
            display_progress(i/total_stocks, f"Analyzing {symbol} ({i}/{total_stocks})...")
            result = analyzer.process_stock(symbol)
            print("process_multiple_stocks result ::: ", result)

            st.session_state.results.append(result)
        except Exception as e:
            display_error(f"Error analyzing {symbol}: {str(e)}")
    
    display_success(f"Mass analysis completed. Processed {total_stocks} stocks.")

def read_stock_symbols(file_path):
    """Read stock symbols from a file."""
    try:
        with open(file_path, 'r') as file:
            # Clean each symbol by removing whitespace and \r\n
            symbols = [line.strip() for line in file.readlines()]
            # Filter out empty lines
            symbols = [symbol for symbol in symbols if symbol]
            print(f"Cleaned symbols: {symbols}")  # Debug print
            return symbols
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return []

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Stock Analyzer",
        page_icon="📈",
        layout="wide"
    )
    
    initialize_session_state()
    
    # Render sidebar and get configuration
    config = render_sidebar()
    
    # Setup Google Drive if enabled
    setup_google_drive(config)
    
    # Initialize services
    stock_service = StockService()
    report_service = ReportService()
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["Single Stock Analysis", "Mass Stock Analysis"]
    )
    
    if page == "Single Stock Analysis":
        # Single stock analysis
        result = render_single_stock_analysis(config)
        if result:
            st.session_state.results = [result]
    
    else:  # Mass Stock Analysis
        # Get analysis parameters from render_mass_analysis
        analysis_params = render_mass_analysis(config)
        
        if analysis_params and analysis_params.get("analyze") and analysis_params.get("symbols"):
            # Process each stock
            for symbol in analysis_params["symbols"]:
                try:
                    st.write(f"\nProcessing {symbol}...")
                    
                    # Fetch stock data
                    stock_data = stock_service.fetch_stock_data(symbol)
                    filtered_data = stock_service.filter_stock_data(stock_data)

                    # Generate report
                    report_path = report_service.generate_excel_report(symbol, filtered_data)
                    
                    if os.path.exists(report_path):
                        st.success(f"Report generated for {symbol}")
                        st.download_button(
                            label=f"Download {symbol} Report",
                            data=open(report_path, 'rb').read(),
                            file_name=f"{symbol}_report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error(f"Failed to generate report for {symbol}")
                
                except Exception as e:
                    st.error(f"Error processing {symbol}: {str(e)}")
    
    # Display results
    if st.session_state.results:
        display_analysis_results(st.session_state.results, Path(OUTPUT_DIR))
    
    # Display error if any
    if st.session_state.error:
        display_error(st.session_state.error)
    
    # Cleanup old reports if enabled
    if config['cleanup_days'] > 0:
        analyzer = StockAnalyzer(
            input_dir=INPUT_DIR,
            output_dir=OUTPUT_DIR,
            ai_mode=config.get('ai_mode') if ENABLE_AI_FEATURES else None,
            days_back=config['days_back'],
            delay_between_calls=config['delay_between_calls']
        )
        analyzer.cleanup_old_reports(days=config['cleanup_days'])

def render_single_stock_analysis(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Render single stock analysis section."""
    st.header("Single Stock Analysis")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.text_input("Enter Stock Symbol", placeholder="e.g., AAPL", key="single_stock_symbol")
    with col2:
        analyze = st.button("Analyze", key="analyze_single")
    
    if analyze and symbol:
        try:
            analyzer = StockAnalyzer(
                input_dir=INPUT_DIR,
                output_dir=OUTPUT_DIR,
                ai_mode=config.get('ai_mode') if ENABLE_AI_FEATURES else None,
                days_back=config['days_back'],
                delay_between_calls=config['delay_between_calls']
            )
            result = analyzer.process_stock(symbol)
            return result
        except Exception as e:
            st.session_state.error = f"Error analyzing {symbol}: {str(e)}"
            print(traceback.format_exc())
            return None
    
    return None

def render_mass_analysis(config: Dict[str, Any]) -> Dict[str, Any]:
    """Render mass analysis section."""
    st.header("Mass Analysis")
    
    uploaded_file = st.file_uploader("Upload Stock Symbols File", type=['txt'], key="mass_analysis_uploader")
    analyze = st.button("Analyze All", key="analyze_mass")
    
    if analyze and uploaded_file:
        try:
            # Save the uploaded file temporarily
            with open("temp_stocks.txt", "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Read stock symbols
            symbols = read_stock_symbols("temp_stocks.txt")
            
            if symbols:
                analyzer = StockAnalyzer(
                    input_dir=INPUT_DIR,
                    output_dir=OUTPUT_DIR,
                    ai_mode=config.get('ai_mode') if ENABLE_AI_FEATURES else None,
                    days_back=config['days_back'],
                    delay_between_calls=config['delay_between_calls']
                )
                return {
                    "analyze": True,
                    "symbols": symbols
                }
            else:
                st.error("No valid stock symbols found in the file")
                return {"analyze": False, "symbols": []}
            
        except Exception as e:
            st.session_state.error = f"Error in mass analysis: {str(e)}"
            return {"analyze": False, "symbols": []}
        finally:
            # Clean up temporary file
            if os.path.exists("temp_stocks.txt"):
                os.remove("temp_stocks.txt")
    
    return {"analyze": False, "symbols": []}


if __name__ == "__main__":
    main() 