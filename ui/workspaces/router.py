"""
Workspace Router

Workspace routing logic with context memory for preserving user context
across workspace navigation.
"""

import streamlit as st
from typing import Dict, Any, Optional


# Context keys for session state
CONTEXT_KEYS = {
    'symbol': 'active_symbol',
    'strategy': 'active_strategy_id',
    'signal': 'active_signal_id',
    'order': 'active_order_id'
}


def get_active_workspace() -> str:
    """
    Get the currently active workspace.
    
    Returns:
        Active workspace ID
    """
    # Check query params first
    try:
        query_params = st.query_params
        if 'workspace' in query_params:
            workspace = query_params['workspace']
            if workspace in ['insight', 'discover', 'decide', 'execute', 'review']:
                st.session_state.active_workspace = workspace
                return workspace
    except Exception:
        # Fallback if query_params not available
        pass
    
    # Fall back to session state
    return st.session_state.get('active_workspace', 'insight')


def set_active_workspace(workspace_id: str) -> None:
    """
    Set the active workspace.
    
    Args:
        workspace_id: Workspace ID to activate
    """
    if workspace_id in ['insight', 'discover', 'decide', 'execute', 'review']:
        st.session_state.active_workspace = workspace_id


def get_active_context() -> Dict[str, Any]:
    """
    Get active context (symbol, strategy, signal, order).
    
    Returns:
        Dictionary with active context
    """
    return {
        'symbol': st.session_state.get(CONTEXT_KEYS['symbol']),
        'strategy': st.session_state.get(CONTEXT_KEYS['strategy']),
        'signal': st.session_state.get(CONTEXT_KEYS['signal']),
        'order': st.session_state.get(CONTEXT_KEYS['order'])
    }


def set_active_context(
    symbol: Optional[str] = None,
    strategy: Optional[str] = None,
    signal: Optional[str] = None,
    order: Optional[str] = None
) -> None:
    """
    Set active context.
    
    Args:
        symbol: Active symbol
        strategy: Active strategy ID
        signal: Active signal ID
        order: Active order ID
    """
    if symbol:
        st.session_state[CONTEXT_KEYS['symbol']] = symbol
    if strategy:
        st.session_state[CONTEXT_KEYS['strategy']] = strategy
    if signal:
        st.session_state[CONTEXT_KEYS['signal']] = signal
    if order:
        st.session_state[CONTEXT_KEYS['order']] = order


def clear_context() -> None:
    """Clear active context."""
    for key in CONTEXT_KEYS.values():
        if key in st.session_state:
            del st.session_state[key]


def restore_context() -> Dict[str, Any]:
    """
    Restore context from session state.
    
    Returns:
        Dictionary with restored context
    """
    return get_active_context()

