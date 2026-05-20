# GitHub 快照（Stars Search API + Trending）

本文件由 `tools/update_github_topz.py` 生成，两块内容独立编排：

- **模块一**：`tools/github_topz/stars_merge.py` → GitHub REST `/search/repositories` 全局 Star 前十名，并按既有规则与本节历史 Markdown 表格合并（列结构与原 `github-topz.md` 一致）。
- **模块二**：`tools/github_topz/trending_fetch.py` → 抓取 Trending 「今日 / 本周 / 本月」页面 HTML，`article.Box-row` 解析后与中文简介渲染。
- **标记列**：各表相对**本次运行前**已保存的 `github-topz.md` 中对应表格出现过的 `owner/repo` 做差集；首次出现标 **新增**；再次运行会先清空上一轮「新增」后仅标记新一轮新增（详见 `.cursor/rules/dual-digest-on-pull.mdc`）。

---
## 全局 Star Search API（与文件历史合并）

- 数据源：[`dual-digest-on-pull`](../.cursor/rules/dual-digest-on-pull.mdc) 工作流程下配套的 GitHub Search API：`sort=stars` **全局前十名**（`/search/repositories`）。与本节历史行合并时：**已出现的仓库更新 Stars**，新仓库按 Star **降序** 参与整表排序。
- **仓库简介**列：数据源为 GitHub `description`，**写入时为中文简述**——常见仓库内置固定中文提要；其余在渲染时尽力通过公开翻译接口转写，失败则回退英文摘录。表格中若为中文且无新的英文数据源，会直接沿用原有中文单元格。
- **与 Trending 区别**：本节为全局累计 Star 排序快照；文末 Trending 为 GitHub「今日 / 本周 / 本月热度」榜单，数据源与口径均不同。
- **标记**列：相对**本次拉取前**磁盘上 `github-topz.md` 中本节表格已存在的 `owner/repo`，不存在的行标为 **新增**；下次拉取会重新计算并清空上一次的「新增」（仅保留新一轮相对上一轮新增）。

**最近一次更新时间**（Asia/Shanghai）： 2026-05-20 08:35:45

| 序号 | 仓库 | Stars | 仓库简介（中文） | 链接 | 标记 |
| --- | --- | ---:| --- | --- | --- |
| 1 | `codecrafters-io/build-your-own-x` | 502595 | 通过从零重写各类代表性技术来学习编程与设计，加深对底层原理的理解。 | https://github.com/codecrafters-io/build-your-own-x |  |
| 2 | `sindresorhus/awesome` | 468157 | 围绕多种主题整理的「Awesome」精品清单合集。 | https://github.com/sindresorhus/awesome |  |
| 3 | `freeCodeCamp/freeCodeCamp` | 445160 | freeCodeCamp 官网开源代码与学习课程：可免费学习编程、数学与计算机科学。 | https://github.com/freeCodeCamp/freeCodeCamp |  |
| 4 | `public-apis/public-apis` | 435944 | 免费可用的公共 API 资源汇总清单。 | https://github.com/public-apis/public-apis |  |
| 5 | `EbookFoundation/free-programming-books` | 388593 | 可免费获取的编程与计算机类书籍书单汇总。 | https://github.com/EbookFoundation/free-programming-books |  |
| 6 | `openclaw/openclaw` | 373264 | 可在多系统运行的个人 AI 助手（吉祥物为龙虾图标）。 | https://github.com/openclaw/openclaw |  |
| 7 | `nilbuild/developer-roadmap` | 355096 | 交互式开发者路线图、入门与进阶教程等学习资料合集。 | https://github.com/nilbuild/developer-roadmap |  |
| 8 | `donnemartin/system-design-primer` | 349343 | 大厂级系统设计学习与面试备战材料（含 Anki 卡片范例）。 | https://github.com/donnemartin/system-design-primer |  |
| 9 | `jwasham/coding-interview-university` | 347080 | 面向软件工程师岗位的系统化计算机科学与面试自学路线图。 | https://github.com/jwasham/coding-interview-university |  |
| 10 | `vinta/awesome-python` | 298586 | 带选型倾向的 Python 框架、扩展库、工具与学习资源合集。 | https://github.com/vinta/awesome-python |  |

---
## Trending 页面快照（HTML 抓取）

**说明**：与上方「全局 Star Search」数据源不同；本段按 GitHub trending 页的 **daily / weekly / monthly** 各拉一页并解析。**若前端改版导致选择器失效，需更新解析逻辑。**

- **标记**列：三个 `since` 子表**各自独立**对照本次拉取前文件中该小节表格已出现的 `owner/repo`；新出现的行标 **新增**。下次拉取会先清空上一轮「新增」再重算（只保留相对**上一版文件**的新仓库）。

### 今日 trending（since=daily）

**页面**： `https://github.com/trending?since=daily`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 | 标记 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- | --- |
| 1 | `tinyhumansai/openhuman` | 21180 | 1865 | Rust | 3,973 stars today | 您的个人人工智能超级智能。私密、简单且功能强大。 | https://github.com/tinyhumansai/openhuman |  |
| 2 | `HKUDS/CLI-Anything` | 37693 | 3609 | Python | 1,038 stars today | "CLI-Anything: Making ALL Software Agent-Native" -- CLI-Hub: https://clianything.cc/ | https://github.com/HKUDS/CLI-Anything |  |
| 3 | `Imbad0202/academic-research-skills` | 14109 | 1333 | Python | 3,164 stars today | Claude Code的学术研究技能：研究→撰写→评审→修订→最终确定 | https://github.com/Imbad0202/academic-research-skills |  |
| 4 | `obra/superpowers` | 198358 | 17698 | Shell | 1,623 stars today | 有效的代理技能框架和软件开发方法。 | https://github.com/obra/superpowers | 新增 |
| 5 | `anthropics/claude-plugins-official` | 20174 | 2506 | Python | 171 stars today | 由Anthropic管理的高质量Claude Code插件的官方目录。 | https://github.com/anthropics/claude-plugins-official | 新增 |
| 6 | `rohitg00/agentmemory` | 14133 | 1179 | TypeScript | 1,609 stars today | # 1基于真实世界基准的AI编码代理持久内存 | https://github.com/rohitg00/agentmemory | 新增 |
| 7 | `CloakHQ/CloakBrowser` | 16576 | 1279 | Python | 1,463 stars today | Stealth Chromium可通过每次机器人检测测试。插入式剧作家更换源级指纹补丁，通过30/30测试 | https://github.com/CloakHQ/CloakBrowser |  |
| 8 | `rtk-ai/rtk` | 50872 | 3102 | Rust | 704 stars today | CLI代理，可将常见开发命令的LLM令牌消耗量减少60-90%。单个Rust二进制文件，零依赖 | https://github.com/rtk-ai/rtk | 新增 |
| 9 | `msitarzewski/agency-agents` | 101595 | 16795 | Shell | 1,120 stars today | 一个完整的人工智能机构，触手可及--从前端向导到Reddit社区忍者，从奇思妙想的注入者到现实检查者。每位客服代表都是具有个性、流程和经过验证的交付成果的专家。 | https://github.com/msitarzewski/agency-agents | 新增 |
| 10 | `colbymchenry/codegraph` | 6588 | 435 | TypeScript | 1,850 stars today | Claude Code、Codex、Cursor和OpenCode的预索引代码知识图—更少的代币、更少的工具调用、100%本地 | https://github.com/colbymchenry/codegraph | 新增 |
| 11 | `multica-ai/andrej-karpathy-skills` | 137980 | 14144 | — | 1,955 stars today | 一个用于改进Claude Code行为的CLAUDE.md文件，源自Andrej Karpathy对LLM编码陷阱的观察。 | https://github.com/multica-ai/andrej-karpathy-skills | 新增 |
| 12 | `humanlayer/12-factor-agents` | 21174 | 1598 | TypeScript | 736 stars today | 我们可以使用哪些原则来构建基于LLM的软件，这些软件实际上足以交付给生产客户？ | https://github.com/humanlayer/12-factor-agents |  |
| 13 | `Diolinux/PhotoGIMP` | 10769 | 375 | CSS | 493 stars today | 适用于Photoshop用户的GIMP 3 +修补程序 | https://github.com/Diolinux/PhotoGIMP | 新增 |
| 14 | `Alishahryar1/free-claude-code` | 26369 | 3930 | Python | 563 stars today | 在终端中免费使用claude-code、VSCode扩展或像OpenClaw这样的不和谐（支持语音） | https://github.com/Alishahryar1/free-claude-code | 新增 |
| 15 | `pascalorg/editor` | 15874 | 2080 | TypeScript | 110 stars today | 创建和共享3D建筑项目。 | https://github.com/pascalorg/editor | 新增 |
| 16 | `frappe/erpnext` | 34272 | 11314 | Python | 98 stars today | 免费开源企业资源规划（ ERP ） | https://github.com/frappe/erpnext | 新增 |
| 17 | `microsoft/ai-agents-for-beginners` | 64327 | 21291 | Jupyter Notebook | 818 stars today | 开始构建人工智能代理的12个教训 | https://github.com/microsoft/ai-agents-for-beginners |  |
| 18 | `HKUDS/ViMax` | 5416 | 921 | Python | 503 stars today | "ViMax ： Agentic Video Generation （导演、编剧、制片人和视频生成器一体机）" | https://github.com/HKUDS/ViMax | 新增 |


### 本周 trending（since=weekly）

**页面**： `https://github.com/trending?since=weekly`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 | 标记 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- | --- |
| 1 | `tinyhumansai/openhuman` | 21181 | 1865 | Rust | 17,793 stars this week | 您的个人人工智能超级智能。私密、简单且功能强大。 | https://github.com/tinyhumansai/openhuman | 新增 |
| 2 | `rohitg00/agentmemory` | 14133 | 1179 | TypeScript | 8,390 stars this week | # 1基于真实世界基准的AI编码代理持久内存 | https://github.com/rohitg00/agentmemory |  |
| 3 | `CloakHQ/CloakBrowser` | 16576 | 1279 | Python | 8,997 stars this week | Stealth Chromium可通过每次机器人检测测试。插入式剧作家更换源级指纹补丁，通过30/30测试 | https://github.com/CloakHQ/CloakBrowser |  |
| 4 | `Imbad0202/academic-research-skills` | 14109 | 1333 | Python | 7,443 stars this week | Claude Code的学术研究技能：研究→撰写→评审→修订→最终确定 | https://github.com/Imbad0202/academic-research-skills |  |
| 5 | `oven-sh/bun` | 92070 | 4609 | Rust | 2,438 stars this week | 令人难以置信的快速JavaScript运行时、捆绑程序、测试运行程序和包管理器–所有功能于一身 | https://github.com/oven-sh/bun |  |
| 6 | `ruvnet/RuView` | 60857 | 7940 | Rust | 8,076 stars this week | π RuView将商用WiFi信号转化为实时空间智能、生命体征监测和存在检测--所有这些都无需一个像素的视频。 | https://github.com/ruvnet/RuView |  |
| 7 | `mattpocock/skills` | 94444 | 8312 | Shell | 19,038 stars this week | 真正工程师的技能。直接来自我的.claude目录。 | https://github.com/mattpocock/skills |  |
| 8 | `colbymchenry/codegraph` | 6589 | 435 | TypeScript | 4,650 stars this week | Claude Code、Codex、Cursor和OpenCode的预索引代码知识图—更少的代币、更少的工具调用、100%本地 | https://github.com/colbymchenry/codegraph |  |
| 9 | `yikart/AiToEarn` | 15520 | 2529 | TypeScript | 3,926 stars this week | 让我们使用人工智能来赚取收入！ | https://github.com/yikart/AiToEarn |  |
| 10 | `facebook/pyrefly` | 6284 | 371 | Rust | 568 stars this week | Python的快速类型检查器和语言服务器 | https://github.com/facebook/pyrefly |  |
| 11 | `anthropics/financial-services` | 25922 | 3600 | Python | 4,737 stars this week | — | https://github.com/anthropics/financial-services |  |
| 12 | `BigBodyCobain/Shadowbroker` | 8258 | 1245 | Python | 1,902 stars this week | 面向全球影院的开源智能。在一个统一的界面中跟踪从富人的公司/私人飞机和间谍卫星到地震事件的所有内容。连接一个AI特工，让它解析数据并找到以前看不见的相关性。知识…… | https://github.com/BigBodyCobain/Shadowbroker | 新增 |
| 13 | `millionco/react-doctor` | 10333 | 331 | TypeScript | 1,796 stars this week | 您的代理写入了错误的React。这会捕获它 | https://github.com/millionco/react-doctor |  |
| 14 | `obra/superpowers` | 198359 | 17698 | Shell | 10,577 stars this week | 有效的代理技能框架和软件开发方法。 | https://github.com/obra/superpowers | 新增 |
| 15 | `apernet/hysteria` | 21361 | 2187 | Go | 1,307 stars this week | 歇斯底里是一种强大、快如闪电、抗审查的代理。 | https://github.com/apernet/hysteria |  |


### 本月 trending（since=monthly）

**页面**： `https://github.com/trending?since=monthly`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 | 标记 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- | --- |
| 1 | `mattpocock/skills` | 94445 | 8312 | Shell | 77,724 stars this month | 真正工程师的技能。直接来自我的.claude目录。 | https://github.com/mattpocock/skills |  |
| 2 | `Alishahryar1/free-claude-code` | 26370 | 3930 | Python | 24,210 stars this month | 在终端中免费使用claude-code、VSCode扩展或像OpenClaw这样的不和谐（支持语音） | https://github.com/Alishahryar1/free-claude-code |  |
| 3 | `multica-ai/andrej-karpathy-skills` | 137981 | 14144 | — | 78,225 stars this month | 一个用于改进Claude Code行为的CLAUDE.md文件，源自Andrej Karpathy对LLM编码陷阱的观察。 | https://github.com/multica-ai/andrej-karpathy-skills |  |
| 4 | `AIDC-AI/Pixelle-Video` | 18420 | 2626 | Python | 14,219 stars this month | 🚀 AI 全自动短视频引擎 · AI Fully Automated Short Video Engine | https://github.com/AIDC-AI/Pixelle-Video |  |
| 5 | `CloakHQ/CloakBrowser` | 16576 | 1279 | Python | 14,849 stars this month | Stealth Chromium可通过每次机器人检测测试。插入式剧作家更换源级指纹补丁，通过30/30测试 | https://github.com/CloakHQ/CloakBrowser |  |
| 6 | `anthropics/financial-services` | 25922 | 3600 | Python | 18,269 stars this month | — | https://github.com/anthropics/financial-services |  |
| 7 | `rohitg00/agentmemory` | 14133 | 1179 | TypeScript | 11,984 stars this month | # 1基于真实世界基准的AI编码代理持久内存 | https://github.com/rohitg00/agentmemory |  |
| 8 | `Z4nzu/hackingtool` | 75596 | 8530 | Python | 17,621 stars this month | 面向黑客的一体化黑客工具 | https://github.com/Z4nzu/hackingtool |  |
| 9 | `soxoj/maigret` | 29500 | 2119 | Python | 10,054 stars this month | 通过用户名从3000多个网站🕵️‍♂️收集个人档案 | https://github.com/soxoj/maigret |  |
| 10 | `TauricResearch/TradingAgents` | 77379 | 15086 | Python | 26,106 stars this month | TradingAgent ：多代理LLM金融交易框架 | https://github.com/TauricResearch/TradingAgents |  |
| 11 | `addyosmani/agent-skills` | 43865 | 4831 | Shell | 26,168 stars this month | AI编码代理的生产级工程技能。 | https://github.com/addyosmani/agent-skills |  |
| 12 | `Anil-matcha/Open-Generative-AI` | 16057 | 2710 | JavaScript | 10,880 stars this month | 人工智能视频平台的开源替代品—免费的人工智能图像和视频生成工作室，拥有200多种型号（ Flux、Midjourney、Kling、Sora、Veo ）。无内容过滤器。自托管，麻省理工学院许可。 | https://github.com/Anil-matcha/Open-Generative-AI |  |
| 13 | `decolua/9router` | 12547 | 1890 | JavaScript | 9,811 stars this month | 无限免费AI编码。通过40多家供应商将Claude Code、Codex、Cursor、Cline、Copilot、Antigravity连接到免费的Claude/GPT/Gemini。自动回退， RTK -40%代币，从未达到限制。 | https://github.com/decolua/9router |  |
| 14 | `Fincept-Corporation/FinceptTerminal` | 21760 | 2924 | Python | 16,436 stars this month | FinceptTerminal是一款现代金融应用程序，提供先进的市场分析、投资研究和经济数据工具，专为在用户友好的环境中进行交互式探索和数据驱动的决策而设计。 | https://github.com/Fincept-Corporation/FinceptTerminal |  |
| 15 | `Imbad0202/academic-research-skills` | 14109 | 1333 | Python | 10,628 stars this month | Claude Code的学术研究技能：研究→撰写→评审→修订→最终确定 | https://github.com/Imbad0202/academic-research-skills | 新增 |
| 16 | `heygen-com/hyperframes` | 19700 | 1855 | TypeScript | 13,702 stars this month | 编写HTML。渲染视频。专为客服代表打造。 | https://github.com/heygen-com/hyperframes |  |
| 17 | `ruvnet/ruflo` | 53218 | 6027 | TypeScript | 21,104 stars this month | 🌊 Claude的领先代理编排平台。部署智能多智能体群，协调自主工作流程，构建对话式人工智能系统。具有企业级架构、自学群体智能、RAG集成和本地Claude Code/… | https://github.com/ruvnet/ruflo |  |

