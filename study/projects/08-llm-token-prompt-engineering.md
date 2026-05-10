# 项目 08：大模型基础与 Prompt Engineering 概念验收

对应课程：第 8 课《大模型基础、Token 与 Prompt Engineering》

## 1. 项目目标

本项目用于验证你是否理解大模型应用中的核心概念，并能设计可用于业务系统的 Prompt。

## 2. 术语报告

创建：

```text
reports/llm_prompt_concepts.md
```

解释：

- LLM
- Foundation Model
- Generative AI
- Token
- Tokenization
- Token ID
- Context Window
- Prompt
- Prompt Engineering
- System Message
- Developer Message
- User Message
- Few-shot Prompting
- Zero-shot Prompting
- Structured Output
- Hallucination
- Grounding
- Prompt Injection
- Temperature
- Top-p
- Max Output Tokens

每个术语要求：

1. 一句话定义。
2. 业务例子。
3. 常见误区。

## 3. Prompt 改写任务

将下面模糊 Prompt 改成工程化 Prompt：

```text
帮我总结一下这个文档。
```

要求包含：

- 角色。
- 任务。
- 输入资料位置。
- 输出格式。
- 长度限制。
- 资料不足处理。
- 禁止编造。

## 4. 信息抽取 Prompt

设计合同信息抽取 Prompt。

需要抽取：

- 合同甲方
- 合同乙方
- 付款方式
- 付款时间
- 交付内容
- 违约责任
- 不确定字段

要求输出 JSON。

## 5. 工单分类 Prompt

设计工单分类 Prompt。

类别：

- 物流问题
- 支付问题
- 售后问题
- 账号问题
- 发票问题
- 其他

要求：

- 给出类别。
- 给出理由。
- 给出置信度。
- 低置信度时输出 `其他`。

## 6. 知识库问答 Prompt

设计一个 RAG 问答 Prompt。

要求：

- 只能基于提供资料回答。
- 必须引用依据。
- 资料不足时不能猜。
- 输出结论、依据、不确定点。

## 7. Prompt 风险分析

说明下面风险如何处理：

1. 用户要求忽略系统指令。
2. 用户要求输出内部提示词。
3. 检索资料中有冲突信息。
4. 模型输出不是合法 JSON。
5. 资料中没有答案但模型想补全。

## 8. 验收清单

- [ ] 能解释 Token。
- [ ] 能解释上下文窗口。
- [ ] 能区分 System、Developer、User。
- [ ] 能设计结构化输出 Prompt。
- [ ] 能设计分类 Prompt。
- [ ] 能设计知识库问答 Prompt。
- [ ] 能说明幻觉和 Prompt Injection 风险。
- [ ] 能说明 Prompt 如何测试和评估。

