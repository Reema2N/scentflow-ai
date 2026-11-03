"""Step 1: collect product and campaign details."""

import logging

import streamlit as st

from frontend.components.layout import centered_text
from frontend.services.campaign_input import (
    CampaignForm,
    build_initial_state,
    has_required_fields,
    parse_notes,
    sanitize_form,
    validate_form,
)
from frontend.services.workflow_client import start_campaign
from frontend.session import STEP_REVIEW

logger = logging.getLogger(__name__)


def _render_form() -> tuple[CampaignForm, bool]:
    """Render the campaign form and return its values and submit state."""
    with st.form(key="perfume_campaign_form"):
        st.markdown("### 🧪 ١. تفاصيل المنتج (Product)")
        product_name = st.text_input(
            "اسم العطر (Product Name) *",
            placeholder="مثال: إمبريال",
        )

        st.markdown("*النوتات العطرية (Fragrance Notes):*")
        col1, col2, col3 = st.columns(3)
        with col1:
            top_notes = st.text_input(
                "النوتات العليا (Top Notes) *",
                placeholder="مثال: برغموت، حمضيات",
            )
        with col2:
            middle_notes = st.text_input(
                "النوتات الوسطى (Middle Notes) *",
                placeholder="مثال: عنبر، ورد",
            )
        with col3:
            base_notes = st.text_input(
                "النوتات القاعدة (Base Notes) *",
                placeholder="مثال: عود، مسك",
            )

        description = st.text_area(
            "وصف العطر (Description) - (اختياري)",
            placeholder="مثال: عطر فاخر مستوحى من التراث السعودي الأصيل.",
        )

        st.divider()

        st.markdown("### 📣 ٢. تفاصيل الحملة التسويقية (Campaign)")
        occasion = st.text_input(
            "المناسبة (Occasion) *",
            placeholder="مثال: اليوم الوطني السعودي",
        )
        channels = st.multiselect(
            "قنوات النشر (Channels) *",
            options=["Instagram", "Email"],
            default=["Instagram", "Email"],
        )

        submitted = st.form_submit_button(label="🚀 بدء المعالجة وإنشاء المحتوى")

    form = CampaignForm(
        product_name=product_name,
        top_notes=parse_notes(top_notes),
        middle_notes=parse_notes(middle_notes),
        base_notes=parse_notes(base_notes),
        description=description,
        occasion=occasion,
        channels=channels,
    )
    return form, submitted


def _run_campaign(form: CampaignForm) -> bool:
    """Validate the form and run the workflow. Return True on success."""
    try:
        errors = validate_form(form)

        if errors:
            st.error("⚠️ بعض المدخلات غير صحيحة. يرجى تعديلها قبل بدء الحملة.")
            for error in errors:
                st.warning(error)
            return False

        with st.spinner("⏳ جاري ترجمة المدخلات وتجهيز سير العمل..."):
            initial_state = build_initial_state(form)

        with st.spinner("🤖 جاري توليد المحتوى التسويقي..."):
            thread_id, result = start_campaign(initial_state)

    except Exception:
        logger.exception("Campaign generation failed")
        st.error("⚠️ تعذر إنشاء الحملة. يرجى المحاولة مرة أخرى.")
        return False

    st.session_state.channels = [channel.lower() for channel in form.channels]
    st.session_state.thread_id = thread_id
    st.session_state.graph_result = result
    st.session_state.step = STEP_REVIEW
    return True


def render() -> None:
    centered_text("🌸 ScentFlow AI", tag="h1")
    centered_text("إعداد تفاصيل العطر والحملة التسويقية", tag="h3")
    centered_text("أدخل البيانات التالية للبدء في توليد المحتوى والتسويق المخصص.")

    form, submitted = _render_form()

    if not submitted:
        return

    if not has_required_fields(form):
        st.error("⚠️ يرجى تعبئة جميع الحقول المطلوبة (*)")
        return

    if _run_campaign(sanitize_form(form)):
        st.rerun()
