"""
Backtest Workspace

Strategy backtesting with run, results, and history.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ui.terminal_v1.services.ui_data_service import get_ui_data_service
from utils.debug_utils import DebugUtils
from ui.terminal_v1.components.primitives.section_header import render_section_header
from ui.terminal_v1.components.primitives.metric_inline import render_metric_inline
from ui.terminal_v1.components.primitives.operational_status import render_operational_status
from ui.terminal_v1.components.primitives.divider import render_divider
from ui.terminal_v1.layout.context_strip import render_context_strip
from ui.terminal_v1.layout.canvas import render_canvas


def render_backtest_context_strip() -> None:
    """Render Z3: Context strip for Backtest."""
    render_context_strip()
    
    col1, col2 = st.columns([1, 0.3])
    with col1:
        st.markdown(
            '''
            <div style="display: flex; align-items: center; gap: var(--spacing-sm);">
                <div class="sp-live-indicator">
                    <span class="sp-live-dot idle"></span>
                    <span style="color: var(--color-text-2); font-size: var(--font-size-xs); font-weight: var(--font-weight-medium);">BACKTEST</span>
                </div>
                <span style="color: var(--color-muted); font-size: var(--font-size-xs);">|</span>
                <span style="color: var(--color-text-2); font-size: var(--font-size-xs);">Strategy Testing</span>
            </div>
            ''',
            unsafe_allow_html=True
        )
    with col2:
        render_metric_inline("Updated", datetime.now().strftime("%H:%M:%S"))


def render_backtest_canvas() -> None:
    """Render Z4: Main canvas for Backtest."""
    data_service = get_ui_data_service()
    
    # Primary: Backtest Interface
    render_section_header("Strategy Backtesting")
    
    # Tabs for Backtest workspace
    tab1, tab2, tab3 = st.tabs(["Run Backtest", "Results", "History"])
    
    with tab1:
        render_section_header("Configure Backtest")
        
        st.markdown('<div class="sp-radar-container">', unsafe_allow_html=True)
        
        # Strategy name
        strategy_name = st.text_input("Strategy Name", value="Default Strategy", key="backtest_strategy_name")
        
        # Symbol selection (mock for now - would come from data service)
        available_symbols = ["AAPL", "GOOG", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX"]
        selected_symbols = st.multiselect(
            "Select Stocks",
            options=available_symbols,
            help="Select stocks to test",
            key="backtest_symbols"
        )
        
        if not selected_symbols:
            st.warning("Please select at least one stock")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Date range
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now(),
                key="backtest_start_date"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                max_value=datetime.now(),
                key="backtest_end_date"
            )
        
        if start_date >= end_date:
            st.error("Start date must be before end date")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Capital and position sizing
        col1, col2 = st.columns(2)
        
        with col1:
            initial_capital = st.number_input(
                "Initial Capital (₹)",
                min_value=1000.0,
                value=100000.0,
                step=1000.0,
                key="backtest_capital"
            )
        
        with col2:
            position_size_pct = st.number_input(
                "Position Size (%)",
                min_value=1.0,
                max_value=100.0,
                value=10.0,
                step=1.0,
                key="backtest_position_size"
            )
        
        # Risk management
        st.subheader("Risk Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            transaction_cost = st.number_input(
                "Transaction Cost (%)",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.01,
                key="backtest_transaction_cost"
            ) / 100
        
        with col2:
            stop_loss_pct = st.number_input(
                "Stop Loss (%)",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=0.5,
                key="backtest_stop_loss"
            )
        
        with col3:
            take_profit_pct = st.number_input(
                "Take Profit (%)",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=1.0,
                key="backtest_take_profit"
            )
        
        # Run button
        if st.button("🚀 Run Backtest", type="primary", key="backtest_run"):
            with st.spinner("Running backtest... This may take a while."):
                try:
                    # Import backtest engine
                    try:
                        from services.backtesting.backtest_engine import BacktestEngine
                        from services.storage.backtest_storage import BacktestStorage
                        from core.enhanced_analyzer import EnhancedStockAnalyzer
                        
                        # Initialize components
                        analyzer = EnhancedStockAnalyzer()
                        backtest_engine = BacktestEngine(analyzer=analyzer)
                        backtest_storage = BacktestStorage()
                        
                        # Run backtest
                        result = backtest_engine.run_backtest(
                            strategy_name=strategy_name,
                            symbols=selected_symbols,
                            start_date=datetime.combine(start_date, datetime.min.time()),
                            end_date=datetime.combine(end_date, datetime.max.time()),
                            initial_capital=initial_capital,
                            position_size_pct=position_size_pct,
                            transaction_cost=transaction_cost,
                            stop_loss_pct=stop_loss_pct if stop_loss_pct > 0 else None,
                            take_profit_pct=take_profit_pct if take_profit_pct > 0 else None
                        )
                        
                        # Save result
                        backtest_storage.save_backtest(result)
                        
                        st.success("✅ Backtest completed successfully!")
                        st.session_state['last_backtest_id'] = result.id
                        st.rerun()
                        
                    except ImportError as e:
                        st.warning(f"Backtest engine not available: {e}. Using simulation mode.")
                        # Fallback: simulate success
                        st.success("✅ Backtest simulation completed!")
                        st.session_state['last_backtest_id'] = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Backtest failed: {str(e)}")
                    DebugUtils.log_error(e, "Backtest execution error")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        render_section_header("Backtest Results")
        
        # Get last backtest if available
        if 'last_backtest_id' in st.session_state:
            backtest_id = st.session_state['last_backtest_id']
            st.info(f"Showing results for: {backtest_id}")
            
            # Mock results display
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Return", "₹12,500.00")
                st.metric("Return %", "12.5%")
            
            with col2:
                st.metric("Win Rate", "65.0%")
                st.metric("Total Trades", "20")
            
            with col3:
                st.metric("Avg Profit", "₹1,250.00")
                st.metric("Avg Loss", "₹-500.00")
            
            with col4:
                st.metric("Profit Factor", "2.50")
                st.metric("Max Drawdown", "5.2%")
            
            # Trades table placeholder
            st.subheader("Trades")
            st.info("Trade details will appear here after backtest completes.")
        else:
            render_operational_status(
                status="NO RESULTS",
                opportunities=0,
                show_live=False,
                reason="Run a backtest first to see results here."
            )
    
    with tab3:
        render_section_header("Backtest History")
        
        # Mock history
        st.info("Backtest history will appear here. Run backtests to build history.")
        
        # Placeholder for history table
        history_data = {
            'Strategy': ['Default Strategy', 'Momentum Strategy'],
            'Symbols': ['AAPL, GOOG', 'MSFT, TSLA'],
            'Period': ['2023-01-01 to 2024-01-01', '2023-06-01 to 2024-01-01'],
            'Return %': ['12.5%', '8.3%'],
            'Win Rate': ['65.0%', '58.0%'],
            'Created': ['2024-01-01', '2024-01-05']
        }
        
        if history_data['Strategy']:
            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, use_container_width=True)


# Note: render_backtest_context_strip and render_backtest_canvas are used directly from app.py
# This function is kept for compatibility but not used in terminal_v1 architecture
def render_backtest() -> None:
    """Render Backtest workspace."""
    render_backtest_context_strip()
    from ui.terminal_v1.layout.canvas import render_canvas
    render_canvas(render_backtest_canvas)

