from typing import List, Literal
from pydantic import BaseModel, Field

# Review Issue
class ReviewIssue(BaseModel):

    category: Literal["strategy", "brand_guidelines", "language", "channel_requirements", "factual_claim", "slogan",
    ] = Field(
        description=(
            "The category of the identified violation."
        )
    )

    target: Literal["slogan", "instagram", "email",] = Field(
        description=(
            "The specific content area affected by the violation."
        )
    )

    source: Literal["llm", "rule",] = Field(
        description=(
            "The source that identified the violation. "
            "Use 'llm' for semantic review issues and "
            "'rule' for deterministic validation issues."
        )
    )

    issue: str = Field(
        description=(
            "A specific and objective description of the violation."
        )
    )

    violated_rule: str = Field(
        description=(
            "The specific campaign strategy requirement, brand guideline, "
            "or review rule that was violated."
        )
    )


# Review Output
class ReviewOutput(BaseModel):

    slogan_approved: bool = Field(
        description=(
            "Whether the generated slogan follows the campaign strategy "
            "and brand guidelines."
        )
    )

    slogan_feedback: str = Field(
        description=(
            "Specific feedback explaining a meaningful slogan violation. "
            "Return an empty string when the slogan is approved."
        )
    )

    content_approved: bool = Field(
        description=(
            "Whether the generated content for the requested marketing "
            "channels meets the campaign and brand requirements."
        )
    )

    content_feedback: List[ReviewIssue] = Field(
        description=(
            "Objective violations found in the generated channel content. "
            "Each issue must identify its category, target, source, "
            "specific problem, and violated rule. "
            "Return an empty list when no meaningful violations exist."
        )
    )

    overall_approved: bool = Field(
        description=(
            "True only when both the slogan and all requested channel "
            "content are approved."
        )
    )

    overall_feedback: str = Field(
        description=(
            "A concise summary of the review decision. "
            "Do not introduce new issues that are not already identified "
            "in slogan_feedback or content_feedback."
        )
    )