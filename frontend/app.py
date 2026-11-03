import uuid
import html
import re
import streamlit as st

from deep_translator import GoogleTranslator
from langgraph.types import Command

from workflow.graph import graph
from agents.input_validation_agent import (validate_input, validate_human_feedback,)

# =====================================
# Page Configuration
# =====================================
st.set_page_config(
    page_title="ScentFlow AI - Human in the Loop",
    page_icon="🌸",
    layout="centered"
)
# =====================================
# CSS Styling
# =====================================
st.markdown(
    """
    <style>
    .stApp,
    .stApp * {
        direction: rtl !important;
        text-align: right !important;
    }
    .centered-title,
    .centered-title * {
        text-align: center !important;
    }
    div[data-baseweb="select"] {
        direction: rtl !important;
        text-align: right !important;
    }
    .stButton,
    div[st-eval-id] {
        text-align: right !important;
    }
    /* ================================
       Slogan Card
       ================================ */
    .slogan-card {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 20px;
        text-align: center !important;
        margin-bottom: 25px;
    }
    .slogan-text {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center !important;
        margin: 0;
    }
    /* ================================
       Instagram Card
       ================================ */
    .instagram-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 0;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .instagram-header {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        border-bottom: 1px solid #f0f0f0;
    }
    .instagram-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(
            45deg,
            #f09433,
            #e6683c,
            #dc2743,
            #cc2366,
            #bc1888
        );
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        margin-left: 10px;
    }
    .instagram-username {
        font-weight: bold;
        font-size: 14px;
        color: #262626;
    }
    .instagram-body {
        padding: 16px;
        font-size: 15px;
        line-height: 1.6;
        color: #262626;
        white-space: pre-wrap;
    }
    .instagram-hashtags {
        color: #00376b;
        font-weight: 500;
        margin-top: 10px;
        direction: ltr !important;
        text-align: right !important;
    }
    /* ================================
       Email Card
       ================================ */
    .email-card {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .email-header {
        background-color: #f3f4f6;
        padding: 12px 16px;
        border-bottom: 1px solid #e5e7eb;
        font-size: 14px;
    }
    .email-subject {
        font-size: 16px;
        font-weight: bold;
        color: #111827;
        margin-bottom: 4px;
    }
    .email-meta {
        color: #6b7280;
        font-size: 13px;
    }
    .email-body {
        padding: 20px;
        font-size: 15px;
        line-height: 1.7;
        color: #374151;
        white-space: pre-wrap;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================
# Sensitive Data Sanitization
# =====================================
def sanitize_input(text: str) -> str:
    """
    Redacts common sensitive data before the input
    is sent to validation, translation, tracing, or LLMs.
    """
    if not text:
        return text

    # Email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[REDACTED_EMAIL]",
        text,
    )

    # Phone numbers
    text = re.sub(
        r"(?<!\w)(?:\+?\d[\d\s\-()]{7,}\d)(?!\w)",
        "[REDACTED_PHONE]",
        text,
    )

    # Customer / User / Client IDs
    text = re.sub(
        r"\b(?:CUST|CUSTOMER|USER|CLIENT)[-_]?[A-Za-z0-9-]+\b",
        "[REDACTED_ID]",
        text,
        flags=re.IGNORECASE,
    )

    return text
# =====================================
# Translation
# =====================================
def translate_to_en(
    text: str
) -> str:
    if not text or not text.strip():
        return text
    try:
        return GoogleTranslator(
            source="auto",
            target="en"
        ).translate(text)
    except Exception:
        return text
# =====================================
# Session State
# =====================================
if "step" not in st.session_state:
    st.session_state.step = "input"
if "graph_result" not in st.session_state:
    st.session_state.graph_result = None
if "channels" not in st.session_state:
    st.session_state.channels = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None


# =========================================================
# المرحلة الأولى: واجهة إدخال البيانات
# =========================================================
if st.session_state.step == "input":
    st.markdown(
        """
        <h1 class='centered-title'>
        🌸 ScentFlow AI
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <h3 class='centered-title'>
        إعداد تفاصيل العطر والحملة التسويقية
        </h3>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <p class='centered-title'>
        أدخل البيانات التالية للبدء في توليد المحتوى
        والتسويق المخصص.
        </p>
        """,
        unsafe_allow_html=True
    )
    with st.form(
        key="perfume_campaign_form"
    ):
        # =====================================
        # Product
        # =====================================
        st.markdown(
            "### 🧪 ١. تفاصيل المنتج (Product)"
        )
        product_name = st.text_input(
            "اسم العطر (Product Name) *",
            placeholder="مثال: إمبريال"
        )
        st.markdown(
            "*النوتات العطرية (Fragrance Notes):*"
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            top_notes = st.text_input(
                "النوتات العليا (Top Notes) *",
                placeholder="مثال: برغموت، حمضيات"
            )
        with col2:
            middle_notes = st.text_input(
                "النوتات الوسطى (Middle Notes) *",
                placeholder="مثال: عنبر، ورد"
            )
        with col3:
            base_notes = st.text_input(
                "النوتات القاعدة (Base Notes) *",
                placeholder="مثال: عود، مسك"
            )
        description = st.text_area(
            "وصف العطر (Description) - (اختياري)",
            placeholder=(
                "مثال: عطر فاخر مستوحى من "
                "التراث السعودي الأصيل."
            )
        )
        st.divider()
        # =====================================
        # Campaign
        # =====================================
        st.markdown(
            "### 📣 ٢. تفاصيل الحملة التسويقية (Campaign)"
        )
        
        occasion = st.text_input(
            "المناسبة (Occasion) *",
            placeholder="مثال: اليوم الوطني السعودي"
        )
        channels = st.multiselect(
            "قنوات النشر (Channels) *",
            options=[
                "Instagram",
                "Email"
            ],
            default=[
                "Instagram",
                "Email"
            ]
        )
        submit_button = st.form_submit_button(
            label="🚀 بدء المعالجة وإنشاء المحتوى"
        )
    # =====================================================
    # Submit
    # =====================================================
    if submit_button:
        # =====================================
        # Required Fields
        # =====================================
        if (
            not product_name
            or not top_notes.strip()
            or not middle_notes.strip()
            or not base_notes.strip()
            or not occasion
            or not channels
        ):
            st.error(
                "⚠️ يرجى تعبئة جميع الحقول المطلوبة (*)"
            )
        else:
            # =====================================
            # Prepare Notes
            # =====================================
            top_list = [
                n.strip()
                for n in top_notes.split(",")
                if n.strip()
            ]
            middle_list = [
                n.strip()
                for n in middle_notes.split(",")
                if n.strip()
            ]
            base_list = [
                n.strip()
                for n in base_notes.split(",")
                if n.strip()
            ]

            # =====================================
            # Sanitize User Input
            # =====================================
            product_name = sanitize_input(product_name)
            description = sanitize_input(description)
            occasion = sanitize_input(occasion)

            top_list = [
                sanitize_input(note)
                for note in top_list
            ]

            middle_list = [
                sanitize_input(note)
                for note in middle_list
            ]

            base_list = [
                sanitize_input(note)
                for note in base_list
            ]
            # =====================================
            # Input Validation
            # =====================================
            validation_errors = []

            # =====================================
            # Product Name
            # =====================================
            product_name_validation = validate_input(
                user_input=product_name,
                field="product name"
            )

            if not product_name_validation.is_valid:
                validation_errors.append(
                    (
                        "❌ اسم العطر: "
                        f"{product_name_validation.reason}"
                    )
                )


            # =====================================
            # Description
            # =====================================
            if description.strip():
                description_validation = validate_input(
                    user_input=description,
                    field="description"
                )

                if not description_validation.is_valid:
                    validation_errors.append(
                        (
                            "❌ وصف العطر: "
                            f"{description_validation.reason}"
                        )
                    )
            # =====================================
            # Top Notes
            # =====================================
            for note in top_list:
                validation_result = validate_input(
                    user_input=note,
                    field="fragrance note"
                )
                if not validation_result.is_valid:
                    validation_errors.append(
                        (
                            f"❌ النوتة العليا "
                            f"'{note}': "
                            f"{validation_result.reason}"
                        )
                    )
            # =====================================
            # Middle Notes
            # =====================================
            for note in middle_list:
                validation_result = validate_input(
                    user_input=note,
                    field="fragrance note"
                )
                if not validation_result.is_valid:
                    validation_errors.append(
                        (
                            f"❌ النوتة الوسطى "
                            f"'{note}': "
                            f"{validation_result.reason}"
                        )
                    )
            # =====================================
            # Base Notes
            # =====================================
            for note in base_list:
                validation_result = validate_input(
                    user_input=note,
                    field="fragrance note"
                )
                if not validation_result.is_valid:
                    validation_errors.append(
                        (
                            f"❌ النوتة القاعدية "
                            f"'{note}': "
                            f"{validation_result.reason}"
                        )
                    )
            
            # =====================================
            # Occasion
            # =====================================
            occasion_validation = validate_input(
                user_input=occasion,
                field="occasion"
            )
            if not occasion_validation.is_valid:
                validation_errors.append(
                    (
                        "❌ المناسبة: "
                        f"{occasion_validation.reason}"
                    )
                )
            # =====================================
            # Stop Workflow If Invalid
            # =====================================
            if validation_errors:
                st.error(
                    "⚠️ بعض المدخلات غير صحيحة. "
                    "يرجى تعديلها قبل بدء الحملة."
                )
                for error in validation_errors:
                    st.warning(error)
            # =====================================
            # Continue If Valid
            # =====================================
            else:
                with st.spinner(
                    "⏳ جاري ترجمة المدخلات وتجهيز "
                    "سير العمل..."
                ):
                    selected_channels = channels

                    st.session_state.channels = [
                        channel.lower()
                        for channel in channels
                    ]
                    # =====================================
                    # User Context
                    # =====================================
                    user_context = {
                        "product": {
                            "name": product_name,
                            "fragrance_notes": {
                                "top_notes": [
                                    translate_to_en(note)
                                    for note in top_list
                                ],
                                "middle_notes": [
                                    translate_to_en(note)
                                    for note in middle_list
                                ],
                                "base_notes": [
                                    translate_to_en(note)
                                    for note in base_list
                                ],
                            },
                            "description": (
                                translate_to_en(
                                    description
                                )
                                if description
                                else ""
                            ),
                        },
                        "campaign": {
            
                            "occasion": translate_to_en(
                                occasion
                            ),
                            "channels": selected_channels,
                        },
                    }
                    # =====================================
                    # Initial State
                    # =====================================
                    initial_state = {
                        "user_context": user_context,
                        "revision_count": 0,
                        "max_revisions": 3,
                    }
                # =====================================
                # Run Workflow
                # =====================================
                with st.spinner(
                    "🤖 جاري توليد المحتوى التسويقي..."
                ):
                    st.session_state.thread_id = str(
                        uuid.uuid4()
                    )

                    config = {
                        "configurable": {
                            "thread_id": st.session_state.thread_id
                        }
                    }

                    st.session_state.graph_result = graph.invoke(
                        initial_state,
                        config=config
                    )

                    st.session_state.step = (
                        "review"
                    )
                    st.rerun()
# =========================================================
# Human-in-the-Loop
# =========================================================
elif st.session_state.step == "review":
    if st.session_state.pop("revision_completed", False):
        st.session_state["human_decision"] = "موافقة (Approve)"
        st.session_state["human_feedback"] = ""
        st.session_state["human_target"] = "all"

        st.success("✅ تم تحديث المحتوى بناءً على ملاحظاتك!")

        st.markdown(
            """
            <script>
                window.parent.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });
            </script>
            """,
            unsafe_allow_html=True
        )
    st.markdown(
        """
        <h2 class='centered-title'>
        🤝 مراجعة المحتوى المُوَلَّد
        (Human Approval)
        </h2>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <p class='centered-title'>
        يرجى الاطلاع على المحتوى الناتج وإبداء
        موافقتك أو طلب التعديل:
        </p>
        """,
        unsafe_allow_html=True
    )
    result = st.session_state.graph_result
    content = (
        result.get("generated_content")
        if isinstance(result, dict)
        else None
    )
    active_channels = st.session_state.get(
        "channels",
        []
    )
    # =====================================
    # Display Generated Content
    # =====================================
    if content:
        # =====================================
        # Slogan
        # =====================================
        safe_slogan = html.escape(content.slogan)
        st.markdown(
            f"""
            <div class="slogan-card">
                <div style="
                    font-size: 14px;
                    color: #6c757d;
                    margin-bottom: 6px;
                ">
                    ✨ الشعار الإعلاني المقترح ✨
                </div>
                <div class="slogan-text">
                    "{safe_slogan}"
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        # =====================================
        # Instagram
        # =====================================
        if (
            "instagram" in active_channels
            and getattr(
                content,
                "instagram_caption",
                None
            )
        ):
            hashtags_str = (
                " ".join(
                    content.instagram_hashtags
                )
                if getattr(
                    content,
                    "instagram_hashtags",
                    None
                )
                else ""
            )

            safe_instagram_caption = html.escape(
                content.instagram_caption
            )

            safe_hashtags = html.escape(
                hashtags_str
            )

            st.markdown(
                f"""
                <div class="instagram-card">
                    <div class="instagram-header">
                        <div class="instagram-avatar">
                            🌸
                        </div>
                        <div class="instagram-username">
                            ScentFlow Brand
                        </div>
                    </div>
                    <div class="instagram-body">
                        {safe_instagram_caption}
                        <div class="instagram-hashtags">
                            {safe_hashtags}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        # =====================================
        # Email
        # =====================================
        if (
            "email" in active_channels
            and getattr(
                content,
                "email_body",
                None
            )
        ):
            email_subject = getattr(
                content,
                "email_subject",
                "بدون عنوان"
            )

            safe_email_subject = html.escape(
                email_subject
            )

            safe_email_body = html.escape(
                content.email_body
            )
            st.markdown(
                f"""
                <div class="email-card">
                    <div class="email-header">
                        <div class="email-subject">
                            📧 {safe_email_subject}
                        </div>
                        <div class="email-meta">
                            من: فريق التسويق
                            &lt;newsletter@scentflow.com&gt;
                        </div>
                    </div>
                    <div class="email-body">
                        {safe_email_body}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    st.divider()
    # =====================================
    # Human Decision
    # =====================================
    st.markdown(
        "### 🎯 قرارك بخصوص المحتوى:"
    )
    decision = st.radio(
        "هل توافق على المحتوى المولد؟",
        [
            "موافقة (Approve)",
            "رفض وتعديل (Reject)"
        ],
        index=0,
        key="human_decision"
    )
    # =====================================================
    # REJECT
    # =====================================================
    if decision == "رفض وتعديل (Reject)":
        feedback = st.text_area(
            "✏️ ما هي التعديلات التي ترغب بإضافتها؟ *",
            placeholder="مثال: اجعل النبرة أكثر إبداعاً وفخامة.",
            key="human_feedback"
        )
        # =====================================
        # Target Options
        # =====================================
        target_options = [
            "all",
            "slogan"
        ]
        if "instagram" in active_channels:
            target_options.append(
                "instagram"
            )
        if "email" in active_channels:
            target_options.append(
                "email"
            )
        target = st.selectbox(
            "🎯 أي جزء ترغب في تعديله؟",
            target_options,
            key="human_target"
        )
        # =====================================
        # Revision Button
        # =====================================
        if st.button(
            "🔄 إعادة التوليد بناءً على الملاحظات"
        ):
            # =====================================
            # Empty Feedback
            # =====================================
            if not feedback.strip():
                st.error(
                    "⚠️ يرجى كتابة ملاحظاتك قبل "
                    "إعادة الإرسال."
                )
            else:
                # =====================================
                # Validate Human Feedback
                # =====================================
                feedback_validation = (
                    validate_human_feedback(
                        human_feedback=feedback,
                        target=target,
                    )
                )
                # =====================================
                # Invalid Feedback
                # =====================================
                if not feedback_validation.is_valid:
                    st.error(
                        "⚠️ يرجى كتابة ملاحظة واضحة "
                        "توضّح التعديل المطلوب."
                    )
                    st.warning(
                        feedback_validation.reason
                    )
                    if (
                        feedback_validation
                        .suggested_example
                    ):
                        st.info(
                            "💡 مثال: "
                            + feedback_validation
                            .suggested_example
                        )
                # =====================================
                # Valid Feedback
                # =====================================
                else:
                    # =====================================
                    # Translate After Validation
                    # =====================================
                    translated_feedback = (
                        translate_to_en(
                            feedback
                        )
                    )
                    review_data = {
                        "decision": "reject",
                        "feedback": translated_feedback,
                        "target": target,
                    }

                    config = {
                        "configurable": {
                            "thread_id": st.session_state.thread_id
                        }
                    }

                    with st.spinner(
                        "🤖 جاري تحديث المحتوى "
                        "بناءً على ملاحظاتك..."
                    ):
                        st.session_state.graph_result = graph.invoke(
                            Command(resume=review_data),
                            config=config
                        )

                        st.session_state.revision_completed = True

                        st.rerun()
    # =====================================================
    # APPROVE
    # =====================================================
    else:
        if st.button(
            "✅ اعتماد وإظهار النتائج النهائية"
        ):
            review_data = {
                "decision": "approve",
                "feedback": None,
                "target": None,
            }

            config = {
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }

            st.session_state.graph_result = graph.invoke(
                Command(resume=review_data),
                config=config
            )

            st.session_state.step = "final"
            st.rerun()
# =========================================================
# المرحلة الثالثة: النتائج النهائية
# =========================================================
elif st.session_state.step == "final":
    st.markdown(
        """
        <h1 class='centered-title'>
        🎉 الحملة التسويقية النهائية المعتمدة
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.caption(
        "💡 يمكنك وضع مؤشر الفأرة فوق أي نص "
        "للضغط على أيقونة النسخ السريع (Copy)."
    )
    result = st.session_state.graph_result
    final_content = (
        result.get("generated_content")
        if isinstance(result, dict)
        else None
    )
    active_channels = st.session_state.get(
        "channels",
        []
    )
    # =====================================
    # Final Content
    # =====================================
    if final_content:
        # =====================================
        # Final Slogan
        # =====================================
        st.subheader(
            "✨ الشعار الإعلاني المعتمد"
        )
        st.code(
            final_content.slogan,
            language=None
        )
        # =====================================
        # Final Instagram
        # =====================================
        if (
            "instagram" in active_channels
            and getattr(
                final_content,
                "instagram_caption",
                None
            )
        ):
            st.subheader(
                "📱 محتوى الإنستجرام النهائي"
            )

            # تجهيز الكابشن والهاشتاقات
            caption_text = final_content.instagram_caption.strip()
            hashtags_list = getattr(final_content, "instagram_hashtags", None)

            # دمج الهاشتاقات إذا كانت موجودة
            if hashtags_list:
                if isinstance(hashtags_list, list):
                    hashtags_text = " ".join(hashtags_list)
                else:
                    hashtags_text = str(hashtags_list).strip()
                
                # دمج الكابشن والهاشتاقات مع أسطر فارغة بينهما
                full_instagram_post = f"{caption_text}\n\n\n{hashtags_text}"
            else:
                full_instagram_post = caption_text

            # عرض المنشور كاملاً في صندوق واحد مع زر نسخ تلقائي
            st.code(
                full_instagram_post,
                language=None
            )
        # =====================================
        # Final Email
        # =====================================
        if (
            "email" in active_channels
            and getattr(
                final_content,
                "email_body",
                None
            )
        ):
            st.subheader(
                "📧 البريد الإلكتروني النهائي"
            )
            email_subject = getattr(
                final_content,
                "email_subject",
                ""
            )
            if email_subject:
                st.markdown(
                    "*عنوان الرسالة (Subject):*"
                )
                st.code(
                    email_subject,
                    language=None
                )
            st.markdown(
                "*نص الرسالة (Email Body):*"
            )
            st.code(
                final_content.email_body,
                language=None
            )
    st.divider()
    # =====================================
    # New Campaign
    # =====================================
    if st.button(
        "➕ إنشاء حملة جديدة"
    ):
        st.session_state.step = "input"
        st.session_state.graph_result = None
        st.session_state.thread_id = None
        st.session_state.channels = []
        st.rerun()
