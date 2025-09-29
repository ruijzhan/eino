# Schema 包

`schema` 包为 Eino 框架提供核心数据结构和接口。该包定义了整个框架在消息处理、流式处理、工具调用以及文档处理过程中使用的基础类型。

## 概览

schema 包是 Eino 的基石，提供：

- **消息类型与模板**：用于聊天交互
- **流式抽象**：用于实时数据处理
- **工具调用模式**：用于函数执行
- **文档结构**：用于检索操作

## 核心组件

### 1. 消息系统 (`message.go`)

#### 消息类型
- **`Message`**：核心聊天消息结构，包含角色、内容以及多模态支持
- **`RoleType`**：消息角色枚举（User、Assistant、System、Tool）
- **`ChatMessagePart`**：多模态消息片段（文本、图像、音频、视频、文件）

#### 消息模板
- **`MessagesTemplate`**：消息模板格式化接口
- **`FormatType`**：模板格式选项（FString、GoTemplate、Jinja2）
- **辅助函数**：
  - `UserMessage()`, `AssistantMessage()`, `SystemMessage()`, `ToolMessage()`
  - `MessagesPlaceholder()`：用于动态插入消息

#### 消息内容
- **多模态支持**：在单条消息中处理文本、图像、音频、视频和文件
- **工具调用**：通过 `ToolCall` 和 `FunctionCall` 结构体支持函数调用
- **响应元数据**：包含令牌使用量、结束原因与对数概率

### 2. 流系统 (`stream.go`)

#### 核心流类型
- **`StreamReader[T]`**：泛型流读取器，用于接收数据
- **`StreamWriter[T]`**：泛型流写入器，用于发送数据
- **`Pipe[T]`**：创建互联的读写器对以进行流式处理

#### 关键特性
- **类型安全**：使用泛型实现编译期类型检查
- **错误处理**：在流中内建错误传播机制
- **资源管理**：通过 `Close()` 方法自动清理
- **并发性**：线程安全的流式操作

#### 常见模式
```go
// 创建一个流管道
sr, sw := schema.Pipe[string](10)

// 生产者 goroutine
go func() {
    defer sw.Close()
    for _, item := range data {
        sw.Send(item, nil)
    }
}()

// 消费者
for chunk, err := sr.Recv() {
    if errors.Is(err, io.EOF) {
        break
    }
    if err != nil {
        // 处理错误
    }
    fmt.Println(chunk)
}
```

### 3. 工具系统 (`tool.go`)

#### 工具定义
- **`ToolInfo`**：完整的工具描述，包含名称、描述与参数
- **`ParameterInfo`**：参数模式，包含类型、校验与必填要求
- **`ParamsOneOf`**：灵活的参数定义（直接模式或 OpenAPI v3）

#### 工具控制
- **`ToolChoice`**：控制工具调用行为（禁止、允许、强制）
- **数据类型**：支持所有 JSON Schema 类型（Object、Number、String、Array 等）

#### 参数定义选项
1. **直接参数**：简洁的参数模式定义
2. **OpenAPI v3**：完全遵循 OpenAPI 规范

### 4. 文档系统 (`document.go`)

#### 文档结构
- **`Document`**：核心文档结构，包含 ID、内容和元数据
- **元数据支持**：内建评分、向量以及自定义数据字段

#### 元数据键
- `_sub_indexes`：搜索引擎的子索引
- `_score`：文档相关性评分
- `_extra_info`：额外文档信息
- `_dense_vector` / `_sparse_vector`：嵌入向量

### 5. 流选择 (`select.go`)

针对最多 5 个并发流进行优化的流选择，使用生成的 select 语句以提升性能。

## 使用模式

### 创建聊天消息
```go
// 简单的文本消息
msg := schema.UserMessage("Hello, how are you?")

// 多模态消息
msg := &schema.Message{
    Role: schema.User,
    MultiContent: []schema.ChatMessagePart{
        {
            Type: schema.ChatMessagePartTypeText,
            Text: "What's in this image?",
        },
        {
            Type: schema.ChatMessagePartTypeImageURL,
            ImageURL: &schema.ChatMessageImageURL{
                URL: "https://example.com/image.jpg",
                Detail: schema.ImageURLDetailHigh,
            },
        },
    },
}
```

### 使用流
```go
// 将切片转换为流
stream := schema.SliceReader([]string{"a", "b", "c"})

// 转换流
transformed := schema.StreamReaderWithConvert(stream, func(s string) (int, error) {
    return len(s), nil
})

// 拼接多个流
concatenated := schema.ConcatReaders(stream1, stream2)
```

### 定义工具
```go
tool := &schema.ToolInfo{
    Name: "weather",
    Desc: "Get weather information for a location",
    ParamsOneOf: schema.NewParamsOneOfByParams(&schema.ParameterInfo{
        Type: schema.Object,
        SubParams: map[string]*schema.ParameterInfo{
            "location": {
                Type:     schema.String,
                Required: true,
                Desc:     "City name or zip code",
            },
            "units": {
                Type: schema.String,
                Enum: []string{"celsius", "fahrenheit"},
                Desc: "Temperature units",
            },
        },
    }),
}
```

### 使用文档
```go
doc := &schema.Document{
    ID:      "doc-001",
    Content: "This is a sample document",
    MetaData: map[string]any{
        "category": "example",
        "author":   "john_doe",
    },
}

// 为相似度搜索添加向量
doc.WithDenseVector([]float32{0.1, 0.2, 0.3})

// 为搜索引擎添加子索引
doc.WithSubIndexes([]string{"main", "archive"})
```

## 设计原则

### 1. 类型安全
- 广泛使用 Go 泛型以实现编译期类型检查
- 清晰区分不同数据类型
- 严谨的接口定义

### 2. 可扩展性
- 各结构体均支持可选字段
- 元数据允许自定义扩展
- 基于接口的设计便于实现

### 3. 性能
- 无额外分配的流式模式
- 使用切片提升内存效率
- 优化并发操作

### 4. 标准遵循
- 工具模式符合 OpenAPI v3 规范
- 数据类型遵循 JSON Schema
- 错误处理遵循标准库模式

## 错误处理

该包采用标准的 Go 错误处理模式：
- `io.EOF`：表示流结束
- `schema.ErrNoValue`：用于过滤流元素
- 自定义错误类型：针对特定场景

## 测试

该包提供全面的测试覆盖以下内容：
- 消息的格式化与解析
- 流操作及边界情况
- 工具模式校验
- 文档元数据处理

## 依赖

主要外部依赖：
- `github.com/nikolalohinski/gonja`：Jinja2 模板
- `github.com/slongfield/pyfmt`：Python f-string 格式化
- `github.com/eino-contrib/jsonschema`：JSON Schema 支持
- `github.com/getkin/kin-openapi`：OpenAPI 规范支持

## 贡献指南

当你在此包上工作时：
1. 遵循 Go 的标准约定
2. 保持向后兼容
3. 为新功能编写完善的测试
4. 为新增类型和函数编写文档