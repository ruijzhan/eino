# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies with uv
uv pip install -r requirements.txt

# Install in development mode with uv
uv pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_template.py -v

# Run single test function
pytest tests/test_model.py::test_create_openai_chat_model_success -v

# Install development dependencies
uv pip install -e ".[dev]"
```

### Installation
```bash
# Install dependencies with uv
uv pip install -r requirements.txt

# Install in development mode with uv
uv pip install -e .
```

### Running the Application
```bash
# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"

# Run the main application
python -m chat.main

# Test launch configuration
python chat/test_launch.py
```

## Architecture Overview

This is a Python LangChain implementation of a chat application that mirrors the functionality of the Go-based Eino framework. The project provides a clean, async-first interface for AI chat interactions with robust error handling and streaming capabilities.

### Core Components

#### **Model Management** (`chat/model.py`)
- `create_openai_chat_model()`: Factory function for OpenAI chat models
- Environment variable configuration with sensible defaults
- Type-safe model creation with validation

#### **Message Generation** (`chat/generate.py`)
- `generate()`: Core async generation with timing and logging
- `generate_with_retry()`: Retry logic with exponential backoff
- `is_retryable_error()`: Network-aware error classification
- Built-in support for timeout, connection, and rate limit errors

#### **Streaming** (`chat/stream.py`)
- `stream()`: Async generator for real-time response streaming
- `report_stream()`: Utility for processing and displaying streamed content
- Non-blocking I/O for improved user experience

#### **Templates** (`chat/template.py`)
- `create_template()`: LangChain ChatPromptTemplate factory
- `create_messages_from_template()`: Message formatting with chat history
- Default "programmer encouragement" persona with Chinese language support

### Key Design Patterns

#### **Async/Await Pattern**
- All I/O operations use async/await for non-blocking execution
- Async generators for streaming responses
- Proper exception handling in async context

#### **Type Safety**
- Comprehensive type hints throughout the codebase
- LangChain type abstractions for model interoperability
- Runtime type validation where appropriate

#### **Error Handling**
- Retry logic for transient network failures
- Clear error messages for configuration issues
- Graceful degradation for non-critical failures

#### **Configuration Management**
- Environment variable-based configuration
- Sensible defaults with override capability
- Validation for required parameters

### Testing Strategy

The project uses pytest with comprehensive test coverage:

- **Unit Tests**: Each module has dedicated test files
- **Mock Objects**: Custom mock models for testing without API calls
- **Async Testing**: Full async test support with pytest-asyncio
- **Environment Isolation**: Tests use mocked environment variables

### Dependencies

- **LangChain Core**: Core abstractions and interfaces
- **LangChain OpenAI**: OpenAI model integration
- **LangGraph**: Graph-based orchestration (future enhancement)
- **Python-dotenv**: Environment variable management
- **pytest**: Testing framework with async support

### Development Environment

The project is structured as a Python package with:
- Modern pyproject.toml configuration
- Separate development dependencies
- Virtual environment support (.venv)
- Test launch verification script
- **uv**: Fast Python package manager for dependency management

### Key Differences from Go Implementation

| Aspect | Go Implementation | Python Implementation |
|--------|-------------------|----------------------|
| **Framework** | Custom Eino framework | LangChain + LangGraph |
| **Concurrency** | Goroutines + Channels | Asyncio |
| **Type System** | Compile-time generics | Runtime type hints |
| **Error Handling** | Explicit error returns | Exception-based |
| **Streaming** | StreamReader pattern | Async generators |
| **Configuration** | Struct-based | Environment variables |