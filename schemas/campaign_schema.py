from pydantic import BaseModel, Field


class CampaignStrategyOutput(BaseModel):
    campaign_theme: str = Field(
        description="The central creative theme of the marketing campaign."
    )

    marketing_angle: str = Field(
        description="The strategic marketing angle used to position the perfume."
    )

    main_message: str = Field(
        description="The core message the campaign should communicate to the audience."
    )

    slogan_direction: str = Field(
        description="Creative direction for the slogan, not the final slogan itself."
    )

    content_style: str = Field(
        description="The recommended style and tone for the campaign content."
    )

    call_to_action_direction: str = Field(
        description=(
            "Strategic direction for the call to action, "
            "not the final call-to-action wording."
        )
    )