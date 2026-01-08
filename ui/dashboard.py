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
    
    from ui.services import get_ui_data_service
    data_service = get_ui_data_service()
    capital_overview = data_service.get_capital_overview()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Capital", f"${capital_overview.get('total', 0):,.2f}")
    
    with col2:
        st.metric("Available", f"${capital_overview.get('available', 0):,.2f}")
    
    with col3:
        st.metric("Allocated", f"${capital_overview.get('allocated', 0):,.2f}")
    
    with col4:
        # Calculate daily P&L from positions
        positions = data_service.get_positions()
        daily_pnl = sum(pos.get('pnl', 0) for pos in positions)
        daily_pnl_pct = (daily_pnl / capital_overview.get('total', 1)) * 100 if capital_overview.get('total', 0) > 0 else 0
        st.metric("Daily P&L", f"${daily_pnl:,.2f}", delta=f"{daily_pnl_pct:+.2f}%")
    
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
    
    opportunities_data = data_service.get_opportunities(limit=5)
    
    if opportunities_data:
        # Format opportunities for display
        display_data = []
        for opp in opportunities_data[:5]:  # Top 5
            display_data.append({
                "symbol": opp.get("symbol", ""),
                "score": opp.get("score", 0),
                "strategy": opp.get("strategy_id", "unknown"),
                "price": opp.get("price", 0.0)
            })
        
        if display_data:
            df = st.dataframe(
                display_data,
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
    
    signals_data = data_service.get_signals(limit=10)
    
    if signals_data:
        # Format signals for display
        display_signals = []
        for signal in signals_data[:10]:  # Top 10
            timestamp = signal.get("timestamp", "")
            if isinstance(timestamp, str):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%I:%M %p")
                except:
                    time_str = timestamp
            else:
                time_str = str(timestamp)
            
            display_signals.append({
                "time": time_str,
                "symbol": signal.get("symbol", ""),
                "strategy": signal.get("strategy_id", "unknown"),
                "decision": signal.get("decision", "UNKNOWN")
            })
        
        if display_signals:
            st.dataframe(display_signals, hide_index=True)
        else:
            st.info("No recent signals")
    else:
        st.info("No recent signals")
    
    # Open Positions Section
    st.header("📈 Open Positions")
    
    positions_data = data_service.get_positions()
    
    if positions_data:
        # Format positions for display
        display_positions = []
        for pos in positions_data:
            pnl = pos.get("pnl", 0.0)
            pnl_pct = pos.get("pnl_percent", 0.0)
            display_positions.append({
                "symbol": pos.get("symbol", ""),
                "quantity": pos.get("quantity", 0),
                "entry": pos.get("entry_price", 0.0),
                "current": pos.get("current_price", 0.0),
                "pnl": f"${pnl:.2f}",
                "pnl_pct": f"{pnl_pct:+.2f}%"
            })
        
        if display_positions:
            st.dataframe(display_positions, hide_index=True)
        else:
            st.info("No open positions")
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
    
    health_data = data_service.get_data_health()
    overall_status = health_data.get("overall_status", "GREEN")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Overall status badge
        if overall_status == "GREEN":
            st.success(f"✅ **{overall_status}** - All systems healthy")
        elif overall_status == "YELLOW":
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

