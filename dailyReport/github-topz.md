# GitHub 快照（Stars Search API + Trending）

本文件由 `tools/update_github_topz.py` 生成，两块内容独立编排：

- **模块一**：`tools/github_topz/stars_merge.py` → GitHub REST `/search/repositories` 全局 Star 前十名，并按既有规则与本节历史 Markdown 表格合并（列结构与原 `github-topz.md` 一致）。
- **模块二**：`tools/github_topz/trending_fetch.py` → 抓取 Trending 「今日 / 本周 / 本月」页面 HTML，`article.Box-row` 解析后与中文简介渲染。

---
## 全局 Star Search API（与文件历史合并）

- 数据源：[`dual-digest-on-pull`](../.cursor/rules/dual-digest-on-pull.mdc) 工作流程下配套的 GitHub Search API：`sort=stars` **全局前十名**（`/search/repositories`）。与本节历史行合并时：**已出现的仓库更新 Stars**，新仓库按 Star **降序** 参与整表排序。
- **仓库简介**列：数据源为 GitHub `description`，**写入时为中文简述**——常见仓库内置固定中文提要；其余在渲染时尽力通过公开翻译接口转写，失败则回退英文摘录。表格中若为中文且无新的英文数据源，会直接沿用原有中文单元格。
- **与 Trending 区别**：本节为全局累计 Star 排序快照；文末 Trending 为 GitHub「今日 / 本周 / 本月热度」榜单，数据源与口径均不同。

**最近一次更新时间**（Asia/Shanghai）： 2026-05-17 07:37:29

| 序号 | 仓库 | Stars | 仓库简介（中文） | 链接 |
| --- | --- | ---:| --- | --- |
| 1 | `codecrafters-io/build-your-own-x` | 501846 | 通过从零重写各类代表性技术来学习编程与设计，加深对底层原理的理解。 | https://github.com/codecrafters-io/build-your-own-x |
| 2 | `sindresorhus/awesome` | 467076 | 围绕多种主题整理的「Awesome」精品清单合集。 | https://github.com/sindresorhus/awesome |
| 3 | `freeCodeCamp/freeCodeCamp` | 444933 | freeCodeCamp 官网开源代码与学习课程：可免费学习编程、数学与计算机科学。 | https://github.com/freeCodeCamp/freeCodeCamp |
| 4 | `public-apis/public-apis` | 435326 | 免费可用的公共 API 资源汇总清单。 | https://github.com/public-apis/public-apis |
| 5 | `EbookFoundation/free-programming-books` | 388422 | 可免费获取的编程与计算机类书籍书单汇总。 | https://github.com/EbookFoundation/free-programming-books |
| 6 | `openclaw/openclaw` | 372436 | 可在多系统运行的个人 AI 助手（吉祥物为龙虾图标）。 | https://github.com/openclaw/openclaw |
| 7 | `nilbuild/developer-roadmap` | 354894 | 交互式开发者路线图、入门与进阶教程等学习资料合集。 | https://github.com/nilbuild/developer-roadmap |
| 8 | `donnemartin/system-design-primer` | 348890 | 大厂级系统设计学习与面试备战材料（含 Anki 卡片范例）。 | https://github.com/donnemartin/system-design-primer |
| 9 | `jwasham/coding-interview-university` | 346866 | 面向软件工程师岗位的系统化计算机科学与面试自学路线图。 | https://github.com/jwasham/coding-interview-university |
| 10 | `vinta/awesome-python` | 298003 | 带选型倾向的 Python 框架、扩展库、工具与学习资源合集。 | https://github.com/vinta/awesome-python |
| 11 | `awesome-selfhosted/awesome-selfhosted` | 292255 | 可自行部署的各类自由软件网络服务与 Web 应用清单。 | https://github.com/awesome-selfhosted/awesome-selfhosted |
| 12 | `996icu/996.ICU` | 276176 | 倡议关注「996」工作制、计数星标与交流的开发社区仓库（含网络迷因用语）。 | https://github.com/996icu/996.ICU |
| 13 | `facebook/react` | 245012 | 用于构建 Web 与原生用户界面的 React 视图库（含多端生态）。 | https://github.com/facebook/react |

---
## Trending 页面快照（HTML 抓取）

**说明**：与上方「全局 Star Search」数据源不同；本段按 GitHub trending 页的 **daily / weekly / monthly** 各拉一页并解析。**若前端改版导致选择器失效，需更新解析逻辑。**

### 今日 trending（since=daily）

**页面**： `https://github.com/trending?since=daily`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- |
| 1 | `oven-sh/bun` | 91180 | 4547 | Rust | 414 stars today | 令人难以置信的快速JavaScript运行时、捆绑程序、测试运行程序和包管理器–所有功能于一身 | https://github.com/oven-sh/bun |
| 2 | `K-Dense-AI/scientific-agent-skills` | 23106 | 2487 | Python | 669 stars today | 一套随时可用的代理技能，用于研究、科学、工程、分析、财务和写作。 | https://github.com/K-Dense-AI/scientific-agent-skills |
| 3 | `obra/superpowers` | 193965 | 17259 | Shell | 1,281 stars today | 有效的代理技能框架和软件开发方法。 | https://github.com/obra/superpowers |
| 4 | `Anil-matcha/Open-Generative-AI` | 14404 | 2513 | JavaScript | 393 stars today | 人工智能视频平台的开源替代品—免费的人工智能图像和视频生成工作室，拥有200多种型号（ Flux、Midjourney、Kling、Sora、Veo ）。无内容过滤器。自托管，麻省理工学院许可。 | https://github.com/Anil-matcha/Open-Generative-AI |
| 5 | `supertone-inc/supertonic` | 6841 | 700 | Swift | 745 stars today | 闪电般的快速、设备上、多语言TTS —通过ONNX本地运行。 | https://github.com/supertone-inc/supertonic |
| 6 | `tinyhumansai/openhuman` | 10663 | 919 | Rust | 1,601 stars today | 您的个人人工智能超级智能。私密、简单且功能强大。 | https://github.com/tinyhumansai/openhuman |
| 7 | `ruvnet/RuView` | 58314 | 7620 | Rust | 990 stars today | π RuView将商用WiFi信号转化为实时空间智能、生命体征监测和存在检测--所有这些都无需一个像素的视频。 | https://github.com/ruvnet/RuView |
| 8 | `colbymchenry/codegraph` | 2486 | 208 | TypeScript | 397 stars today | Claude Code的预索引代码知识图—更少的代币、更少的工具调用、100%本地 | https://github.com/colbymchenry/codegraph |


### 本周 trending（since=weekly）

**页面**： `https://github.com/trending?since=weekly`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- |
| 1 | `CloakHQ/CloakBrowser` | 12615 | 972 | Python | 9,120 stars this week | Stealth Chromium可通过每次机器人检测测试。插入式剧作家更换源级指纹补丁，通过30/30测试 | https://github.com/CloakHQ/CloakBrowser |
| 2 | `yikart/AiToEarn` | 14273 | 2402 | TypeScript | 4,762 stars this week | 让我们使用人工智能来赚取收入！ | https://github.com/yikart/AiToEarn |
| 3 | `rohitg00/agentmemory` | 10306 | 862 | TypeScript | 6,865 stars this week | # 1基于真实世界基准的AI编码代理持久内存 | https://github.com/rohitg00/agentmemory |
| 4 | `anthropics/financial-services` | 23798 | 3286 | Python | 9,480 stars this week | — | https://github.com/anthropics/financial-services |
| 5 | `bytedance/UI-TARS-desktop` | 34234 | 3416 | TypeScript | 3,529 stars this week | 开源多模态人工智能代理堆栈：连接尖端人工智能模型和代理基础设施 | https://github.com/bytedance/UI-TARS-desktop |
| 6 | `decolua/9router` | 11093 | 1702 | JavaScript | 5,377 stars this week | 无限免费AI编码。通过40多家供应商将Claude Code、Codex、Cursor、Cline、Copilot、Antigravity连接到免费的Claude/GPT/Gemini。自动回退， RTK -40%代币，从未达到限制。 | https://github.com/decolua/9router |
| 7 | `Imbad0202/academic-research-skills` | 8069 | 903 | Python | 2,762 stars this week | Claude Code的学术研究技能：研究→撰写→评审→修订→最终确定 | https://github.com/Imbad0202/academic-research-skills |
| 8 | `oven-sh/bun` | 91183 | 4547 | Rust | 940 stars this week | 令人难以置信的快速JavaScript运行时、捆绑程序、测试运行程序和包管理器–所有功能于一身 | https://github.com/oven-sh/bun |
| 9 | `mattpocock/skills` | 86813 | 7554 | Shell | 18,278 stars this week | 真正工程师的技能。直接来自我的.claude目录。 | https://github.com/mattpocock/skills |
| 10 | `Hmbown/DeepSeek-TUI` | 30508 | 2560 | Rust | 8,701 stars this week | 在您的终端中运行的DeepSeek模型的编码代理 | https://github.com/Hmbown/DeepSeek-TUI |
| 11 | `HKUDS/AI-Trader` | 17551 | 2699 | Python | 3,004 stars this week | “AI-Trader ： 100%全自动代理本地交易” | https://github.com/HKUDS/AI-Trader |
| 12 | `ruvnet/RuView` | 58315 | 7620 | Rust | 4,963 stars this week | π RuView将商用WiFi信号转化为实时空间智能、生命体征监测和存在检测--所有这些都无需一个像素的视频。 | https://github.com/ruvnet/RuView |
| 13 | `apernet/hysteria` | 20952 | 2156 | Go | 952 stars this week | 歇斯底里是一种强大、快如闪电、抗审查的代理。 | https://github.com/apernet/hysteria |
| 14 | `millionco/react-doctor` | 9766 | 304 | TypeScript | 3,314 stars this week | 您的代理写入了错误的React。这会捕获它 | https://github.com/millionco/react-doctor |
| 15 | `playcanvas/supersplat` | 8161 | 882 | TypeScript | 2,571 stars this week | 3D高斯拼接编辑器 | https://github.com/playcanvas/supersplat |


### 本月 trending（since=monthly）

**页面**： `https://github.com/trending?since=monthly`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- |
| 1 | `mattpocock/skills` | 86813 | 7554 | Shell | 69,142 stars this month | 真正工程师的技能。直接来自我的.claude目录。 | https://github.com/mattpocock/skills |
| 2 | `Alishahryar1/free-claude-code` | 25006 | 3726 | Python | 22,992 stars this month | 在终端中免费使用claude-code、VSCode扩展或像OpenClaw这样的不和谐（支持语音） | https://github.com/Alishahryar1/free-claude-code |
| 3 | `multica-ai/andrej-karpathy-skills` | 132453 | 13499 | — | 91,995 stars this month | 一个用于改进Claude Code行为的CLAUDE.md文件，源自Andrej Karpathy对LLM编码陷阱的观察。 | https://github.com/multica-ai/andrej-karpathy-skills |
| 4 | `heygen-com/hyperframes` | 18684 | 1746 | TypeScript | 18,559 stars this month | 编写HTML。渲染视频。专为客服代表打造。 | https://github.com/heygen-com/hyperframes |
| 5 | `AIDC-AI/Pixelle-Video` | 17443 | 2517 | Python | 13,040 stars this month | 🚀 AI 全自动短视频引擎 · AI Fully Automated Short Video Engine | https://github.com/AIDC-AI/Pixelle-Video |
| 6 | `ComposioHQ/awesome-codex-skills` | 10043 | 940 | Python | 9,051 stars this month | 用于跨Codex CLI和API自动化工作流程的实用Codex技能精选列表。 | https://github.com/ComposioHQ/awesome-codex-skills |
| 7 | `anthropics/financial-services` | 23798 | 3286 | Python | 15,671 stars this month | — | https://github.com/anthropics/financial-services |
| 8 | `Z4nzu/hackingtool` | 74966 | 8463 | Python | 16,836 stars this month | 面向黑客的一体化黑客工具 | https://github.com/Z4nzu/hackingtool |
| 9 | `addyosmani/agent-skills` | 42494 | 4665 | Shell | 26,378 stars this month | AI编码代理的生产级工程技能。 | https://github.com/addyosmani/agent-skills |
| 10 | `soxoj/maigret` | 28993 | 2079 | Python | 9,406 stars this month | 通过用户名从3000多个网站🕵️‍♂️收集个人档案 | https://github.com/soxoj/maigret |
| 11 | `TauricResearch/TradingAgents` | 76155 | 14822 | Python | 25,571 stars this month | TradingAgent ：多代理LLM金融交易框架 | https://github.com/TauricResearch/TradingAgents |
| 12 | `thunderbird/thunderbolt` | 4586 | 311 | TypeScript | 4,594 stars this month | 你控制的人工智能：选择你的模型。拥有您的数据。消除供应商锁定。 | https://github.com/thunderbird/thunderbolt |
| 13 | `NousResearch/hermes-agent` | 153394 | 24459 | Python | 64,550 stars this month | 与您一起成长的客服代表 | https://github.com/NousResearch/hermes-agent |
| 14 | `CloakHQ/CloakBrowser` | 12615 | 972 | Python | 10,339 stars this month | Stealth Chromium可通过每次机器人检测测试。插入式剧作家更换源级指纹补丁，通过30/30测试 | https://github.com/CloakHQ/CloakBrowser |
| 15 | `rohitg00/agentmemory` | 10306 | 862 | TypeScript | 7,834 stars this month | # 1基于真实世界基准的AI编码代理持久内存 | https://github.com/rohitg00/agentmemory |
| 16 | `Anil-matcha/Open-Generative-AI` | 14405 | 2513 | JavaScript | 9,079 stars this month | 人工智能视频平台的开源替代品—免费的人工智能图像和视频生成工作室，拥有200多种型号（ Flux、Midjourney、Kling、Sora、Veo ）。无内容过滤器。自托管，麻省理工学院许可。 | https://github.com/Anil-matcha/Open-Generative-AI |
| 17 | `zilliztech/claude-context` | 11208 | 834 | TypeScript | 5,221 stars this month | 代码搜索MCP以查找Claude Code。使整个代码库成为任何编码代理的上下文。 | https://github.com/zilliztech/claude-context |
| 18 | `Tracer-Cloud/opensre` | 5256 | 657 | Python | 4,345 stars this month | 构建您自己的AI SRE代理。人工智能时代的开源工具包。 | https://github.com/Tracer-Cloud/opensre |
| 19 | `decolua/9router` | 11093 | 1702 | JavaScript | 8,091 stars this month | 无限免费AI编码。通过40多家供应商将Claude Code、Codex、Cursor、Cline、Copilot、Antigravity连接到免费的Claude/GPT/Gemini。自动回退， RTK -40%代币，从未达到限制。 | https://github.com/decolua/9router |

