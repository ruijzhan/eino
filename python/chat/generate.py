"""Core chat generation functionality."""

import time
import logging
from typing import Optional
from asyncio import sleep
from contextlib import asynccontextmanager

from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_core.outputs import ChatResult

logger = logging.getLogger(__name__)

# Retry configuration
RETRY_BASE_DELAY = 1.0  # seconds
MAX_RETRIES = 3


async def generate(
    model: BaseChatModel,
    messages: list[BaseMessage],
    config: Optional[RunnableConfig] = None,
) -> BaseMessage:
    """Generate a single response from the chat model."""
    start_time = time.time()

    try:
        result = await model.ainvoke(messages, config=config)
        duration = time.time() - start_time
        logger.info(f"Generate completed in {duration:.2f}s")

        # Handle different return types from the model
        if hasattr(result, 'generations') and result.generations:
            # ChatResult object
            return result.generations[0].message
        elif isinstance(result, BaseMessage):
            # Direct message object
            return result
        else:
            # Convert to AIMessage if it's just content
            return AIMessage(content=str(result))
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Generate failed after {duration:.2f}s: {e}")
        raise


async def generate_with_retry(
    model: BaseChatModel,
    messages: list[BaseMessage],
    config: Optional[RunnableConfig] = None,
) -> BaseMessage:
    """Generate a response with retry logic for network errors."""

    for attempt in range(MAX_RETRIES):
        try:
            result = await generate(model, messages, config)
            if attempt > 0:
                logger.info(f"Generate succeeded on retry attempt {attempt + 1}")
            return result
        except Exception as e:
            if is_retryable_error(e) and attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (attempt + 1)
                logger.warning(f"Generate attempt {attempt + 1} failed: {e}, retrying in {delay}s")
                await sleep(delay)
                continue
            raise

    raise RuntimeError("generate_with_retry: unexpected error after all retries")


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable."""
    if error is None:
        return False

    # Check for timeout errors
    if "timeout" in str(error).lower():
        return True

    # Check for connection errors
    if "connection" in str(error).lower() or "network" in str(error).lower():
        return True

    # Check for rate limit errors
    if "rate limit" in str(error).lower() or "429" in str(error):
        return True

    return False