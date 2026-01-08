"""
Main Dashboard

Control room dashboard for Stockport v4.
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime
import plotly.graph_objects as go

from utils.debug_utils import DebugUtils


def render_dashboard():
    """
    Render the main dashboard.
    
    Shows:
    - System status
    - Capital overview
    - Risk metrics
    - Active opportunities
    - Recent signals
    - Open positions
    - Performance chart
    """
    st.title("📊 Stockport v4 - Control Room")
    
    # System Status Section
    st.header("System Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        system_status = st.selectbox(
            "System Status",
            ["Running", "Stopped", "Paused"],
            key="system_status"
        )
        status_color = "🟢" if system_status == "Running" else "🔴"
        st.markdown(f"{status_color} **{system_status}**")
    
    with col2:
        trading_mode = st.selectbox(
            "Trading Mode",
            ["Manual", "Semi-Auto", "Full Auto"],
            key="trading_mode"
        )
    
    with col3:
        st.metric("Uptime", "99.5%")
    
    # Capital Overview Section
    st.header("💰 Capital Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Capital", "$100,000.00")
    
    with col2:
        st.metric("Available", "$75,000.00")
    
    with col3:
        st.metric("Allocated", "$20,000.00")
    
    with col4:
        st.metric("Daily P&L", "$1,250.00", delta="+1.25%")
    
    # Risk Metrics Section
    st.header("⚠️ Risk Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Exposure", "20%")
        st.progress(0.20)
    
    with col2:
        st.metric("Daily Loss", "$500.00", delta="-0.5%")
    
    with col3:
        st.metric("Drawdown", "2.5%")
        st.progress(0.025)
    
    # Active Opportunities Section
    st.header("🎯 Active Opportunities")
    
    opportunities_data = [
        {"symbol": "AAPL", "score": 85, "strategy": "trend_following_v1", "price": 150.25},
        {"symbol": "MSFT", "score": 78, "strategy": "momentum_v1", "price": 380.50},
        {"symbol": "GOOGL", "score": 72, "strategy": "trend_following_v1", "price": 142.75}
    ]
    
    if opportunities_data:
        df = st.dataframe(
            opportunities_data,
            column_config={
                "symbol": "Symbol",
                "score": st.column_config.NumberColumn("Score", format="%d"),
                "strategy": "Strategy",
                "price": st.column_config.NumberColumn("Price", format="$%.2f")
            },
            hide_index=True
        )
    else:
        st.info("No active opportunities at this time")
    
    # Recent Signals Section
    st.header("📡 Recent Signals")
    
    signals_data = [
        {"time": "10:30 AM", "symbol": "AAPL", "strategy": "trend_following_v1", "decision": "APPROVE"},
        {"time": "10:25 AM", "symbol": "MSFT", "strategy": "momentum_v1", "decision": "APPROVE"},
        {"time": "10:20 AM", "symbol": "TSLA", "strategy": "trend_following_v1", "decision": "REJECT"}
    ]
    
    if signals_data:
        st.dataframe(signals_data, hide_index=True)
    else:
        st.info("No recent signals")
    
    # Open Positions Section
    st.header("📈 Open Positions")
    
    positions_data = [
        {"symbol": "AAPL", "quantity": 10, "entry": 148.50, "current": 150.25, "pnl": "$17.50", "pnl_pct": "+1.18%"},
        {"symbol": "MSFT", "quantity": 5, "entry": 375.00, "current": 380.50, "pnl": "$27.50", "pnl_pct": "+1.47%"}
    ]
    
    if positions_data:
        st.dataframe(positions_data, hide_index=True)
    else:
        st.info("No open positions")
    
    # Performance Chart Section
    st.header("📊 Performance Chart")
    
    # Sample performance data
    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
    portfolio_values = [100000, 100500, 101200, 100800, 101250]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=portfolio_values,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Value ($)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Market State Section
    st.header("🌐 Market State")
    
    from ui.services import get_ui_data_service
    
    data_service = get_ui_data_service()
    market_state = data_service.get_market_state()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        regime = market_state.get("regime", "unknown")
        regime_color = "🟢" if "up" in regime.lower() else "🔴" if "down" in regime.lower() else "🟡"
        st.metric("Regime", f"{regime_color} {regime.replace('_', ' ').title()}")
        
        volatility = market_state.get("volatility_state", "unknown")
        volatility_color = "🟢" if volatility == "low" else "🟡" if volatility == "normal" else "🔴"
        st.metric("Volatility", f"{volatility_color} {volatility.title()}")
    
    with col2:
        breadth = market_state.get("breadth_state", "unknown")
        breadth_color = "🟢" if breadth == "bullish" else "🔴" if breadth == "bearish" else "🟡"
        st.metric("Breadth", f"{breadth_color} {breadth.title()}")
        
        liquidity = market_state.get("liquidity_state", "unknown")
        liquidity_color = "🟢" if liquidity == "high" else "🟡" if liquidity == "normal" else "🔴"
        st.metric("Liquidity", f"{liquidity_color} {liquidity.title()}")
    
    with col3:
        vix = market_state.get("vix_level", 0.0)
        vix_color = "🟢" if vix < 20 else "🟡" if vix < 30 else "🔴"
        st.metric("VIX", f"{vix_color} {vix:.1f}")
        
        confidence = market_state.get("confidence", 0.0)
        confidence_pct = f"{confidence:.1%}"
        st.metric("Confidence", confidence_pct)
    
    with col4:
        # Market state visualization
        st.subheader("State Summary")
        regime_display = regime.replace('_', ' ').title()
        st.write(f"**Current Regime:** {regime_display}")
        st.write(f"**Volatility:** {volatility.title()}")
        st.write(f"**Breadth:** {breadth.title()}")
        
        # Confidence gauge
        st.progress(confidence)
        st.caption(f"Market State Confidence: {confidence:.1%}")
    
    # Data Health Section
    st.header("🔍 Data Health")
    
    from ui.services import get_ui_data_service
    from backend.data.integrity.health_monitor import HealthStatus
    
    data_service = get_ui_data_service()
    health_data = data_service.get_data_health()
    overall_status = health_data.get("overall_status", "GREEN")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Overall status badge
        if overall_status == HealthStatus.GREEN:
            st.success(f"✅ **{overall_status}** - All systems healthy")
        elif overall_status == HealthStatus.YELLOW:
            st.warning(f"⚠️ **{overall_status}** - Minor issues detected")
        else:
            st.error(f"❌ **{overall_status}** - Critical issues - trading halted")
    
    with col2:
        st.metric("Green Symbols", health_data.get("green_count", 0))
    
    with col3:
        st.metric("Yellow Symbols", health_data.get("yellow_count", 0))
    
    with col4:
        st.metric("Red Symbols", health_data.get("red_count", 0))
    
    # Health breakdown by symbol (if available)
    if st.checkbox("Show Detailed Health", key="show_detailed_health"):
        st.info("Detailed health breakdown would be shown here (symbol-by-symbol)")


def main():
    """Main dashboard entry point."""
    render_dashboard()


if __name__ == "__main__":
    main()

