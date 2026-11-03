"""Streamlit session state shared by the application views."""

import streamlit as st

STEP_INPUT = "input"
STEP_REVIEW = "review"
STEP_FINAL = "final"

_DEFAULTS = {
    "step": STEP_INPUT,
    "graph_result": None,
    "channels": [],
    "thread_id": None,
}


def initialize_session() -> None:
    """Create any missing session values."""
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session() -> None:
    """Return to the input step and clear the current campaign."""
    for key, value in _DEFAULTS.items():
        st.session_state[key] = value


def get_generated_content():
    """Return the generated content from the latest workflow result."""
    result = st.session_state.graph_result
    return result.get("generated_content") if isinstance(result, dict) else None
