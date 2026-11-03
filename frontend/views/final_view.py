"""Step 3: show the approved campaign."""

import streamlit as st

from frontend.components.content_cards import render_final_content
from frontend.components.layout import centered_text
from frontend.session import get_generated_content, reset_session


def render() -> None:
    centered_text("🎉 الحملة التسويقية النهائية المعتمدة", tag="h1")
    st.caption(
        "💡 يمكنك وضع مؤشر الفأرة فوق أي نص للضغط على أيقونة النسخ السريع (Copy)."
    )

    content = get_generated_content()

    if content:
        render_final_content(content, st.session_state.channels)

    st.divider()

    if st.button("➕ إنشاء حملة جديدة"):
        reset_session()
        st.rerun()
