# 第 9 课：Embedding、语义搜索与向量数据库

## 0. 本课阅读方式

本课进入 RAG 和知识库问答的关键前置知识：Embedding、语义搜索和向量数据库。

学习本课时，请先理解概念，再看实现。

本课重点是：

```text
Embedding 为什么能表示语义？
语义搜索和关键词搜索有什么区别？
向量相似度如何工作？
向量数据库为什么存在？
pgvector、Milvus、Qdrant、Pinecone 这类工具解决什么问题？
检索结果如何评估？
```

【核心】RAG 的第一步不是生成答案，而是把用户问题和知识库内容都转成可检索的向量表示。

## 0.1 概念讲义：Embedding、语义搜索与向量数据库术语详解

### 0.1.1 第 9 课到底在学什么

第 8 课讲 Prompt，本课讲模型如何“找到相关资料”。

知识库问答通常不是把所有文档直接塞给大模型，因为：

- 文档太长。
- 上下文窗口有限。
- 成本高。
- 噪声多。
- 模型容易忽略关键信息。

更常见做法是：

```text
先检索相关片段
再把相关片段放进 Prompt
让模型基于片段回答
```

这个检索过程的核心就是 Embedding 和向量搜索。

【核心】Embedding 是 RAG 的检索基础。

### 0.1.2 Embedding

Embedding 是把文本、图片、商品、用户等对象转换成向量。

文本例子：

```text
"如何申请年假？"
  -> [0.12, -0.08, 0.33, ...]
```

向量中的每个数字没有简单的人工含义，但整体向量能表示语义位置。

【核心】Embedding 把不可直接计算的语义，变成可以计算相似度的数字向量。

### 0.1.3 Embedding Model

Embedding Model 是专门把输入转换成向量的模型。

它和聊天模型不同：

```text
聊天模型：输入文本，输出文本。
Embedding 模型：输入文本，输出向量。
```

【重点】做语义搜索时，文档和查询通常必须使用同一个 Embedding 模型生成向量。

### 0.1.4 Vector 向量

向量是一组数字。

在 Embedding 场景中：

```text
向量代表语义位置。
```

语义接近的文本，向量方向或距离通常更接近。

例如：

```text
"年假怎么申请"
"如何提交休假流程"
```

字面不同，但语义接近。

### 0.1.5 Semantic Search 语义搜索

语义搜索根据意思查找，而不是只匹配关键词。

关键词搜索：

```text
查询“年假”
只容易找到包含“年假”的文档。
```

语义搜索：

```text
查询“怎么请假”
也可能找到“年假申请流程”。
```

【核心】语义搜索解决“表达不同但意思接近”的检索问题。

### 0.1.6 Keyword Search 关键词搜索

关键词搜索依赖词项匹配。

优点：

- 精确。
- 可解释。
- 对专业术语、编号、代码、SKU 很有效。

缺点：

- 同义表达难召回。
- 依赖分词。
- 不理解语义。

【工程经验】真实系统常使用混合检索：关键词搜索 + 向量搜索。

### 0.1.7 Similarity 相似度

相似度衡量两个向量有多接近。

常见方式：

- Cosine similarity
- Dot product
- Euclidean distance

【重点】不同向量数据库或模型可能推荐不同距离度量，要保持一致。

### 0.1.8 Cosine Similarity

余弦相似度衡量两个向量方向是否接近。

在语义检索中常用。

【核心】语义相近通常意味着向量方向相近。

### 0.1.9 Dot Product

点积也可用于衡量向量相关性。

有些 Embedding 模型会配合点积使用。

【重点】选择相似度算法时，应参考 Embedding 模型和向量库的推荐。

### 0.1.10 Vector Database 向量数据库

向量数据库用于存储和检索向量。

它不仅存向量，还通常存：

- 文档 ID。
- 文档片段文本。
- 元数据。
- 来源文件。
- 权限字段。
- 时间信息。

【核心】向量数据库解决“大量向量如何高效相似度检索”的问题。

### 0.1.11 Collection / Table

向量数据库通常把向量组织到 collection 或 table 中。

类比关系：

```text
关系数据库：database / table / row
向量数据库：collection / point / vector
PostgreSQL + pgvector：table / row / vector column
```

### 0.1.12 Metadata / Payload

Metadata 是和向量一起存储的业务信息。

例如：

```json
{
  "doc_id": "policy-001",
  "title": "年假管理制度",
  "department": "HR",
  "permission": "employee",
  "chunk_index": 3
}
```

【核心】元数据用于过滤、权限控制、结果展示和溯源。

### 0.1.13 Chunk

Chunk 是文档切分后的片段。

为什么要切分？

- 文档太长。
- Embedding 模型有输入长度限制。
- 检索需要更精确片段。
- 大模型上下文窗口有限。

【重点】Chunk 切太大，噪声多；切太小，上下文不足。

### 0.1.14 Chunking Strategy

切分策略决定如何把文档拆成片段。

常见策略：

- 按固定字数。
- 按标题层级。
- 按段落。
- 按语义边界。
- 滑动窗口重叠。

【工程经验】文档结构越强，越应该利用标题、段落、章节切分，而不是简单按字数硬切。

### 0.1.15 Overlap

Overlap 是相邻 chunk 之间的重叠内容。

作用：

- 防止关键信息被切断。
- 保留上下文连续性。

代价：

- 增加存储。
- 增加检索重复。
- 增加成本。

### 0.1.16 Top-k

Top-k 表示返回最相似的前 k 条结果。

例如：

```text
top_k = 5
```

表示返回最相关的 5 个文档片段。

【重点】k 太小可能漏召回，k 太大可能引入噪声。

### 0.1.17 ANN

ANN 是 Approximate Nearest Neighbor，近似最近邻搜索。

因为精确搜索大量向量成本高，向量数据库常用近似算法提升速度。

【工程经验】向量搜索通常在准确率、速度、索引大小之间做权衡。

### 0.1.18 HNSW

HNSW 是常见 ANN 索引算法。

它通过图结构加速相似向量搜索。

pgvector、Qdrant、Milvus 等都支持或使用类似 ANN 索引能力。

### 0.1.19 IVFFlat

IVFFlat 是另一类向量索引思路，通过聚类分区减少搜索范围。

在 pgvector 中，HNSW 和 IVFFlat 都是常见索引选择。

### 0.1.20 pgvector

pgvector 是 PostgreSQL 的向量扩展。

它让 PostgreSQL 能存储向量并执行相似度搜索。

适合：

- 已经使用 PostgreSQL。
- 数据规模中小。
- 希望关系数据和向量数据放在一起。
- 需要 SQL、事务、权限集成。

【核心】pgvector 是 Java/Spring 系统落地 RAG 的常见选择。

### 0.1.21 Hybrid Search 混合检索

混合检索结合关键词搜索和向量搜索。

适合：

- 既要语义召回。
- 又要精确匹配编号、术语、代码、产品型号。

【工程经验】企业知识库中，纯向量检索经常不如混合检索稳定。

### 0.1.22 Rerank 重排序

Rerank 是对初步检索结果再次排序。

流程：

```text
向量搜索召回 top 20
  -> reranker 精排
  -> 选 top 5 给大模型
```

【重点】Rerank 可以提升最终送入大模型的上下文质量。

### 0.1.23 Recall@k

Recall@k 衡量正确结果是否出现在前 k 个检索结果中。

例如：

```text
用户问题的正确文档出现在 top 5 中
```

说明 Recall@5 命中。

### 0.1.24 本课重点标注汇总

【核心】Embedding 把语义转换成向量。

【核心】语义搜索通过向量相似度找相关内容。

【核心】向量数据库解决大规模向量存储和相似度检索。

【核心】Chunking 直接影响 RAG 检索质量。

【核心】Metadata 是权限、过滤、溯源和展示的基础。

【重点】关键词搜索和语义搜索各有优缺点，真实系统常用混合检索。

【重点】Top-k、相似度阈值、重排序都会影响最终回答质量。

【易错】向量相似不等于答案一定正确，还需要上下文验证。

### 0.1.25 自我检查问题

1. Embedding 是什么？
2. Embedding 模型和聊天模型有什么区别？
3. 语义搜索和关键词搜索有什么区别？
4. 为什么文档要切 chunk？
5. chunk 太大或太小分别有什么问题？
6. 向量数据库存什么？
7. Metadata 有什么作用？
8. Top-k 如何影响检索结果？
9. HNSW 和 IVFFlat 解决什么问题？
10. pgvector 适合什么场景？
11. 为什么企业知识库常用混合检索？
12. Rerank 解决什么问题？

## 1. 本课目标

学完本课后，你应该能够：

1. 解释 Embedding、语义搜索、向量数据库的关系。
2. 区分语义搜索和关键词搜索。
3. 理解向量相似度、Top-k、ANN、HNSW、IVFFlat。
4. 理解 Chunk、Overlap、Metadata 对 RAG 的影响。
5. 解释 pgvector 的作用和适用场景。
6. 设计一个基础知识库向量检索流程。
7. 说明检索结果如何评估和优化。

## 2. 语义搜索流程

```text
文档入库：
  原始文档
    -> 清洗
    -> 切分 chunk
    -> 生成 embedding
    -> 存入向量数据库

用户查询：
  用户问题
    -> 生成 query embedding
    -> 向量相似度搜索
    -> 取回 top-k chunk
    -> 可选 rerank
    -> 送给大模型回答
```

【核心】入库和查询必须使用兼容的 Embedding 表示。

## 3. 关键词搜索 vs 语义搜索

| 对比 | 关键词搜索 | 语义搜索 |
|---|---|---|
| 匹配方式 | 词项匹配 | 向量相似度 |
| 优点 | 精确、可解释 | 能理解同义表达 |
| 缺点 | 同义词召回差 | 可能召回语义相关但不精确内容 |
| 适合 | 编号、代码、术语 | 自然语言问题 |

【工程经验】企业系统中优先考虑混合检索，而不是非此即彼。

## 4. Chunk 设计

切分文档时要考虑：

1. 文档结构。
2. 段落边界。
3. 标题层级。
4. 表格。
5. 列表。
6. 语义完整性。
7. 模型上下文窗口。

示例：

```text
制度标题
  -> 一级章节
  -> 二级章节
  -> 段落
```

【重点】好的 chunk 应该能独立回答一个小问题，同时保留必要上下文。

## 5. 向量数据库设计

一条向量记录通常包含：

```text
id
embedding
content
metadata
created_at
updated_at
```

metadata 示例：

```json
{
  "doc_id": "hr-policy-001",
  "title": "员工休假管理制度",
  "source": "hr_policy.pdf",
  "department": "HR",
  "permission": "employee",
  "chunk_index": 5
}
```

【核心】没有 metadata，检索结果难以权限过滤和结果溯源。

## 6. pgvector 概念示例

pgvector 让 PostgreSQL 支持向量字段。

概念表结构：

```sql
CREATE TABLE document_chunks (
    id bigserial PRIMARY KEY,
    doc_id text NOT NULL,
    content text NOT NULL,
    metadata jsonb,
    embedding vector(1536)
);
```

相似度查询概念：

```sql
SELECT id, content
FROM document_chunks
ORDER BY embedding <=> :query_embedding
LIMIT 5;
```

说明：

```text
embedding 存文档向量。
query_embedding 是用户问题向量。
ORDER BY 距离排序。
LIMIT 5 返回 top-5。
```

## 7. 检索评估

检索要评估：

1. 正确文档是否被召回。
2. 正确片段排名是否靠前。
3. 返回内容是否足够回答问题。
4. 是否返回大量噪声。
5. 是否遵守权限过滤。

常见指标：

- Recall@k
- Precision@k
- MRR
- 人工标注命中率
- 最终回答正确率

【核心】RAG 质量首先取决于检索质量。

## 8. 常见误区

1. 以为向量相似就一定答案正确。
2. chunk 随便按字数切。
3. 不存 metadata。
4. 不做权限过滤。
5. top-k 固定不调。
6. 忽略关键词检索价值。
7. 不评估检索，只评估最终回答。
8. 文档更新后不重新入库。

## 9. 实践任务

1. 用自己的话解释 Embedding、语义搜索、向量数据库。
2. 设计一个企业制度知识库的 chunk 策略。
3. 设计向量库表结构，包括 metadata 字段。
4. 说明如何做权限过滤。
5. 对比关键词搜索和语义搜索适合的场景。
6. 设计 10 个测试问题，评估 Recall@5。

## 10. 自测题

1. Embedding 为什么能用于语义搜索？
2. 为什么用户问题也要生成 embedding？
3. 什么是 Top-k？
4. 为什么需要 ANN 索引？
5. pgvector 解决什么问题？
6. Metadata 为什么重要？
7. 混合检索有什么价值？
8. Rerank 解决什么问题？
9. Recall@k 代表什么？
10. 为什么检索质量会影响最终回答？

## 11. 阶段验收标准

完成本课后，你应该能做到：

1. 能解释 Embedding 和向量相似度。
2. 能解释语义搜索流程。
3. 能说明向量数据库存储内容。
4. 能设计 chunk 和 metadata。
5. 能解释 pgvector 基本作用。
6. 能说明 Top-k、ANN、HNSW、IVFFlat。
7. 能设计基础检索评估方案。

## 12. 本课使用的信息源

- OpenAI Embeddings 文档：Embedding、向量表示、语义搜索。
- OpenAI Retrieval 相关文档：向量存储、检索、文件搜索。
- pgvector GitHub README：PostgreSQL 向量类型、距离计算、索引、HNSW、IVFFlat。
- Pinecone Learning Center：向量数据库、语义搜索、ANN。
- Qdrant Documentation：collection、payload、filter、相似度搜索。

