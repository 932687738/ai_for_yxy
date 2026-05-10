# 项目 12：Spring Boot + Spring AI 架构设计

对应课程：第 12 课《Spring Boot + Spring AI》

## 1. 项目目标

设计一个 Spring Boot + Spring AI 智能知识库助手的工程架构。

## 2. 术语报告

创建：

```text
reports/spring_ai_concepts.md
```

解释：

- Spring AI
- Chat Model
- ChatClient
- Prompt
- Message
- PromptTemplate
- Advisor
- EmbeddingModel
- VectorStore
- Document
- ETL Pipeline
- Tool Calling
- `@Tool`
- ToolCallback

## 3. 架构设计

画出：

```text
Controller -> Service -> ChatClient -> Advisor / Tool / VectorStore -> Model
```

并说明每层职责。

## 4. RAG 设计

设计：

- 文档读取。
- 文档切分。
- Embedding。
- VectorStore。
- 检索增强。
- PromptTemplate。
- 引用来源。

## 5. 工具调用设计

设计两个工具：

- 查询订单状态。
- 创建客服工单。

说明：

- 参数。
- 返回。
- 权限。
- 是否需要人工确认。

## 6. 日志字段设计

模型调用日志至少包含：

- userId
- conversationId
- model
- promptVersion
- inputTokens
- outputTokens
- latency
- toolCalls
- retrievedDocs
- errorCode

## 7. 验收清单

- [ ] 能解释 Spring AI 定位。
- [ ] 能解释 ChatClient。
- [ ] 能解释 Advisor。
- [ ] 能解释 VectorStore。
- [ ] 能设计 Spring AI RAG 架构。
- [ ] 能设计工具调用权限边界。
- [ ] 能设计模型调用日志。

