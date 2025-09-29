"""Model configuration and management."""

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Model configuration with sensible defaults."""
    api_key: str
    model: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    timeout: float = 30.0
    max_retries: int = 3


@dataclass
class _DefaultConfig:
    """Private class to hold default configuration values."""
    temperature: float = 0.7
    timeout: float = 30.0
    max_retries: int = 3


def default_model_config() -> ModelConfig:
    """Create a default model configuration."""
    return ModelConfig(
        api_key="",  # Will be overridden by load_model_config
        model="",   # Will be overridden by load_model_config
        temperature=_DefaultConfig.temperature,
        timeout=_DefaultConfig.timeout,
        max_retries=_DefaultConfig.max_retries,
    )


def load_model_config() -> ModelConfig:
    """Load model configuration from environment variables."""
    config = default_model_config()

    # API key validation
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    config.api_key = api_key

    # Model name validation
    model_name = os.getenv("OPENAI_MODEL_NAME")
    if not model_name:
        raise ValueError("OPENAI_MODEL_NAME environment variable is required")
    config.model = model_name

    # Optional BaseURL
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        config.base_url = base_url

    # Optional temperature
    temp_str = os.getenv("OPENAI_TEMPERATURE")
    if temp_str:
        try:
            config.temperature = float(temp_str)
        except ValueError as e:
            raise ValueError(f"Invalid OPENAI_TEMPERATURE value: {e}")

    # Optional timeout
    timeout_str = os.getenv("OPENAI_TIMEOUT")
    if timeout_str:
        try:
            config.timeout = float(timeout_str)
        except ValueError as e:
            raise ValueError(f"Invalid OPENAI_TIMEOUT value: {e}")

    # Optional max retries
    max_retries_str = os.getenv("OPENAI_MAX_RETRIES")
    if max_retries_str:
        try:
            config.max_retries = int(max_retries_str)
            if config.max_retries < 0:
                raise ValueError("OPENAI_MAX_RETRIES must be non-negative")
        except ValueError as e:
            raise ValueError(f"Invalid OPENAI_MAX_RETRIES value: {e}")

    return config


def create_openai_chat_model(
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.0,
) -> BaseChatModel:
    """Create OpenAI chat model with configuration from environment variables."""
    return create_openai_chat_model_with_config(None)


def create_openai_chat_model_with_config(
    custom_config: Optional[ModelConfig] = None
) -> BaseChatModel:
    """Create OpenAI chat model with explicit configuration."""
    if custom_config:
        config = custom_config
    else:
        try:
            config = load_model_config()
        except ValueError as e:
            logger.error(f"Failed to load model config: {e}")
            raise

    # Retry logic for model creation
    last_error = None
    for attempt in range(config.max_retries + 1):
        try:
            model = ChatOpenAI(
                model=config.model,
                openai_api_key=config.api_key,
                openai_api_base=config.base_url,
                temperature=config.temperature,
                request_timeout=config.timeout,
                max_retries=0,  # We handle retries ourselves
            )

            if attempt > 0:
                logger.info(f"Model created successfully after {attempt + 1} attempts")

            return model

        except Exception as e:
            last_error = e
            if attempt < config.max_retries:
                wait_time = (attempt + 1) * 1.0  # Exponential backoff
                logger.warning(
                    f"Model creation attempt {attempt + 1} failed: {e}, "
                    f"retrying in {wait_time}s"
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    f"Failed to create OpenAI chat model after {config.max_retries + 1} attempts: {e}"
                )

    # If we get here, all retries failed
    raise RuntimeError(f"Failed to create model after {config.max_retries + 1} attempts: {last_error}")