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
                        st.error(f"❌ Backtest engine not available: {e}")
                        st.error("Please ensure all required services are properly installed and configured.")
                        DebugUtils.log_error(e, "Backtest engine import error")
                        return
                
                except Exception as e:
                    st.error(f"❌ Backtest failed: {str(e)}")
                    st.error("Check logs for detailed error information.")
                    DebugUtils.log_error(e, "Backtest execution error")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        render_section_header("Backtest Results")
        
        # Get last backtest if available
        if 'last_backtest_id' in st.session_state:
            backtest_id = st.session_state['last_backtest_id']
            
            try:
                # Load actual backtest result from storage
                from services.storage.backtest_storage import BacktestStorage
                from models.backtest_result import BacktestResult, BacktestTrade, TradeStatus, TradeType
                from datetime import datetime as dt
                
                backtest_storage = BacktestStorage()
                result_data = backtest_storage.load_backtest(backtest_id)
                
                if result_data:
                    st.info(f"Showing results for: {backtest_id}")
                    
                    # Display actual metrics from result data
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_return = result_data.get('total_return', 0.0)
                        return_pct = result_data.get('total_return_pct', 0.0)
                        st.metric("Total Return", f"₹{total_return:,.2f}")
                        st.metric("Return %", f"{return_pct:.2f}%")
                    
                    with col2:
                        win_rate = result_data.get('win_rate', 0.0)
                        total_trades = result_data.get('total_trades', 0)
                        st.metric("Win Rate", f"{win_rate:.1f}%")
                        st.metric("Total Trades", str(total_trades))
                    
                    with col3:
                        avg_profit = result_data.get('avg_profit', 0.0)
                        avg_loss = result_data.get('avg_loss', 0.0)
                        st.metric("Avg Profit", f"₹{avg_profit:,.2f}")
                        st.metric("Avg Loss", f"₹{avg_loss:,.2f}")
                    
                    with col4:
                        profit_factor = result_data.get('profit_factor', 0.0)
                        max_drawdown_pct = result_data.get('max_drawdown_pct', 0.0)
                        st.metric("Profit Factor", f"{profit_factor:.2f}")
                        st.metric("Max Drawdown", f"{max_drawdown_pct:.2f}%")
                    
                    # Display actual trades
                    trades_list = result_data.get('trades', [])
                    if trades_list:
                        st.subheader("Trades")
                        trades_data = []
                        for trade_data in trades_list:
                            # Parse entry/exit dates
                            entry_date_str = trade_data.get('entry_date', '')
                            exit_date_str = trade_data.get('exit_date', '')
                            
                            try:
                                entry_date = dt.fromisoformat(entry_date_str.replace('Z', '+00:00')) if entry_date_str else None
                            except:
                                entry_date = None
                            
                            try:
                                exit_date = dt.fromisoformat(exit_date_str.replace('Z', '+00:00')) if exit_date_str else None
                            except:
                                exit_date = None
                            
                            trades_data.append({
                                'Symbol': trade_data.get('symbol', 'N/A'),
                                'Entry Date': entry_date.strftime('%Y-%m-%d %H:%M') if entry_date else 'N/A',
                                'Exit Date': exit_date.strftime('%Y-%m-%d %H:%M') if exit_date else 'N/A',
                                'Entry Price': f"₹{trade_data.get('entry_price', 0):.2f}",
                                'Exit Price': f"₹{trade_data.get('exit_price', 0):.2f}" if trade_data.get('exit_price') else 'N/A',
                                'Quantity': trade_data.get('quantity', 0),
                                'P&L': f"₹{trade_data.get('profit_loss', 0):,.2f}",
                                'Status': trade_data.get('status', 'N/A')
                            })
                        trades_df = pd.DataFrame(trades_data)
                        st.dataframe(trades_df, use_container_width=True)
                    else:
                        st.info("No trades executed in this backtest.")
                else:
                    st.error(f"❌ Backtest result not found: {backtest_id}")
                    st.error("The backtest may have failed or was not saved properly.")
                    render_operational_status(
                        status="NO RESULTS",
                        opportunities=0,
                        show_live=False,
                        reason=f"Backtest {backtest_id} not found in storage."
                    )
                    
            except Exception as e:
                st.error(f"❌ Error loading backtest results: {str(e)}")
                DebugUtils.log_error(e, "Error loading backtest results")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())
        else:
            render_operational_status(
                status="NO RESULTS",
                opportunities=0,
                show_live=False,
                reason="Run a backtest first to see results here."
            )
    
    with tab3:
        render_section_header("Backtest History")
        
        try:
            # Load actual backtest history from storage
            from services.storage.backtest_storage import BacktestStorage
            from datetime import datetime as dt
            
            backtest_storage = BacktestStorage()
            history = backtest_storage.list_backtests()
            
            if history:
                # Build history table from actual results
                history_data = {
                    'ID': [],
                    'Strategy': [],
                    'Symbols': [],
                    'Period': [],
                    'Return %': [],
                    'Win Rate': [],
                    'Total Trades': [],
                    'Created': []
                }
                
                for backtest in history:
                    history_data['ID'].append(backtest.get('id', 'N/A'))
                    history_data['Strategy'].append(backtest.get('strategy_name', 'N/A'))
                    
                    symbols = backtest.get('symbols', [])
                    history_data['Symbols'].append(', '.join(symbols) if symbols else 'N/A')
                    
                    # Parse dates
                    start_date_str = backtest.get('start_date', '')
                    end_date_str = backtest.get('end_date', '')
                    
                    try:
                        if start_date_str:
                            start_dt = dt.fromisoformat(start_date_str.replace('Z', '+00:00'))
                            start_str = start_dt.strftime('%Y-%m-%d')
                        else:
                            start_str = 'N/A'
                    except:
                        start_str = 'N/A'
                    
                    try:
                        if end_date_str:
                            end_dt = dt.fromisoformat(end_date_str.replace('Z', '+00:00'))
                            end_str = end_dt.strftime('%Y-%m-%d')
                        else:
                            end_str = 'N/A'
                    except:
                        end_str = 'N/A'
                    
                    history_data['Period'].append(f"{start_str} to {end_str}")
                    
                    return_pct = backtest.get('total_return_pct', 0.0)
                    history_data['Return %'].append(f"{return_pct:.2f}%")
                    
                    win_rate = backtest.get('win_rate', 0.0)
                    history_data['Win Rate'].append(f"{win_rate:.1f}%")
                    
                    # Get full backtest to get total_trades
                    backtest_id = backtest.get('id')
                    if backtest_id:
                        full_result = backtest_storage.load_backtest(backtest_id)
                        total_trades = full_result.get('total_trades', 0) if full_result else 0
                    else:
                        total_trades = 0
                    history_data['Total Trades'].append(str(total_trades))
                    
                    created_str = backtest.get('created_at', '')
                    try:
                        if created_str:
                            created_dt = dt.fromisoformat(created_str.replace('Z', '+00:00'))
                            created_str = created_dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                    history_data['Created'].append(created_str if created_str else 'N/A')
                
                history_df = pd.DataFrame(history_data)
                st.dataframe(history_df, use_container_width=True)
                
                # Allow selecting a backtest to view
                if len(history) > 0:
                    selected_id = st.selectbox(
                        "Select backtest to view details:",
                        options=[bt.get('id') for bt in history if bt.get('id')],
                        key="backtest_history_select"
                    )
                    if selected_id:
                        st.session_state['last_backtest_id'] = selected_id
                        st.info("Switch to 'Results' tab to view details.")
            else:
                render_operational_status(
                    status="NO HISTORY",
                    opportunities=0,
                    show_live=False,
                    reason="No backtests have been run yet. Run a backtest to see history here."
                )
                
        except Exception as e:
            st.error(f"❌ Error loading backtest history: {str(e)}")
            DebugUtils.log_error(e, "Error loading backtest history")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())


# Note: render_backtest_context_strip and render_backtest_canvas are used directly from app.py
# This function is kept for compatibility but not used in terminal_v1 architecture
def render_backtest() -> None:
    """Render Backtest workspace."""
    render_backtest_context_strip()
    from ui.terminal_v1.layout.canvas import render_canvas
    render_canvas(render_backtest_canvas)

