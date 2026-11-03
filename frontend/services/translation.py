"""Translate user text to English for the agents."""

from deep_translator import GoogleTranslator


def translate_to_en(text: str) -> str:
    """Translate text to English, keeping the original if translation fails."""
    if not text or not text.strip():
        return text

    try:
        return GoogleTranslator(source="auto", target="en").translate(text)
    except Exception:
        return text
