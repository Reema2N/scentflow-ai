from typing import List
from pydantic import BaseModel, Field


class ProductAnalysisOutput(BaseModel):
    fragrance_family: List[str] = Field(
        description="The most suitable fragrance family classification."
    )

    season: List[str] = Field(
    description=(
        "The individual seasons most suitable for wearing the fragrance. "
        "Return each season as a separate list item, for example: "
        "['Autumn', 'Winter'], not ['Autumn / Winter']."
    )
)
    wearing_occasion: List[str] = Field(
        description="Suitable wearing occasions, independent of the campaign event."
    )