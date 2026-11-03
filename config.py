import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# =====================================
# Project Root
# =====================================

PROJECT_ROOT = Path(__file__).resolve().parent


# =====================================
# Environment Setup
# =====================================

load_dotenv(PROJECT_ROOT / ".env")


# =====================================
# API Keys
# =====================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# =====================================
# LLM Configuration
# =====================================

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    os.getenv("OPENAI_MODEL", "gpt-4o-mini")
)

LLM_API_KEY = os.getenv(
    "LLM_API_KEY",
    OPENAI_API_KEY
)

LLM_BASE_URL = os.getenv("LLM_BASE_URL")


# =====================================
# LLM Factory
# =====================================

def get_llm(
    temperature: float = 0.0,
    model: str | None = None,
):
    """
    Create and return the configured LLM.

    By default, ScentFlow uses OpenAI.

    The configuration is centralized here so the
    model provider can be changed later without
    modifying every agent.

    If an OpenAI-compatible AIDC endpoint becomes
    available, it can be configured through:

    LLM_MODEL
    LLM_API_KEY
    LLM_BASE_URL
    """

    selected_model = model or LLM_MODEL

    llm_kwargs = {
        "model": selected_model,
        "api_key": LLM_API_KEY,
        "temperature": temperature,
        "max_retries": 3,
        "timeout": 60,
    }

    # Only provide base_url when a custom endpoint
    # such as an AIDC endpoint is configured.
    if LLM_BASE_URL:
        llm_kwargs["base_url"] = LLM_BASE_URL

    return ChatOpenAI(**llm_kwargs)
