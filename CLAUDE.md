# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
```bash
# Run all tests with coverage
go test -race -v -coverprofile=coverage.out -gcflags="all=-l -N" ./...

# Run single test file
go test -race -v ./compose/graph_test.go

# Run tests with coverage for specific packages
go test -race -v -coverprofile=coverage.out ./compose/... ./schema/...
```

### Linting
```bash
# Run golangci-lint (uses .golangci.yaml config)
golangci-lint run

# Format imports
goimports -w .

# Format code
gofmt -w .
```

### Go Workspace
The project uses Go workspaces. Initialize with:
```bash
go work init
go work use .
go work sync
```

## Architecture Overview

Eino is a Go-based LLM application development framework with three core orchestration patterns:

### 1. **Graph Orchestration** (`compose/`)
- **Graph**: Generic directed graph with type safety
- **Nodes**: Components (ChatModel, Tool, Retriever, etc.) and Lambda functions
- **Edges**: Data flow and control flow connections
- **State**: Thread-safe state management with pre/post handlers

### 2. **Chain Orchestration** (`compose/`)
- **Chain**: Linear sequence of nodes
- **Parallel Chains**: Concurrent execution patterns
- **Lambda Functions**: Custom logic integration

### 3. **Workflow Orchestration** (`compose/workflow.go`)
- **Field-level mapping**: Structural data transformation between nodes
- **Stateful execution**: Enhanced state management

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

### Key Interfaces to Understand
- `composableRunnable`: Core executable abstraction
- `AnyGraph`: Graph interface for nesting
- `Component`: Component type system
- `StreamReader[I]`: Streaming interface

### Development Notes
- Framework uses extensive reflection for type inference
- Heavy emphasis on type safety at compile time
- Streaming is first-class citizen throughout
- Graph compilation validates type compatibility
- State management is opt-in per graph