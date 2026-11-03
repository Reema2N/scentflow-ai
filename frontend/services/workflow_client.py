"""Start and resume the LangGraph campaign workflow."""

import uuid

from langgraph.types import Command

from workflow.graph import graph


def _thread_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def start_campaign(initial_state: dict) -> tuple[str, dict]:
    """Run the workflow until it pauses for human review."""
    thread_id = str(uuid.uuid4())
    result = graph.invoke(initial_state, config=_thread_config(thread_id))
    return thread_id, result


def approve_campaign(thread_id: str) -> dict:
    """Approve the content and finish the workflow."""
    review_data = {"decision": "approve", "feedback": None, "target": None}
    return graph.invoke(Command(resume=review_data), config=_thread_config(thread_id))


def request_revision(thread_id: str, feedback: str, target: str) -> dict:
    """Send human feedback and run the revision path."""
    review_data = {"decision": "reject", "feedback": feedback, "target": target}
    return graph.invoke(Command(resume=review_data), config=_thread_config(thread_id))
