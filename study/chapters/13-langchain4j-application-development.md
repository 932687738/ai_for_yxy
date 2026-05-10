# 第 13 课：LangChain4j 应用开发

## 0. 本课阅读方式

LangChain4j 是 Java 生态中常用的大模型应用开发框架。它和 Spring AI 一样，目标都是帮助 Java 开发者更方便地接入大模型、工具、记忆、RAG 等能力。

本课重点不是比较“谁更好”，而是理解 LangChain4j 的核心抽象：

```text
ChatModel
AI Services
Tools
ChatMemory
EmbeddingModel
EmbeddingStore
ContentRetriever
RetrievalAugmentor
Spring Boot Integration
```

【核心】LangChain4j 的一个重要特点是通过 Java 接口定义 AI Service，让模型调用更像调用业务服务。

## 0.1 概念讲义：LangChain4j 术语详解

### 0.1.1 第 13 课到底在学什么

本课回答：

```text
如何用 LangChain4j 在 Java 中构建 LLM 应用？
```

核心场景：

- 聊天助手。
- 智能客服。
- 工具调用。
- RAG 知识库。
- 结构化输出。
- 多轮对话记忆。
- Spring Boot 集成。

### 0.1.2 LangChain4j

LangChain4j 是面向 Java 的 LLM 应用开发框架。

它提供：

- 模型抽象。
- AI Services。
- 工具调用。
- 记忆。
- RAG。
- Embedding。
- 向量存储。
- Spring Boot 集成。

【核心】LangChain4j 帮助 Java 开发者用熟悉的接口和对象构建 LLM 应用。

### 0.1.3 ChatModel

ChatModel 是聊天模型抽象。

它接收消息并返回模型回复。

【重点】ChatModel 是最基础的模型调用入口。

### 0.1.4 StreamingChatModel

StreamingChatModel 支持流式输出。

适合：

- 聊天界面。
- 长回答。
- 用户体验要求高的场景。

【工程经验】智能客服通常需要流式输出提升体验。

### 0.1.5 AI Services

AI Services 是 LangChain4j 的高级抽象。

你可以定义 Java 接口，让 LangChain4j 生成实现。

概念示例：

```java
interface Assistant {
    String chat(String userMessage);
}
```

【核心】AI Services 把大模型交互包装成 Java 接口调用。

### 0.1.6 SystemMessage

SystemMessage 用于定义助手角色、规则和行为边界。

在 AI Services 中，可以通过注解或配置定义。

### 0.1.7 UserMessage

UserMessage 表示用户输入。

AI Service 方法参数通常会映射为用户消息或变量。

### 0.1.8 Tools

Tools 是暴露给模型使用的 Java 方法。

通过 `@Tool` 可以声明工具。

【核心】工具执行仍然发生在 Java 应用内部。

### 0.1.9 ChatMemory

ChatMemory 用于保存对话历史。

常见实现：

- MessageWindowChatMemory：保留最近 N 条消息。
- TokenWindowChatMemory：按 token 数保留历史。

【重点】记忆不是越多越好，要控制成本和隐私风险。

### 0.1.10 EmbeddingModel

EmbeddingModel 把文本转成向量。

用于：

- 语义搜索。
- RAG。
- 相似度匹配。

### 0.1.11 EmbeddingStore

EmbeddingStore 是向量存储抽象。

它保存：

- embedding。
- 原始文本。
- metadata。

### 0.1.12 ContentRetriever

ContentRetriever 是检索器。

给定用户问题，返回相关内容。

【核心】RAG 中 ContentRetriever 决定模型能看到哪些知识。

### 0.1.13 RetrievalAugmentor

RetrievalAugmentor 用于把检索结果增强到模型输入中。

它连接：

```text
用户问题 -> 检索 -> 上下文增强 -> 模型回答
```

### 0.1.14 DocumentSplitter

DocumentSplitter 用于切分文档。

类似 RAG 中的 Text Splitter。

### 0.1.15 Spring Boot Integration

LangChain4j 提供 Spring Boot 集成，方便通过配置和 Bean 管理模型、服务、工具等组件。

【重点】在 Spring Boot 项目中，LangChain4j 组件应和原有权限、日志、配置体系集成。

### 0.1.16 本课重点标注汇总

【核心】AI Services 让 LLM 调用像 Java 接口调用。

【核心】Tools 把 Java 方法暴露给模型，但执行和校验仍在应用侧。

【核心】ChatMemory 解决多轮对话历史，但要控制长度和隐私。

【核心】ContentRetriever 和 RetrievalAugmentor 是 LangChain4j RAG 的关键抽象。

【重点】流式输出适合聊天体验。

【重点】Spring Boot 集成不等于自动完成权限、日志和安全治理。

### 0.1.17 自我检查问题

1. LangChain4j 解决什么问题？
2. ChatModel 和 AI Services 有什么区别？
3. AI Services 为什么适合 Java 开发者？
4. `@Tool` 方法由谁执行？
5. ChatMemory 有什么风险？
6. ContentRetriever 在 RAG 中做什么？
7. RetrievalAugmentor 做什么？
8. LangChain4j 和 Spring Boot 如何集成？

## 1. 本课目标

学完本课后，你应该能够：

1. 解释 LangChain4j 的定位。
2. 理解 ChatModel、StreamingChatModel、AI Services。
3. 理解 Tools、ChatMemory、EmbeddingModel、EmbeddingStore。
4. 理解 ContentRetriever、RetrievalAugmentor、DocumentSplitter。
5. 设计 LangChain4j 智能客服或知识库助手架构。
6. 说明 LangChain4j 与 Spring Boot 的集成关注点。

## 2. LangChain4j 应用架构

```text
Controller
  -> AI Service Interface
      -> ChatModel / StreamingChatModel
      -> Tools
      -> ChatMemory
      -> RetrievalAugmentor
          -> ContentRetriever
          -> EmbeddingStore
```

【核心】AI Services 是面向业务代码的入口，底层组合模型、工具、记忆和 RAG。

## 3. AI Services 设计

AI Services 的优势：

- 接口化。
- 易测试。
- 贴近 Java 编程习惯。
- 可组合工具和记忆。
- 可定义系统消息和用户消息。

概念示例：

```java
interface CustomerSupportAssistant {
    String chat(String userMessage);
}
```

【重点】AI Service 接口应表达业务能力，而不是暴露底层模型细节。

## 4. Tools 设计

工具适合：

- 查询订单。
- 查询库存。
- 创建工单。
- 查询用户权益。
- 调用业务规则。

工具不适合：

- 无权限校验地修改数据。
- 暴露高风险内部接口。
- 执行不可逆操作。

## 5. ChatMemory 设计

多轮对话需要记忆。

但记忆会带来：

- token 成本。
- 隐私风险。
- 上下文污染。
- 历史错误影响当前回答。

【工程经验】只保留完成任务所需的最小记忆。

## 6. RAG 设计

LangChain4j RAG 关键组件：

```text
Document
DocumentSplitter
EmbeddingModel
EmbeddingStore
ContentRetriever
RetrievalAugmentor
AI Service
```

流程：

```text
用户问题
  -> ContentRetriever 检索
  -> RetrievalAugmentor 增强上下文
  -> AI Service 调用模型
  -> 返回答案
```

## 7. Spring Boot 集成关注点

需要考虑：

1. 配置管理。
2. Bean 生命周期。
3. API 鉴权。
4. 用户权限。
5. 对话 ID。
6. 日志审计。
7. 流式输出。
8. 异常处理。
9. 模型调用成本。
10. 工具调用安全。

## 8. LangChain4j 与 Spring AI 对比视角

| 维度 | LangChain4j | Spring AI |
|---|---|---|
| 编程风格 | AI Services 接口抽象突出 | Spring 风格统一抽象突出 |
| 工具调用 | `@Tool` | `@Tool` / ToolCallback |
| RAG | ContentRetriever / RetrievalAugmentor | Advisor / VectorStore / ETL |
| Spring 集成 | 支持 Spring Boot | Spring 官方生态 |

【重点】选择框架时应看团队技术栈、生态、维护成本和业务需求。

## 9. 常见误区

1. 把 AI Service 设计得过于底层。
2. ChatMemory 不设边界。
3. 工具调用不做权限校验。
4. RAG 不做评估。
5. 流式输出不处理异常中断。
6. 框架替代了架构设计。

## 10. 实践任务

1. 设计一个智能客服 AI Service 接口。
2. 设计两个 `@Tool` 工具。
3. 设计 ChatMemory 策略。
4. 设计 RAG 组件关系。
5. 设计 Spring Boot Controller 到 AI Service 的调用流程。
6. 设计日志和审计字段。

## 11. 自测题

1. LangChain4j 的核心定位是什么？
2. AI Services 有什么价值？
3. ChatModel 和 StreamingChatModel 区别是什么？
4. ChatMemory 为什么不能无限增长？
5. ContentRetriever 做什么？
6. RetrievalAugmentor 做什么？
7. `@Tool` 方法需要哪些安全控制？
8. LangChain4j 和 Spring AI 如何选择？

## 12. 阶段验收标准

完成本课后，你应该能做到：

1. 能解释 LangChain4j 核心抽象。
2. 能设计 AI Service。
3. 能设计工具调用。
4. 能设计对话记忆。
5. 能设计 RAG 组件。
6. 能说明 Spring Boot 集成注意事项。

## 13. 本课使用的信息源

- LangChain4j Documentation：总体概念、模型、AI Services、RAG、工具、记忆。
- LangChain4j AI Services 文档：接口式 AI 服务、声明式方法、结构化返回。
- LangChain4j Tools 文档：`@Tool`、工具调用、函数调用。
- LangChain4j RAG 文档：ContentRetriever、EmbeddingStore、DocumentSplitter、RetrievalAugmentor。
- LangChain4j Memory 文档：ChatMemory、MessageWindowChatMemory。
- LangChain4j Spring Boot Integration 文档：Spring Boot Starter、自动配置、模型 Bean 集成。

