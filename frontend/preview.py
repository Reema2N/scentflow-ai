"""Preview the campaign screens with sample content (no API key needed)."""

import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from frontend.components.content_cards import (
    render_content_preview,
    render_final_content,
)
from frontend.components.layout import centered_text, load_styles

SAMPLE_CONTENT = SimpleNamespace(
    slogan="عطر يروي حكاية الوطن",
    instagram_caption=(
        "في يومنا الوطني، نحتفي بالأصالة بعطر يجمع دفء العود ونعومة الورد "
        "وانتعاش البرغموت. ✨\n\n"
        "إمبريال رفيقك في كل لحظة فخر، بحضور يبقى في الذاكرة ورائحة تعبر "
        "عن جمال التراث السعودي. اكتشفه الآن واجعل احتفالك أكثر تميزًا."
    ),
    instagram_hashtags=["#اليوم_الوطني", "#عطور", "#إمبريال"],
    email_subject="احتفل باليوم الوطني مع عطر إمبريال",
    email_body=(
        "مرحبًا،\n\n"
        "بمناسبة اليوم الوطني السعودي، نقدم لك إمبريال، عطرًا يجمع البرغموت "
        "والورد والعود في تجربة فاخرة.\n\n"
        "اكتشف العطر الآن.\n\n"
        "فريق التسويق"
    ),
)
SAMPLE_CHANNELS = ["instagram", "email"]

st.set_page_config(page_title="ScentFlow AI - Preview", page_icon="🌸")
load_styles()

st.info("👀 معاينة بمحتوى تجريبي، بدون تشغيل الوكلاء.")
screen = st.radio("الصفحة", ["مراجعة المحتوى", "النتيجة النهائية"], horizontal=True)
st.divider()

if screen == "مراجعة المحتوى":
    centered_text("🤝 مراجعة المحتوى المُوَلَّد (Human Approval)", tag="h2")
    centered_text("يرجى الاطلاع على المحتوى الناتج وإبداء موافقتك أو طلب التعديل:")
    render_content_preview(SAMPLE_CONTENT, SAMPLE_CHANNELS)
else:
    centered_text("🎉 الحملة التسويقية النهائية المعتمدة", tag="h1")
    render_final_content(SAMPLE_CONTENT, SAMPLE_CHANNELS)
