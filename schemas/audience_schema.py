from pydantic import BaseModel, Field


class AudienceAnalysisOutput(BaseModel):

    target_gender: str = Field(
        description=(
            "The most suitable target gender for the fragrance, "
            "such as Female, Male, or Unisex."
        )
    )

    target_age_range: str = Field(
        description=(
            "A reasonable target age range inferred from the fragrance "
            "profile, product positioning, campaign context, and similar "
            "perfume references."
        )
    )