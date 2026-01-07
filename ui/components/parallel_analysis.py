"""
Parallel Analysis UI Component

This module provides UI components for parallel stock analysis with
real-time progress tracking and live results streaming.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
import pandas as pd

from core.parallel_analyzer import ParallelStockAnalyzer
from core.stock_analyzer import StockAnalyzer
from utils.debug_utils import DebugUtils
from config.app_config import ENABLE_PARALLEL_PROCESSING, DEFAULT_MAX_WORKERS


def render_parallel_analysis_ui(
    symbols: List[str],
    days_back: int = 365,
    generate_excel: bool = True,
    generate_word: bool = True
) -> Dict[str, Any]:
    """
    Render parallel analysis UI with progress tracking.
    
    Args:
        symbols: List of stock symbols to analyze
        days_back: Days of historical data
        generate_excel: Whether to generate Excel reports
        generate_word: Whether to generate Word reports
        
    Returns:
        Dictionary with analysis results
    """
    if not ENABLE_PARALLEL_PROCESSING:
        st.warning("Parallel processing is disabled. Enable it in config/app_config.py")
        return {}
    
    if not symbols:
        st.info("No symbols provided for analysis")
        return {}
    
    # Progress tracking
    progress_container = st.container()
    results_container = st.container()
    
    with progress_container:
        st.subheader("📊 Parallel Analysis Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
        stats_text = st.empty()
    
    # Initialize parallel analyzer
    max_workers = st.session_state.get('max_workers', DEFAULT_MAX_WORKERS)
    analyzer = ParallelStockAnalyzer(max_workers=max_workers)
    
    # Create analysis function
    def analyze_stock(symbol: str) -> Dict[str, Any]:
        """Analyze a single stock."""
        stock_analyzer = StockAnalyzer(
            input_dir="input",
            output_dir="output",
            days_back=days_back,
            generate_excel_report=generate_excel,
            generate_word_report=generate_word
        )
        return stock_analyzer.process_stock(symbol)
    
    # Progress callback
    def progress_callback(completed: int, total: int, current_symbol: str):
        """Update progress display."""
        progress = completed / total if total > 0 else 0
        progress_bar.progress(progress)
        status_text.text(f"Analyzing {current_symbol}... ({completed}/{total})")
        
        progress_info = analyzer.get_progress()
        stats_text.text(
            f"✅ Completed: {progress_info['completed']} | "
            f"❌ Failed: {progress_info['failed']} | "
            f"⏳ Remaining: {progress_info['remaining']}"
        )
    
    # Run parallel analysis
    try:
        results = analyzer.analyze_batch(
            symbols,
            analyze_stock,
            progress_callback
        )
        
        # Display results
        with results_container:
            st.subheader("📈 Analysis Results")
            
            # Summary statistics
            successful = [r for r in results.values() if r.get('status') == 'success']
            failed = [r for r in results.values() if r.get('status') == 'error']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(results))
            with col2:
                st.metric("Successful", len(successful), delta=f"{len(successful)/len(results)*100:.1f}%")
            with col3:
                st.metric("Failed", len(failed), delta=f"-{len(failed)/len(results)*100:.1f}%")
            
            return results
            
    except Exception as e:
        st.error(f"Error in parallel analysis: {str(e)}")
        DebugUtils.log_error(e, "Error in parallel analysis UI")
        return {}

