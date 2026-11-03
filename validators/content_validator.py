import re
import emoji

from schemas.review_schema import ReviewIssue


# Instagram Validation Rules
INSTAGRAM_MIN_WORDS = 30
INSTAGRAM_MAX_WORDS = 60

INSTAGRAM_MIN_HASHTAGS = 3
INSTAGRAM_MAX_HASHTAGS = 5

INSTAGRAM_MIN_EMOJIS = 1
INSTAGRAM_MAX_EMOJIS = 2


ALLOWED_EMOJIS = ["✨", "🖤", "🌿", "🤍"]


# Validation Helpers
def count_words(text: str) -> int:
    """
    Count words in the Instagram caption accurately.
    1. Removes emojis so they are not counted as words.
    2. Strips punctuation attached to Arabic words.
    """

    text_without_emojis = emoji.replace_emoji(text, replace="")

    clean_text = re.sub(r'[^\w\s]', ' ', text_without_emojis)

    words = clean_text.split()
    return len(words)


def count_emojis(text: str) -> int:
    """
    Count all emojis used in the Instagram caption.
    """
    return emoji.emoji_count(text)


def get_used_emojis(text: str) -> list[str]:
    """
    Extract all emojis used in the Instagram caption.
    """
    return [
        item["emoji"]
        for item in emoji.emoji_list(text)
    ]


# Instagram Content Validator
def validate_instagram_content(
    caption: str | None,
    hashtags: list[str] | None,
) -> list[ReviewIssue]:
    """
    Validate deterministic Instagram content rules.

    This validator checks:
    - Caption word count
    - Hashtag count
    - Emoji count
    - Allowed emojis

    Semantic quality is handled separately
    by the Review Agent.
    """

    issues = []

    if caption is None and hashtags is None:
        return issues

    caption = caption or ""
    hashtags = hashtags or []

    word_count = count_words(caption)
    hashtag_count = len(hashtags)
    emoji_count = count_emojis(caption)
    used_emojis = get_used_emojis(caption)

    print("\n📊 Instagram Validation:")
    print(f"Words: {word_count}")
    print(f"Hashtags: {hashtag_count}")
    print(f"Emojis: {emoji_count}")


# Word Count
    if word_count < INSTAGRAM_MIN_WORDS:
        issues.append(
            ReviewIssue(
                category="channel_requirements",
                target="instagram",
                source="rule",
                issue=(
                    f"The Instagram caption contains "
                    f"{word_count} words, which is below "
                    f"the required minimum of "
                    f"{INSTAGRAM_MIN_WORDS} words."
                ),
                violated_rule=(
                    f"Instagram captions should contain "
                    f"{INSTAGRAM_MIN_WORDS}-"
                    f"{INSTAGRAM_MAX_WORDS} words."
                ),
            )
        )

    elif word_count > INSTAGRAM_MAX_WORDS:
        issues.append(
            ReviewIssue(
                category="channel_requirements",
                target="instagram",
                source="rule",
                issue=(
                    f"The Instagram caption contains "
                    f"{word_count} words, which exceeds "
                    f"the required maximum of "
                    f"{INSTAGRAM_MAX_WORDS} words."
                ),
                violated_rule=(
                    f"Instagram captions should contain "
                    f"{INSTAGRAM_MIN_WORDS}-"
                    f"{INSTAGRAM_MAX_WORDS} words."
                ),
            )
        )


# Hashtag Count
    if hashtag_count < INSTAGRAM_MIN_HASHTAGS:
        issues.append(
            ReviewIssue(
                category="channel_requirements",
                target="instagram",
                source="rule",
                issue=(
                    f"The Instagram content contains "
                    f"{hashtag_count} hashtags, which is below "
                    f"the required minimum of "
                    f"{INSTAGRAM_MIN_HASHTAGS}."
                ),
                violated_rule=(
                    f"Instagram content should use "
                    f"{INSTAGRAM_MIN_HASHTAGS}-"
                    f"{INSTAGRAM_MAX_HASHTAGS} relevant hashtags."
                ),
            )
        )

    elif hashtag_count > INSTAGRAM_MAX_HASHTAGS:
        issues.append(
            ReviewIssue(
                category="channel_requirements",
                target="instagram",
                source="rule",
                issue=(
                    f"The Instagram content contains "
                    f"{hashtag_count} hashtags, which exceeds "
                    f"the required maximum of "
                    f"{INSTAGRAM_MAX_HASHTAGS}."
                ),
                violated_rule=(
                    f"Instagram content should use "
                    f"{INSTAGRAM_MIN_HASHTAGS}-"
                    f"{INSTAGRAM_MAX_HASHTAGS} relevant hashtags."
                ),
            )
        )


# Emoji Count
    if emoji_count < INSTAGRAM_MIN_EMOJIS:
        issues.append(
            ReviewIssue(
                category="channel_requirements",
                target="instagram",
                source="rule",
                issue=(
                    f"The Instagram caption contains "
                    f"{emoji_count} emojis, which is below "
                    f"the recommended minimum of "
                    f"{INSTAGRAM_MIN_EMOJIS}."
                ),
                violated_rule=(
                    f"Instagram content should use "
                    f"{INSTAGRAM_MIN_EMOJIS}-"
                    f"{INSTAGRAM_MAX_EMOJIS} emojis."
                ),
            )
        )

    elif emoji_count > INSTAGRAM_MAX_EMOJIS:
        issues.append(
            ReviewIssue(
                category="channel_requirements",
                target="instagram",
                source="rule",
                issue=(
                    f"The Instagram caption contains "
                    f"{emoji_count} emojis, which exceeds "
                    f"the maximum of "
                    f"{INSTAGRAM_MAX_EMOJIS}."
                ),
                violated_rule=(
                    f"Instagram content should use "
                    f"{INSTAGRAM_MIN_EMOJIS}-"
                    f"{INSTAGRAM_MAX_EMOJIS} emojis."
                ),
            )
        )


# Allowed Emojis
    unsupported_emojis = [
        used_emoji
        for used_emoji in used_emojis
        if used_emoji not in ALLOWED_EMOJIS
    ]

    if unsupported_emojis:
        issues.append(
            ReviewIssue(
                category="brand_guidelines",
                target="instagram",
                source="rule",
                issue=(
                    "The Instagram caption contains emojis "
                    "that are not approved by the brand guidelines: "
                    f"{', '.join(unsupported_emojis)}."
                ),
                violated_rule=(
                    "Instagram content may only use the approved "
                    f"emojis: {', '.join(ALLOWED_EMOJIS)}."
                ),
            )
        )

    return issues