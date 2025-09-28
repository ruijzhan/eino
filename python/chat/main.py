"""Main entry point for the chat application."""

import asyncio
import logging
from contextlib import asynccontextmanager

from model import create_openai_chat_model
from generate import generate, generate_with_retry
from stream import stream, report_stream
from template import create_messages_from_template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main application entry point."""

    # Create messages from template
    messages = create_messages_from_template()
    logger.info(f"Created {len(messages)} messages from template")

    # Create chat model
    try:
        model = create_openai_chat_model()
        logger.info("Created OpenAI chat model")
    except ValueError as e:
        logger.error(f"Failed to create chat model: {e}")
        print(f"Error: {e}")
        return

    # Test generation
    try:
        print("\n=== Testing Generation ===")
        result = await generate_with_retry(model, messages)
        print(f"Generation result: {result.content}")
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        print(f"Generation error: {e}")

    # Test streaming
    try:
        print("\n=== Testing Streaming ===")
        stream_iter = stream(model, messages)
        await report_stream(stream_iter)
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        print(f"Streaming error: {e}")


if __name__ == "__main__":
    asyncio.run(main())