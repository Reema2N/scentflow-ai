"""Shared page styling and headings."""

from pathlib import Path

import streamlit as st

STYLES_PATH = Path(__file__).resolve().parent.parent / "assets" / "styles.css"


def load_styles() -> None:
    """Apply the application stylesheet."""
    css = STYLES_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def centered_text(text: str, tag: str = "p") -> None:
    """Render centered text using the given HTML tag."""
    st.markdown(
        f"<{tag} class='centered-title'>{text}</{tag}>",
        unsafe_allow_html=True,
    )
