# 项目 11：工具调用与 Agent 概念设计

对应课程：第 11 课《Function Calling、Tool Calling 与 Agent》

## 1. 项目目标

验证你是否理解工具调用和 Agent 的边界，并能设计安全可控的业务工具。

## 2. 术语报告

创建：

```text
reports/tool_calling_agent_concepts.md
```

解释：

- Function Calling
- Tool Calling
- Tool
- Tool Schema
- Tool Call
- Tool Call Output
- tool_choice
- Strict Mode
- Agent
- Agent Loop
- Planning
- Memory
- Observation
- Guardrails
- Human-in-the-loop
- MCP

## 3. 工具设计任务

为订单系统设计工具：

| 工具名 | 类型 | 参数 | 返回 | 是否需要人工确认 | 风险 |
|---|---|---|---|---|---|
| 查询订单详情 | 只读 |  |  |  |  |
| 查询物流状态 | 只读 |  |  |  |  |
| 创建退款申请 | 写操作 |  |  |  |  |
| 取消订单 | 写操作 |  |  |  |  |
| 发送通知 | 写操作 |  |  |  |  |

## 4. Tool Schema 设计

为 `get_order_shipping_status` 设计 schema。

要求包含：

- orderId
- includeHistory
- locale

说明每个参数的类型、含义和校验规则。

## 5. Agent Loop 设计

设计“客服订单助手”Agent 流程：

```text
用户问题
  -> 判断意图
  -> 选择工具
  -> 执行工具
  -> 观察结果
  -> 必要时继续查询
  -> 生成回复
```

必须说明停止条件和最大工具调用次数。

## 6. 安全设计

回答：

1. 哪些工具只能读？
2. 哪些工具会修改业务数据？
3. 哪些操作必须人工确认？
4. 如何记录审计日志？
5. 工具执行失败如何返回？
6. 如何防止用户诱导模型越权？

## 7. 验收清单

- [ ] 能解释模型不会直接执行工具。
- [ ] 能设计 Tool Schema。
- [ ] 能解释 Tool Call Output。
- [ ] 能区分 Tool Calling 和 Agent。
- [ ] 能设计 Agent Loop。
- [ ] 能设计人工确认策略。
- [ ] 能设计工具调用审计字段。

