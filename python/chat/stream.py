"""Streaming functionality for chat responses."""

import asyncio
import logging
import sys
import time
from typing import AsyncIterator, Optional, TextIO
from contextlib import asynccontextmanager

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
        stream_result = model.astream(messages, config=config)
        async for chunk in stream_result:
            yield chunk
        duration = time.time() - start_time
        logger.info(f"Stream completed in {duration:.2f}s")
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Stream failed after {duration:.2f}s: {e}")
        raise


async def report_stream(stream_iter: AsyncIterator[ChatGenerationChunk]) -> None:
    """Process and report streaming chunks."""
    return await report_stream_with_context(stream_iter, sys.stdout)


async def report_stream_with_context(
    stream_iter: AsyncIterator[ChatGenerationChunk],
    writer: TextIO
) -> None:
    """Process and report streaming chunks with context cancellation support."""
    async with stream_with_cancellation(stream_iter) as safe_stream:
        async for chunk in safe_stream:
            if chunk and hasattr(chunk, 'content') and chunk.content:
                try:
                    writer.write(chunk.content)
                    writer.flush()
                except (IOError, BrokenPipeError) as e:
                    logger.error(f"Write error: {e}")
                    raise
    print()  # New line at the end


@asynccontextmanager
async def stream_with_cancellation(
    stream_iter: AsyncIterator[ChatGenerationChunk]
) -> AsyncIterator[ChatGenerationChunk]:
    """Context manager for handling stream cancellation gracefully."""
    # Create a wrapper that handles cancellation
    async def _cancellable_stream():
        try:
            async for chunk in stream_iter:
                yield chunk
        except asyncio.CancelledError:
            logger.info("Stream cancelled by context")
            raise

    yield _cancellable_stream()