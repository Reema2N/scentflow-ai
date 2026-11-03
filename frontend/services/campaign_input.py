"""Prepare, validate, and package the campaign form input."""

import re
from dataclasses import dataclass

from agents.input_validation_agent import validate_input
from frontend.services.translation import translate_to_en

MAX_AUTOMATIC_REVISIONS = 3


@dataclass
class CampaignForm:
    """Values entered in the campaign form."""

    product_name: str
    top_notes: list[str]
    middle_notes: list[str]
    base_notes: list[str]
    description: str
    occasion: str
    channels: list[str]


def parse_notes(raw_notes: str) -> list[str]:
    """Split fragrance notes on English or Arabic commas."""
    return [note.strip() for note in re.split(r"[,،]", raw_notes) if note.strip()]


def sanitize_input(text: str) -> str:
    """
    Redact common sensitive data before the input is sent
    to validation, translation, tracing, or LLMs.
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

    # Customer / User / Client IDs. The digit check keeps ordinary
    # words such as "custom" and "customers" unchanged.
    text = re.sub(
        r"\b(?:CUST|CUSTOMER|USER|CLIENT)[-_]?(?=[A-Za-z0-9-]*\d)[A-Za-z0-9-]+\b",
        "[REDACTED_ID]",
        text,
        flags=re.IGNORECASE,
    )

    return text


def has_required_fields(form: CampaignForm) -> bool:
    """Return True when every required form field has a value."""
    return all(
        [
            form.product_name.strip(),
            form.top_notes,
            form.middle_notes,
            form.base_notes,
            form.occasion.strip(),
            form.channels,
        ]
    )


def sanitize_form(form: CampaignForm) -> CampaignForm:
    """Return a copy of the form with sensitive data redacted."""
    return CampaignForm(
        product_name=sanitize_input(form.product_name),
        top_notes=[sanitize_input(note) for note in form.top_notes],
        middle_notes=[sanitize_input(note) for note in form.middle_notes],
        base_notes=[sanitize_input(note) for note in form.base_notes],
        description=sanitize_input(form.description),
        occasion=sanitize_input(form.occasion),
        channels=form.channels,
    )


def validate_form(form: CampaignForm) -> list[str]:
    """Validate the form and return Arabic error messages."""
    errors = []

    def check(value: str, field: str, label: str) -> None:
        result = validate_input(user_input=value, field=field)
        if not result.is_valid:
            errors.append(f"❌ {label}: {result.reason}")

    check(form.product_name, "product name", "اسم العطر")

    if form.description.strip():
        check(form.description, "description", "وصف العطر")

    note_groups = (
        ("النوتة العليا", form.top_notes),
        ("النوتة الوسطى", form.middle_notes),
        ("النوتة القاعدية", form.base_notes),
    )
    for label, notes in note_groups:
        for note in notes:
            check(note, "fragrance note", f"{label} '{note}'")

    check(form.occasion, "occasion", "المناسبة")

    return errors


def build_initial_state(form: CampaignForm) -> dict:
    """Translate the form and create the initial workflow state."""
    return {
        "user_context": {
            "product": {
                "name": form.product_name,
                "fragrance_notes": {
                    "top_notes": [translate_to_en(n) for n in form.top_notes],
                    "middle_notes": [translate_to_en(n) for n in form.middle_notes],
                    "base_notes": [translate_to_en(n) for n in form.base_notes],
                },
                "description": (
                    translate_to_en(form.description) if form.description else ""
                ),
            },
            "campaign": {
                "occasion": translate_to_en(form.occasion),
                "channels": form.channels,
            },
        },
        "revision_count": 0,
        "max_revisions": MAX_AUTOMATIC_REVISIONS,
    }
