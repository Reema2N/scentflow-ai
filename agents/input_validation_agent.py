from langchain_core.prompts import PromptTemplate

from config import get_llm
from schemas.input_validation_schema import (ValidationOutput,HumanFeedbackValidationOutput,)
from prompts.input_validation_prompt import (INPUT_VALIDATION_PROMPT, HUMAN_FEEDBACK_VALIDATION_PROMPT,)


# Input Validation Agent
llm = get_llm(temperature=0)

# General Input Validation
validation_prompt = PromptTemplate(template=INPUT_VALIDATION_PROMPT,
    input_variables=["user_input", "field",],
)

validation_chain = (validation_prompt | llm.with_structured_output(ValidationOutput)
)

# Human Feedback Validation
human_feedback_prompt = PromptTemplate(
    template=HUMAN_FEEDBACK_VALIDATION_PROMPT,
    input_variables=[
        "human_feedback",
        "target",
    ],)

human_feedback_validation_chain = (human_feedback_prompt | llm.with_structured_output(
        HumanFeedbackValidationOutput)
)

# Validation Functions
def validate_input(user_input: str, field: str,) -> ValidationOutput:
    """
    Validates product and campaign inputs.
    """
    result = validation_chain.invoke({"user_input": user_input, "field": field,})
    
    return result

def validate_human_feedback(human_feedback: str, target: str,) -> HumanFeedbackValidationOutput:
    """
    Validates human feedback before sending it
    to the Revision Agent.
    """
    result = human_feedback_validation_chain.invoke({"human_feedback": human_feedback, "target": target,})
    
    return result