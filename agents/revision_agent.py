from pathlib import Path
from langchain_core.prompts import PromptTemplate

from schemas.content_schema import ContentGenerationOutput
from schemas.campaign_schema import CampaignStrategyOutput
from schemas.review_schema import ReviewOutput
from schemas.input_schema import ProductInput
from prompts.revision_prompt import (REVISION_PROMPT, REVISION_RETRY_PROMPT,)
from config import get_llm
from validators.content_validator import (count_words, INSTAGRAM_MIN_WORDS, INSTAGRAM_MAX_WORDS,)

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# LLM Setup
llm = get_llm(temperature=0.0)

# Load Brand Guidelines
guidelines_path = (PROJECT_ROOT / "data" / "Guidelines" / "brand_guidelines.md")

try:
    BRAND_GUIDELINES = guidelines_path.read_text(encoding="utf-8")

except FileNotFoundError:BRAND_GUIDELINES = (
        "No specific brand guidelines were provided."
    )

# Main Revision Prompt
revision_prompt = PromptTemplate(template=REVISION_PROMPT,
    input_variables=[
        "product_information",
        "campaign_strategy",
        "original_content",
        "brand_guidelines",
        "review_feedback",
        "human_feedback",
        "human_target",
        "instagram_min_words",
        "instagram_max_words",
    ], )

revision_chain = (revision_prompt | llm.with_structured_output(ContentGenerationOutput))

# Revision Retry Prompt
revision_retry_prompt = PromptTemplate(template=REVISION_RETRY_PROMPT,
    input_variables=[
        "current_content",
        "validation_feedback",
        "instagram_min_words",
        "instagram_max_words",
    ],)

revision_retry_chain = (revision_retry_prompt | llm.with_structured_output(ContentGenerationOutput))

# Helper Functions
def get_review_feedback_text(review_feedback: ReviewOutput | None,) -> str:
    """
    Combines Review Agent issues and violated rules
    into one searchable text.
    """

    if review_feedback is None:
        return ""

    feedback_parts = []

    for issue in review_feedback.content_feedback:
        feedback_parts.append(issue.category)
        feedback_parts.append(issue.issue)
        feedback_parts.append(issue.violated_rule)

    return " ".join(feedback_parts).lower()

# Preservation Safeguards
def apply_revision_safeguards(
    revised_content: ContentGenerationOutput,
    original_content: ContentGenerationOutput,
    review_feedback: ReviewOutput | None,
    human_feedback: str | None,
    human_target: str | None,
) -> ContentGenerationOutput:
    """
    Preserves approved or unrelated content unless
    AI review feedback or targeted human feedback
    explicitly requires changes.
    """

    has_human_feedback = bool(human_feedback and human_feedback.strip())

    review_text = get_review_feedback_text(review_feedback)

    # Human Target Flags
    human_targets_slogan = (has_human_feedback and human_target in ["slogan", "all"])

    human_targets_instagram = (has_human_feedback and human_target in ["instagram", "all"])

    human_targets_email = (has_human_feedback and human_target in ["email", "all"])

    # Preserve approved slogan
    if (
        review_feedback is not None
        and review_feedback.slogan_approved
        and not human_targets_slogan
    ):
        revised_content.slogan = (original_content.slogan)

    # Preserve Instagram Hashtags
    hashtag_feedback_exists = ("hashtag" in review_text)

    if (
        not hashtag_feedback_exists
        and not human_targets_instagram
    ):
        revised_content.instagram_hashtags = (original_content.instagram_hashtags)

    # Preserve Instagram from unrelated Human Feedback
    instagram_ai_feedback_exists = any(
        issue.target == "instagram"
        for issue in review_feedback.content_feedback
    ) if review_feedback is not None else False

    if (
        not human_targets_instagram
        and not instagram_ai_feedback_exists
    ):
        revised_content.instagram_caption = (original_content.instagram_caption)

        revised_content.instagram_hashtags = (original_content.instagram_hashtags)

    # Preserve Email from unrelated Human Feedback
    email_ai_feedback_exists = any(issue.target == "email"
        for issue in review_feedback.content_feedback
    ) if review_feedback is not None else False

    if (
        not human_targets_email
        and not email_ai_feedback_exists
    ):
        revised_content.email_subject = (original_content.email_subject)

        revised_content.email_body = (original_content.email_body)

    # Preserve unused channels
    if original_content.instagram_caption is None:
        revised_content.instagram_caption = None

    if original_content.instagram_hashtags is None:
        revised_content.instagram_hashtags = None

    if original_content.email_subject is None:
        revised_content.email_subject = None

    if original_content.email_body is None:
        revised_content.email_body = None

    return revised_content

# Revision Validation
def validate_revision(revised_content: ContentGenerationOutput, review_feedback: ReviewOutput | None,) -> bool:
    """
    Checks whether measurable AI review violations
    were actually fixed by the Revision Agent.
    """

    if review_feedback is None:
        return True

    review_text = get_review_feedback_text(review_feedback)

    # Instagram Word Count
    required_range = (f"{INSTAGRAM_MIN_WORDS}-"f"{INSTAGRAM_MAX_WORDS} words")

    if (
        required_range in review_text
        and revised_content.instagram_caption is not None
    ):
        word_count = count_words(revised_content.instagram_caption)

        if (INSTAGRAM_MIN_WORDS <= word_count <= INSTAGRAM_MAX_WORDS ):
            return True

        return False

    return True

# Main Agent Function
def revise_content(
    product_information: ProductInput,
    campaign_strategy: CampaignStrategyOutput,
    original_content: ContentGenerationOutput,
    review_feedback: ReviewOutput | None = None,
    human_feedback: str | None = None,
    human_target: str | None = None,
) -> ContentGenerationOutput:
    """
    Revises generated marketing content based on
    AI review feedback and/or targeted human feedback.
    """

    # Product Information
    product_context = (product_information.model_dump_json(indent=2))

    # Campaign Strategy
    campaign_context = (campaign_strategy.model_dump_json(indent=2))

    # Original Content
    content_context = (original_content.model_dump_json(indent=2))

    # AI Review Feedback
    if review_feedback is not None:
        review_context = (review_feedback.model_dump_json(indent=2))
    else:
        review_context = ("No AI review feedback provided.")

    # Human Feedback
    original_human_feedback = human_feedback

    if not human_feedback:
        human_feedback = ("No human feedback provided.")

    # Human Target
    original_human_target = human_target

    if not human_target:
        human_target = ("No human revision target provided.")

    # Revise Content
    revised_content = revision_chain.invoke({
        "instagram_min_words": INSTAGRAM_MIN_WORDS,
        "instagram_max_words": INSTAGRAM_MAX_WORDS,
        "product_information": product_context,
        "campaign_strategy": campaign_context,
        "original_content": content_context,
        "brand_guidelines": BRAND_GUIDELINES,
        "review_feedback": review_context,
        "human_feedback": human_feedback,
        "human_target": human_target,
    })

    # Apply Safeguards
    revised_content = apply_revision_safeguards(
        revised_content=revised_content,
        original_content=original_content,
        review_feedback=review_feedback,
        human_feedback=original_human_feedback,
        human_target=original_human_target,
    )

    # Validate Revision
    revision_valid = validate_revision(
        revised_content=revised_content,
        review_feedback=review_feedback,
    )

    # Retry Failed Measurable Revision
    if not revision_valid:

        word_count = count_words(revised_content.instagram_caption)

        validation_feedback = (
            f"The Instagram caption currently contains "
            f"{word_count} words. "
            f"The required range is "
            f"{INSTAGRAM_MIN_WORDS}-"
            f"{INSTAGRAM_MAX_WORDS} words. "
            f"Add or remove enough actual words to satisfy "
            f"the required range."
        )

        retry_content = (
            revision_retry_chain.invoke({
                "current_content": revised_content.model_dump_json(indent=2),
                "validation_feedback": validation_feedback,
                "instagram_min_words": INSTAGRAM_MIN_WORDS,
                "instagram_max_words": INSTAGRAM_MAX_WORDS,})
        )

        revised_content = (
            apply_revision_safeguards(
                revised_content=retry_content,
                original_content=revised_content,
                review_feedback=review_feedback,
                human_feedback=original_human_feedback,
                human_target=original_human_target,
            )
        )

        validate_revision(revised_content=revised_content, review_feedback=review_feedback,)

    return revised_content