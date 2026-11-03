from typing import Literal
from pydantic import BaseModel


class HumanReviewOutput(BaseModel):
    """
    Structured output for Human-in-the-Loop.
    Stores the human's decision, optional feedback,
    and the content area targeted for revision.
    """

    decision: Literal["approve", "reject"]

    feedback: str | None = None

    target: Literal["slogan", "instagram", "email", "all",] | None = None