# GitHub 快照（Stars Search API + Trending）

本文件由 `tools/update_github_topz.py` 生成，两块内容独立编排：

- **模块一**：`tools/github_topz/stars_merge.py` → GitHub REST `/search/repositories` 全局 Star 前十名，并按既有规则与本节历史 Markdown 表格合并（列结构与原 `github-topz.md` 一致）。
- **模块二**：`tools/github_topz/trending_fetch.py` → 抓取 Trending 「今日 / 本周 / 本月」页面 HTML，`article.Box-row` 解析后与中文简介渲染。

---
## 全局 Star Search API（与文件历史合并）

- 数据源：[`dual-digest-on-pull`](../.cursor/rules/dual-digest-on-pull.mdc) 工作流程下配套的 GitHub Search API：`sort=stars` **全局前十名**（`/search/repositories`）。与本节历史行合并时：**已出现的仓库更新 Stars**，新仓库按 Star **降序** 参与整表排序。
- **仓库简介**列：数据源为 GitHub `description`，**写入时为中文简述**——常见仓库内置固定中文提要；其余在渲染时尽力通过公开翻译接口转写，失败则回退英文摘录。表格中若为中文且无新的英文数据源，会直接沿用原有中文单元格。
- **与 Trending 区别**：本节为全局累计 Star 排序快照；文末 Trending 为 GitHub「今日 / 本周 / 本月热度」榜单，数据源与口径均不同。

**最近一次更新时间**（Asia/Shanghai）： 2026-05-15 09:43:21

| 序号 | 仓库 | Stars | 仓库简介（中文） | 链接 |
| --- | --- | ---:| --- | --- |
| 1 | `codecrafters-io/build-your-own-x` | 501471 | 通过从零重写各类代表性技术来学习编程与设计，加深对底层原理的理解。 | https://github.com/codecrafters-io/build-your-own-x |
| 2 | `sindresorhus/awesome` | 466397 | 围绕多种主题整理的「Awesome」精品清单合集。 | https://github.com/sindresorhus/awesome |
| 3 | `freeCodeCamp/freeCodeCamp` | 444739 | freeCodeCamp 官网开源代码与学习课程：可免费学习编程、数学与计算机科学。 | https://github.com/freeCodeCamp/freeCodeCamp |
| 4 | `public-apis/public-apis` | 435042 | 免费可用的公共 API 资源汇总清单。 | https://github.com/public-apis/public-apis |
| 5 | `EbookFoundation/free-programming-books` | 388303 | 可免费获取的编程与计算机类书籍书单汇总。 | https://github.com/EbookFoundation/free-programming-books |
| 6 | `openclaw/openclaw` | 371900 | 可在多系统运行的个人 AI 助手（吉祥物为龙虾图标）。 | https://github.com/openclaw/openclaw |
| 7 | `nilbuild/developer-roadmap` | 354766 | 交互式开发者路线图、入门与进阶教程等学习资料合集。 | https://github.com/nilbuild/developer-roadmap |
| 8 | `donnemartin/system-design-primer` | 348612 | 大厂级系统设计学习与面试备战材料（含 Anki 卡片范例）。 | https://github.com/donnemartin/system-design-primer |
| 9 | `jwasham/coding-interview-university` | 346750 | 面向软件工程师岗位的系统化计算机科学与面试自学路线图。 | https://github.com/jwasham/coding-interview-university |
| 10 | `vinta/awesome-python` | 297672 | 带选型倾向的 Python 框架、扩展库、工具与学习资源合集。 | https://github.com/vinta/awesome-python |
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
| 1 | `ruvnet/RuView` | 56076 | 7420 | Rust | 1,715 stars today | π RuView将商用WiFi信号转化为实时空间智能、生命体征监测和存在检测--所有这些都无需一个像素的视频。 | https://github.com/ruvnet/RuView |
| 2 | `tinyhumansai/openhuman` | 7808 | 629 | Rust | 3,329 stars today | 您的个人人工智能超级智能。私密、简单且功能强大。 | https://github.com/tinyhumansai/openhuman |
| 3 | `rohitg00/agentmemory` | 9012 | 746 | TypeScript | 1,879 stars today | # 1基于真实世界基准的AI编码代理持久内存 | https://github.com/rohitg00/agentmemory |
| 4 | `obra/superpowers` | 191262 | 17014 | Shell | 1,780 stars today | 有效的代理技能框架和软件开发方法。 | https://github.com/obra/superpowers |
| 5 | `K-Dense-AI/scientific-agent-skills` | 21817 | 2376 | Python | 654 stars today | 一套随时可用的代理技能，用于研究、科学、工程、分析、财务和写作。 | https://github.com/K-Dense-AI/scientific-agent-skills |
| 6 | `shiyu-coder/Kronos` | 24846 | 4346 | Python | 363 stars today | Kronos ：金融市场语言的基础模型 | https://github.com/shiyu-coder/Kronos |
| 7 | `roboflow/supervision` | 38896 | 3479 | Python | 83 stars today | 我们为您编写可重复使用的计算机视觉工具。 💜 | https://github.com/roboflow/supervision |
| 8 | `influxdata/telegraf` | 17225 | 5795 | Go | 215 stars today | 用于收集、处理、汇总和编写指标、日志和其他任意数据的代理。 | https://github.com/influxdata/telegraf |
| 9 | `supertone-inc/supertonic` | 5365 | 527 | Swift | 1,128 stars today | 闪电般的快速、设备上、多语言TTS —通过ONNX本地运行。 | https://github.com/supertone-inc/supertonic |
| 10 | `Genymobile/scrcpy` | 141373 | 13051 | C | 851 stars today | 显示和控制您的Android设备 | https://github.com/Genymobile/scrcpy |
| 11 | `NVIDIA-AI-Blueprints/video-search-and-summarization` | 855 | 246 | Python | 62 stars today | 用于构建GPU加速视觉代理和人工智能视频分析应用程序的参考架构套件。 | https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization |
| 12 | `CloakHQ/CloakBrowser` | 10936 | 815 | Python | 1,354 stars today | Stealth Chromium可通过每次机器人检测测试。插入式剧作家更换源级指纹补丁，通过30/30测试 | https://github.com/CloakHQ/CloakBrowser |
| 13 | `mattpocock/skills` | 82419 | 7116 | Shell | 2,987 stars today | 真正工程师的技能。直接来自我的.claude目录。 | https://github.com/mattpocock/skills |
| 14 | `github/spec-kit` | 99524 | 8671 | Python | 1,232 stars today | 帮助您开始规格驱动开发💫的工具包 | https://github.com/github/spec-kit |
| 15 | `garrytan/gstack` | 96802 | 14396 | TypeScript | 915 stars today | 使用Garry Tan确切的Claude Code设置： 23个自以为是的工具，分别担任首席执行官、设计师、工程经理、发布经理、文档工程师和QA | https://github.com/garrytan/gstack |


### 本周 trending（since=weekly）

**页面**： `https://github.com/trending?since=weekly`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- |
| 1 | `anthropics/financial-services` | 22802 | 3116 | Python | 12,529 stars this week | — | https://github.com/anthropics/financial-services |
| 2 | `CloakHQ/CloakBrowser` | 10936 | 815 | Python | 8,404 stars this week | Stealth Chromium可通过每次机器人检测测试。插入式剧作家更换源级指纹补丁，通过30/30测试 | https://github.com/CloakHQ/CloakBrowser |
| 3 | `bytedance/UI-TARS-desktop` | 33935 | 3370 | TypeScript | 4,184 stars this week | 开源多模态人工智能代理堆栈：连接尖端人工智能模型和代理基础设施 | https://github.com/bytedance/UI-TARS-desktop |
| 4 | `Hmbown/DeepSeek-TUI` | 29042 | 2418 | Rust | 11,303 stars this week | 在您的终端中运行的DeepSeek模型的编码代理 | https://github.com/Hmbown/DeepSeek-TUI |
| 5 | `rohitg00/agentmemory` | 9013 | 746 | TypeScript | 6,467 stars this week | # 1基于真实世界基准的AI编码代理持久内存 | https://github.com/rohitg00/agentmemory |
| 6 | `yikart/AiToEarn` | 13792 | 2340 | TypeScript | 4,412 stars this week | 让我们使用人工智能来赚取收入！ | https://github.com/yikart/AiToEarn |
| 7 | `decolua/9router` | 10314 | 1578 | JavaScript | 6,024 stars this week | 无限免费AI编码。通过40多家供应商将Claude Code、Codex、Cursor、Cline、Copilot、Antigravity连接到免费的Claude/GPT/Gemini。自动回退， RTK -40%代币，从未达到限制。 | https://github.com/decolua/9router |
| 8 | `HKUDS/AI-Trader` | 17223 | 2659 | Python | 3,013 stars this week | “AI-Trader ： 100%全自动代理本地交易” | https://github.com/HKUDS/AI-Trader |
| 9 | `Imbad0202/academic-research-skills` | 7218 | 827 | Python | 2,246 stars this week | Claude Code的学术研究技能：研究→撰写→评审→修订→最终确定 | https://github.com/Imbad0202/academic-research-skills |
| 10 | `addyosmani/agent-skills` | 41606 | 4568 | Shell | 9,198 stars this week | AI编码代理的生产级工程技能。 | https://github.com/addyosmani/agent-skills |
| 11 | `playcanvas/supersplat` | 7967 | 863 | TypeScript | 2,866 stars this week | 3D高斯拼接编辑器 | https://github.com/playcanvas/supersplat |
| 12 | `mattpocock/skills` | 82423 | 7116 | Shell | 17,059 stars this week | 真正工程师的技能。直接来自我的.claude目录。 | https://github.com/mattpocock/skills |
| 13 | `ruvnet/ruflo` | 51064 | 5720 | TypeScript | 5,106 stars this week | 🌊 Claude的领先代理编排平台。部署智能多智能体群，协调自主工作流程，构建对话式人工智能系统。具有企业级架构、自学群体智能、RAG集成和本地Claude Code/… | https://github.com/ruvnet/ruflo |
| 14 | `apernet/hysteria` | 20776 | 2144 | Go | 874 stars this week | 歇斯底里是一种强大、快如闪电、抗审查的代理。 | https://github.com/apernet/hysteria |
| 15 | `datawhalechina/easy-vibe` | 10873 | 1013 | JavaScript | 3,096 stars this week | 💻 vibe coding 2026 ·您的第一个现代编程课程，供初学者一步一步掌握。 | https://github.com/datawhalechina/easy-vibe |
| 16 | `LearningCircuit/local-deep-research` | 7607 | 655 | Python | 1,553 stars this week | SimpleQA约95% （例如3090上的Qwen3.6-27B ）。支持所有本地和云LLM （ llama.cpp、Ollama、Google等）。10多个搜索引擎- arXiv、PubMed、您的私人文档。本地和加密的一切。 | https://github.com/LearningCircuit/local-deep-research |


### 本月 trending（since=monthly）

**页面**： `https://github.com/trending?since=monthly`

| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 |
| ---: | --- | ---:| ---:| --- | --- | --- | --- |
| 1 | `multica-ai/andrej-karpathy-skills` | 129709 | 13156 | — | 99,894 stars this month | 一个用于改进Claude Code行为的CLAUDE.md文件，源自Andrej Karpathy对LLM编码陷阱的观察。 | https://github.com/multica-ai/andrej-karpathy-skills |
| 2 | `mattpocock/skills` | 82424 | 7116 | Shell | 66,519 stars this month | 真正工程师的技能。直接来自我的.claude目录。 | https://github.com/mattpocock/skills |
| 3 | `Alishahryar1/free-claude-code` | 24611 | 3658 | Python | 22,809 stars this month | 在终端中免费使用claude-code、VSCode扩展或像OpenClaw这样的不和谐（支持语音） | https://github.com/Alishahryar1/free-claude-code |
| 4 | `AIDC-AI/Pixelle-Video` | 16720 | 2417 | Python | 12,733 stars this month | 🚀 AI 全自动短视频引擎 · AI Fully Automated Short Video Engine | https://github.com/AIDC-AI/Pixelle-Video |
| 5 | `lsdefine/GenericAgent` | 11397 | 1299 | Python | 10,252 stars this month | 自我进化剂：从3.3K行种子中生长技能树，实现全系统控制，代币消耗量减少6倍 | https://github.com/lsdefine/GenericAgent |
| 6 | `ComposioHQ/awesome-codex-skills` | 9600 | 896 | Python | 8,774 stars this month | 用于跨Codex CLI和API自动化工作流程的实用Codex技能精选列表。 | https://github.com/ComposioHQ/awesome-codex-skills |
| 7 | `NousResearch/hermes-agent` | 150426 | 23821 | Python | 68,208 stars this month | 与您一起成长的客服代表 | https://github.com/NousResearch/hermes-agent |
| 8 | `addyosmani/agent-skills` | 41606 | 4568 | Shell | 26,393 stars this month | AI编码代理的生产级工程技能。 | https://github.com/addyosmani/agent-skills |
| 9 | `Z4nzu/hackingtool` | 74498 | 8407 | Python | 16,576 stars this month | 面向黑客的一体化黑客工具 | https://github.com/Z4nzu/hackingtool |
| 10 | `anthropics/financial-services` | 22802 | 3116 | Python | 15,279 stars this month | — | https://github.com/anthropics/financial-services |
| 11 | `soxoj/maigret` | 28639 | 2052 | Python | 9,233 stars this month | 通过用户名从3000多个网站🕵️‍♂️收集个人档案 | https://github.com/soxoj/maigret |
| 12 | `Tracer-Cloud/opensre` | 5075 | 643 | Python | 4,410 stars this month | 构建您自己的AI SRE代理。人工智能时代的开源工具包。 | https://github.com/Tracer-Cloud/opensre |
| 13 | `TauricResearch/TradingAgents` | 75520 | 14699 | Python | 25,430 stars this month | TradingAgent ：多代理LLM金融交易框架 | https://github.com/TauricResearch/TradingAgents |
| 14 | `Anil-matcha/Open-Generative-AI` | 13627 | 2397 | JavaScript | 8,834 stars this month | 人工智能视频平台的开源替代品—免费的人工智能图像和视频生成工作室，拥有200多种型号（ Flux、Midjourney、Kling、Sora、Veo ）。无内容过滤器。自托管，麻省理工学院许可。 | https://github.com/Anil-matcha/Open-Generative-AI |
| 15 | `hugohe3/ppt-master` | 16450 | 1597 | Python | 11,276 stars this month | AI从任何文档生成本机可编辑的PPTX —具有本机动画的真实PowerPoint形状，而不是Hugo He的图像· | https://github.com/hugohe3/ppt-master |
| 16 | `zilliztech/claude-context` | 11067 | 825 | TypeScript | 5,157 stars this month | 代码搜索MCP以查找Claude Code。使整个代码库成为任何编码代理的上下文。 | https://github.com/zilliztech/claude-context |
| 17 | `CloakHQ/CloakBrowser` | 10936 | 815 | Python | 9,136 stars this month | Stealth Chromium可通过每次机器人检测测试。插入式剧作家更换源级指纹补丁，通过30/30测试 | https://github.com/CloakHQ/CloakBrowser |
| 18 | `decolua/9router` | 10314 | 1578 | JavaScript | 7,780 stars this month | 无限免费AI编码。通过40多家供应商将Claude Code、Codex、Cursor、Cline、Copilot、Antigravity连接到免费的Claude/GPT/Gemini。自动回退， RTK -40%代币，从未达到限制。 | https://github.com/decolua/9router |
| 19 | `multica-ai/multica` | 28448 | 3426 | TypeScript | 16,456 stars this month | 开源托管代理平台。将编码代理转变为真正的队友—分配任务、跟踪进度、复合技能。 | https://github.com/multica-ai/multica |

