"""
Scanner View

Monitor scanner activity and opportunities.
"""

import streamlit as st
from typing import List, Dict, Any
from datetime import datetime

from utils.debug_utils import DebugUtils


def render_scanner_view():
    """
    Render the scanner view.
    
    Shows:
    - Scanner status
    - Opportunity stream
    - Filters
    - Opportunity details
    """
    st.title("🔍 Market Scanner")
    
    # Scanner Status Section
    st.header("Scanner Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        scanner_active = st.checkbox("Scanner Active", value=True)
        st.write("🟢 Active" if scanner_active else "🔴 Inactive")
    
    with col2:
        scan_frequency = st.selectbox(
            "Scan Frequency",
            ["Every 5 minutes", "Every 15 minutes", "Every 30 minutes"],
            key="scan_frequency"
        )
    
    with col3:
        st.metric("Last Scan", "10:30 AM")
        st.metric("Opportunities Found", "15")
    
    # Filters Section
    st.header("Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sector_filter = st.multiselect(
            "Sector",
            ["Technology", "Healthcare", "Finance", "Energy", "Consumer"],
            key="sector_filter"
        )
    
    with col2:
        min_score = st.slider("Min Score", 0, 100, 70, key="min_score")
    
    with col3:
        min_volume = st.number_input(
            "Min Volume ($)",
            min_value=0,
            value=500000,
            step=100000,
            key="min_volume"
        )
    
    with col4:
        market_cap_filter = st.selectbox(
            "Market Cap",
            ["All", "Large Cap", "Mid Cap", "Small Cap"],
            key="market_cap_filter"
        )
    
    # Opportunity Stream Section
    st.header("📊 Opportunity Stream")
    
    # Sample opportunities
    opportunities = [
        {
            "symbol": "AAPL",
            "timestamp": "10:30:15 AM",
            "price": 150.25,
            "volume": 1500000,
            "score": 85,
            "sector": "Technology",
            "source": "market_scanner",
            "indicators": {
                "sma_20": 149.50,
                "sma_50": 148.00,
                "rsi": 65,
                "macd": 0.5
            }
        },
        {
            "symbol": "MSFT",
            "timestamp": "10:30:12 AM",
            "price": 380.50,
            "volume": 2000000,
            "score": 78,
            "sector": "Technology",
            "source": "market_scanner",
            "indicators": {
                "sma_20": 378.00,
                "sma_50": 375.00,
                "rsi": 58,
                "macd": 0.3
            }
        },
        {
            "symbol": "GOOGL",
            "timestamp": "10:30:08 AM",
            "price": 142.75,
            "volume": 1200000,
            "score": 72,
            "sector": "Technology",
            "source": "market_scanner",
            "indicators": {
                "sma_20": 141.50,
                "sma_50": 140.00,
                "rsi": 55,
                "macd": 0.2
            }
        }
    ]
    
    # Filter opportunities
    filtered_opportunities = opportunities
    if sector_filter:
        filtered_opportunities = [
            opp for opp in filtered_opportunities
            if opp["sector"] in sector_filter
        ]
    filtered_opportunities = [
        opp for opp in filtered_opportunities
        if opp["score"] >= min_score
    ]
    
    # Display opportunities
    for opp in filtered_opportunities:
        with st.expander(f"{opp['symbol']} - Score: {opp['score']} - ${opp['price']:.2f}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Timestamp:** {opp['timestamp']}")
                st.write(f"**Sector:** {opp['sector']}")
                st.write(f"**Volume:** ${opp['volume']:,.0f}")
                st.write(f"**Source:** {opp['source']}")
            
            with col2:
                st.write("**Indicators:**")
                for indicator, value in opp['indicators'].items():
                    st.write(f"- {indicator}: {value}")
            
            if st.button(f"View Details", key=f"view_{opp['symbol']}"):
                # Show explanation if available
                from backend.explainability import ExplainerEngine
                from models.opportunity import Opportunity
                from models.strategy_signal import StrategySignal
                from models.trading_decision import TradingDecision
                from datetime import datetime
                
                explainer = ExplainerEngine()
                
                # Create mock decision for explanation
                opportunity_obj = Opportunity(
                    symbol=opp['symbol'],
                    price=opp['price'],
                    volume=opp['volume'],
                    timestamp=datetime.now(),
                    sector=opp.get('sector', 'Unknown'),
                    market_cap=opp.get('market_cap', 0),
                    indicators=opp.get('indicators', {})
                )
                
                signal = StrategySignal(
                    signal_id=f"signal_{opp['symbol']}",
                    strategy_id="trend_following_v1",
                    opportunity=opportunity_obj,
                    score=opp['score'],
                    entry_price=opp['price'],
                    stop_loss=opp['price'] * 0.95,
                    take_profit=opp['price'] * 1.10,
                    confidence=opp['score'] / 100.0,
                    timestamp=datetime.now()
                )
                
                decision_dict = {
                    'symbol': opp['symbol'],
                    'decision': 'APPROVE',
                    'signal': {
                        'strategy_id': 'trend_following_v1',
                        'score': opp['score'],
                        'confidence': opp['score'] / 100.0,
                        'entry_price': opp['price'],
                        'stop_loss': opp['price'] * 0.95,
                        'take_profit': opp['price'] * 1.10,
                        'conditions': []
                    },
                    'risk_amount': opp['price'] * 10 * 0.05,
                    'risk_percent': 0.5,
                    'reward_amount': opp['price'] * 10 * 0.10,
                    'risk_reward_ratio': 2.0,
                    'entry_price': opp['price']
                }
                
                explanation = explainer.explain_decision(decision_dict)
                
                st.subheader(f"📊 Explanation for {opp['symbol']}")
                
                # Entry reasoning
                st.markdown("**Why this trade?**")
                st.info(explanation['explanation'].get('entry_reasoning', 'No explanation available'))
                
                # Risk justification
                st.markdown("**Risk justification:**")
                st.info(explanation['explanation'].get('risk_justification', 'No risk justification available'))
                
                # Invalidation conditions
                st.markdown("**What could invalidate this trade?**")
                invalidation = explanation['explanation'].get('invalidation_conditions', [])
                if invalidation:
                    for condition in invalidation[:5]:  # Top 5
                        st.write(f"• {condition}")
                
                # Confidence and uncertainty
                col1, col2 = st.columns(2)
                with col1:
                    confidence = explanation.get('confidence', 0.0)
                    st.metric("Confidence", f"{confidence:.1%}")
                    st.progress(confidence)
                
                with col2:
                    uncertainty = explanation.get('uncertainty', {})
                    total_uncertainty = uncertainty.get('total_uncertainty', 0.0) if isinstance(uncertainty, dict) else 0.0
                    st.metric("Uncertainty", f"{total_uncertainty:.1%}")
                    st.progress(total_uncertainty)
    
    # Pre-filter Stats Section
    st.header("📈 Pre-filter Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Avg Volume", "$1.5M")
        st.metric("Avg Price", "$125.00")
    
    with col2:
        st.metric("Avg Market Cap", "$500M")
        st.metric("Avg Score", "75")
    
    with col3:
        st.metric("Sectors Scanned", "5")
        st.metric("Symbols Scanned", "500")


def main():
    """Main scanner view entry point."""
    render_scanner_view()


if __name__ == "__main__":
    main()

