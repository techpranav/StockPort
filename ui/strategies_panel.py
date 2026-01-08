"""
Strategies Control Panel

Manage trading strategies.
"""

import streamlit as st
from typing import List, Dict, Any
from datetime import datetime

from utils.debug_utils import DebugUtils


def render_strategies_panel():
    """
    Render the strategies control panel.
    
    Shows:
    - Strategy list with status
    - Strategy performance
    - Strategy controls
    - Backtest results
    """
    st.title("⚙️ Strategies Control Panel")
    
    # Strategy List Section
    st.header("Strategy List")
    
    strategies = [
        {
            "id": "trend_following_v1",
            "name": "Trend Following v1",
            "type": "trend_following",
            "status": "active",
            "win_rate": 0.55,
            "profit_factor": 1.8,
            "sharpe": 1.2,
            "total_return": 0.15,
            "total_trades": 45
        },
        {
            "id": "momentum_v1",
            "name": "Momentum v1",
            "type": "momentum",
            "status": "active",
            "win_rate": 0.48,
            "profit_factor": 1.5,
            "sharpe": 0.9,
            "total_return": 0.12,
            "total_trades": 38
        },
        {
            "id": "mean_reversion_v1",
            "name": "Mean Reversion v1",
            "type": "mean_reversion",
            "status": "paused",
            "win_rate": 0.42,
            "profit_factor": 1.1,
            "sharpe": 0.5,
            "total_return": 0.05,
            "total_trades": 30
        }
    ]
    
    # Display strategies
    for strategy in strategies:
        with st.expander(f"{strategy['name']} - {strategy['status'].upper()}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Type:** {strategy['type']}")
                st.write(f"**Status:** {strategy['status']}")
                st.write(f"**Total Trades:** {strategy['total_trades']}")
            
            with col2:
                st.write(f"**Win Rate:** {strategy['win_rate']:.1%}")
                st.write(f"**Profit Factor:** {strategy['profit_factor']:.2f}")
                st.write(f"**Sharpe Ratio:** {strategy['sharpe']:.2f}")
            
            with col3:
                st.write(f"**Total Return:** {strategy['total_return']:.1%}")
                
                # Strategy controls
                if strategy['status'] == 'active':
                    if st.button(f"Pause", key=f"pause_{strategy['id']}"):
                        st.info(f"Strategy {strategy['name']} paused")
                else:
                    if st.button(f"Activate", key=f"activate_{strategy['id']}"):
                        st.info(f"Strategy {strategy['name']} activated")
                
                if st.button(f"View Details", key=f"details_{strategy['id']}"):
                    st.info(f"Strategy details for {strategy['name']} would be shown here")
    
    # Strategy Performance Charts Section
    st.header("📊 Strategy Performance")
    
    selected_strategy = st.selectbox(
        "Select Strategy",
        [s['name'] for s in strategies],
        key="selected_strategy"
    )
    
    if selected_strategy:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Win Rate Over Time")
            # Would show chart here
            st.info("Win rate chart would be displayed here")
        
        with col2:
            st.subheader("Profit Factor Over Time")
            # Would show chart here
            st.info("Profit factor chart would be displayed here")
    
    # Backtest Section
    st.header("🧪 Backtesting Lab")
    
    col1, col2 = st.columns(2)
    
    with col1:
        backtest_strategy = st.selectbox(
            "Strategy to Backtest",
            [s['name'] for s in strategies],
            key="backtest_strategy"
        )
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
            key="backtest_date_range"
        )
    
    with col2:
        initial_capital = st.number_input(
            "Initial Capital",
            min_value=1000,
            value=100000,
            step=10000,
            key="backtest_capital"
        )
        
        if st.button("Run Backtest", key="run_backtest"):
            st.info("Backtest would be executed here")
    
    # Shadow Trading Comparison Section
    st.header("👻 Shadow Trading Comparison")
    
    from backend.shadow.comparison_engine import ComparisonEngine
    from backend.learning.performance_tracker import PerformanceTracker
    
    performance_tracker = PerformanceTracker()
    comparison_engine = ComparisonEngine(performance_tracker)
    
    shadow_strategy = st.selectbox(
        "Select Strategy for Comparison",
        [s['id'] for s in strategies],
        key="shadow_strategy"
    )
    
    if shadow_strategy and st.button("Compare Shadow vs Live", key="compare_shadow"):
        comparison = comparison_engine.compare(shadow_strategy, days=30)
        
        if comparison:
            st.subheader(f"Shadow vs Live: {shadow_strategy}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Live Performance**")
                st.metric("Win Rate", f"{comparison.live_win_rate:.1%}")
                st.metric("Profit Factor", f"{comparison.live_profit_factor:.2f}")
                st.metric("Sharpe Ratio", f"{comparison.live_sharpe:.2f}")
                st.metric("Max Drawdown", f"{comparison.live_drawdown:.1%}")
            
            with col2:
                st.markdown("**Shadow Performance**")
                st.metric("Win Rate", f"{comparison.shadow_win_rate:.1%}", 
                         delta=f"{comparison.win_rate_diff:+.1%}")
                st.metric("Profit Factor", f"{comparison.shadow_profit_factor:.2f}",
                         delta=f"{comparison.profit_factor_diff:+.2f}")
                st.metric("Sharpe Ratio", f"{comparison.shadow_sharpe:.2f}",
                         delta=f"{comparison.sharpe_diff:+.2f}")
                st.metric("Max Drawdown", f"{comparison.shadow_drawdown:.1%}",
                         delta=f"{comparison.drawdown_diff:+.1%}")
            
            # Recommendation
            st.divider()
            recommendation = comparison.recommendation
            if recommendation == "activate":
                st.success(f"✅ **Recommendation: ACTIVATE** - Shadow performance significantly outperforms live")
            elif recommendation == "keep_shadow":
                st.info(f"ℹ️ **Recommendation: KEEP SHADOW** - Continue monitoring shadow performance")
            elif recommendation == "disable":
                st.error(f"❌ **Recommendation: DISABLE** - Shadow performance is poor")
            else:
                st.warning(f"⚠️ **Recommendation: {recommendation.upper()}**")
        else:
            st.warning("Insufficient data for comparison. Need at least 30 days of both live and shadow performance.")
    
    # Backtest Results (if available)
    if st.checkbox("Show Backtest Results", key="show_backtest_results"):
        st.subheader("Backtest Results")
        
        results = {
            "Total Return": "15.2%",
            "Win Rate": "55%",
            "Profit Factor": "1.8",
            "Sharpe Ratio": "1.2",
            "Max Drawdown": "8.5%",
            "Total Trades": "45"
        }
        
        for metric, value in results.items():
            st.metric(metric, value)


def main():
    """Main strategies panel entry point."""
    render_strategies_panel()


if __name__ == "__main__":
    main()

