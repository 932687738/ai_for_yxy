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

**最近一次更新时间**（Asia/Shanghai）： 2026-05-18 08:58:25

| 序号 | 仓库 | Stars | 仓库简介（中文） | 链接 | 标记 |
| --- | --- | ---:| --- | --- | --- |
| 1 | `codecrafters-io/build-your-own-x` | 502057 | 通过从零重写各类代表性技术来学习编程与设计，加深对底层原理的理解。 | https://github.com/codecrafters-io/build-your-own-x |  |
| 2 | `sindresorhus/awesome` | 467426 | 围绕多种主题整理的「Awesome」精品清单合集。 | https://github.com/sindresorhus/awesome |  |
| 3 | `freeCodeCamp/freeCodeCamp` | 445021 | freeCodeCamp 官网开源代码与学习课程：可免费学习编程、数学与计算机科学。 | https://github.com/freeCodeCamp/freeCodeCamp |  |
| 4 | `public-apis/public-apis` | 435531 | 免费可用的公共 API 资源汇总清单。 | https://github.com/public-apis/public-apis |  |
| 5 | `EbookFoundation/free-programming-books` | 388470 | 可免费获取的编程与计算机类书籍书单汇总。 | https://github.com/EbookFoundation/free-programming-books |  |
| 6 | `openclaw/openclaw` | 372693 | 可在多系统运行的个人 AI 助手（吉祥物为龙虾图标）。 | https://github.com/openclaw/openclaw |  |
| 7 | `nilbuild/developer-roadmap` | 354967 | 交互式开发者路线图、入门与进阶教程等学习资料合集。 | https://github.com/nilbuild/developer-roadmap |  |
| 8 | `donnemartin/system-design-primer` | 349050 | 大厂级系统设计学习与面试备战材料（含 Anki 卡片范例）。 | https://github.com/donnemartin/system-design-primer |  |
| 9 | `jwasham/coding-interview-university` | 346935 | 面向软件工程师岗位的系统化计算机科学与面试自学路线图。 | https://github.com/jwasham/coding-interview-university |  |
| 10 | `vinta/awesome-python` | 298225 | 带选型倾向的 Python 框架、扩展库、工具与学习资源合集。 | https://github.com/vinta/awesome-python |  |

---
## Trending 页面快照（HTML 抓取）

**说明**：与上方「全局 Star Search」数据源不同；本段按 GitHub trending 页的 **daily / weekly / monthly** 各拉一页并解析。**若前端改版导致选择器失效，需更新解析逻辑。**

- **标记**列：三个 `since` 子表**各自独立**对照本次拉取前文件中该小节表格已出现的 `owner/repo`；新出现的行标 **新增**。下次拉取会先清空上一轮「新增」再重算（只保留相对**上一版文件**的新仓库）。

### 今日 trending（since=daily）

**页面**： `https://github.com/trending?since=daily`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 | 标记 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- | --- |
| 1 | `tinyhumansai/openhuman` | 13219 | 1138 | Rust | 1,690 stars today | 您的个人人工智能超级智能。私密、简单且功能强大。 | https://github.com/tinyhumansai/openhuman |  |
| 2 | `HKUDS/CLI-Anything` | 35615 | 3480 | Python | 238 stars today | "CLI-Anything: Making ALL Software Agent-Native" -- CLI-Hub: https://clianything.cc/ | https://github.com/HKUDS/CLI-Anything |  |
| 3 | `calcom/cal.diy` | 43273 | 13403 | TypeScript | 433 stars today | 为每个人安排基础设施。 | https://github.com/calcom/cal.diy |  |
| 4 | `oven-sh/bun` | 91715 | 4578 | Rust | 910 stars today | 令人难以置信的快速JavaScript运行时、捆绑程序、测试运行程序和包管理器–所有功能于一身 | https://github.com/oven-sh/bun |  |
| 5 | `Anil-matcha/Open-Generative-AI` | 15101 | 2589 | JavaScript | 703 stars today | 人工智能视频平台的开源替代品—免费的人工智能图像和视频生成工作室，拥有200多种型号（ Flux、Midjourney、Kling、Sora、Veo ）。无内容过滤器。自托管，麻省理工学院许可。 | https://github.com/Anil-matcha/Open-Generative-AI |  |
| 6 | `BigBodyCobain/Shadowbroker` | 7085 | 1111 | Python | 333 stars today | 面向全球影院的开源智能。在一个统一的界面中跟踪从富人的公司/私人飞机和间谍卫星到地震事件的所有内容。连接一个AI特工，让它解析数据并找到以前看不见的相关性。知识…… | https://github.com/BigBodyCobain/Shadowbroker |  |
| 7 | `tech-leads-club/agent-skills` | 3534 | 320 | TypeScript | 225 stars today | 专业AI编码代理的安全、经过验证的技能注册表。绝对自信地扩展Antigravity、Claude Code、Cursor、Copilot等。 | https://github.com/tech-leads-club/agent-skills |  |
| 8 | `NirDiamant/agents-towards-production` | 19919 | 2647 | Jupyter Notebook | 172 stars today | 用于构建生产级GenAI代理的端到端代码优先教程。从原型到企业部署。 | https://github.com/NirDiamant/agents-towards-production |  |
| 9 | `dograh-hq/dograh` | 1670 | 370 | Python | 223 stars today | 开源语音代理平台 | https://github.com/dograh-hq/dograh |  |
| 10 | `K-Dense-AI/scientific-agent-skills` | 23818 | 2536 | Python | 762 stars today | 一套随时可用的代理技能，用于研究、科学、工程、分析、财务和写作。 | https://github.com/K-Dense-AI/scientific-agent-skills |  |
| 11 | `Light-Heart-Labs/DreamServer` | 1164 | 206 | Python | 112 stars today | 适用于所有人的本地AI — LLM推理、聊天UI、语音、代理、工作流程、RAG和图像生成。无云，无订阅。 | https://github.com/Light-Heart-Labs/DreamServer |  |
| 12 | `KeygraphHQ/shannon` | 42711 | 4871 | TypeScript | 200 stars today | Shannon Lite是一款适用于Web应用程序和API的自动化白盒AI探测器。它会分析您的源代码，识别攻击媒介，并在漏洞到达生产环境之前执行真正的漏洞利用来证明漏洞。 | https://github.com/KeygraphHQ/shannon |  |
| 13 | `TryGhost/Ghost` | 53300 | 11611 | JavaScript | 231 stars today | 用于现代出版、会员、订阅和时事通讯的独立技术。 | https://github.com/TryGhost/Ghost |  |
| 14 | `medusajs/medusa` | 33494 | 4468 | TypeScript | 211 stars today | 全球最灵活的商务平台。 | https://github.com/medusajs/medusa |  |
| 15 | `knadh/listmonk` | 20603 | 2146 | Go | 242 stars today | 高性能、自托管、时事通讯和邮件列表管理器，配备现代化仪表板。单一二进制应用。 | https://github.com/knadh/listmonk |  |
| 16 | `plausible/analytics` | 25424 | 1459 | Elixir | 186 stars today | 开源、隐私至上的网络分析。轻量级、无Cookie的Google Analytics替代方案。自托管或云。 | https://github.com/plausible/analytics |  |
| 17 | `colbymchenry/codegraph` | 3319 | 259 | TypeScript | 857 stars today | Claude Code、Codex和Cursor的预索引代码知识图—更少的代币、更少的工具调用、100%本地 | https://github.com/colbymchenry/codegraph |  |
| 18 | `microsoft/ai-agents-for-beginners` | 62540 | 21033 | Jupyter Notebook | 485 stars today | 开始构建人工智能代理的12个教训 | https://github.com/microsoft/ai-agents-for-beginners |  |


### 本周 trending（since=weekly）

**页面**： `https://github.com/trending?since=weekly`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 | 标记 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- | --- |
| 1 | `CloakHQ/CloakBrowser` | 13776 | 1074 | Python | 9,007 stars this week | Stealth Chromium可通过每次机器人检测测试。插入式剧作家更换源级指纹补丁，通过30/30测试 | https://github.com/CloakHQ/CloakBrowser |  |
| 2 | `rohitg00/agentmemory` | 11302 | 950 | TypeScript | 7,103 stars this week | # 1基于真实世界基准的AI编码代理持久内存 | https://github.com/rohitg00/agentmemory |  |
| 3 | `yikart/AiToEarn` | 14699 | 2451 | TypeScript | 4,687 stars this week | 让我们使用人工智能来赚取收入！ | https://github.com/yikart/AiToEarn |  |
| 4 | `anthropics/financial-services` | 24396 | 3366 | Python | 5,977 stars this week | — | https://github.com/anthropics/financial-services |  |
| 5 | `oven-sh/bun` | 91715 | 4578 | Rust | 2,098 stars this week | 令人难以置信的快速JavaScript运行时、捆绑程序、测试运行程序和包管理器–所有功能于一身 | https://github.com/oven-sh/bun |  |
| 6 | `Imbad0202/academic-research-skills` | 9340 | 1034 | Python | 3,624 stars this week | Claude Code的学术研究技能：研究→撰写→评审→修订→最终确定 | https://github.com/Imbad0202/academic-research-skills |  |
| 7 | `mattpocock/skills` | 88975 | 7773 | Shell | 19,679 stars this week | 真正工程师的技能。直接来自我的.claude目录。 | https://github.com/mattpocock/skills |  |
| 8 | `ruvnet/RuView` | 59211 | 7728 | Rust | 6,733 stars this week | π RuView将商用WiFi信号转化为实时空间智能、生命体征监测和存在检测--所有这些都无需一个像素的视频。 | https://github.com/ruvnet/RuView |  |
| 9 | `bytedance/UI-TARS-desktop` | 34417 | 3447 | TypeScript | 2,563 stars this week | 开源多模态人工智能代理堆栈：连接尖端人工智能模型和代理基础设施 | https://github.com/bytedance/UI-TARS-desktop |  |
| 10 | `apernet/hysteria` | 21092 | 2170 | Go | 1,124 stars this week | 歇斯底里是一种强大、快如闪电、抗审查的代理。 | https://github.com/apernet/hysteria |  |
| 11 | `decolua/9router` | 11609 | 1766 | JavaScript | 4,458 stars this week | 无限免费AI编码。通过40多家供应商将Claude Code、Codex、Cursor、Cline、Copilot、Antigravity连接到免费的Claude/GPT/Gemini。自动回退， RTK -40%代币，从未达到限制。 | https://github.com/decolua/9router |  |
| 12 | `HKUDS/AI-Trader` | 17879 | 2730 | Python | 2,499 stars this week | “AI-Trader ： 100%全自动代理本地交易” | https://github.com/HKUDS/AI-Trader |  |
| 13 | `millionco/react-doctor` | 9953 | 315 | TypeScript | 2,430 stars this week | 您的代理写入了错误的React。这会捕获它 | https://github.com/millionco/react-doctor |  |
| 14 | `Hmbown/DeepSeek-TUI` | 31251 | 2637 | Rust | 7,444 stars this week | 在您的终端中运行的DeepSeek模型的编码代理 | https://github.com/Hmbown/DeepSeek-TUI |  |
| 15 | `facebook/pyrefly` | 6112 | 361 | Rust | 394 stars this week | Python的快速类型检查器和语言服务器 | https://github.com/facebook/pyrefly |  |
| 16 | `obra/superpowers` | 195138 | 17353 | Shell | 10,094 stars this week | 有效的代理技能框架和软件开发方法。 | https://github.com/obra/superpowers |  |


### 本月 trending（since=monthly）

**页面**： `https://github.com/trending?since=monthly`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 | 标记 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- | --- |
| 1 | `mattpocock/skills` | 88976 | 7773 | Shell | 72,549 stars this month | 真正工程师的技能。直接来自我的.claude目录。 | https://github.com/mattpocock/skills |  |
| 2 | `Alishahryar1/free-claude-code` | 25237 | 3767 | Python | 23,360 stars this month | 在终端中免费使用claude-code、VSCode扩展或像OpenClaw这样的不和谐（支持语音） | https://github.com/Alishahryar1/free-claude-code |  |
| 3 | `multica-ai/andrej-karpathy-skills` | 133989 | 13692 | — | 80,814 stars this month | 一个用于改进Claude Code行为的CLAUDE.md文件，源自Andrej Karpathy对LLM编码陷阱的观察。 | https://github.com/multica-ai/andrej-karpathy-skills |  |
| 4 | `Fincept-Corporation/FinceptTerminal` | 21423 | 2894 | Python | 18,300 stars this month | FinceptTerminal是一款现代金融应用程序，提供先进的市场分析、投资研究和经济数据工具，专为在用户友好的环境中进行交互式探索和数据驱动的决策而设计。 | https://github.com/Fincept-Corporation/FinceptTerminal |  |
| 5 | `AIDC-AI/Pixelle-Video` | 17763 | 2559 | Python | 13,649 stars this month | 🚀 AI 全自动短视频引擎 · AI Fully Automated Short Video Engine | https://github.com/AIDC-AI/Pixelle-Video |  |
| 6 | `heygen-com/hyperframes` | 19012 | 1786 | TypeScript | 17,005 stars this month | 编写HTML。渲染视频。专为客服代表打造。 | https://github.com/heygen-com/hyperframes |  |
| 7 | `ComposioHQ/awesome-codex-skills` | 10261 | 950 | Python | 9,458 stars this month | 用于跨Codex CLI和API自动化工作流程的实用Codex技能精选列表。 | https://github.com/ComposioHQ/awesome-codex-skills |  |
| 8 | `anthropics/financial-services` | 24396 | 3366 | Python | 16,660 stars this month | — | https://github.com/anthropics/financial-services |  |
| 9 | `Z4nzu/hackingtool` | 75141 | 8472 | Python | 17,238 stars this month | 面向黑客的一体化黑客工具 | https://github.com/Z4nzu/hackingtool |  |
| 10 | `soxoj/maigret` | 29171 | 2089 | Python | 9,724 stars this month | 通过用户名从3000多个网站🕵️‍♂️收集个人档案 | https://github.com/soxoj/maigret |  |
| 11 | `addyosmani/agent-skills` | 42913 | 4721 | Shell | 26,146 stars this month | AI编码代理的生产级工程技能。 | https://github.com/addyosmani/agent-skills |  |
| 12 | `TauricResearch/TradingAgents` | 76544 | 14910 | Python | 25,690 stars this month | TradingAgent ：多代理LLM金融交易框架 | https://github.com/TauricResearch/TradingAgents |  |
| 13 | `CloakHQ/CloakBrowser` | 13777 | 1075 | Python | 11,968 stars this month | Stealth Chromium可通过每次机器人检测测试。插入式剧作家更换源级指纹补丁，通过30/30测试 | https://github.com/CloakHQ/CloakBrowser |  |
| 14 | `rohitg00/agentmemory` | 11303 | 950 | TypeScript | 9,195 stars this month | # 1基于真实世界基准的AI编码代理持久内存 | https://github.com/rohitg00/agentmemory |  |
| 15 | `Anil-matcha/Open-Generative-AI` | 15101 | 2589 | JavaScript | 9,874 stars this month | 人工智能视频平台的开源替代品—免费的人工智能图像和视频生成工作室，拥有200多种型号（ Flux、Midjourney、Kling、Sora、Veo ）。无内容过滤器。自托管，麻省理工学院许可。 | https://github.com/Anil-matcha/Open-Generative-AI |  |
| 16 | `zilliztech/claude-context` | 11309 | 835 | TypeScript | 5,370 stars this month | 代码搜索MCP以查找Claude Code。使整个代码库成为任何编码代理的上下文。 | https://github.com/zilliztech/claude-context |  |
| 17 | `NousResearch/hermes-agent` | 154808 | 24799 | Python | 59,362 stars this month | 与您一起成长的客服代表 | https://github.com/NousResearch/hermes-agent |  |
| 18 | `decolua/9router` | 11609 | 1766 | JavaScript | 8,852 stars this month | 无限免费AI编码。通过40多家供应商将Claude Code、Codex、Cursor、Cline、Copilot、Antigravity连接到免费的Claude/GPT/Gemini。自动回退， RTK -40%代币，从未达到限制。 | https://github.com/decolua/9router |  |
| 19 | `ruvnet/ruflo` | 52374 | 5921 | TypeScript | 20,419 stars this month | 🌊 Claude的领先代理编排平台。部署智能多智能体群，协调自主工作流程，构建对话式人工智能系统。具有企业级架构、自学群体智能、RAG集成和本地Claude Code/… | https://github.com/ruvnet/ruflo |  |

