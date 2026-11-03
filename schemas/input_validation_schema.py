from pydantic import BaseModel, Field

class ValidationOutput(BaseModel):
    """
    Structured output for validating
    product and campaign inputs.
    """
    is_valid: bool = Field(
        description="Whether the user input is valid and appropriate for the requested field."
    )
    reason: str = Field(
        description="A short explanation in ARABIC (اللغة العربية) of why the input is valid or invalid."
    )
    corrected_guidance: str | None = Field(
        default=None,
        description="Guidance in ARABIC (اللغة العربية) explaining what the user should enter if the input is invalid."
    )

class HumanFeedbackValidationOutput(BaseModel):
    """
    Structured output for validating
    human revision feedback.
    """
    is_valid: bool = Field(
        description="Whether the human feedback is a clear and actionable revision request."
    )
    reason: str = Field(
        description="A short explanation in ARABIC (اللغة العربية) of why the feedback is valid or invalid."
    )
    suggested_example: str | None = Field(
        default=None,
        description="A short example in ARABIC (اللغة العربية) of a valid revision request if the feedback is invalid."
    )