"""Tests for generate functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.outputs import ChatResult
from langchain_core.language_models import BaseChatModel

from generate import generate, generate_with_retry, is_retryable_error, RETRY_BASE_DELAY, MAX_RETRIES


class MockChatModel(BaseChatModel):
    """Mock chat model for testing."""

    def __init__(self, should_fail=False, fail_times=1):
        super().__init__()
        self.should_fail = should_fail
        self.fail_times = fail_times
        self.call_count = 0

    async def ainvoke(self, messages, config=None):
        self.call_count += 1
        if self.should_fail and self.call_count <= self.fail_times:
            if self.fail_times == 1:
                raise Exception("Mock error")
            else:
                raise Exception("Network timeout error")

        # Return a mock result
        result = ChatResult(generations=[
            MagicMock(message=AIMessage(content=f"Mock response {self.call_count}"))
        ])
        return result

    def _generate(self, messages, stop=None, run_manager=None):
        # Not used in async tests
        pass

    @property
    def _llm_type(self):
        return "mock"


@pytest.mark.asyncio
async def test_generate_success():
    """Test successful generation."""
    model = MockChatModel()
    messages = [HumanMessage(content="Hello")]

    result = await generate(model, messages)

    assert isinstance(result, AIMessage)
    assert "Mock response 1" in result.content
    assert model.call_count == 1


@pytest.mark.asyncio
async def test_generate_error():
    """Test generation with error."""
    model = MockChatModel(should_fail=True)
    messages = [HumanMessage(content="Hello")]

    with pytest.raises(Exception):
        await generate(model, messages)

    assert model.call_count == 1


@pytest.mark.asyncio
async def test_generate_with_retry_succeeds_after_retry():
    """Test retry mechanism succeeds after failures."""
    model = MockChatModel(should_fail=True, fail_times=2)
    messages = [HumanMessage(content="Hello")]

    with patch('chat.generate.RETRY_BASE_DELAY', 0.001):  # Speed up retry
        result = await generate_with_retry(model, messages)

    assert isinstance(result, AIMessage)
    assert "Mock response 3" in result.content
    assert model.call_count == 3


@pytest.mark.asyncio
async def test_generate_with_retry_non_retryable():
    """Test retry mechanism with non-retryable error."""
    model = MockChatModel(should_fail=True, fail_times=1)
    messages = [HumanMessage(content="Hello")]

    with patch('chat.generate.RETRY_BASE_DELAY', 0.001):
        result = await generate_with_retry(model, messages)

    # Should return the result after one attempt since error is not retryable
    assert isinstance(result, AIMessage)
    assert model.call_count == 1


@pytest.mark.asyncio
async def test_generate_with_retry_max_retries():
    """Test retry mechanism reaches max retries."""
    model = MockChatModel(should_fail=True, fail_times=10)  # More than MAX_RETRIES
    messages = [HumanMessage(content="Hello")]

    with patch('chat.generate.RETRY_BASE_DELAY', 0.001):
        with pytest.raises(Exception):
            await generate_with_retry(model, messages)

    assert model.call_count == MAX_RETRIES


def test_is_retryable_error():
    """Test retryable error detection."""
    assert is_retryable_error(Exception("timeout occurred")) == True
    assert is_retryable_error(Exception("connection failed")) == True
    assert is_retryable_error(Exception("rate limit exceeded")) == True
    assert is_retryable_error(Exception("429 Too Many Requests")) == True
    assert is_retryable_error(Exception("regular error")) == False
    assert is_retryable_error(None) == False