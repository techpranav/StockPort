"""
Educational Tooltips UI Component

Provides educational content and tooltips for non-trading users.
"""

import streamlit as st


def render_educational_content() -> None:
    """Render educational content section."""
    st.subheader("📚 Learn About Stock Analysis")
    
    # Key concepts
    with st.expander("💡 What is Technical Analysis?"):
        st.write("""
        Technical analysis is a method of evaluating stocks by analyzing statistical trends 
        gathered from trading activity, such as price movement and volume. It helps predict 
        future price movements based on historical patterns.
        """)
    
    with st.expander("📊 Understanding Signals"):
        st.write("""
        - **Strong Buy**: Multiple indicators suggest this is an excellent buying opportunity
        - **Buy**: Positive signals indicate a good time to buy
        - **Watch**: Mixed signals - wait for clearer direction
        - **Avoid**: Negative signals suggest staying away
        """)
    
    with st.expander("⚠️ Understanding Risk"):
        st.write("""
        - **Low Risk**: Stock price is relatively stable, less chance of big losses
        - **Medium Risk**: Moderate price swings, invest cautiously
        - **High Risk**: High volatility, only invest what you can afford to lose
        """)
    
    with st.expander("🎯 Key Terms Explained"):
        st.write("""
        - **Entry Price**: Suggested price to buy the stock
        - **Stop Loss**: Price at which to sell to limit losses
        - **Take Profit**: Price at which to sell to lock in gains
        - **Confidence**: How sure the analysis is about the recommendation
        - **Volatility**: How much the stock price fluctuates
        """)
    
    with st.expander("💼 Portfolio Tips"):
        st.write("""
        1. **Diversify**: Don't put all your money in one stock
        2. **Set Limits**: Always use stop-loss to protect your capital
        3. **Be Patient**: Don't make hasty decisions based on short-term movements
        4. **Stay Informed**: Regularly check your portfolio and market conditions
        5. **Risk Management**: Only invest money you can afford to lose
        """)


def render_tooltip(term: str, explanation: str) -> None:
    """
    Render a tooltip for a term.
    
    Args:
        term: Term to explain
        explanation: Explanation text
    """
    st.help(explanation)

