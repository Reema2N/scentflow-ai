"""ScentFlow AI Streamlit application."""

import sys
from pathlib import Path

# Streamlit adds frontend/ to the import path, not the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from config import LLM_API_KEY
from frontend.components.layout import load_styles
from frontend.session import (
    STEP_FINAL,
    STEP_INPUT,
    STEP_REVIEW,
    initialize_session,
)


def main() -> None:
    st.set_page_config(
        page_title="ScentFlow AI - Human in the Loop",
        page_icon="🌸",
        layout="centered",
    )
    load_styles()

    if not LLM_API_KEY:
        st.error("⚠️ لم يتم العثور على OPENAI_API_KEY. أضف المفتاح إلى ملف .env ثم أعد التشغيل.")
        st.stop()

    # The agents create their LLM clients on import, so the views
    # load only after the API key check.
    from frontend.views import final_view, input_view, review_view

    views = {
        STEP_INPUT: input_view,
        STEP_REVIEW: review_view,
        STEP_FINAL: final_view,
    }

    initialize_session()
    views[st.session_state.step].render()


main()
