import json
from langchain_core.prompts import ChatPromptTemplate
from config import get_llm
from prompts.product_prompt import PRODUCT_ANALYSIS_PROMPT
from schemas.product_schema import ProductAnalysisOutput


# LLM Setup
llm = get_llm(temperature=0)
structured_llm = llm.with_structured_output(ProductAnalysisOutput)

# Product Analysis Chain
prompt = ChatPromptTemplate.from_template(PRODUCT_ANALYSIS_PROMPT)

product_chain = prompt | structured_llm

# Product Intelligence Agent
def analyze_product(user_input: dict, retrieved_docs: list) -> ProductAnalysisOutput:

    # Extract product information
    product = user_input["product"]

    name = product["name"]
    notes = product["fragrance_notes"]

    top_notes = notes["top_notes"]
    middle_notes = notes["middle_notes"]
    base_notes = notes["base_notes"]
    
    # Prepare shared retrieved knowledge for the LLM
    similar_perfumes = "\n\n".join(doc.page_content for doc in retrieved_docs)

    # Prepare product context
    product_context = {
        "name": name,
        "top_notes": top_notes,
        "middle_notes": middle_notes,
        "base_notes": base_notes,
        "description": product.get("description")
    }

    product_context = json.dumps(product_context, ensure_ascii=False, indent=2)

    # Run product analysis
    result = product_chain.invoke({"product_context": product_context, "similar_perfumes": similar_perfumes})


    return result