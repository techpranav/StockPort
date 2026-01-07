"""
Signal Interpreter UI Component

Displays signal interpretation in user-friendly format.
"""

import streamlit as st
from typing import Dict, Any

from services.interpreters.signal_translator import SignalTranslator


def render_signal_interpretation(
    symbol: str,
    analyzer_result: Dict[str, Any]
) -> None:
    """
    Render signal interpretation for a stock.
    
    Args:
        symbol: Stock symbol
        analyzer_result: Analysis result dictionary
    """
    translator = SignalTranslator()
    entry_signal = analyzer_result.get('entry_signals', {})
    
    if not entry_signal:
        st.warning(f"No entry signal available for {symbol}")
        return
    
    # Translate signal
    translation = translator.translate_signal(entry_signal)
    
    # Display in cards
    st.subheader(f"📊 Analysis for {symbol}")
    
    # Recommendation card
    st.info(f"**{translation['recommendation']}**")
    
    # Explanation
    st.write("**What this means:**")
    st.write(translation['explanation'])
    
    # Advice
    st.write("**What you should do:**")
    st.write(translation['advice'])
    
    # Risk and confidence
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Risk Level:**")
        st.write(translation['risk_level'])
    
    with col2:
        st.write("**Confidence:**")
        st.write(translation['confidence_text'])
    
    # Technical details (collapsible)
    with st.expander("📈 Technical Details (Advanced)"):
        st.json(entry_signal)

