import streamlit as st
from pathlib import Path
import os
import json
from typing import Dict, Any, List, Optional

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
            st.session_state.results.append(result)
        except Exception as e:
            display_error(f"Error analyzing {symbol}: {str(e)}")
    
    display_success(f"Mass analysis completed. Processed {total_stocks} stocks.")

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
    
    # Render main content
    render_main_content(config)
    
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

def render_main_content(config: Dict[str, Any]) -> None:
    """Render the main content of the application."""
    # Single stock analysis
    single_result = render_single_stock_analysis()
    if single_result:
        st.session_state.results = [single_result]
    
    # Mass analysis
    mass_results = render_mass_analysis()
    if mass_results:
        st.session_state.results = mass_results

def render_single_stock_analysis() -> Optional[Dict[str, Any]]:
    """Render single stock analysis section."""
    st.header("Single Stock Analysis")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.text_input("Enter Stock Symbol", placeholder="e.g., AAPL")
    with col2:
        analyze = st.button("Analyze", key="analyze_single")
    
    if analyze and symbol:
        try:
            analyzer = StockAnalyzer(
                input_dir=INPUT_DIR,
                output_dir=OUTPUT_DIR,
                ai_mode=config.get('ai_mode') if ENABLE_AI_FEATURES else None
            )
            result = analyzer.process_stock(symbol)
            return result
        except Exception as e:
            st.session_state.error = f"Error analyzing {symbol}: {str(e)}"
            return None
    
    return None

def render_mass_analysis() -> Optional[List[Dict[str, Any]]]:
    """Render mass analysis section."""
    st.header("Mass Analysis")
    
    uploaded_file = st.file_uploader("Upload Stock Symbols File", type=['txt'])
    analyze = st.button("Analyze All", key="analyze_mass")
    
    if analyze and uploaded_file:
        try:
            analyzer = StockAnalyzer(
                input_dir=INPUT_DIR,
                output_dir=OUTPUT_DIR,
                ai_mode=config.get('ai_mode') if ENABLE_AI_FEATURES else None
            )
            results = analyzer.process_multiple_stocks(uploaded_file)
            return results
        except Exception as e:
            st.session_state.error = f"Error in mass analysis: {str(e)}"
            return None
    
    return None

if __name__ == "__main__":
    main() 