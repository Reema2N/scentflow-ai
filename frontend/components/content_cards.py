"""Display generated campaign content."""

import html

import streamlit as st


def _safe_text(text: str) -> str:
    """
    Escape model output for HTML and keep its line breaks.

    Card HTML stays on one line because blank lines end an
    HTML block in Markdown and expose the raw tags.
    """
    normalized = text.replace("\r\n", "\n").strip()
    return html.escape(normalized).replace("\n", "<br>")


def _render_html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def _hashtags_text(hashtags) -> str:
    if not hashtags:
        return ""
    if isinstance(hashtags, list):
        return " ".join(hashtags)
    return str(hashtags).strip()


def _render_slogan_card(slogan: str) -> None:
    _render_html(
        '<div class="slogan-card">'
        '<div style="font-size: 14px; color: #6c757d; margin-bottom: 6px;">'
        "✨ الشعار الإعلاني المقترح ✨"
        "</div>"
        f'<div class="slogan-text">"{_safe_text(slogan)}"</div>'
        "</div>"
    )


def _render_instagram_card(caption: str, hashtags) -> None:
    _render_html(
        '<div class="instagram-card">'
        '<div class="instagram-header">'
        '<div class="instagram-avatar">🌸</div>'
        '<div class="instagram-username">ScentFlow Brand</div>'
        "</div>"
        '<div class="instagram-body">'
        f"{_safe_text(caption)}"
        f'<div class="instagram-hashtags">{_safe_text(_hashtags_text(hashtags))}</div>'
        "</div>"
        "</div>"
    )


def _render_email_card(subject: str | None, body: str) -> None:
    _render_html(
        '<div class="email-card">'
        '<div class="email-header">'
        f'<div class="email-subject">📧 {_safe_text(subject or "بدون عنوان")}</div>'
        '<div class="email-meta">'
        "من: فريق التسويق &lt;newsletter@scentflow.com&gt;"
        "</div>"
        "</div>"
        f'<div class="email-body">{_safe_text(body)}</div>'
        "</div>"
    )


def render_content_preview(content, channels: list[str]) -> None:
    """Show styled cards for human review."""
    _render_slogan_card(content.slogan)

    if "instagram" in channels and content.instagram_caption:
        _render_instagram_card(content.instagram_caption, content.instagram_hashtags)

    if "email" in channels and content.email_body:
        _render_email_card(content.email_subject, content.email_body)


def render_final_content(content, channels: list[str]) -> None:
    """Show approved content in copyable blocks."""
    st.subheader("✨ الشعار الإعلاني المعتمد")
    st.code(content.slogan, language=None)

    if "instagram" in channels and content.instagram_caption:
        st.subheader("📱 محتوى الإنستجرام النهائي")

        post = content.instagram_caption.strip()
        hashtags = _hashtags_text(content.instagram_hashtags)
        if hashtags:
            post = f"{post}\n\n\n{hashtags}"

        st.code(post, language=None)

    if "email" in channels and content.email_body:
        st.subheader("📧 البريد الإلكتروني النهائي")

        if content.email_subject:
            st.markdown("*عنوان الرسالة (Subject):*")
            st.code(content.email_subject, language=None)

        st.markdown("*نص الرسالة (Email Body):*")
        st.code(content.email_body, language=None)
