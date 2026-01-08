"""
Portfolio View

View capital and positions.
"""

import streamlit as st
from typing import List, Dict, Any
import plotly.graph_objects as go

from utils.debug_utils import DebugUtils


def render_portfolio_view():
    """
    Render the portfolio view.
    
    Shows:
    - Capital breakdown
    - Position list
    - Sector allocation
    - Risk metrics
    - Correlation matrix
    """
    st.title("💼 Portfolio & Capital")
    
    # Capital Breakdown Section
    st.header("💰 Capital Breakdown")
    
    from ui.services import get_ui_data_service
    data_service = get_ui_data_service()
    capital_overview = data_service.get_capital_overview()
    
    total = capital_overview.get("total", 0.0)
    allocated = capital_overview.get("allocated", 0.0)
    available = capital_overview.get("available", 0.0)
    reserved = capital_overview.get("reserved", 0.0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Capital", f"${total:,.2f}")
    
    with col2:
        allocated_pct = (allocated / total * 100) if total > 0 else 0
        st.metric("Allocated", f"${allocated:,.2f}", delta=f"{allocated_pct:.1f}%")
    
    with col3:
        available_pct = (available / total * 100) if total > 0 else 0
        st.metric("Available", f"${available:,.2f}", delta=f"{available_pct:.1f}%")
    
    with col4:
        reserved_pct = (reserved / total * 100) if total > 0 else 0
        st.metric("Reserved", f"${reserved:,.2f}", delta=f"{reserved_pct:.1f}%")
    
    # Position List Section
    st.header("📈 Open Positions")
    
    positions_data = data_service.get_positions()
    
    # Format positions for display
    positions = []
    for pos in positions_data:
        positions.append({
            "symbol": pos.get("symbol", ""),
            "quantity": pos.get("quantity", 0),
            "entry_price": pos.get("entry_price", 0.0),
            "current_price": pos.get("current_price", 0.0),
            "value": pos.get("value", 0.0),
            "pnl": pos.get("pnl", 0.0),
            "pnl_percent": pos.get("pnl_percent", 0.0),
            "sector": "Unknown",  # Would need to get from opportunity/position data
            "strategy": "Unknown"  # Would need to get from position data
        })
    
    if positions:
        for pos in positions:
            with st.expander(f"{pos['symbol']} - {pos['quantity']} shares - P&L: ${pos['pnl']:.2f} ({pos['pnl_percent']:+.2f}%)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Entry Price:** ${pos['entry_price']:.2f}")
                    st.write(f"**Current Price:** ${pos['current_price']:.2f}")
                    st.write(f"**Value:** ${pos['value']:.2f}")
                
                with col2:
                    st.write(f"**Sector:** {pos['sector']}")
                    st.write(f"**Strategy:** {pos['strategy']}")
                    st.write(f"**P&L:** ${pos['pnl']:.2f}")
                
                with col3:
                    if st.button(f"Close Position", key=f"close_{pos['symbol']}"):
                        st.info(f"Position {pos['symbol']} would be closed")
                    
                    if st.button(f"View Details", key=f"details_{pos['symbol']}"):
                        st.info(f"Position details for {pos['symbol']} would be shown here")
    else:
        st.info("No open positions")
    
    # Sector Allocation Section
    st.header("📊 Sector Allocation")
    
    sector_data = {
        "Technology": 0.40,
        "Healthcare": 0.25,
        "Finance": 0.20,
        "Energy": 0.10,
        "Consumer": 0.05
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=list(sector_data.keys()),
        values=list(sector_data.values()),
        hole=0.3
    )])
    
    fig.update_layout(title="Sector Allocation", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk Metrics Section
    st.header("⚠️ Risk Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Per-Trade Risk", "2.0%")
        st.metric("Daily Risk", "5.0%")
    
    with col2:
        st.metric("Portfolio Risk", "20.0%")
        st.metric("Max Sector Exposure", "40.0%")
    
    with col3:
        st.metric("Avg Correlation", "0.35")
        st.metric("Diversification Score", "0.75")
    
    # Correlation Matrix Section
    st.header("🔗 Correlation Matrix")
    
    correlation_data = {
        "AAPL": {"AAPL": 1.0, "MSFT": 0.65, "GOOGL": 0.70},
        "MSFT": {"AAPL": 0.65, "MSFT": 1.0, "GOOGL": 0.68},
        "GOOGL": {"AAPL": 0.70, "MSFT": 0.68, "GOOGL": 1.0}
    }
    
    st.dataframe(correlation_data, use_container_width=True)
    
    # Export Section
    st.header("📥 Export")
    
    if st.button("Export Portfolio Report"):
        st.info("Portfolio report would be exported here")


def main():
    """Main portfolio view entry point."""
    render_portfolio_view()


if __name__ == "__main__":
    main()

