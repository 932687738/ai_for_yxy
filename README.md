# ai_for_learning

本项目已新增一组“AI 课程导师”自定义 Agent（基于 Cursor Subagents），用于围绕单一课程大纲文件进行持续教学与项目实战辅导。

## 新增 Agent 列表（已拆分）

- 课程模式：`.cursor/agents/ai-course-mentor-course-mode.md`
  - 仅做课程评估、逐课教学、问答回写、进度维护。
- 项目模式：`.cursor/agents/ai-course-mentor-project-mode.md`
  - 聚焦 Java/Python 项目分析与改造，并将实战结论回写课程章节。

## 使用说明

建议在对话开始时提供以下参数：

- `{COURSE_PATH}`（必填）：课程大纲文件路径，例如 `study/COURSE_OUTLINE.md`
- `{JAVA_PROJECT_PATH}`（选填）：Java 项目根目录
- `{PYTHON_PROJECT_PATH}`（选填）：Python 项目根目录

若未提供 `{COURSE_PATH}`，Agent 会先询问后再开始教学。

## 使用 Python（PyCharm 解释器）

在本仓库中若要运行或编辑 Python 相关代码，请在 **PyCharm** 中为当前工程配置解释器：

1. 打开 **Settings / Preferences**（Windows/Linux：`File` → `Settings`；macOS：`PyCharm` → `Preferences`）。
2. 进入 **Project → Python Interpreter**（左侧项目区域下）。
3. 在 **Python Interpreter** 下拉框中选择本机已有的解释器；若尚无合适环境，可通过 **Add Interpreter** 新建虚拟环境（venv）或指定 Conda/Python 路径。

配置完成后，PyCharm 的代码补全、运行/调试与会话所使用的 Python 才与项目目录一致。

### `ai-learning` 脚本依赖安装

仓库内 `ai-learning/**/scripts/*.py` 累计使用到的第三方包如下，运行前请先安装：

| 包名 | 说明 |
| --- | --- |
| `numpy` | 数值与张量练习（向量/矩阵、广播、线性回归、余弦相似度等） |
| `pandas` | CSV 读写与统计（学生成绩、房价等示例） |
| `matplotlib` | 图表展示；`stats_houses.py` 在未安装时会跳过绘图，其余依赖绘图的脚本需安装 |

在项目已激活的虚拟环境中执行（推荐先 `cd` 到仓库根目录再执行）：

```bash
python -m pip install numpy pandas matplotlib
```

**续课（控制上下文长度）**：进度已落在 `study/COURSE_PROGRESS.md`，新开对话时让助手**先读该文件**再讲，无需复述整段聊天历史。

## 触发示例

> 已精简为“短指令 + 参数”，更容易触发。

### 课程模式（最短）

```text
调用 /ai-course-mentor-course-mode
COURSE_PATH=study/COURSE_OUTLINE.md
从第1课开始讲。
```

### 项目模式（最短）

```text
调用 /ai-course-mentor-project-mode
COURSE_PATH=study/COURSE_OUTLINE.md
JAVA_PROJECT_PATH=D:/workspace/order-ai-demo
先识别技术栈并回写项目实战。
```

## 约束与回写规则（简要）

- 所有讲解、问答、外部补充都写回 `{COURSE_PATH}`，不额外创建独立笔记。
- 不删除已有内容，只做追加或精确插入。
- 严格逐课推进，需学生明确确认“这节课已经学会”后再进入下一课。
