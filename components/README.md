# Components 包

`components` 包为 Eino 框架中的 LLM 应用开发提供基础构建块。它定义了各种 AI/ML 组件的接口与实现，这些组件既可以独立使用，也可以在框架的编排模式中组合使用。

## 概览

该包采用模块化设计，每类组件都在独立的子包中定义，包含：
- 定义契约的核心接口
- 用于配置的可选项
- 辅助函数与工具
- 对回调与可扩展性的支持

## 组件类型

### 1. 模型 (`model/`)

用于语言模型交互的聊天模型组件。

**关键接口：**
- `BaseChatModel`：聊天模型核心接口，提供 Generate 与 Stream 方法
- `ToolCallingChatModel`：扩展接口，支持安全的工具绑定
- `ChatModel`：已弃用接口（请使用 `ToolCallingChatModel`）

**特性：**
- 支持同步与流式推理
- 支持带安全绑定的工具调用
- 可配置参数（temperature、top-p 等）
- 提供用于测试的模拟生成

```go
// 示例用法
model, err := openai.NewChatModel(ctx, &openai.ChatModelConfig{})
response, err := model.Generate(ctx, messages, model.WithTemperature(0.7))
```

### 2. 向量嵌入 (`embedding/`)

用于向量表示的文本嵌入组件。

**关键接口：**
- `Embedder`：将文本转换为向量嵌入的接口

**特性：**
- 批量文本嵌入
- 可配置的嵌入参数
- 一致的向量输出格式

```go
// 示例用法
embedder, err := openai.NewEmbedder(ctx, &openai.EmbedderConfig{})
vectors, err := embedder.EmbedStrings(ctx, []string{"hello", "world"})
```

### 3. 检索器 (`retriever/`)

用于 RAG 应用的文档检索组件。

**关键接口：**
- `Retriever`：基于查询检索文档的接口

**特性：**
- 基于查询的文档检索
- 可配置的检索选项（TopK 等）
- 与向量存储和搜索引擎的集成

```go
// 示例用法
retriever, err := redis.NewRetriever(ctx, &redis.RetrieverConfig{})
docs, err := retriever.Retrieve(ctx, "query", retriever.WithTopK(3))
```

### 4. 工具 (`tool/`)

用于 AI Agent 能力的工具调用组件。

**关键接口：**
- `BaseTool`：基础工具信息接口
- `InvokableTool`：支持同步执行的工具
- `StreamableTool`：支持流式执行的工具

**特性：**
- 工具模式定义
- 基于 JSON 的参数传递
- 支持同步与流式执行模式
- 提供供 LLM 识别意图的工具元信息

```go
// 示例用法
type WeatherTool struct{}
func (t *WeatherTool) Info(ctx context.Context) (*schema.ToolInfo, error) {
    return &schema.ToolInfo{Name: "weather"}, nil
}
func (t *WeatherTool) InvokableRun(ctx context.Context, args string, opts ...tool.Option) (string, error) {
    return "Sunny, 25°C", nil
}
```

### 5. 文档 (`document/`)

用于文档处理的组件。

**关键接口：**
- `Loader`：从多种来源加载文档
- `Transformer`：执行文档转换与处理

**特性：**
- 基于 URI 的文档加载
- 文档转换流水线
- 可配置的处理选项

### 6. 索引器 (`indexer/`)

用于向量存储的文档索引组件。

**关键接口：**
- `Indexer`：将文档存入索引的接口

**特性：**
- 支持带 ID 生成的文档存储
- 集成向量数据库
- 支持批量索引

### 7. 提示词 (`prompt/`)

提示模板组件。

**关键接口：**
- `ChatTemplate`：基于模板生成消息的接口

**特性：**
- 基于模板的消息格式化
- 变量替换
- 支持复杂的提示词结构

## 设计模式

### 可选项模式

每个组件都使用函数式可选项模式进行配置：

```go
// 各组件通用模式
component.DoSomething(ctx, input, component.WithOption(value))
```

### 组件类型识别

组件可实现 `Typer` 接口以进行类型识别：

```go
type Typer interface {
    GetType() string
}
```

### 回调支持

组件可实现 `Checker` 接口以自定义回调行为：

```go
type Checker interface {
    IsCallbacksEnabled() bool
}
```

## 核心抽象

### 组件枚举

该包定义了一组标准的组件类型：

```go
const (
    ComponentOfPrompt      Component = "ChatTemplate"
    ComponentOfChatModel   Component = "ChatModel"
    ComponentOfEmbedding   Component = "Embedding"
    ComponentOfIndexer     Component = "Indexer"
    ComponentOfRetriever   Component = "Retriever"
    ComponentOfLoader      Component = "Loader"
    ComponentOfTransformer Component = "DocumentTransformer"
    ComponentOfTool        Component = "Tool"
)
```

### 流式支持

许多组件通过 schema 包中的 `StreamReader` 接口支持流式处理，实现实时处理与响应生成。

## 使用模式

### 直接使用组件

组件可以独立使用：

```go
// 初始化组件
model := openai.NewChatModel(config)

// 直接使用
response, err := model.Generate(ctx, messages)
```

### 图形集成

组件与框架的编排模式无缝配合：

```go
// 图式组合
graph := compose.NewGraph[inputType, outputType](compose.RunTypeDAG)
graph.AddChatModelNode("model_node", model)
graph.AddRetrieverNode("retriever_node", retriever)
```

## 可扩展性

组件接口设计易于扩展：

1. **自定义实现**：实现核心接口以构建自有组件
2. **可选项**：通过可选项模式添加特定实现的配置项
3. **回调**：借助回调系统自定义行为
4. **元数据**：使用 `Typer` 接口识别组件

## 测试支持

每个组件包都包含用于测试的 mock 生成：

```go
//go:generate mockgen -destination ../../internal/mock/components/model/ChatModel_mock.go --package model -source interface.go
```

## 最佳实践

1. **类型安全**：使用提供的接口与类型定义
2. **可选项**：优先使用函数式可选项模式进行配置
3. **上下文**：始终传递 context 以支持取消与追踪
4. **流式处理**：为长时间运行的操作考虑流式支持
5. **错误处理**：实现完善的错误处理与传播
6. **Mock**：使用生成的 mock 进行单元测试

## 集成示例

组件可在复杂工作流中协同：

```go
// RAG 模式示例
retriever := vector.NewRetriever(config)
model := openai.NewChatModel(modelConfig)

// 在图中使用
graph.AddRetrieverNode("retrieve", retriever)
graph.AddChatModelNode("generate", model)
```

这种模块化设计在保持框架一致性与互操作性的同时，使 AI/ML 组件能够灵活组合。