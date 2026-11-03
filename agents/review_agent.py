from pathlib import Path
import re

from langchain_core.prompts import PromptTemplate
from config import get_llm

from schemas.review_schema import ReviewOutput, ReviewIssue
from schemas.content_schema import ContentGenerationOutput
from schemas.campaign_schema import CampaignStrategyOutput
from schemas.input_schema import ProductInput

from prompts.review_prompt import REVIEW_PROMPT
from validators.content_validator import validate_instagram_content


PROJECT_ROOT = Path(__file__).resolve().parent.parent


# LLM Setup
llm = get_llm(temperature=0)

# Load Brand Guidelines
guidelines_path = (PROJECT_ROOT / "data" / "Guidelines" / "brand_guidelines.md")

try:
    BRAND_GUIDELINES = guidelines_path.read_text(encoding="utf-8")
except FileNotFoundError:
    BRAND_GUIDELINES = ("No specific brand guidelines were provided.")

# Prompt
review_prompt = PromptTemplate(template=REVIEW_PROMPT,
    input_variables=[
        "product_information",
        "campaign_strategy",
        "generated_content",
        "brand_guidelines",
    ],)

# Review Chain
review_chain = (review_prompt | llm.with_structured_output(ReviewOutput))

# Numeric Feedback Filter
def is_numeric_instagram_issue(issue: ReviewIssue) -> bool:
    """
    Detect Instagram numeric-rule feedback accidentally
    produced by the LLM.

    Word boundaries prevent valid terms such as
    'wording' from matching the keyword 'word'.
    """

    combined_text = (f"{issue.issue} {issue.violated_rule}").lower()

    numeric_pattern = (r"\b("r"words?|"r"hashtags?|"r"emojis?|"r"length"r")\b")

    return bool(re.search(numeric_pattern,combined_text,flags=re.IGNORECASE,) )

# Main Agent Function
def review_content(product_information: ProductInput, campaign_strategy: CampaignStrategyOutput, generated_content: ContentGenerationOutput,) -> ReviewOutput:
    """
    Review generated marketing content using:

    1. LLM semantic review
    2. Deterministic content validation

    The LLM evaluates meaning, strategy alignment,
    language quality, tone, and factual boundaries.

    Product information is provided as the factual
    source of truth for product-specific claims.

    Deterministic Instagram rules are validated
    separately by the content validator.
    """

# Product Information
    product_context = (product_information.model_dump_json(indent=2))

# Campaign Strategy
    campaign_context = (campaign_strategy.model_dump_json(indent=2))

# Generated Content
    content_context = (generated_content.model_dump_json(indent=2))

# Run Semantic Review
    review = review_chain.invoke({
        "product_information": product_context,
        "campaign_strategy": campaign_context,
        "generated_content": content_context,
        "brand_guidelines": BRAND_GUIDELINES,
    })

# Run Deterministic Validation
    instagram_issues = validate_instagram_content(
        caption=generated_content.instagram_caption,
        hashtags=generated_content.instagram_hashtags,
    )

# Remove LLM Numeric Violations
    semantic_feedback = []

    for issue in review.content_feedback:

        if not is_numeric_instagram_issue(issue):
            semantic_feedback.append(issue)

# Merge Review Results
    review.content_feedback = (semantic_feedback + instagram_issues)

# Deterministic Approval Logic
    review.content_approved = (len(review.content_feedback) == 0)

    review.overall_approved = (review.slogan_approved and review.content_approved)

    if review.slogan_approved:
        review.slogan_feedback = ""

# Update Overall Feedback
    if review.overall_approved:
        review.overall_feedback = ("The slogan and generated marketing content " "meet the campaign strategy and brand requirements.")

    elif not review.slogan_approved and review.content_approved:
        review.overall_feedback = ("The marketing content is approved, but the slogan " "requires revision.")

    elif review.slogan_approved and not review.content_approved:
        review.overall_feedback = ("The slogan is approved, but the marketing content " "contains violations that require revision.")

    else:
        review.overall_feedback = ("Both the slogan and marketing content contain " "violations that require revision.")

# Return Final Review
    return review