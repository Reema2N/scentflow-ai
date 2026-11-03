from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from workflow.state import CampaignState
from workflow.nodes import (
    retrieval_node, product_node,
    audience_node, strategy_node,
    content_node, review_node,
    human_review_node, revision_node,
    route_after_review, route_after_human_review,
)

# Create Workflow
workflow = StateGraph(CampaignState)


# Add Nodes
workflow.add_node("retrieval", retrieval_node)
workflow.add_node("product", product_node)
workflow.add_node("audience", audience_node)
workflow.add_node("strategy", strategy_node)
workflow.add_node("content", content_node)
workflow.add_node("review", review_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("revision", revision_node)


# Entry Point
workflow.set_entry_point("retrieval")


# Normal Edges
workflow.add_edge("retrieval", "product")
workflow.add_edge("product", "audience")
workflow.add_edge("audience", "strategy")
workflow.add_edge("strategy", "content")
workflow.add_edge("content", "review")


# Conditional Routing After AI Review
workflow.add_conditional_edges("review", route_after_review,{
        "human_review": "human_review",
        "revision": "revision",}
)


# Conditional Routing After Human Review
workflow.add_conditional_edges("human_review", route_after_human_review,{
        "end": END, "revision": "revision",}
)

# Revision Returns to AI Review
workflow.add_edge("revision", "review")


# Compile Graph with Checkpointer
checkpointer = MemorySaver()

graph = workflow.compile(checkpointer=checkpointer)