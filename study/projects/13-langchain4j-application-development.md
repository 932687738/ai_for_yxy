# 项目 13：LangChain4j 应用架构设计

对应课程：第 13 课《LangChain4j 应用开发》

## 1. 项目目标

设计一个基于 LangChain4j 的智能客服或知识库助手。

## 2. 术语报告

创建：

```text
reports/langchain4j_concepts.md
```

解释：

- LangChain4j
- ChatModel
- StreamingChatModel
- AI Services
- SystemMessage
- UserMessage
- Tools
- `@Tool`
- ChatMemory
- MessageWindowChatMemory
- EmbeddingModel
- EmbeddingStore
- ContentRetriever
- RetrievalAugmentor
- DocumentSplitter
- Spring Boot Integration

## 3. AI Service 设计

设计接口：

```java
interface CustomerSupportAssistant {
    String chat(String userId, String message);
}
```

说明：

- 方法参数含义。
- 是否需要会话 ID。
- 是否需要流式输出。
- 返回值格式。

## 4. 工具设计

设计三个工具：

- 查询订单状态。
- 查询用户权益。
- 创建客服工单。

说明权限、参数、返回和风险。

## 5. 记忆设计

回答：

1. 保留多少轮对话？
2. 是否按用户隔离？
3. 是否需要持久化？
4. 如何避免隐私泄露？
5. 如何清理过期记忆？

## 6. RAG 设计

设计：

- DocumentSplitter。
- EmbeddingModel。
- EmbeddingStore。
- ContentRetriever。
- RetrievalAugmentor。
- AI Service。

## 7. Spring Boot 集成设计

画出：

```text
Controller -> Service -> AI Service -> Model / Tools / RAG / Memory
```

并说明每一层职责。

## 8. 验收清单

- [ ] 能解释 LangChain4j。
- [ ] 能解释 AI Services。
- [ ] 能设计 `@Tool`。
- [ ] 能设计 ChatMemory。
- [ ] 能设计 RAG 组件。
- [ ] 能说明 Spring Boot 集成方式。
- [ ] 能说明 LangChain4j 和 Spring AI 差异。

