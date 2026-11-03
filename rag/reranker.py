import re
from typing import List

from langchain_core.documents import Document


def normalize_note(note: str) -> str:
    """Normalize a fragrance note for comparison."""
    return re.sub(r"\s+", " ", note.strip().lower())


def split_notes(notes_text: str) -> set[str]:
    """Convert stored comma-separated notes into a normalized set."""
    if not notes_text:
        return set()

    return {
        normalize_note(note)
        for note in notes_text.split(",")
        if note.strip()
    }


def calculate_note_match_score(document: Document, query_notes: List[str],) -> int:
    """Calculate how many requested fragrance notes appear in a perfume."""

    perfume_notes = set()

    perfume_notes.update(
        split_notes(document.metadata.get("top_notes", ""))
    )
    perfume_notes.update(
        split_notes(document.metadata.get("middle_notes", ""))
    )
    perfume_notes.update(
        split_notes(document.metadata.get("base_notes", ""))
    )

    normalized_query_notes = {
        normalize_note(note)
        for note in query_notes
        if note.strip()
    }

    return len(normalized_query_notes.intersection(perfume_notes))


def rerank_by_note_matches(documents: List[Document], query_notes: List[str],) -> List[Document]:
    """Rerank semantic-search results using exact fragrance-note matches."""

    return sorted(
        documents,
        key=lambda doc: calculate_note_match_score(doc, query_notes,),
        reverse=True,
    )