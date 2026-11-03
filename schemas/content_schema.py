from typing import Optional
from pydantic import BaseModel, Field


class ContentGenerationOutput(BaseModel):

    slogan: str = Field(
        description=(
            "A short, memorable Arabic campaign slogan that follows "
            "the slogan direction defined by the campaign strategy."
        )
    )

    instagram_caption: Optional[str] = Field(
        default=None,
        description=(
            "Ready-to-publish Arabic Instagram caption without hashtags. "
            "Generated only when Instagram is a selected marketing channel."
        )
    )

    instagram_hashtags: Optional[list[str]] = Field(
        default=None,
        description=(
            "A list of relevant Instagram hashtags returned separately "
            "from the caption. Generated only when Instagram is a selected "
            "marketing channel."
        )
    )

    email_subject: Optional[str] = Field(
        default=None,
        description=(
            "Arabic marketing email subject line. "
            "Generated only when Email is a selected marketing channel."
        )
    )

    email_body: Optional[str] = Field(
        default=None,
        description=(
            "Arabic marketing email body. "
            "Generated only when Email is a selected marketing channel."
        )
    )