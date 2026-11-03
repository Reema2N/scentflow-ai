from typing import TypedDict

from schemas.product_schema import ProductAnalysisOutput
from schemas.audience_schema import AudienceAnalysisOutput
from schemas.campaign_schema import CampaignStrategyOutput
from schemas.content_schema import ContentGenerationOutput
from schemas.review_schema import ReviewOutput
from schemas.human_review_schema import HumanReviewOutput


class CampaignState(TypedDict, total=False):
    """
    Shared state passed between all nodes
    in the ScentFlow workflow.
    """

# User Input
    user_context: dict


# Shared Retrieval
    retrieved_perfumes: list


# Agent Outputs
    product_analysis: ProductAnalysisOutput
    audience_analysis: AudienceAnalysisOutput
    campaign_strategy: CampaignStrategyOutput
    generated_content: ContentGenerationOutput


# Review Outputs
    ai_review: ReviewOutput
    human_review: HumanReviewOutput | None


# Revision Control
    revision_count: int
    max_revisions: int