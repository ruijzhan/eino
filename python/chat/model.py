"""Model configuration and management."""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel


def create_openai_chat_model(
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.0,
) -> BaseChatModel:
    """Create OpenAI chat model with configuration from environment variables."""

    # Get configuration from environment variables if not provided
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    model_name = model_name or os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    base_url = base_url or os.getenv("OPENAI_BASE_URL")

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    return ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=temperature,
    )