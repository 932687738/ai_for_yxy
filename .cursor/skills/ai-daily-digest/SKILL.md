---
name: ai-daily-digest
description: Generates an AI Daily News Digest in Chinese. Use when the user says 拉取AI新闻, AI新闻摘要, 更新AI日报, 生成AI资讯汇总, or requests force=true. Incrementally searches broad AI news including LLMs, agents, Claude Code, Codex, OpenClaw, Hermes, Spring AI, LangChain, RAG, MCP, model infrastructure, papers, official blogs, releases, GitHub changelogs, enterprise AI adoption, AI safety, and policy updates, then writes fused daily Markdown summaries with persistent state.
---

# AI Daily News Digest

## 使用场景

当用户提到以下任意意图时使用本 Skill：

- 拉取AI新闻
- AI新闻摘要
- 更新AI日报
- 生成AI资讯汇总
- 带 `force=true` 的 AI 新闻刷新请求

目标：按 Asia/Shanghai 时区增量拉取 AI/人工智能相关每日资讯，融合总结后写入本地 Markdown 文件，并用状态文件避免重复拉取。

## 触发后的日期选择

触发本 Skill 后，除非用户已经明确提供 `force=true`，否则先向用户出示数字选项并等待选择：

```text
请选择拉取方式：
1. 不指定日期，按增量逻辑拉取
2. 指定日期，拉取某一天的信息
```

选择规则：

- 用户回复 `1`：走“日期计算”中的非 force 增量逻辑。
- 用户回复 `2`：要求用户提供一个 `YYYY-MM-DD` 格式日期；若用户已经在同一句回复中提供日期，可直接使用。
- 指定日期模式只处理该单日，时间范围仍为该日期的 `00:00:00` 到 `23:59:59`（Asia/Shanghai）。
- 如果指定日期已经存在于 `processed_dates`，或日报文件中已存在精确章节标题 `## YYYY-MM-DD`，视为日期重复，直接跳过，不检索、不写入、不更新状态，并输出 `该日期已处理，跳过：YYYY-MM-DD`。
- 如果用户提供的日期格式无效，要求用户重新提供，不要自行猜测。

## 固定路径

（以下路径均相对当前项目/工作区根目录。）

- 日报目录：`dailyReport/ai-daily-news`
- 状态文件：`dailyReport/ai-daily-news/ai-daily-state.json`
- 日报文件：`dailyReport/ai-daily-news/ai-daily-digest.md`

如日报目录不存在，先创建目录。如日报文件不存在，创建文件并写入标题。

## 状态文件格式

状态文件必须持久化为 JSON：

```json
{
  "last_end_date": "YYYY-MM-DD",
  "last_sync_ymd": "YYYY-MM-DD",
  "processed_dates": ["YYYY-MM-DD"]
}
```

字段规则：

- `last_end_date`：最近一次成功处理到的日期。
- `last_sync_ymd`：首次运行或最近同步的结束日期，保留用于审计。
- `processed_dates`：所有已处理日期，必须去重并按升序保存。

## 日期计算

所有日期均按 Asia/Shanghai 计算。

1. 设 `today_ymd` 为当前运行日期，`end_ymd = today_ymd - 1 天`。
2. 非 force 模式：
   - 如果状态文件不存在或无有效 `last_end_date`，只处理 `end_ymd`，并将该日期记录为 `last_sync_ymd`。
   - 如果状态文件存在，从 `last_end_date + 1 天` 开始处理到 `end_ymd`，左开右闭。
   - 跳过已经存在于 `processed_dates` 的日期。
   - 目标日期必须按时间升序处理。
3. 指定日期模式：
   - 只处理用户指定的 `YYYY-MM-DD`。
   - 如果该日期已经存在于 `processed_dates`，或日报文件中已有 `## YYYY-MM-DD` 章节，直接跳过。
   - 如果该日期未处理，则按该日期当天检索、生成章节并写入 Markdown。
4. force 模式：
   - 当用户文本包含 `force=true` 时启用。
   - 忽略状态文件对目标日期的限制，强制处理最近 3 个完整日期：`end_ymd - 2 天` 到 `end_ymd`。
   - 允许覆盖这些日期在 Markdown 中已有的章节。
   - 成功后仍要把这些日期合并进 `processed_dates`，并把 `last_end_date` 更新为现有值和 `end_ymd` 中较晚者。
5. 如果非 force 增量模式下没有新日期需要处理，只输出：

```text
本次无新资讯
```

此时不要修改日报文件或状态文件。

## 检索规则

每个目标日期的时间范围固定为：

- `YYYY-MM-DD 00:00:00 Asia/Shanghai`
- `YYYY-MM-DD 23:59:59 Asia/Shanghai`

检索关键词必须覆盖以下任意一个或多个，并围绕当天日期组合查询：

`AI`, `人工智能`, `生成式 AI`, `LLM`, `大语言模型`, `agent`, `AI agent`, `autonomous agent`, `coding agent`, `agentic AI`, `skills`, `Agent Skills`, `AI skills`, `Codex Skills`, `Claude Skills`, `Cursor Skills`, `Claude Code skills`, `LangChain`, `LangGraph`, `LlamaIndex`, `RAG`, `GraphRAG`, `OpenAI`, `Anthropic`, `Claude`, `Claude Code`, `Codex`, `OpenClaw`, `Hermes`, `Spring AI`, `Spring Boot AI`, `Google DeepMind`, `Gemini`, `Meta Llama`, `MCP`, `A2A`, `向量数据库`, `vector database`, `embedding`, `reranker`, `提示工程`, `prompt engineering`, `模型评测`, `eval`, `benchmark`, `AI 编程`, `AI coding`, `AI 安全`, `AI safety`, `AI 产品发布`, `AI 政策监管`, `模型基础设施`, `GPU`, `TPU`, `推理加速`, `inference`, `enterprise AI`, `企业 AI 落地`, `AI 搜索`, `多模态`, `语音模型`, `机器人`, `具身智能`

优先来源（按优先级）：

1. 官方发布：OpenAI、Anthropic、Google / DeepMind、Microsoft、AWS、Meta、NVIDIA、GitHub、LangChain 等官方博客、文档、changelog、release notes。
2. 论文原文：arXiv、Hugging Face Papers、项目主页、论文作者页面。
3. 开源项目：GitHub Releases、项目文档、可信 release 聚合。
4. 可信技术媒体：The Verge、Ars Technica、TechCrunch、VentureBeat、InfoQ、官方新闻稿等。
5. 政策与标准：NIST、欧盟、美国政府、监管机构、标准组织公告。

扩展来源池（用于扩大覆盖面，仍需按可信度筛选）：

- 官方与厂商：`openai.com`, `anthropic.com`, `deepmind.google`, `blog.google`, `research.google`, `ai.meta.com`, `about.fb.com/news`, `microsoft.com/en-us/research`, `blogs.microsoft.com`, `azure.microsoft.com/blog`, `aws.amazon.com/blogs`, `developer.nvidia.com/blog`, `github.blog`, `huggingface.co/blog`, `mistral.ai/news`, `cohere.com/blog`, `x.ai/news`, `perplexity.ai/hub`, `cursor.com/blog`, `windsurf.com/blog`。
- 框架与开发生态：`blog.langchain.com`, `docs.langchain.com`, `changelog.langchain.com`, `llamaindex.ai/blog`, `spring.io/blog`, `docs.spring.io/spring-ai`, `github.com/spring-projects/spring-ai`, `github.com/openai/codex`, `github.com/anthropics/claude-code`, `github.com/modelcontextprotocol`, `github.com/langchain-ai`, `github.com/NousResearch/hermes-agent`, `cursor.com/blog`, `docs.cursor.com`, `openai.com/codex`, `platform.openai.com/docs`, `docs.anthropic.com`, `code.claude.com/docs`。
- 论文与模型社区：`arxiv.org`, `huggingface.co/papers`, `paperswithcode.com`, `openreview.net`, `neurips.cc`, `icml.cc`, `iclr.cc`, `aclanthology.org`, 作者项目主页和代码仓库。
- 开源与工程：GitHub Releases、GitHub Trending、GitHub Discussions、release notes、changelog、package registry 页面（npm、PyPI、Maven Central）以及项目官方文档。
- 可信媒体与深度来源：The Verge、Ars Technica、TechCrunch、VentureBeat、InfoQ、MIT Technology Review、IEEE Spectrum、The Batch、Sebastian Raschka、Simon Willison、Latent Space、Ben's Bites、Import AI。
- 中文可信来源：机器之心、量子位、InfoQ 中文、腾讯云开发者、阿里云开发者、华为云开发者、火山引擎开发者、百度智能云技术博客；中文来源只作补充，重大事实优先回溯官方原文。
- 政策与标准：NIST、CAISI、AISI、White House、FTC、EU AI Office、European Commission、European Parliament、OECD AI、ISO、IEEE、UNESCO、各国监管机构和标准组织。

过滤规则：

- 过滤纯营销、重复转载、无明确来源、标题党、低质量聚合、无技术/产品/政策增量内容。
- 同一事件以官方来源或原始论文为准，媒体报道只作为补充。
- 对时间不明确的内容，只有能合理确认属于目标日期范围时才纳入。
- 如果内容发布日期不在目标日期，但在目标日期中国时间窗口内传播或与当天重要事件直接相关，可以收录；必须在日期字段标注“相邻日期/中国时间窗口传播”。
- 信息不足或可信度不足时不要强行写成重大更新。

## 推荐检索步骤

对每个日期执行：

1. 用 WebSearch 分组检索官方发布、论文原文、开源 release、可信技术媒体、政策监管。
2. 使用多个组合查询交叉验证，至少覆盖“关键词+日期+official”“官方站点 site 检索”“论文站点检索”“GitHub/changelog 检索”“政策监管检索”。
3. 对 `Claude Code`、`Codex`、`OpenClaw`、`Hermes`、`Spring AI`、`skills/Agent Skills/Codex Skills/Claude Skills/Cursor Skills` 必须单独执行专项检索（即使当天无结果也要检索并在总结中说明）。
4. 对高价值或不确定结果，必须用 WebFetch 打开原文核验日期和事实。
5. 日期核验时区分发布时间、更新时间、抓取时间、相邻时区传播时间，避免把搜索摘要日期当成发布日期。
6. 建立去重后的来源列表，记录标题、URL、发布日期/更新时间、类型、可信度、与研发/学习的关系。
7. 不要按 URL 逐篇输出摘要；先融合信息，再按统一脉络生成当天日报。

最低覆盖矩阵：

- 每个目标日期至少执行 13 组检索：官方厂商、模型/产品、开发者工具、Agent 框架、RAG/MCP/向量数据库、Spring AI/Java AI、Claude Code/Codex/OpenClaw/Hermes、skills/Agent Skills、论文、GitHub release、技术媒体、政策监管、中文补充来源。
- 若某一组没有可靠结果，在对应主题中说明“未发现可核验重大更新”，不要省略该组。
- 同一事件至少用 2 个来源交叉验证；如果只有一个来源，必须是官方原文、论文原文或 GitHub release。
- 对“看起来重大”的媒体报道，必须反查官方公告、原始论文、GitHub release 或监管原文。
- 对开源 release，优先核验 GitHub release 的 `Published` 时间、tag、变更列表、仓库归属和 star/生态影响；不要只依据第三方 release 聚合。
- 对论文，优先核验 arXiv submitted/revised 日期、论文标题、作者、代码链接、任务指标；不要把旧论文的新引用当作当天论文。
- 对企业 AI 落地，优先收录包含可量化效果、架构细节、开源代码、生产实践或治理方法的内容。

主题覆盖清单：

- 模型与产品：新模型、默认模型变更、API 能力、价格/限额、上下文窗口、多模态、语音、图像、视频。
- AI 编程：Codex、Claude Code、GitHub Copilot、Cursor、Windsurf、JetBrains AI、代码审查、浏览器/终端/IDE 集成。
- Agent 与工程框架：LangChain、LangGraph、LlamaIndex、Spring AI、Hermes、OpenClaw、MCP、A2A、Agent Skills、Codex Skills、Claude Skills、Cursor Skills、多 Agent、长期记忆、工具调用、工作流编排。
- RAG 与数据层：GraphRAG、向量数据库、混合检索、rerank、embedding、知识图谱、数据连接器、权限与审计。
- 模型评测与安全：system card、eval、red team、可解释性、AI 安全、网络安全、隐私、内容安全、模型治理。
- 基础设施：GPU/TPU、推理框架、算力合作、模型部署、边缘推理、云服务、开发平台。
- 论文与研究：LLM、agent、RAG、对齐、推理、可解释性、多模态、具身智能、科学发现。
- 政策与标准：AI Act、NIST/CAISI/AISI、美国/欧盟/中国监管、版权、数据合规、行业规范。
- 企业落地：金融、医疗、教育、制造、软件工程、客服、办公协作、数据分析、研发提效。

建议查询示例：

- `"AI" "May 7, 2026" official`
- `site:openai.com/index "May 7, 2026"`
- `site:anthropic.com "May 7, 2026"`
- `site:deepmind.google "May 7, 2026"`
- `site:github.blog/changelog "May 7, 2026" Copilot AI`
- `site:arxiv.org/abs "Submitted" "7 May 2026" "large language model"`
- `site:huggingface.co/papers/date/YYYY-MM-DD LLM agent RAG`
- `"Claude Code" "May 7, 2026" release OR changelog`
- `"Codex" "May 7, 2026" OpenAI`
- `"OpenClaw" "May 7, 2026" AI`
- `"Hermes" "May 7, 2026" LLM OR agent`
- `"Spring AI" OR "Spring Boot AI" "May 7, 2026" release OR blog OR changelog`
- `site:spring.io/blog "Spring AI" "May 7, 2026"`
- `site:github.com/spring-projects/spring-ai/releases "2026"`
- `"Agent Skills" OR "AI skills" "May 7, 2026" release OR update OR marketplace`
- `"Codex Skills" "May 7, 2026"`
- `"Claude Code" skills "May 7, 2026"`
- `"Cursor Skills" OR "Cursor agent skills" "May 7, 2026"`
- `site:openai.com/index skills Codex "May 7, 2026"`
- `site:docs.cursor.com skills "May 7, 2026"`
- `site:docs.anthropic.com "skills" "Claude Code" "May 7, 2026"`
- `site:github.com/*/releases "May 7, 2026" "AI agent"`
- `site:github.com/openai/codex/releases "May 7, 2026"`
- `site:github.com/anthropics/claude-code/releases "May 7, 2026"`
- `site:github.com/modelcontextprotocol "May 7, 2026" MCP`
- `site:huggingface.co/blog "May 7, 2026" AI`
- `site:huggingface.co/papers/date/YYYY-MM-DD "agent" OR "RAG" OR "LLM"`
- `site:developer.nvidia.com/blog "May 7, 2026" AI`
- `site:aws.amazon.com/blogs "May 7, 2026" generative AI`
- `site:azure.microsoft.com/blog "May 7, 2026" AI agent`
- `site:venturebeat.com "May 7, 2026" AI`
- `site:techcrunch.com "May 7, 2026" AI`
- `site:theverge.com "May 7, 2026" AI`
- `site:jiqizhixin.com "2026-05-07" AI`
- `site:qbitai.com "2026-05-07" AI`

## 质量控制与查漏补缺

生成日报前执行覆盖检查：

1. 检查是否覆盖官方发布、论文、开源 release、技术媒体、政策监管、开发者工具、Agent/RAG/MCP、企业落地至少 8 类。
2. 检查专项主题 `Claude Code`、`Codex`、`OpenClaw`、`Hermes`、`Spring AI`、`skills/Agent Skills/Codex Skills/Claude Skills/Cursor Skills` 是否均已检索并有结论。
3. 检查每条“重要事件与发布”是否包含标题、链接、发布日期/更新时间、信息类型、研发影响。
4. 检查来源清单表格是否包含所有正文引用来源，且日期字段标注准确。
5. 检查是否存在同一事件重复列出；如果重复，合并为一条并保留最权威来源。
6. 检查是否有只来自媒体且无官方/原文支撑的重大结论；若有，降级为背景或移除。
7. 若可靠来源少于 3 个，扩大到相邻日期、中国时间窗口传播、中文可信来源和 GitHub release，但必须标注日期关系。
8. 若当天无重大更新，仍要说明已覆盖的检索组和未发现重大更新的主题。

## 日期章节模板

每个日期必须写成一个 `## YYYY-MM-DD` 章节，并包含以下 6 个子节。总结语言为中文，突出研发和学习价值。行文必须先给整体趋势，再分主题归纳。优先采用“结论 + 表格”的可扫读格式，避免长段落和超长项目符号。

```markdown
## YYYY-MM-DD

### 今日总览

**一句话结论**：[用 1 句话融合当天主线，说明最重要的趋势。]

| 维度 | 本日结论 |
| --- | --- |
| 检索范围 | [列出核心检索主题] |
| 核心趋势 | [2-4 个融合后的趋势，不逐 URL 罗列] |
| 可直接关注 | [对研发/学习/架构/治理最有价值的 3-5 个方向] |
| 专项检索结论 | [Claude Code/Codex/OpenClaw/Hermes/Spring AI/skills 等专项检索结论] |

### 重要事件与发布

| 主题 | 标题 | 日期 | 类型 | 研发/学习价值 |
| --- | --- | --- | --- | --- |
| [主题] | [标题](URL) | YYYY-MM-DD | [类型] | [一句话说明对研发/学习/架构/治理的影响] |

### 技术文档与教程

| 方向 | 推荐资料 | 核心技术点 | 适合谁看 |
| --- | --- | --- | --- |
| [方向] | [资料](URL) | [核心技术点] | [目标读者] |

### LangChain / Agent / LLM 工程相关进展

**总体判断**：[用 1 句话总结 Agent/LLM 工程方向的变化。]

| 主题 | 进展 | 工程启发 |
| --- | --- | --- |
| [主题] | [进展] | [可复用的工程启发] |

### 值得深入阅读的资料

| 推荐级别 | 资料 | 为什么值得读 |
| --- | --- | --- |
| 必读/推荐/延伸 | [资料](URL) | [推荐理由] |

### 来源清单

- 检索范围：YYYY-MM-DD 00:00:00 到 YYYY-MM-DD 23:59:59（Asia/Shanghai）
- 引用域名：[domain1], [domain2], [domain3]
- 来源清单表格：

| 类型 | 标题 | 日期 | 链接 |
| --- | --- | --- | --- |
| 官方发布/论文原文/开源发布/技术媒体/政策标准 | xxx | YYYY-MM-DD（或相邻日期/中国时间窗口传播） | https://... |
```

如果某一天没有新内容或检索不到可靠信息，也必须写入该日期章节：

```markdown
## YYYY-MM-DD

### 今日总览

本次按 Asia/Shanghai 的 YYYY-MM-DD 00:00:00 到 23:59:59 检索 AI、人工智能、LLM、Agent、RAG、MCP、LangChain、模型发布、论文与政策监管等关键词，未发现可确认属于该日期且具备可靠出处的重大更新。

### 重要事件与发布

- 未发现可核验的重大事件或发布。

### 技术文档与教程

- 未发现值得收录的新文档或教程。

### LangChain / Agent / LLM 工程相关进展

- 未发现可复现价值明确的新进展。

### 值得深入阅读的资料

- 本日暂无推荐。

### 来源清单

- 检索范围：YYYY-MM-DD 00:00:00 到 YYYY-MM-DD 23:59:59（Asia/Shanghai）
- 引用域名：无可靠新增来源
- 来源清单表格：

| 类型 | 标题 | 日期 | 链接 |
| --- | --- | --- | --- |
| 无 | 无可靠新增来源 | - | - |
```

## Markdown 写入规则

1. 确保日报目录存在。
2. 如果日报文件不存在，创建并写入：

```markdown
# AI Daily News Digest

按 Asia/Shanghai 时区增量汇总 AI/人工智能相关每日资讯。
```

3. 每个日期章节标题必须精确为 `## YYYY-MM-DD`。
4. 如果目标日期章节已存在，覆盖该章节，从该标题开始到下一个 `## YYYY-MM-DD` 标题前结束。
5. 如果目标日期章节不存在，追加到文件末尾。
6. 写入多个日期后，确保所有 `## YYYY-MM-DD` 日期章节按日期倒序排列，最新日期必须最靠前，保证每次打开文件先看到最新日报。
7. 不要删除文件顶部标题和非日期说明内容。

## 状态更新规则

仅当至少一个日期的章节成功写入后才更新状态文件。

更新时：

- 将成功处理日期并入 `processed_dates`，去重升序。
- 将 `last_end_date` 更新为原 `last_end_date` 和成功处理日期中的较晚日期；force 或指定日期模式下如果原 `last_end_date` 更晚，则保留更晚值。
- 首次运行时设置 `last_sync_ymd = end_ymd`；后续运行可更新为本次同步结束日期。
- JSON 使用 UTF-8 和稳定缩进。

## 输出要求

完成后简要告知用户：

- 处理了哪些日期。
- 写入或覆盖了哪个 Markdown 文件。
- 状态文件已更新。

指定日期重复时，唯一输出必须是：

```text
该日期已处理，跳过：YYYY-MM-DD
```

非 force 且无新日期时，唯一输出必须是：

```text
本次无新资讯
```
