# 第 11 课：Function Calling、Tool Calling 与 Agent

## 0. 本课阅读方式

本课进入“大模型会使用外部能力”的阶段。你需要先建立一个非常重要的认知：

```text
模型不会真的执行工具。
模型只是根据上下文提出“我想调用哪个工具，以及参数是什么”。
真正执行工具的是你的应用程序。
```

建议学习顺序：

```text
先理解 Function Calling / Tool Calling
  -> 理解工具定义、工具调用、工具结果
  -> 理解应用侧执行和安全校验
  -> 再理解 Agent 是如何循环使用工具完成任务
  -> 最后再看 Java/Spring 和 LangChain4j 的工具抽象
```

【核心】Tool Calling 的本质是“模型决策 + 应用执行 + 结果回传”。

## 0.1 概念讲义：工具调用与 Agent 术语详解

### 0.1.1 第 11 课到底在学什么

前面 RAG 解决的是“给模型外部知识”。本课解决的是“让模型请求外部动作”。

例如用户问：

```text
帮我查一下订单 A10086 的物流状态。
```

模型本身不知道实时订单状态，因此需要工具：

```text
getOrderShippingStatus(orderId)
```

流程是：

```text
用户问题
  -> 模型判断需要查订单
  -> 模型输出工具调用请求
  -> 应用执行订单查询
  -> 应用把查询结果回传给模型
  -> 模型组织最终回答
```

【重点】工具调用让大模型从“只会生成文本”扩展到“能连接业务系统”。

### 0.1.2 Function Calling

Function Calling 是让模型按照函数 schema 生成函数调用请求。

它通常包括：

- 函数名。
- 函数描述。
- 参数 JSON Schema。
- 模型生成的参数。
- 应用执行后的结果。

【核心】Function Calling 不是模型直接调用函数，而是模型生成结构化调用意图。

### 0.1.3 Tool Calling

Tool Calling 是更通用的说法，工具可以是：

- Java 方法。
- HTTP API。
- 数据库查询。
- 搜索服务。
- RAG 检索。
- 工作流操作。
- 文件处理。
- MCP 工具。

【重点】Function Calling 通常是 Tool Calling 的一种具体形式。

### 0.1.4 Tool

Tool 是提供给模型可选择的外部能力。

一个好的工具定义应该包含：

```text
工具名称
工具描述
参数定义
参数约束
返回结果含义
错误情况
安全边界
```

【易错】工具描述写得模糊，模型就容易选错工具或填错参数。

### 0.1.5 Tool Schema

Tool Schema 定义工具参数结构。

例如：

```json
{
  "type": "object",
  "properties": {
    "orderId": {
      "type": "string",
      "description": "订单编号"
    }
  },
  "required": ["orderId"]
}
```

【核心】Schema 是模型和应用之间的参数契约。

### 0.1.6 Tool Call

Tool Call 是模型提出的工具调用请求。

它通常包含：

- 工具名。
- 参数。
- 调用 ID。

【重点】应用收到 Tool Call 后，必须先校验参数和权限，再执行。

### 0.1.7 Tool Call Output

Tool Call Output 是应用执行工具后返回给模型的结果。

例如：

```json
{
  "orderId": "A10086",
  "status": "运输中",
  "latestLocation": "上海分拨中心"
}
```

【核心】模型需要工具结果才能生成最终回答。

### 0.1.8 tool_choice

`tool_choice` 用于控制模型是否调用工具或调用哪个工具。

常见策略：

- 自动选择。
- 强制调用某个工具。
- 禁止调用工具。

【重点】工具选择策略会影响成本、稳定性和安全性。

### 0.1.9 Strict Mode

Strict Mode 用于要求模型严格遵守参数 schema。

价值：

- 降低参数格式错误。
- 便于后端校验。
- 适合生产系统。

【工程经验】业务关键工具应尽量使用严格参数校验。

### 0.1.10 Agent

Agent 是能根据目标进行多步决策、使用工具、观察结果并继续行动的系统。

简单问答：

```text
用户问 -> 模型答
```

Agent：

```text
用户给目标
  -> 模型计划
  -> 调工具
  -> 观察结果
  -> 再决定下一步
  -> 直到完成或停止
```

【核心】Agent 不是单次模型调用，而是“模型 + 工具 + 状态 + 控制循环”。

### 0.1.11 Agent Loop

Agent Loop 是 Agent 的执行循环：

```text
观察
  -> 思考或决策
  -> 选择工具
  -> 执行工具
  -> 获取结果
  -> 更新状态
  -> 判断是否结束
```

【重点】Agent 系统必须有停止条件，否则可能无限循环或成本失控。

### 0.1.12 Planning

Planning 是让模型拆解任务步骤。

例如：

```text
1. 查询订单信息
2. 查询物流状态
3. 判断是否延迟
4. 生成客服回复
```

【易错】不是所有任务都需要复杂 planning。简单工具调用不必强行做 Agent。

### 0.1.13 Memory

Memory 是 Agent 或对话系统保存历史上下文的机制。

类型：

- 短期对话记忆。
- 长期用户偏好。
- 任务状态。
- 工具执行记录。

【工程经验】记忆要设计边界，不能无脑保存所有内容。

### 0.1.14 Observation

Observation 是工具执行后的结果或环境反馈。

Agent 根据 observation 决定下一步。

例如：

```text
工具返回：订单不存在
下一步：询问用户确认订单号
```

### 0.1.15 Guardrails

Guardrails 是保护机制。

包括：

- 参数校验。
- 权限校验。
- 工具白名单。
- 最大调用次数。
- 超时控制。
- 人工确认。
- 敏感操作拦截。

【核心】Agent 越能行动，越需要 Guardrails。

### 0.1.16 Human-in-the-loop

Human-in-the-loop 是关键操作前需要人工确认。

例如：

- 发送邮件。
- 删除数据。
- 退款。
- 提交审批。
- 修改订单。

【工程经验】只读工具可以自动执行，写操作和高风险操作通常需要人工确认。

### 0.1.17 MCP

MCP 是 Model Context Protocol，用于把外部工具和上下文以统一协议暴露给模型或 Agent。

【重点】MCP 可以降低工具接入碎片化，但仍需要权限和安全设计。

### 0.1.18 本课重点标注汇总

【核心】模型不会直接执行工具，应用程序负责执行。

【核心】工具 schema 是模型和业务系统之间的契约。

【核心】工具调用必须做参数校验、权限校验和错误处理。

【核心】Agent = 模型 + 工具 + 状态 + 控制循环。

【重点】简单工具调用不等于 Agent。

【重点】Agent 必须有停止条件、预算控制和审计日志。

【易错】不要把高风险写操作直接交给模型自动执行。

【工程经验】先做只读工具，再逐步开放写操作。

### 0.1.19 自我检查问题

1. Function Calling 和 Tool Calling 有什么关系？
2. 模型会真的执行工具吗？
3. Tool Schema 解决什么问题？
4. Tool Call Output 为什么要回传给模型？
5. 什么是 Agent？
6. Agent 和普通聊天有什么区别？
7. Agent Loop 包含哪些步骤？
8. 为什么 Agent 需要 Guardrails？
9. 哪些工具需要人工确认？
10. Java 后端在工具调用中负责什么？

## 1. 本课目标

学完本课后，你应该能够：

1. 解释 Function Calling、Tool Calling、Agent 的区别。
2. 设计工具名称、描述和参数 schema。
3. 理解工具调用的多轮流程。
4. 说明应用侧执行、校验和错误处理责任。
5. 解释 Agent Loop、Planning、Memory、Observation。
6. 设计工具安全边界和人工确认策略。
7. 从 Java/Spring 系统角度理解工具调用落地。

## 2. 工具调用完整流程

```text
1. 应用把可用工具列表发给模型
2. 用户提出任务
3. 模型判断是否需要工具
4. 模型输出 Tool Call
5. 应用校验工具名和参数
6. 应用执行工具
7. 应用把 Tool Call Output 发回模型
8. 模型基于工具结果生成最终回答
```

【核心】工具调用是多步交互，不是一次请求就结束。

## 3. 工具设计原则

### 3.1 工具名称清晰

不好：

```text
query
doAction
handle
```

较好：

```text
get_order_shipping_status
search_employee_policy
create_refund_request
```

### 3.2 工具描述明确

描述应说明：

- 什么时候使用。
- 输入参数含义。
- 返回什么。
- 不适合什么场景。

### 3.3 参数尽量结构化

参数应该使用明确类型和约束。

避免：

```text
input: string
```

更好：

```text
orderId: string
includeHistory: boolean
```

## 4. Agent 设计边界

Agent 适合：

- 多步骤任务。
- 需要根据中间结果决策。
- 需要多个工具协作。
- 任务路径不固定。

不适合：

- 简单问答。
- 单次固定 API 调用。
- 高风险无监督操作。
- 强合规确定性流程。

【重点】能不用 Agent 就不用 Agent，先用简单、可控的工具调用解决问题。

## 5. Java/Spring 落地视角

Java 后端负责：

```text
工具注册
参数校验
权限校验
业务执行
异常处理
审计日志
人工确认
结果回传
```

典型工具：

- 查询订单。
- 查询库存。
- 查询客户资料。
- 创建工单。
- 发起审批。
- 发送通知。

【工程经验】工具调用必须遵守原业务系统权限模型，不能因为是 AI 调用就绕过权限。

## 6. 常见误区

1. 以为模型会直接调用接口。
2. 工具参数不校验。
3. 工具描述模糊。
4. 写操作不要求确认。
5. 没有最大工具调用次数。
6. 不记录工具调用日志。
7. 把所有业务 API 都暴露给模型。
8. 把 Agent 当成所有问题的默认方案。

## 7. 实践任务

1. 设计 5 个只读工具。
2. 设计 3 个写操作工具，并说明人工确认策略。
3. 为“查询订单物流”设计 Tool Schema。
4. 画出 Tool Calling 流程。
5. 画出 Agent Loop。
6. 设计工具调用审计日志字段。

## 8. 自测题

1. Tool Call 和 Tool Call Output 分别是什么？
2. 为什么工具调用需要 call_id？
3. 工具调用失败时应如何处理？
4. 为什么工具需要权限校验？
5. Agent 为什么需要停止条件？
6. Human-in-the-loop 适合哪些场景？
7. 什么情况下不应该使用 Agent？

## 9. 阶段验收标准

完成本课后，你应该能做到：

1. 能解释工具调用完整流程。
2. 能设计工具 schema。
3. 能说明应用侧执行责任。
4. 能区分 Tool Calling 和 Agent。
5. 能设计 Agent 安全边界。
6. 能说明 Java 后端如何承接工具调用。

## 10. 本课使用的信息源

- OpenAI Function Calling 文档：工具调用流程、函数定义、tool call、tool call output。
- OpenAI Tools 文档：内置工具、自定义函数、远程 MCP。
- OpenAI Responses API 迁移文档：Responses API 中 tool call item、call_id、tool output。
- Spring AI Tool Calling 文档：`@Tool`、`ToolCallback`、方法工具、函数工具。
- LangChain4j Tools 文档：Java Function Calling、`@Tool`、AI Services 工具执行。
- LangChain4j AI Services 文档：AI Services、工具、RAG、结构化接口。

