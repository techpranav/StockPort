"""
Simple Dashboard UI Component

User-friendly dashboard for non-trading users with simple language and visual indicators.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.interpreters.signal_translator import SignalTranslator
from ui.components.signal_interpreter import render_signal_interpretation
from ui.components.educational_tooltips import render_educational_content


def render_simple_dashboard(
    watchlist_symbols: List[str],
    portfolio_symbols: List[str],
    analyzer_results: Dict[str, Any]
) -> None:
    """
    Render simple, user-friendly dashboard.
    
    Args:
        watchlist_symbols: List of symbols in watchlist
        portfolio_symbols: List of symbols in portfolio
        analyzer_results: Analysis results for symbols
    """
    st.title("📊 Your Stock Dashboard")
    st.markdown("**Simple insights for smart investing**")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Stocks to Watch",
        "✅ Recommended Actions",
        "💼 Your Portfolio",
        "📰 Market Summary"
    ])
    
    with tab1:
        render_stocks_to_watch(watchlist_symbols, analyzer_results)
    
    with tab2:
        render_recommended_actions(analyzer_results)
    
    with tab3:
        render_portfolio_view(portfolio_symbols, analyzer_results)
    
    with tab4:
        render_market_summary(analyzer_results)


def render_stocks_to_watch(
    symbols: List[str],
    analyzer_results: Dict[str, Any]
) -> None:
    """Render stocks to watch section."""
    st.subheader("📈 Stocks to Watch")
    
    if not symbols:
        st.info("Add stocks to your watchlist to see recommendations here.")
        return
    
    # Filter for buy/watch signals
    watch_stocks = []
    for symbol in symbols:
        if symbol in analyzer_results:
            result = analyzer_results[symbol]
            entry_signal = result.get('entry_signals', {})
            signal_type = entry_signal.get('signal_type', '')
            
            if signal_type in ['STRONG_BUY', 'BUY', 'WATCH']:
                watch_stocks.append({
                    'Symbol': symbol,
                    'Recommendation': signal_type.replace('_', ' ').title(),
                    'Current Price': entry_signal.get('entry_price', 'N/A'),
                    'Confidence': f"{entry_signal.get('confidence', 0) * 100:.0f}%",
                    'Score': f"{entry_signal.get('score', 0):.1f}/100"
                })
    
    if watch_stocks:
        df = pd.DataFrame(watch_stocks)
        st.dataframe(df, use_container_width=True)
        
        # Show detailed view for selected stock
        selected_symbol = st.selectbox("View Details", options=[s['Symbol'] for s in watch_stocks])
        if selected_symbol and selected_symbol in analyzer_results:
            render_signal_interpretation(selected_symbol, analyzer_results[selected_symbol])
    else:
        st.info("No stocks with buy/watch signals in your watchlist.")


def render_recommended_actions(
    analyzer_results: Dict[str, Any]
) -> None:
    """Render recommended actions section."""
    st.subheader("✅ Recommended Actions")
    
    # Categorize recommendations
    strong_buy = []
    buy = []
    watch = []
    avoid = []
    
    for symbol, result in analyzer_results.items():
        entry_signal = result.get('entry_signals', {})
        signal_type = entry_signal.get('signal_type', '')
        
        action = {
            'Symbol': symbol,
            'Price': entry_signal.get('entry_price', 'N/A'),
            'Confidence': f"{entry_signal.get('confidence', 0) * 100:.0f}%",
            'Reason': entry_signal.get('reason', 'Technical analysis')
        }
        
        if signal_type == 'STRONG_BUY':
            strong_buy.append(action)
        elif signal_type == 'BUY':
            buy.append(action)
        elif signal_type == 'WATCH':
            watch.append(action)
        elif signal_type == 'AVOID':
            avoid.append(action)
    
    # Display by priority
    if strong_buy:
        st.success("### 🚀 Strong Buy Opportunities")
        df = pd.DataFrame(strong_buy)
        st.dataframe(df, use_container_width=True)
    
    if buy:
        st.info("### ✅ Buy Recommendations")
        df = pd.DataFrame(buy)
        st.dataframe(df, use_container_width=True)
    
    if watch:
        st.warning("### 👀 Watch List")
        df = pd.DataFrame(watch)
        st.dataframe(df, use_container_width=True)
    
    if avoid:
        st.error("### ⚠️ Avoid These Stocks")
        df = pd.DataFrame(avoid)
        st.dataframe(df, use_container_width=True)
    
    if not (strong_buy or buy or watch or avoid):
        st.info("No recommendations available. Run analysis on stocks to get recommendations.")


def render_portfolio_view(
    portfolio_symbols: List[str],
    analyzer_results: Dict[str, Any]
) -> None:
    """Render portfolio view."""
    st.subheader("💼 Your Portfolio")
    
    if not portfolio_symbols:
        st.info("Add stocks to your portfolio to track performance here.")
        return
    
    portfolio_data = []
    for symbol in portfolio_symbols:
        if symbol in analyzer_results:
            result = analyzer_results[symbol]
            entry_signal = result.get('entry_signals', {})
            risk_metrics = result.get('risk_metrics', {})
            
            portfolio_data.append({
                'Symbol': symbol,
                'Current Price': entry_signal.get('entry_price', 'N/A'),
                'Signal': entry_signal.get('signal_type', 'N/A').replace('_', ' ').title(),
                'Risk Level': risk_metrics.get('risk_level', 'N/A'),
                'Volatility': f"{risk_metrics.get('volatility', 0):.1f}%"
            })
    
    if portfolio_data:
        df = pd.DataFrame(portfolio_data)
        st.dataframe(df, use_container_width=True)
        
        # Portfolio summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Holdings", len(portfolio_data))
        with col2:
            buy_signals = sum(1 for p in portfolio_data if 'Buy' in p['Signal'])
            st.metric("Buy Signals", buy_signals)
        with col3:
            avg_volatility = sum(float(p['Volatility'].replace('%', '')) for p in portfolio_data if p['Volatility'] != 'N/A') / len(portfolio_data) if portfolio_data else 0
            st.metric("Avg Volatility", f"{avg_volatility:.1f}%")
    else:
        st.info("No portfolio data available.")


def render_market_summary(
    analyzer_results: Dict[str, Any]
) -> None:
    """Render market summary."""
    st.subheader("📰 Market Summary")
    
    if not analyzer_results:
        st.info("Run analysis to see market summary.")
        return
    
    # Calculate summary statistics
    total_stocks = len(analyzer_results)
    strong_buy_count = 0
    buy_count = 0
    watch_count = 0
    avoid_count = 0
    
    for result in analyzer_results.values():
        entry_signal = result.get('entry_signals', {})
        signal_type = entry_signal.get('signal_type', '')
        
        if signal_type == 'STRONG_BUY':
            strong_buy_count += 1
        elif signal_type == 'BUY':
            buy_count += 1
        elif signal_type == 'WATCH':
            watch_count += 1
        elif signal_type == 'AVOID':
            avoid_count += 1
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyzed", total_stocks)
    
    with col2:
        st.metric("Strong Buy", strong_buy_count, delta=f"{strong_buy_count/total_stocks*100:.1f}%")
    
    with col3:
        st.metric("Buy", buy_count, delta=f"{buy_count/total_stocks*100:.1f}%")
    
    with col4:
        st.metric("Watch", watch_count, delta=f"{watch_count/total_stocks*100:.1f}%")
    
    # Educational content
    st.divider()
    render_educational_content()

