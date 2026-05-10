# 第 12 课：Spring Boot + Spring AI

## 0. 本课阅读方式

本课开始把 AI 能力接入 Java/Spring Boot 应用。你需要把 Spring AI 理解为：

```text
Spring 生态中连接大模型、Embedding、VectorStore、工具调用和 RAG 的应用框架。
```

本课不是让你死记某个配置项，而是理解：

```text
Spring AI 在 Java 项目中解决什么问题？
ChatClient 是什么？
Prompt、Message、Model、Advisor、VectorStore 分别是什么？
Spring AI 如何做工具调用和 RAG？
Spring Boot 项目中哪些部分仍然要自己负责？
```

【核心】Spring AI 不是替你设计业务系统，它提供 AI 能力接入抽象；权限、日志、异常、成本和业务规则仍然由你的应用负责。

## 0.1 概念讲义：Spring AI 术语详解

### 0.1.1 第 12 课到底在学什么

前面的课程讲的是 AI 概念。本课回答 Java 开发者最关心的问题：

```text
如何把大模型能力接入 Spring Boot 系统？
```

Spring AI 可以帮助你统一：

- Chat Model 调用。
- Prompt 构造。
- Embedding 调用。
- VectorStore 集成。
- Tool Calling。
- RAG 流程。
- Advisor 拦截和增强。

【重点】Spring AI 适合熟悉 Spring Boot 的 Java 开发者做 AI 应用工程化。

### 0.1.2 Spring AI

Spring AI 是 Spring 生态的 AI 应用框架。

它提供统一抽象，连接不同模型提供商和 AI 能力。

【核心】Spring AI 的价值是把 AI 能力纳入 Spring Boot 熟悉的编程模型。

### 0.1.3 Chat Model

Chat Model 是聊天模型抽象。

它代表可以接收对话消息并返回模型响应的模型。

【重点】不同厂商模型通过统一接口接入，降低切换成本。

### 0.1.4 ChatClient

ChatClient 是 Spring AI 中更高层的聊天调用客户端。

它用于构造：

- system prompt。
- user prompt。
- 参数。
- advisor。
- tool。
- 返回解析。

【核心】ChatClient 是 Spring AI 中构建大模型调用链的常用入口。

### 0.1.5 Prompt

Prompt 是发送给模型的完整输入。

在 Spring AI 中，Prompt 可以由多个 Message 组成。

### 0.1.6 Message

Message 是对话中的一条消息。

常见角色：

- System。
- User。
- Assistant。
- Tool。

### 0.1.7 PromptTemplate

PromptTemplate 是提示词模板。

用于把变量填入固定提示词结构。

例如：

```text
请根据以下资料回答问题：
资料：{context}
问题：{question}
```

【重点】业务系统中应把稳定 Prompt 模板化，而不是散落在代码中。

### 0.1.8 Advisor

Advisor 是对 ChatClient 调用过程进行增强的组件。

可以用于：

- RAG 检索增强。
- 对话记忆。
- 日志。
- 参数增强。
- 上下文注入。

【核心】Advisor 类似 AI 调用链上的拦截器或增强器。

### 0.1.9 Embedding Model

Embedding Model 用于把文本转换成向量。

Spring AI 提供 Embedding 抽象，便于接入不同模型。

### 0.1.10 VectorStore

VectorStore 是向量存储抽象。

它用于：

- 写入文档向量。
- 相似度检索。
- metadata 过滤。

【重点】VectorStore 是 Spring AI RAG 的关键组件。

### 0.1.11 Document

Document 是 Spring AI 中表示文本内容和 metadata 的对象。

它通常包含：

- content。
- metadata。

### 0.1.12 ETL Pipeline

ETL Pipeline 是文档入库流程。

```text
Extract：读取文档
Transform：清洗和切分
Load：写入向量库
```

【核心】RAG 的离线入库可以按 ETL 思想组织。

### 0.1.13 Tool Calling

Spring AI 支持把 Java 方法暴露为模型可调用工具。

常见方式：

- `@Tool` 注解。
- ToolCallback。

【核心】工具执行仍然在 Java 应用侧完成。

### 0.1.14 本课重点标注汇总

【核心】Spring AI 是 Java/Spring 生态中的 AI 应用抽象层。

【核心】ChatClient 是模型调用的常用入口。

【核心】VectorStore + Embedding + Advisor 可以组合出 RAG。

【核心】Tool Calling 中，Java 后端负责真正执行业务逻辑。

【重点】Prompt 应模板化、版本化、可测试。

【重点】Spring AI 不替代权限、日志、异常和成本控制。

【易错】不要把模型输出直接当成可信业务结果。

### 0.1.15 自我检查问题

1. Spring AI 解决什么问题？
2. ChatModel 和 ChatClient 有什么区别？
3. Prompt 和 Message 有什么关系？
4. PromptTemplate 有什么价值？
5. Advisor 类似什么？
6. VectorStore 在 RAG 中负责什么？
7. Document metadata 为什么重要？
8. Spring AI Tool Calling 中谁执行工具？
9. Java 系统还需要负责哪些工程能力？

## 1. 本课目标

学完本课后，你应该能够：

1. 解释 Spring AI 在 Java AI 应用中的定位。
2. 理解 ChatClient、Prompt、Message、Advisor。
3. 理解 EmbeddingModel、VectorStore、Document。
4. 设计 Spring Boot + Spring AI 的 RAG 架构。
5. 设计 Spring AI 工具调用边界。
6. 说明生产系统中权限、日志、成本、异常处理责任。

## 2. Spring Boot + Spring AI 架构

```text
Controller
  -> Service
  -> ChatClient
      -> Advisor / Tool / VectorStore
      -> Chat Model
  -> 返回结果
```

RAG 架构：

```text
文档入库：
  DocumentReader -> TextSplitter -> EmbeddingModel -> VectorStore

问答：
  User Question -> Retriever/Advisor -> Prompt -> ChatModel -> Answer
```

## 3. ChatClient 使用思路

ChatClient 负责构造模型调用。

概念示例：

```java
String answer = chatClient.prompt()
    .system("你是企业知识库助手。")
    .user("如何申请年假？")
    .call()
    .content();
```

你要理解：

```text
system 放稳定行为规则。
user 放当前用户问题。
call 触发模型调用。
content 获取文本结果。
```

## 4. RAG 在 Spring AI 中的组成

RAG 需要：

- 文档读取。
- 文本切分。
- Embedding。
- VectorStore。
- 检索增强。
- Prompt 组装。
- 模型回答。

【核心】Spring AI 提供组件，但 RAG 质量仍取决于文档、切分、检索和评估。

## 5. Tool Calling 在 Spring AI 中的角色

Java 方法可以作为工具暴露给模型。

例如：

```java
@Tool(description = "根据订单号查询订单状态")
public OrderStatus getOrderStatus(String orderId) {
    return orderService.getStatus(orderId);
}
```

【重点】工具方法内部必须复用原有业务权限和校验逻辑。

## 6. 生产工程关注点

Spring AI 应用上线要考虑：

1. API 鉴权。
2. 用户权限。
3. Prompt 版本。
4. 模型参数。
5. Token 成本。
6. 调用延迟。
7. 日志审计。
8. 异常兜底。
9. 输出校验。
10. 数据安全。

【工程经验】AI 调用应该像外部依赖一样被治理：超时、重试、限流、监控都不能少。

## 7. 常见误区

1. 以为引入 Spring AI 就自动有完整智能应用。
2. Prompt 写死在 Controller。
3. 不记录模型调用日志。
4. 不做输出校验。
5. 工具调用绕过权限。
6. RAG 不做评估。
7. 文档更新后不刷新向量库。

## 8. 实践任务

1. 画出 Spring Boot + Spring AI 聊天架构。
2. 设计一个 ChatClient 调用流程。
3. 设计一个 PromptTemplate。
4. 设计一个 VectorStore 文档 metadata。
5. 设计一个工具方法和权限校验。
6. 设计模型调用日志字段。

## 9. 自测题

1. Spring AI 和 Spring Boot 的关系是什么？
2. ChatClient 解决什么问题？
3. Advisor 能做什么？
4. VectorStore 在 RAG 中是什么角色？
5. `@Tool` 方法为什么仍需要权限校验？
6. PromptTemplate 为什么要版本化？
7. AI 调用日志应记录什么？

## 10. 阶段验收标准

完成本课后，你应该能做到：

1. 能解释 Spring AI 核心抽象。
2. 能设计 ChatClient 调用链。
3. 能设计 Spring AI RAG 组件关系。
4. 能设计工具调用安全边界。
5. 能说明生产工程治理点。

## 11. 本课使用的信息源

- Spring AI Reference Documentation：总体架构、模型、ChatClient、Prompt、Advisor、VectorStore。
- Spring AI Chat Client API：`ChatClient`、系统提示、用户提示、响应处理。
- Spring AI Prompts 文档：Prompt、Message、PromptTemplate。
- Spring AI Tool Calling 文档：`@Tool`、`ToolCallback`、工具调用。
- Spring AI Vector Databases 文档：VectorStore 和向量数据库集成。
- Spring AI ETL Pipeline 文档：文档读取、转换、切分、向量化入库。

