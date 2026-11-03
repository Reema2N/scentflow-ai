import json
from langchain_core.prompts import ChatPromptTemplate

from config import get_llm
from prompts.audience_prompt import AUDIENCE_ANALYSIS_PROMPT
from schemas.audience_schema import AudienceAnalysisOutput
from schemas.product_schema import ProductAnalysisOutput


# LLM Setup

llm = get_llm(temperature=0)
structured_llm = llm.with_structured_output(AudienceAnalysisOutput)

# Audience Analysis Chain

prompt = ChatPromptTemplate.from_template(AUDIENCE_ANALYSIS_PROMPT)
audience_chain = prompt | structured_llm


# Audience Intelligence Agent

def analyze_audience(user_input: dict, product_analysis: ProductAnalysisOutput, retrieved_docs: list) -> AudienceAnalysisOutput:

    # Extract product information
    product = user_input["product"]

    name = product["name"]
    notes = product["fragrance_notes"]

    top_notes = notes["top_notes"]
    middle_notes = notes["middle_notes"]
    base_notes = notes["base_notes"]

    # Prepare shared retrieved knowledge for the LLM
    similar_perfumes = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    # Prepare product context
    product_context = {
        "name": name,
        "top_notes": top_notes,
        "middle_notes": middle_notes,
        "base_notes": base_notes,
        "description": product.get("description")
    }

    product_context = json.dumps(product_context, ensure_ascii=False, indent=2) 

    # Prepare Product Intelligence analysis
    product_analysis_context = (product_analysis.model_dump_json(indent=2))

    # Prepare campaign context
    campaign_context = json.dumps(user_input.get("campaign", {}), ensure_ascii=False, indent=2)

    # Run audience analysis
    result = audience_chain.invoke({
        "product_context": product_context,
        "product_analysis": product_analysis_context,
        "campaign_context": campaign_context,
        "similar_perfumes": similar_perfumes
    })

    return result