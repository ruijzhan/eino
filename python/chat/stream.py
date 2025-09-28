"""Streaming functionality for chat responses."""

import time
import logging
from typing import AsyncIterator, Optional

from langchain_core.messages import BaseMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_core.outputs import ChatGenerationChunk

logger = logging.getLogger(__name__)


async def stream(
    model: BaseChatModel,
    messages: list[BaseMessage],
    config: Optional[RunnableConfig] = None,
) -> AsyncIterator[ChatGenerationChunk]:
    """Stream chat responses from the model."""
    start_time = time.time()

    try:
        async for chunk in model.astream(messages, config=config):
            yield chunk
        duration = time.time() - start_time
        logger.info(f"Stream completed in {duration:.2f}s")
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Stream failed after {duration:.2f}s: {e}")
        raise


async def report_stream(stream_iter: AsyncIterator[ChatGenerationChunk]) -> None:
    """Process and report streaming chunks."""
    async for chunk in stream_iter:
        if chunk and hasattr(chunk, 'content') and chunk.content:
            print(chunk.content, end="", flush=True)
    print()  # New line at the end