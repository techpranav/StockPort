"""
Backtest Runner UI Component

Streamlit component for running backtests and viewing results.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta

from services.backtesting.backtest_engine import BacktestEngine
from services.storage.backtest_storage import BacktestStorage
from core.enhanced_analyzer import EnhancedStockAnalyzer


def render_backtest_runner(
    available_symbols: List[str],
    analyzer: EnhancedStockAnalyzer
) -> None:
    """
    Render backtest runner interface.
    
    Args:
        available_symbols: List of available stock symbols
        analyzer: Enhanced analyzer instance
    """
    st.header("🧪 Strategy Backtesting")
    
    backtest_engine = BacktestEngine(analyzer=analyzer)
    backtest_storage = BacktestStorage()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Run Backtest", "Results", "History"])
    
    with tab1:
        render_run_backtest(backtest_engine, backtest_storage, available_symbols)
    
    with tab2:
        render_backtest_results(backtest_storage)
    
    with tab3:
        render_backtest_history(backtest_storage)


def render_run_backtest(
    backtest_engine: BacktestEngine,
    backtest_storage: BacktestStorage,
    available_symbols: List[str]
) -> None:
    """Render backtest configuration and execution."""
    st.subheader("Configure Backtest")
    
    # Strategy name
    strategy_name = st.text_input("Strategy Name", value="Default Strategy")
    
    # Symbol selection
    selected_symbols = st.multiselect(
        "Select Stocks",
        options=available_symbols,
        help="Select stocks to test"
    )
    
    if not selected_symbols:
        st.warning("Please select at least one stock")
        return
    
    # Date range
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    if start_date >= end_date:
        st.error("Start date must be before end date")
        return
    
    # Capital and position sizing
    col1, col2 = st.columns(2)
    
    with col1:
        initial_capital = st.number_input(
            "Initial Capital (₹)",
            min_value=1000.0,
            value=100000.0,
            step=1000.0
        )
    
    with col2:
        position_size_pct = st.number_input(
            "Position Size (%)",
            min_value=1.0,
            max_value=100.0,
            value=10.0,
            step=1.0
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
            step=0.01
        ) / 100
    
    with col2:
        stop_loss_pct = st.number_input(
            "Stop Loss (%)",
            min_value=0.0,
            max_value=50.0,
            value=5.0,
            step=0.5
        )
    
    with col3:
        take_profit_pct = st.number_input(
            "Take Profit (%)",
            min_value=0.0,
            max_value=100.0,
            value=10.0,
            step=1.0
        )
    
    # Run button
    if st.button("🚀 Run Backtest", type="primary"):
        with st.spinner("Running backtest... This may take a while."):
            try:
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
                
            except Exception as e:
                st.error(f"❌ Backtest failed: {str(e)}")


def render_backtest_results(backtest_storage: BacktestStorage) -> None:
    """Render backtest results."""
    st.subheader("Backtest Results")
    
    # Get last backtest if available
    if 'last_backtest_id' in st.session_state:
        backtest_id = st.session_state['last_backtest_id']
    else:
        # List available backtests
        backtests = backtest_storage.list_backtests(limit=10)
        if not backtests:
            st.info("No backtests available. Run a backtest first.")
            return
        
        backtest_options = {f"{b['strategy_name']} ({b['created_at'][:10]})": b['id'] for b in backtests}
        selected = st.selectbox("Select Backtest", options=list(backtest_options.keys()))
        backtest_id = backtest_options[selected]
    
    # Load backtest
    result = backtest_storage.load_backtest(backtest_id)
    
    if not result:
        st.error("Backtest not found")
        return
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Return", f"₹{result.get('total_return', 0):,.2f}")
        st.metric("Return %", f"{result.get('total_return_pct', 0):.2f}%")
    
    with col2:
        st.metric("Win Rate", f"{result.get('win_rate', 0):.1f}%")
        st.metric("Total Trades", result.get('total_trades', 0))
    
    with col3:
        st.metric("Avg Profit", f"₹{result.get('avg_profit', 0):,.2f}")
        st.metric("Avg Loss", f"₹{result.get('avg_loss', 0):,.2f}")
    
    with col4:
        st.metric("Profit Factor", f"{result.get('profit_factor', 0):.2f}")
        st.metric("Max Drawdown", f"{result.get('max_drawdown_pct', 0):.2f}%")
    
    # Trades table
    st.subheader("Trades")
    trades = result.get('trades', [])
    
    if trades:
        trades_df = pd.DataFrame([
            {
                'Symbol': t.get('symbol'),
                'Entry Date': t.get('entry_date', '')[:10],
                'Entry Price': f"₹{t.get('entry_price', 0):.2f}",
                'Exit Date': t.get('exit_date', '')[:10] if t.get('exit_date') else 'Open',
                'Exit Price': f"₹{t.get('exit_price', 0):.2f}" if t.get('exit_price') else 'N/A',
                'P&L': f"₹{t.get('profit_loss', 0):,.2f}",
                'P&L %': f"{t.get('profit_loss_pct', 0):.2f}%",
                'Status': t.get('status', '').title()
            }
            for t in trades
        ])
        st.dataframe(trades_df, use_container_width=True)
    else:
        st.info("No trades executed")


def render_backtest_history(backtest_storage: BacktestStorage) -> None:
    """Render backtest history."""
    st.subheader("Backtest History")
    
    backtests = backtest_storage.list_backtests(limit=50)
    
    if not backtests:
        st.info("No backtest history available.")
        return
    
    # Display as table
    history_df = pd.DataFrame([
        {
            'Strategy': b['strategy_name'],
            'Symbols': ', '.join(b['symbols'][:3]) + ('...' if len(b['symbols']) > 3 else ''),
            'Period': f"{b['start_date'][:10]} to {b['end_date'][:10]}",
            'Return %': f"{b['total_return_pct']:.2f}%",
            'Win Rate': f"{b['win_rate']:.1f}%",
            'Created': b['created_at'][:10] if b.get('created_at') else 'N/A'
        }
        for b in backtests
    ])
    
    st.dataframe(history_df, use_container_width=True)
    
    # Compare selected backtests
    st.subheader("Compare Backtests")
    selected_ids = st.multiselect(
        "Select backtests to compare",
        options=[b['id'] for b in backtests],
        format_func=lambda x: next((b['strategy_name'] for b in backtests if b['id'] == x), x)
    )
    
    if selected_ids and st.button("Compare"):
        comparison = backtest_storage.compare_backtests(selected_ids)
        
        if comparison:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Avg Return", f"{comparison['avg_return_pct']:.2f}%")
            
            with col2:
                st.metric("Avg Win Rate", f"{comparison['avg_win_rate']:.1f}%")
            
            with col3:
                st.metric("Best Return", f"{comparison['best_return']:.2f}%")

