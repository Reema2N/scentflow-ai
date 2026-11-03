from pathlib import Path

from langchain_core.prompts import PromptTemplate

from config import get_llm
from schemas.content_schema import ContentGenerationOutput
from schemas.campaign_schema import CampaignStrategyOutput
from schemas.input_schema import ProductInput

from prompts.content_prompt import CONTENT_GENERATION_PROMPT

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# LLM Setup
llm = get_llm(temperature=0.1)

# Load Brand Guidelines
guidelines_path = (PROJECT_ROOT / "data" / "Guidelines" / "brand_guidelines.md")

try:
    BRAND_GUIDELINES = guidelines_path.read_text(encoding="utf-8")
except FileNotFoundError:
    BRAND_GUIDELINES = ("No specific brand guidelines were provided.")

# Prompt
content_prompt = PromptTemplate(template=CONTENT_GENERATION_PROMPT,
    input_variables=[
    "product_information",
    "campaign_strategy",
    "marketing_channels",
    "brand_guidelines",
    "instagram_min_words",
    "instagram_max_words",
],
)

# Content Generation Chain

content_generation_chain = (content_prompt | llm.with_structured_output(ContentGenerationOutput))

# Main Agent Function

def generate_content(
    campaign_strategy: CampaignStrategyOutput,
    marketing_channels: list[str],
    product_information: ProductInput,
    instagram_min_words: int = 30,
    instagram_max_words: int = 60,
) -> ContentGenerationOutput:
    
    """
    Generate ready-to-use marketing content based on:

    1. Product information
    2. Campaign strategy
    3. Requested marketing channels
    4. Brand guidelines
    """

# 1. Prepare Product Information
    product_context = (product_information.model_dump_json(indent=2))

# 2. Prepare Campaign Strategy
    campaign_context = (campaign_strategy.model_dump_json(indent=2))

# 3. Generate Content
    content = content_generation_chain.invoke({
    "product_information": product_context,
    "campaign_strategy": campaign_context,
    "marketing_channels": str(marketing_channels),
    "brand_guidelines": BRAND_GUIDELINES,
    "instagram_min_words": instagram_min_words,
    "instagram_max_words": instagram_max_words,
})
    # 4. Enforce Requested Marketing Channels
    normalized_channels = {
        channel.strip().lower()
        for channel in marketing_channels
    }

    if "instagram" not in normalized_channels:
        content.instagram_caption = None
        content.instagram_hashtags = None

    if "email" not in normalized_channels:
        content.email_subject = None
        content.email_body = None


    return content