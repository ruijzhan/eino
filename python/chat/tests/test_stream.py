"""Tests for stream functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from io import StringIO

from chat.stream import stream, report_stream, report_stream_with_context, stream_with_cancellation


@pytest.mark.asyncio
async def test_stream_success():
    """Test successful streaming."""
    mock_model = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.content = "Hello"

    # Create a mock async iterator
    class MockAsyncIterator:
        def __init__(self, chunks):
            self.chunks = chunks
            self.index = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.index < len(self.chunks):
                chunk = self.chunks[self.index]
                self.index += 1
                return chunk
            else:
                raise StopAsyncIteration

    mock_model.astream = MagicMock(return_value=MockAsyncIterator([mock_chunk]))

    messages = []

    # Collect chunks
    chunks = []
    async for chunk in stream(mock_model, messages):
        chunks.append(chunk)

    assert len(chunks) == 1
    assert chunks[0] == mock_chunk


@pytest.mark.asyncio
async def test_stream_with_error():
    """Test streaming with error."""
    mock_model = MagicMock()

    # Create a mock async iterator that raises an error
    class ErrorAsyncIterator:
        def __init__(self, error):
            self.error = error

        def __aiter__(self):
            return self

        async def __anext__(self):
            raise self.error

    mock_model.astream = MagicMock(return_value=ErrorAsyncIterator(ValueError("Test error")))

    messages = []

    # Should raise the error
    with pytest.raises(ValueError, match="Test error"):
        async for _ in stream(mock_model, messages):
            pass


@pytest.mark.asyncio
async def test_report_stream():
    """Test report_stream function."""
    mock_chunk = MagicMock()
    mock_chunk.content = "Hello"

    async def mock_stream():
        yield mock_chunk
        yield mock_chunk

    # Capture output
    import sys
    from io import StringIO

    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        await report_stream(mock_stream())

    output = captured_output.getvalue()
    assert "HelloHello" in output
    assert output.endswith("\n")


@pytest.mark.asyncio
async def test_report_stream_with_custom_writer():
    """Test report_stream_with_context function."""
    mock_chunk = MagicMock()
    mock_chunk.content = "Hello"

    async def mock_stream():
        yield mock_chunk

    # Use StringIO as writer
    writer = StringIO()
    await report_stream_with_context(mock_stream(), writer)

    output = writer.getvalue()
    assert "Hello" in output


@pytest.mark.asyncio
async def test_stream_with_cancellation():
    """Test stream_with_cancellation context manager."""
    mock_chunk = MagicMock()
    mock_chunk.content = "Hello"

    async def mock_stream():
        yield mock_chunk

    async with stream_with_cancellation(mock_stream()) as safe_stream:
        chunks = []
        async for chunk in safe_stream:
            chunks.append(chunk)

    assert len(chunks) == 1
    assert chunks[0] == mock_chunk


@pytest.mark.asyncio
async def test_stream_with_cancellation_handles_cancelled_error():
    """Test stream_with_cancellation handles CancelledError gracefully."""
    mock_chunk = MagicMock()
    mock_chunk.content = "Hello"

    async def mock_stream():
        yield mock_chunk
        raise asyncio.CancelledError()

    async with stream_with_cancellation(mock_stream()) as safe_stream:
        chunks = []
        with pytest.raises(asyncio.CancelledError):
            async for chunk in safe_stream:
                chunks.append(chunk)

    # Should have received the first chunk before cancellation
    assert len(chunks) == 1


@pytest.mark.asyncio
async def test_report_stream_handles_empty_chunks():
    """Test report_stream handles chunks with no content."""
    mock_chunk_empty = MagicMock()
    mock_chunk_empty.content = ""
    mock_chunk_none = MagicMock()
    mock_chunk_none.content = None

    async def mock_stream():
        yield mock_chunk_empty
        yield mock_chunk_none

    # Should not print anything for empty chunks
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        await report_stream(mock_stream())

    output = captured_output.getvalue()
    # Should only have the newline at the end
    assert output == "\n"