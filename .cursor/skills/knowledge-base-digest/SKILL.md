---
name: knowledge-base-digest
description: Generates a Chinese knowledge-base digest from a fixed set of Chinese technology portals and team blogs. Use when the user says 拉取知识库, 更新知识库, 知识库摘要, 生成知识库日报, or requests force=true for knowledge-base updates. It follows the same date, force, deduplication, Markdown section overwrite, descending date order, and state-file rules as ai-daily-digest, but only searches the configured fixed URLs and source names.
---

# Knowledge Base Digest

## 使用场景

当用户提到以下任意意图时使用本 Skill：

- 拉取知识库
- 更新知识库
- 知识库摘要
- 生成知识库日报
- 带 `force=true` 的知识库刷新请求

目标：按 Asia/Shanghai 时区增量拉取固定中文技术站点中的新增文章、视频或技术资料，融合总结后写入本地 Markdown 文件，并用状态文件避免重复拉取。

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

- 日报目录：`dailyReport/knowledge-base-news`
- 状态文件：`dailyReport/knowledge-base-news/knowledge-base-state.json`
- 日报文件：`dailyReport/knowledge-base-news/knowledge-base-digest.md`

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
   - 当用户文本包含 `force=true` 或明确要求“强制更新/强制重拉”时启用。
   - 忽略状态文件对目标日期的限制，强制处理最近 3 个完整日期：`end_ymd - 2 天` 到 `end_ymd`；如果用户指定单日强制更新，则只强制处理该日期。
   - 允许覆盖这些日期在 Markdown 中已有的章节。
   - 成功后仍要把这些日期合并进 `processed_dates`，并把 `last_end_date` 更新为现有值和成功处理日期中的较晚者。
5. 如果非 force 增量模式下没有新日期需要处理，只输出：

```text
本次无新资讯
```

此时不要修改日报文件或状态文件。

## 固定来源清单

默认只允许从以下固定来源检索、核验和引用。不要主动扩展到其他站点；搜索引擎结果只可用于定位这些固定站点内的内容。

补漏例外：如果用户明确指出某个固定公司/组织在目标日期有遗漏内容，但该内容没有发布在固定来源原文中，可以补充可信第三方报道作为“非固定来源补充核验”。这类内容必须同时满足：与固定公司/组织直接相关、日期可核验、信息具备技术/产品/工程价值，并在正文和来源清单中明确标注“第三方报道，补充核验”或“非固定来源补充核验”。不要在常规增量拉取中主动使用该例外。

| 公司/组织 | 来源名称 | 固定地址或标识 | 说明 |
| --- | --- | --- | --- |
| 阿里巴巴 | 阿里技术 | https://102.alibaba.com/tech/index/ | 阿里巴巴官方技术门户，分享大规模系统、双11等实战经验。 |
| 阿里巴巴 | 阿里云开发者社区 | https://developer.aliyun.com/ | 涵盖云计算、AI、大数据等多个领域。 |
| 阿里巴巴 | 阿里中间件团队博客 | http://jm.taobao.org/ | 专注 RocketMQ、Dubbo 等中间件技术。 |
| 阿里巴巴 | 语雀·阿里技术干货 | https://www.yuque.com/alidoc/dry | 阿里公开对外的技术干货文章合集。 |
| 腾讯 | 腾讯技术工程 | 公众号：Tencent_TEG | 腾讯技术创新与前沿领域的官方发布平台。 |
| 腾讯 | 腾讯云+社区 | https://cloud.tencent.com/developer/ | 腾讯云官方技术交流社区，涵盖云计算、AI 等。 |
| 腾讯 | 腾讯 AlloyTeam | http://www.alloyteam.com/ | 腾讯 Web 前端团队博客。 |
| 腾讯 | 腾讯大讲堂 | http://djt.qq.com/videos/ | 腾讯内部技术演讲视频汇聚平台。 |
| 字节跳动 | 字节跳动技术团队 | https://techblog.toutiao.com/ | 官方技术博客，分享推荐算法、大模型、音视频等实践。 |
| 字节跳动 | 掘金 | https://juejin.cn/ | 泛前端技术社区，各厂技术团队会同步文章。 |
| 百度 | FEX 技术博客 | http://fex.baidu.com/ | 百度前端技术团队博客。 |
| 百度 | EFE 技术博客 | http://efe.baidu.com/ | 百度工程效率团队博客，关注前端工程化与 Node.js。 |
| 百度 | 百度开发者中心 | https://developer.baidu.com/ | 提供 AI、大数据、云计算等开放能力和资讯。 |
| 美团 | 美团技术团队 | https://tech.meituan.com/ | 覆盖后端、算法、客户端等方向，文章质量高。 |
| 京东 | 京东科技开发者 | https://developer.jdcloud.com/ | JD 官方技术分享社区，发布产品技术、云原生、AIoT 等内容。 |
| 京东 | 凹凸实验室 | https://aotu.io/ | 京东前端团队博客，专注交互体验和前端工程化。 |
| 滴滴 | 滴滴技术博客 | https://didi.github.io/ | 官方技术博客，分享智慧交通、大数据等实践。 |
| 网易 | 网易传媒技术团队 | https://www.zhihu.com/org/wang-yi-yun-54-1/posts | 主要技术输出渠道为知乎专栏。 |
| 360 | 360 核心安全技术博客 | http://blogs.360.cn/ | 聚焦网络安全、攻防技术、漏洞分析。 |
| 有赞 | 有赞技术团队 | https://tech.youzan.com/ | 电商 SaaS 技术博客，覆盖支付、安全、大数据。 |

## 检索规则

每个目标日期的时间范围固定为：

- `YYYY-MM-DD 00:00:00 Asia/Shanghai`
- `YYYY-MM-DD 23:59:59 Asia/Shanghai`

检索关键词应结合固定来源名称、日期和技术主题，重点覆盖：

`AI`, `人工智能`, `大模型`, `LLM`, `Agent`, `RAG`, `云原生`, `架构`, `中间件`, `RocketMQ`, `Dubbo`, `数据库`, `大数据`, `推荐系统`, `搜索`, `音视频`, `前端`, `Node.js`, `工程化`, `客户端`, `安全`, `漏洞`, `攻防`, `DevOps`, `可观测性`, `稳定性`, `性能优化`, `SRE`, `研发效能`, `机器学习`, `算法`, `业务实践`, `双11`, `支付`, `风控`

过滤规则：

- 常规拉取只收录固定来源内的内容；来自转载、聚合、搜索摘要但不能回到固定来源原文的内容不要收录。
- 用户明确指出漏拉时，可按“补漏例外”收录固定公司/组织相关的可信第三方报道，但必须显式标注来源性质，不能伪装成固定来源原文。
- 过滤纯营销、招聘、活动预告、无技术细节、重复转载、无明确发布时间的内容。
- 对时间不明确的内容，只有能合理确认属于目标日期范围时才纳入。
- 如果内容发布日期不在目标日期，但在目标日期中国时间窗口内传播或与当天重要更新直接相关，可以收录；必须在日期字段标注“相邻日期/中国时间窗口传播”。
- 同一文章在多个渠道同步时，以最接近官方/团队原始发布页为准。

## 推荐检索步骤

对每个日期执行：

1. 按固定来源分组检索，每组使用 `site:` 查询或来源名称 + 日期组合查询。
2. 至少覆盖阿里、腾讯、字节、百度、美团、京东、滴滴、网易、360、有赞 10 个公司/组织维度。
3. 对高价值或不确定结果，必须用 WebFetch 打开原文核验标题、发布时间、作者/团队、正文技术含量和链接。
4. 建立去重后的来源列表，记录来源名称、标题、URL、发布日期/更新时间、主题、可信度、研发/学习价值。
5. 不要按 URL 逐篇机械罗列；先融合信息，再按统一脉络生成当天知识库日报。

建议查询示例：

- `site:tech.meituan.com "YYYY-MM-DD" 技术`
- `site:developer.aliyun.com "YYYY-MM-DD" AI OR 大模型 OR 云原生`
- `site:cloud.tencent.com/developer "YYYY-MM-DD" AI OR 架构`
- `site:techblog.toutiao.com "YYYY-MM-DD" 大模型 OR 推荐 OR 音视频`
- `site:juejin.cn "YYYY-MM-DD" 字节跳动 技术团队`
- `site:fex.baidu.com "YYYY-MM-DD"`
- `site:efe.baidu.com "YYYY-MM-DD"`
- `site:developer.baidu.com "YYYY-MM-DD" AI OR 大模型`
- `site:developer.jdcloud.com "YYYY-MM-DD" 技术`
- `site:aotu.io "YYYY-MM-DD"`
- `site:didi.github.io "YYYY-MM-DD"`
- `site:zhihu.com/org/wang-yi-yun-54-1/posts "YYYY-MM-DD"`
- `site:blogs.360.cn "YYYY-MM-DD" 安全 OR 漏洞`
- `site:tech.youzan.com "YYYY-MM-DD"`
- `"Tencent_TEG" "YYYY-MM-DD" 技术`

## 质量控制与查漏补缺

生成日报前执行覆盖检查：

1. 检查是否只引用固定来源清单中的站点或公众号标识。
2. 检查是否覆盖至少 10 个公司/组织维度；若无结果，也要在总结中说明已检索但未发现可核验更新。
3. 检查每条“重要文章与更新”是否包含标题、链接、日期、来源、主题和研发/学习价值。
4. 检查来源清单表格是否包含所有正文引用来源，且日期字段标注准确。
5. 检查是否存在同一文章重复列出；如果重复，合并为一条并保留最权威来源。
6. 若可靠来源少于 3 个，扩大到固定来源内的相邻日期、中国时间窗口传播和站内搜索，但必须标注日期关系。
7. 如果某天没有新内容，仍要说明覆盖了哪些固定来源维度。

## 日期章节模板

每个日期必须写成一个 `## YYYY-MM-DD` 章节，并包含以下 6 个子节。总结语言为中文，突出研发和学习价值。优先采用“结论 + 表格”的可扫读格式。

```markdown
## YYYY-MM-DD

### 今日总览

**一句话结论**：[用 1 句话融合当天知识库更新主线。]

| 维度 | 本日结论 |
| --- | --- |
| 检索范围 | [列出已检索的固定来源维度] |
| 核心趋势 | [2-4 个融合后的技术趋势] |
| 可直接关注 | [对研发/学习/架构/治理最有价值的方向] |
| 未发现更新 | [列出已检索但未发现可核验更新的来源维度] |

### 重要文章与更新

| 主题 | 标题 | 日期 | 来源 | 研发/学习价值 |
| --- | --- | --- | --- | --- |
| [主题] | [标题](URL) | YYYY-MM-DD | [来源名称] | [一句话说明价值] |

### 技术文档与实践

| 方向 | 推荐资料 | 核心技术点 | 适合谁看 |
| --- | --- | --- | --- |
| [方向] | [资料](URL) | [核心技术点] | [目标读者] |

### 工程实践归纳

**总体判断**：[用 1 句话总结当天工程实践变化。]

| 主题 | 进展 | 工程启发 |
| --- | --- | --- |
| [主题] | [进展] | [可复用的工程启发] |

### 值得深入阅读的资料

| 推荐级别 | 资料 | 为什么值得读 |
| --- | --- | --- |
| 必读/推荐/延伸 | [资料](URL) | [推荐理由] |

### 来源清单

- 检索范围：YYYY-MM-DD 00:00:00 到 YYYY-MM-DD 23:59:59（Asia/Shanghai）
- 固定来源覆盖：[已覆盖来源维度]
- 来源清单表格：

| 公司/组织 | 来源 | 类型 | 标题 | 日期 | 链接 |
| --- | --- | --- | --- | --- | --- |
| 公司 | 来源名称 | 技术文章/视频/文档/无新增 | xxx | YYYY-MM-DD（或相邻日期/中国时间窗口传播） | https://... |
```

如果某一天没有新内容或检索不到可靠信息，也必须写入该日期章节：

```markdown
## YYYY-MM-DD

### 今日总览

本次按 Asia/Shanghai 的 YYYY-MM-DD 00:00:00 到 23:59:59 检索固定知识库来源，未发现可确认属于该日期且具备可靠出处的重大技术更新。

### 重要文章与更新

- 未发现可核验的重大文章或更新。

### 技术文档与实践

- 未发现值得收录的新文档或实践文章。

### 工程实践归纳

- 未发现可复现价值明确的新进展。

### 值得深入阅读的资料

- 本日暂无推荐。

### 来源清单

- 检索范围：YYYY-MM-DD 00:00:00 到 YYYY-MM-DD 23:59:59（Asia/Shanghai）
- 固定来源覆盖：已覆盖固定来源清单中的公司/组织维度
- 来源清单表格：

| 公司/组织 | 来源 | 类型 | 标题 | 日期 | 链接 |
| --- | --- | --- | --- | --- | --- |
| 全部 | 固定来源清单 | 无新增 | 无可靠新增来源 | - | - |
```

## Markdown 写入规则

1. 确保日报目录存在。
2. 如果日报文件不存在，创建并写入：

```markdown
# Knowledge Base Digest

按 Asia/Shanghai 时区增量汇总固定中文技术知识库来源。
```

3. 每个日期章节标题必须精确为 `## YYYY-MM-DD`。
4. 如果目标日期章节已存在，覆盖该章节，从该标题开始到下一个 `## YYYY-MM-DD` 标题前结束。
5. 如果目标日期章节不存在，追加到文件末尾。
6. 写入多个日期后，确保所有 `## YYYY-MM-DD` 日期章节按日期倒序排列，最新日期必须最靠前。
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
