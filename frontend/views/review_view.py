"""Step 2: approve the generated content or request changes."""

import logging

import streamlit as st

from agents.input_validation_agent import validate_human_feedback
from frontend.components.content_cards import render_content_preview
from frontend.components.layout import centered_text
from frontend.services.campaign_input import sanitize_input
from frontend.services.translation import translate_to_en
from frontend.services.workflow_client import approve_campaign, request_revision
from frontend.session import STEP_FINAL, get_generated_content

logger = logging.getLogger(__name__)

APPROVE = "موافقة (Approve)"
REJECT = "رفض وتعديل (Reject)"


def _show_revision_notice() -> None:
    """Confirm a completed revision and reset the review controls."""
    if st.session_state.pop("revision_completed", False):
        st.session_state["human_decision"] = APPROVE
        st.session_state["human_feedback"] = ""
        st.session_state["human_target"] = "all"
        st.success("✅ تم تحديث المحتوى بناءً على ملاحظاتك!")


def _target_options(channels: list[str]) -> list[str]:
    options = ["all", "slogan"]
    options += [channel for channel in ("instagram", "email") if channel in channels]
    return options


def _submit_revision(feedback: str, target: str) -> None:
    """Validate human feedback and run the revision workflow."""
    if not feedback.strip():
        st.error("⚠️ يرجى كتابة ملاحظاتك قبل إعادة الإرسال.")
        return

    try:
        clean_feedback = sanitize_input(feedback)
        validation = validate_human_feedback(
            human_feedback=clean_feedback,
            target=target,
        )

        if not validation.is_valid:
            st.error("⚠️ يرجى كتابة ملاحظة واضحة توضّح التعديل المطلوب.")
            st.warning(validation.reason)
            if validation.suggested_example:
                st.info("💡 مثال: " + validation.suggested_example)
            return

        with st.spinner("🤖 جاري تحديث المحتوى بناءً على ملاحظاتك..."):
            st.session_state.graph_result = request_revision(
                thread_id=st.session_state.thread_id,
                feedback=translate_to_en(clean_feedback),
                target=target,
            )

    except Exception:
        logger.exception("Content revision failed")
        st.error("⚠️ تعذر تحديث المحتوى. يرجى المحاولة مرة أخرى.")
        return

    st.session_state.revision_completed = True
    st.rerun()


def _render_revision_form(channels: list[str]) -> None:
    feedback = st.text_area(
        "✏️ ما هي التعديلات التي ترغب بإضافتها؟ *",
        placeholder="مثال: اجعل النبرة أكثر إبداعاً وفخامة.",
        key="human_feedback",
    )
    target = st.selectbox(
        "🎯 أي جزء ترغب في تعديله؟",
        _target_options(channels),
        key="human_target",
    )

    if st.button("🔄 إعادة التوليد بناءً على الملاحظات"):
        _submit_revision(feedback, target)


def _render_approval() -> None:
    if not st.button("✅ اعتماد وإظهار النتائج النهائية"):
        return

    try:
        st.session_state.graph_result = approve_campaign(st.session_state.thread_id)
    except Exception:
        logger.exception("Campaign approval failed")
        st.error("⚠️ تعذر اعتماد المحتوى. يرجى المحاولة مرة أخرى.")
        return

    st.session_state.step = STEP_FINAL
    st.rerun()


def render() -> None:
    _show_revision_notice()

    centered_text("🤝 مراجعة المحتوى المُوَلَّد (Human Approval)", tag="h2")
    centered_text("يرجى الاطلاع على المحتوى الناتج وإبداء موافقتك أو طلب التعديل:")

    content = get_generated_content()
    channels = st.session_state.channels

    if content:
        render_content_preview(content, channels)

    st.divider()

    st.markdown("### 🎯 قرارك بخصوص المحتوى:")
    decision = st.radio(
        "هل توافق على المحتوى المولد؟",
        [APPROVE, REJECT],
        index=0,
        key="human_decision",
    )

    if decision == REJECT:
        _render_revision_form(channels)
    else:
        _render_approval()
