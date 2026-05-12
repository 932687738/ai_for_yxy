# ai_for_yxy

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
