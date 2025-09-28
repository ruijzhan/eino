# Python Chat Implementation

This is a Python reimplementation of the Go chat program using LangChain and LangGraph frameworks.

## Features

- **Chat Model Integration**: Support for OpenAI chat models with configurable parameters
- **Message Templating**: Flexible message template system with chat history support
- **Streaming Responses**: Real-time streaming of chat responses
- **Retry Logic**: Automatic retry with exponential backoff for network errors
- **Async Support**: Full async/await support for better performance
- **Type Safety**: Comprehensive type hints throughout the codebase

## Project Structure

```
chat/
├── __init__.py          # Package initialization
├── main.py              # Main entry point
├── model.py             # Model configuration and management
├── generate.py          # Core chat generation functionality
├── stream.py            # Streaming functionality
├── template.py          # Message template functionality
├── tests/               # Test suite
│   ├── __init__.py
│   ├── test_generate.py
│   ├── test_model.py
│   └── test_template.py
├── requirements.txt     # Python dependencies
└── pyproject.toml      # Project configuration
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Or install in development mode:
```bash
pip install -e .
```

## Usage

### Basic Usage

```python
import asyncio
from chat.model import create_openai_chat_model
from chat.template import create_messages_from_template
from chat.generate import generate
from chat.stream import stream, report_stream

async def main():
    # Create messages from template
    messages = create_messages_from_template()

    # Create model
    model = create_openai_chat_model()

    # Generate response
    response = await generate(model, messages)
    print(f"Response: {response.content}")

    # Stream response
    stream_iter = stream(model, messages)
    await report_stream(stream_iter)

if __name__ == "__main__":
    asyncio.run(main())
```

### Environment Variables

Set these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL_NAME`: Model name (default: "gpt-3.5-turbo")
- `OPENAI_BASE_URL`: Custom base URL (optional)

### Running the Example

```bash
export OPENAI_API_KEY="your-api-key-here"
python -m chat.main
```

## Comparison with Go Implementation

| Feature | Go Implementation | Python Implementation |
|---------|------------------|----------------------|
| Framework | Eino framework | LangChain + LangGraph |
| Concurrency | Goroutines + Channels | Asyncio |
| Type Safety | Generics + Compile-time checks | Type hints + Runtime checks |
| Error Handling | Explicit error returns | Exception-based |
| Streaming | StreamReader pattern | Async generators |
| Retry Logic | Manual retry with backoff | Async retry with exponential backoff |
| Templates | Custom template system | LangChain ChatPromptTemplate |

## Testing

Run tests with:
```bash
pytest tests/ -v
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_template.py -v
```

### Code Style

The code follows Python conventions:
- Use `async/await` for async operations
- Type hints for all function signatures
- Docstrings for all modules and public functions
- Follow PEP 8 style guidelines

## Key Components

### Model Management (`model.py`)
- `create_openai_chat_model()`: Creates OpenAI chat model with environment variable support
- Handles configuration validation and defaults

### Generation (`generate.py`)
- `generate()`: Basic generation with timing and logging
- `generate_with_retry()`: Retry logic with exponential backoff
- `is_retryable_error()`: Determines if an error is retryable

### Streaming (`stream.py`)
- `stream()`: Async generator for streaming responses
- `report_stream()`: Utility to process and display streaming chunks

### Templates (`template.py`)
- `create_template()`: Creates LangChain ChatPromptTemplate
- `create_messages_from_template()`: Formats messages with default chat history

## Error Handling

The implementation includes comprehensive error handling:
- Network timeouts and connection errors are automatically retried
- Rate limiting errors are handled with backoff
- Configuration errors provide clear error messages
- All async operations include proper exception handling

## Performance Considerations

- Uses async/await for non-blocking I/O operations
- Streaming reduces latency for large responses
- Connection pooling is handled by the underlying HTTP client
- Retry logic prevents cascading failures during network issues