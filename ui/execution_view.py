"""
Execution View

Monitor order execution.
"""

import streamlit as st
from typing import List, Dict, Any
from datetime import datetime

from utils.debug_utils import DebugUtils


def render_execution_view():
    """
    Render the execution view.
    
    Shows:
    - Pending orders
    - Order history
    - Execution log
    - Fill details
    """
    st.title("⚡ Positions & Execution")
    
    # Pending Orders Section
    st.header("⏳ Pending Orders")
    
    from ui.services import get_ui_data_service
    data_service = get_ui_data_service()
    all_orders = data_service.get_orders()
    
    # Filter pending orders
    pending_orders = [
        order for order in all_orders
        if order.get("status", "").lower() in ["pending", "submitted", "open"]
    ]
    
    # Format orders for display
    formatted_pending = []
    for order in pending_orders:
        created_at = order.get("created_at", "")
        if isinstance(created_at, str):
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                time_str = dt.strftime("%I:%M:%S %p")
            except:
                time_str = created_at
        else:
            time_str = str(created_at)
        
        formatted_pending.append({
            "order_id": order.get("order_id", ""),
            "symbol": order.get("symbol", ""),
            "side": order.get("side", ""),
            "quantity": order.get("quantity", 0),
            "order_type": order.get("order_type", ""),
            "status": order.get("status", ""),
            "created_at": time_str,
            "strategy": "Unknown"  # Would need to get from order data
        })
    
    pending_orders = formatted_pending
    
    if pending_orders:
        for order in pending_orders:
            with st.expander(f"{order['symbol']} - {order['side'].upper()} {order['quantity']} shares - {order['status'].upper()}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Order ID:** {order['order_id']}")
                    st.write(f"**Type:** {order['order_type']}")
                    st.write(f"**Strategy:** {order['strategy']}")
                
                with col2:
                    st.write(f"**Created:** {order['created_at']}")
                    if st.button(f"Cancel", key=f"cancel_{order['order_id']}"):
                        st.info(f"Order {order['order_id']} would be cancelled")
    else:
        st.info("No pending orders")
    
    # Order History Section
    st.header("📜 Order History")
    
    # Get filled/cancelled orders
    filled_orders = [
        order for order in all_orders
        if order.get("status", "").lower() in ["filled", "cancelled", "rejected", "closed"]
    ]
    
    # Format orders for display
    order_history = []
    for order in filled_orders[:20]:  # Last 20 orders
        filled_at = order.get("created_at", "")  # Would use filled_at if available
        if isinstance(filled_at, str):
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(filled_at.replace('Z', '+00:00'))
                time_str = dt.strftime("%I:%M:%S %p")
            except:
                time_str = filled_at
        else:
            time_str = str(filled_at)
        
        order_history.append({
            "order_id": order.get("order_id", ""),
            "symbol": order.get("symbol", ""),
            "side": order.get("side", ""),
            "quantity": order.get("quantity", 0),
            "fill_price": order.get("fill_price", 0.0),
            "status": order.get("status", ""),
            "filled_at": time_str,
            "slippage": 0.0  # Would calculate from order data
        })
    
    if order_history:
        st.dataframe(order_history, hide_index=True)
    else:
        st.info("No order history")
    
    # Execution Log Section
    st.header("📋 Execution Log")
    
    execution_log = [
        {"time": "10:30:15", "event": "Order submitted", "symbol": "TSLA", "order_id": "ORD-001"},
        {"time": "10:25:30", "event": "Order filled", "symbol": "AAPL", "order_id": "ORD-002", "fill_price": 150.25},
        {"time": "10:20:15", "event": "Order filled", "symbol": "MSFT", "order_id": "ORD-003", "fill_price": 380.50}
    ]
    
    for log_entry in execution_log:
        st.write(f"**{log_entry['time']}** - {log_entry['event']} - {log_entry['symbol']} ({log_entry.get('order_id', 'N/A')})")
        if 'fill_price' in log_entry:
            st.write(f"  Fill Price: ${log_entry['fill_price']:.2f}")
    
    # Fill Details Section
    st.header("📊 Fill Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Avg Slippage", "0.04%")
        st.metric("Fill Rate", "98.5%")
    
    with col2:
        st.metric("Avg Fill Time", "1.2s")
        st.metric("Total Orders", "45")
    
    with col3:
        st.metric("Filled Orders", "44")
        st.metric("Rejected Orders", "1")


def main():
    """Main execution view entry point."""
    render_execution_view()


if __name__ == "__main__":
    main()

