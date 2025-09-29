# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Go Testing
```bash
# Run all tests with coverage
go test -race -v -coverprofile=coverage.out -gcflags="all=-l -N" ./...

# Run single test file
go test -race -v ./compose/graph_test.go

# Run tests with coverage for specific packages
go test -race -v -coverprofile=coverage.out ./compose/... ./schema/...
```

### Python Testing
```bash
# Run all Python tests
cd python && pytest tests/ -v

# Run specific test file
cd python && pytest tests/test_model.py -v

# Run with coverage
cd python && pytest tests/ --cov=chat --cov-report=html
```

### Linting
```bash
# Go linting
golangci-lint run
goimports -w .
gofmt -w .

# Python linting
cd python && ruff check .
cd python && ruff format .
```

### Go Workspace
The project uses Go workspaces. Initialize with:
```bash
go work init
go work use .
go work sync
```

### Python Environment
```bash
# Setup Python environment
cd python && uv pip install -e ".[dev]"

# Run main application
cd python && python -m chat.main
```

## Architecture Overview

Eino is a dual-language LLM application development framework with Go and Python implementations:

**Recent Features:**
- **Dual Language Support**: Full Python LangChain implementation alongside Go framework
- **Enhanced Error Handling**: Robust retry logic with exponential backoff
- **Improved Streaming**: Context cancellation and I/O error handling
- **Type Safety**: Configuration validation and comprehensive error handling
- **Comprehensive Testing**: Full test coverage including streaming and edge cases

### 1. **Go Implementation** (`./`)
- Native Go framework with three core orchestration patterns
- High performance with goroutine-based concurrency
- Compile-time type safety with generics
- Production-ready with extensive component library

### 2. **Python Implementation** (`python/`)
- LangChain-based implementation for rapid development
- Async-first design with proper error handling
- VS Code debugging support and comprehensive testing
- Seamless interoperability with Go components

### 3. **Graph Orchestration** (`compose/`)
- **Graph**: Generic directed graph with type safety
- **Nodes**: Components (ChatModel, Tool, Retriever, etc.) and Lambda functions
- **Edges**: Data flow and control flow connections
- **State**: Thread-safe state management with pre/post handlers

### 4. **Chain Orchestration** (`compose/`)
- **Chain**: Linear sequence of nodes
- **Parallel Chains**: Concurrent execution patterns
- **Lambda Functions**: Custom logic integration

### 5. **Workflow Orchestration** (`compose/workflow.go`)
- **Field-level mapping**: Structural data transformation between nodes
- **Stateful execution**: Enhanced state management

## Go Implementation Details

### Key Components

#### Core Abstractions (`components/`)
- **model/**: ChatModel implementations (OpenAI, etc.)
- **tool/**: Tool calling and execution
- **retriever/**: Document retrieval
- **embedding/**: Vector embeddings
- **prompt/**: Template management
- **document/**: Document processing

#### Schema Types (`schema/`)
- **message.go**: Message types and streaming
- **stream.go**: StreamReader abstraction for streaming
- **tool.go**: Tool calling schemas

#### Runtime Engine (`compose/`)
- **graph.go**: Core graph compilation and execution
- **graph_manager.go**: Task scheduling and channel management
- **state.go**: State management with mutex protection
- **workflow.go**: Field-level data mapping

### Design Patterns

#### Type Safety
- Heavy use of Go generics for compile-time type checking
- Generic helpers for type inference and conversion
- Field mapping with type validation

#### Concurrency Model
- Goroutine-based node execution
- Channel-based communication
- Thread-safe state with mutex protection
- Task manager with cancellation support

#### Streaming
- **StreamReader**: Unified streaming abstraction
- **Stream concatenation**: Automatic stream chunk handling
- **Stream copying**: Fan-out patterns
- **Stream boxing**: Non-stream to stream conversion

### Graph Execution Modes

#### Pregel Mode (`runTypePregel`)
- Supports cyclic graphs
- AnyPredecessor triggering
- Used for complex agent patterns

#### DAG Mode (`runTypeDAG`)
- Directed acyclic graphs only
- AllPredecessor triggering
- Used for linear workflows

### Node Types
- **Component Nodes**: ChatModel, Tool, Retriever implementations
- **Lambda Nodes**: Custom functions with 4 modes (Invoke, Stream, Collect, Transform)
- **Graph Nodes**: Nested graphs/subgraphs
- **Passthrough Nodes**: Data routing (mostly for Pregel)

### State Management
- **GenLocalState[S]**: State generator function
- **StatePreHandler/PostHandler**: Node-level state processors
- **ProcessState()**: Thread-safe state access API
- Context-based state propagation with mutex protection

## Python Implementation Details

### Core Modules

#### **chat/model.py**
- `ModelConfig`: Type-safe configuration with validation
- `create_openai_chat_model()`: Factory function with retry logic
- Environment variable management with sensible defaults

#### **chat/generate.py**
- `generate()`: Core async generation with timing and logging
- `generate_with_retry()`: Exponential backoff retry logic
- `is_retryable_error()`: Network-aware error classification

#### **chat/stream.py**
- `stream()`: Async generator for real-time streaming
- `report_stream()`: Context cancellation and I/O error handling
- `stream_with_cancellation()`: Graceful stream termination

#### **chat/template.py**
- `create_template()`: LangChain ChatPromptTemplate factory
- `create_messages_from_template()`: Message formatting with chat history

### Key Features

#### Error Handling
- Comprehensive retry logic with exponential backoff
- Network error classification and recovery
- Graceful degradation for non-critical failures
- Context cancellation support

#### Type Safety
- Full type hints throughout the codebase
- `ModelConfig` dataclass with validation
- Runtime type checking where appropriate

#### Testing Strategy
- pytest with comprehensive coverage
- Mock objects for testing without API calls
- Async test support with pytest-asyncio
- Environment isolation with mocked variables

### Dependencies
- **LangChain Core**: Core abstractions and interfaces
- **LangChain OpenAI**: OpenAI model integration
- **Python-dotenv**: Environment variable management
- **pytest**: Testing framework with async support
- **uv**: Fast Python package manager

## Development Notes

### Go Framework
- Uses extensive reflection for type inference
- Heavy emphasis on compile-time type safety
- Streaming is first-class citizen throughout
- Graph compilation validates type compatibility
- State management is opt-in per graph

### Python Implementation
- Async-first design with proper error handling
- LangChain-based for rapid development
- Comprehensive testing with edge cases
- VS Code debugging support
- Modern Python packaging with pyproject.toml

### Key Interfaces to Understand
- `composableRunnable`: Core executable abstraction (Go)
- `AnyGraph`: Graph interface for nesting (Go)
- `Component`: Component type system (Go)
- `StreamReader[I]`: Streaming interface (Go)
- `BaseChatModel`: LangChain model interface (Python)
- `ChatPromptTemplate`: LangChain template interface (Python)