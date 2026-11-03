from workflow.state import CampaignState
from rag.retriever import retrieve_similar_perfumes
from schemas.input_schema import ProductInput
from schemas.human_review_schema import HumanReviewOutput
from langgraph.types import interrupt

from agents.product_agent import analyze_product
from agents.audience_agent import analyze_audience
from agents.strategy_agent import create_campaign_strategy
from agents.content_agent import generate_content
from agents.review_agent import review_content
from agents.revision_agent import revise_content


# =====================================
# Shared Retrieval Node
# =====================================

def retrieval_node(state: CampaignState) -> dict:
    """
    Retrieves similar perfumes once and shares them
    with the intelligence agents through the workflow state.
    """

    print("\n🔎 Running Shared Perfume Retrieval...")

    product = state["user_context"]["product"]
    notes = product["fragrance_notes"]

    top_notes = notes["top_notes"]
    middle_notes = notes["middle_notes"]
    base_notes = notes["base_notes"]

    all_notes = top_notes + middle_notes + base_notes

    query = (f"Perfume with top notes: {', '.join(top_notes)}; "f"middle notes: {', '.join(middle_notes)}; "f"base notes: {', '.join(base_notes)}")

    retrieved_docs = retrieve_similar_perfumes(query=query, query_notes=all_notes, fetch_k=10, top_k=5)

    # Temporary retrieval diagnosis
    print("\n=== RETRIEVED SIMILAR PERFUMES ===")

    for i, doc in enumerate(retrieved_docs, start=1):
        print(f"\n--- Perfume {i} ---")
        print(doc.page_content)

    return {"retrieved_perfumes": retrieved_docs}

# =====================================
# Product Intelligence Node
# =====================================
def product_node(state: CampaignState) -> dict:
    """
    Runs the Product Intelligence Agent.
    """

    print("\n🧴 Running Product Intelligence Agent...")

    product_analysis = analyze_product(
        user_input=state["user_context"],
        retrieved_docs=state["retrieved_perfumes"]
    )

    return {"product_analysis": product_analysis}

# =====================================
# Audience Intelligence Node
# =====================================
def audience_node(state: CampaignState) -> dict:
    """
    Runs the Audience Intelligence Agent.
    """

    print("\n👥 Running Audience Intelligence Agent...")

    audience_analysis = analyze_audience(
        user_input=state["user_context"],
        product_analysis=state["product_analysis"],
        retrieved_docs=state["retrieved_perfumes"]
    )

    return {"audience_analysis": audience_analysis}

# =====================================
# Campaign Strategy Node
# =====================================
def strategy_node(state: CampaignState) -> dict:
    """
    Runs the Campaign Strategy Agent.
    """

    print("\n📢 Running Campaign Strategy Agent...")

    campaign_strategy = create_campaign_strategy(
        product_analysis=state["product_analysis"],
        audience_analysis=state["audience_analysis"],
        campaign_information=state["user_context"].get(
            "campaign", {}
        ))

    return {"campaign_strategy": campaign_strategy}

# =====================================
# Content Generation Node
# =====================================
def content_node(state: CampaignState) -> dict:
    """
    Runs the Content Generation Agent.
    """

    print("\n✍️ Running Content Generation Agent...")

    # Convert product dictionary to ProductInput
    product_information = ProductInput(**state["user_context"]["product"])

    # Get campaign information
    campaign = state["user_context"].get("campaign", {})

    # Get selected marketing channels
    marketing_channels = campaign.get("channels", [])

    # Generate marketing content
    content = generate_content(
        campaign_strategy=state["campaign_strategy"],
        marketing_channels=marketing_channels,
        product_information=product_information
    )

    return {"generated_content": content}

# =====================================
# AI Review Node
# =====================================
def review_node(state: CampaignState) -> dict:
    """
    Runs the AI Review Agent.
    """

    print("\n🔍 Running AI Review Agent...")

    # Convert product dictionary to ProductInput
    product_information = ProductInput(**state["user_context"]["product"])

    review = review_content(
        product_information=product_information,
        campaign_strategy=state["campaign_strategy"],
        generated_content=state["generated_content"] )

    # =====================================
    # Diagnosis
    # =====================================
    print("\n" + "=" * 70)
    print("🔎 DIAGNOSIS — AI REVIEW")
    print("=" * 70)

    print(f"Slogan approved: "f"{review.slogan_approved}")
    print(f"Slogan feedback: "f"{review.slogan_feedback}")
    print(f"\nContent approved: "f"{review.content_approved}")
    print("\nContent feedback:")

    for feedback in review.content_feedback:
        print(f"- {feedback}")

    print(f"\nOverall approved: "f"{review.overall_approved}")
    print(f"Overall feedback: "f"{review.overall_feedback}")
    print(f"\nRevision count: "f"{state.get('revision_count', 0)}")

    return {"ai_review": review}


# =====================================
# Human Review Node
# =====================================
def human_review_node(state: CampaignState) -> dict:
    """
    Pauses the workflow and waits for a human
    approval or revision request from the UI.
    """

    print("\n👤 Waiting for Human Review...")

    review_data = interrupt({
        "generated_content": (
            state["generated_content"].model_dump()
        ),
        "message": "Human review required."
    })

    human_review = HumanReviewOutput(
        **review_data
    )

    return {
        "human_review": human_review
    }

# =====================================
# Revision Node
# =====================================
def revision_node(state: CampaignState) -> dict:
    """
    Revises content using AI and/or human feedback.
    """

    print("\n🔄 Running Revision Agent...")

    # Convert product dictionary to ProductInput
    product_information = ProductInput(**state["user_context"]["product"])

    # Get AI and Human review
    ai_review = state.get("ai_review")
    human_review = state.get("human_review")

    # Default human feedback and target
    human_feedback = None
    human_target = None

    # Use human feedback only when the human rejected
    if (human_review is not None and human_review.decision == "reject"):
        human_feedback = human_review.feedback
        human_target = human_review.target

    # Revise content
    revised_content = revise_content(
        product_information=product_information,
        campaign_strategy=state["campaign_strategy"],
        original_content=state["generated_content"],
        review_feedback=ai_review,
        human_feedback=human_feedback,
        human_target=human_target )

    # =====================================
    # Diagnosis
    # =====================================
    print("\n" + "=" * 70)
    print("🔎 DIAGNOSIS — REVISED CONTENT")
    print("=" * 70)
    print(revised_content.model_dump_json(indent=2))

    return {
        "generated_content": revised_content,
        "revision_count": (state.get("revision_count", 0) + 1),

        # Clear previous human decision after
        # its feedback has been used.
        "human_review": None }

# =====================================
# Routing Functions
# =====================================
def route_after_review(state: CampaignState) -> str:
    """
    Decide where to go after AI review.
    """

    review = state["ai_review"]

    # AI automatic revision limit reached.
    # Human-requested revisions are still allowed.
    if review.overall_approved:
        return "human_review"

    # AI rejected, but revision limit reached
    if (state.get("revision_count", 0)>= state.get("max_revisions", 3)):
        return "human_review"

    # AI rejected and revisions are still allowed
    return "revision"


def route_after_human_review(state: CampaignState) -> str:
    """
    Decide where to go after human review.
    """

    human_review = state["human_review"]

    if human_review.decision == "approve":
        return "end"

    return "revision"