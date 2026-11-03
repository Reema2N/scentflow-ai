from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    queries: list[str] = Field(
        min_length=3, max_length=3,
        description=(
            "Exactly 3 targeted web search queries for gathering current market, "
            "consumer, cultural, competitor, and marketing insights "
            "relevant to the perfume campaign."
        )
    )