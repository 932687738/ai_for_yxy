# 项目 09：Embedding、语义搜索与向量数据库概念验收

对应课程：第 9 课《Embedding、语义搜索与向量数据库》

## 1. 项目目标

本项目用于验证你是否理解 Embedding、语义搜索、向量数据库和 RAG 检索基础。

## 2. 术语报告

创建：

```text
reports/embedding_vector_search_concepts.md
```

解释：

- Embedding
- Embedding Model
- Vector
- Semantic Search
- Keyword Search
- Similarity
- Cosine Similarity
- Vector Database
- Collection / Table
- Metadata / Payload
- Chunk
- Chunking Strategy
- Overlap
- Top-k
- ANN
- HNSW
- IVFFlat
- pgvector
- Hybrid Search
- Rerank
- Recall@k

## 3. 知识库切分设计

选择一个业务文档类型：

- 员工制度
- 产品手册
- 项目规范
- 客服 FAQ
- 操作手册

设计 chunk 策略：

| 项目 | 设计 |
|---|---|
| 文档类型 |  |
| 切分单位 |  |
| chunk 大小 |  |
| overlap |  |
| metadata 字段 |  |
| 权限字段 |  |
| 溯源字段 |  |

## 4. 向量库表结构设计

设计 PostgreSQL + pgvector 表结构。

至少包含：

- id
- doc_id
- content
- metadata
- embedding
- created_at
- updated_at

说明每个字段作用。

## 5. 检索评估设计

设计 10 个用户问题，并为每个问题标注正确文档或正确 chunk。

表格：

| 问题 | 正确文档 | 正确 chunk | 是否应命中 top-5 |
|---|---|---|---|

说明如何计算 Recall@5。

## 6. 混合检索分析

回答：

1. 哪些问题适合关键词搜索？
2. 哪些问题适合语义搜索？
3. 哪些问题需要混合检索？
4. 编号、产品型号、制度条款号为什么不能只依赖语义搜索？

## 7. 验收清单

- [ ] 能解释 Embedding。
- [ ] 能解释语义搜索。
- [ ] 能解释向量数据库。
- [ ] 能设计 chunk 策略。
- [ ] 能设计 metadata。
- [ ] 能说明 pgvector 作用。
- [ ] 能解释 Top-k、ANN、HNSW。
- [ ] 能设计 Recall@k 评估。
- [ ] 能说明混合检索价值。

