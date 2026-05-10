# 任务 001：AI Agent 架构设计：ReAct、Plan-and-Execute、Supervisor/Worker

## 0. 课程定位

本课面向已经具备 Java 后端开发经验的学习者，目标是把你从“会调用大模型 API”推进到“能设计 Agent 执行架构”。

学完本课，你应该能：

- 解释 Agent 与普通聊天机器人的本质区别。
- 设计最小 Agent loop。
- 用 Java 表达 `AgentContext`、`AgentResult`、`Plan`、`PlanStep` 等核心模型。
- 理解并实现 ReAct 模式。
- 理解并实现 Plan-and-Execute 模式。
- 理解 Supervisor / Worker 多 Agent 协作模式。
- 判断不同业务场景应该选哪种 Agent 架构。
- 运行一个最小 ReAct Agent 实验，调用天气和计算器两个模拟工具。

【核心】Agent 架构设计的本质，是把“不确定的大模型推理”放进“可约束、可追踪、可恢复的工程流程”中。

## 1. Agent 的核心定义

### 1.1 普通聊天机器人

普通聊天机器人通常是：

```text
用户输入
  -> 模型生成回答
  -> 返回用户
```

ASCII 图：

```text
+--------+      +---------+      +--------+
| User   | ---> |  LLM    | ---> | Answer |
+--------+      +---------+      +--------+
```

它的特点：

- 没有明确任务状态。
- 通常不调用外部工具。
- 不一定知道自己是否完成任务。
- 出错后很难恢复。
- 更像“问答系统”。

### 1.2 AI Agent

Agent 是能围绕目标进行多步执行的系统。

最小结构：

```text
用户目标
  -> Agent 理解目标
  -> 判断是否需要工具
  -> 调用工具
  -> 观察工具结果
  -> 更新状态
  -> 判断是否完成
  -> 继续或输出最终结果
```

ASCII 图：

```text
+--------+
| User   |
+---+----+
    |
    v
+---+-----------------------+
| Agent Loop                |
|                           |
|  observe context          |
|  reason next action       |
|  call tool if needed      |
|  observe result           |
|  update state             |
|  decide continue/finish   |
+---+-----------------------+
    |
    v
+---+----+
| Result |
+--------+
```

Agent 的核心能力：

- 任务理解。
- 步骤决策。
- 工具调用。
- 状态管理。
- 失败处理。
- 完成判断。
- 轨迹记录。

【核心】Agent 不是一次模型调用，而是一条可追踪的任务执行轨迹。

## 2. Agent Loop 最小执行循环

### 2.1 Agent loop 原理图

```text
             +----------------+
             |  User Goal     |
             +-------+--------+
                     |
                     v
             +-------+--------+
             | AgentContext   |
             +-------+--------+
                     |
                     v
        +------------+-------------+
        | Decide next step          |
        | - answer directly?        |
        | - call tool?              |
        | - ask clarification?      |
        | - stop?                   |
        +------+-------------------+
               |
       +-------+--------+
       |                |
       v                v
+------+-----+    +-----+------+
| Tool Call  |    | Final      |
| Execution  |    | Answer     |
+------+-----+    +------------+
       |
       v
+------+------+
| Observation|
+------+------+
       |
       v
  update context
       |
       v
   next loop
```

### 2.2 Agent loop 与普通聊天机器人的本质区别

| 维度 | 普通聊天机器人 | AI Agent |
|---|---|---|
| 目标 | 回答问题 | 完成任务 |
| 执行方式 | 单轮生成为主 | 多步循环 |
| 工具调用 | 可选，通常较少 | 核心能力 |
| 状态 | 对话历史 | 对话 + 任务 + 工具结果 + 计划 |
| 完成判断 | 模型自然结束 | 系统显式判断 |
| 错误恢复 | 弱 | 可通过状态和 checkpoint 恢复 |
| 审计 | 通常只看答案 | 需要完整 trace |

【重点】Agent 的难点不是“让模型更聪明”，而是让模型的每一步都处在工程约束中。

## 3. 核心类设计

下面代码使用纯 Java 风格，方便迁移到 Spring Boot。所有字段都保持明确，避免把所有内容塞进 `Map<String,Object>`。

### 3.1 Message

```java
// 定义一条对话消息。
// 在真实系统中，它可以对应 OpenAI、Spring AI 或 LangChain4j 的 Message。
public class Message {

    // 消息角色，例如 system、user、assistant、tool。
    private final String role;

    // 消息正文。
    private final String content;

    // 构造方法，用于创建不可变消息对象。
    public Message(String role, String content) {
        // 保存消息角色。
        this.role = role;
        // 保存消息内容。
        this.content = content;
    }

    // 返回消息角色。
    public String getRole() {
        return role;
    }

    // 返回消息内容。
    public String getContent() {
        return content;
    }
}
```

设计说明：

- `role` 必须保留，不能只存字符串列表。
- tool 结果也应该作为一种消息或 observation 进入上下文。
- 后续做 trace 时，每条消息都可以记录来源。

### 3.2 ToolDefinition

```java
// 描述一个 Agent 可以调用的工具。
// 注意：这是工具定义，不是工具执行器。
public class ToolDefinition {

    // 工具名称，例如 get_weather、calculator。
    private final String name;

    // 工具描述，模型会根据描述判断何时调用。
    private final String description;

    // 参数 schema。这里为了简化用字符串表示 JSON Schema。
    private final String parameterSchema;

    // 工具风险等级，例如 LOW、MEDIUM、HIGH。
    private final String riskLevel;

    // 创建工具定义。
    public ToolDefinition(String name, String description, String parameterSchema, String riskLevel) {
        // 保存工具名称。
        this.name = name;
        // 保存工具描述。
        this.description = description;
        // 保存参数 schema。
        this.parameterSchema = parameterSchema;
        // 保存风险等级。
        this.riskLevel = riskLevel;
    }

    // 返回工具名称。
    public String getName() {
        return name;
    }

    // 返回工具描述。
    public String getDescription() {
        return description;
    }

    // 返回参数 schema。
    public String getParameterSchema() {
        return parameterSchema;
    }

    // 返回风险等级。
    public String getRiskLevel() {
        return riskLevel;
    }
}
```

【工程经验】工具描述必须包含能力边界。例如“只能查询当前用户有权限访问的数据”，这能帮助模型选工具，但不能替代代码中的权限校验。

### 3.3 ToolCallRecord

```java
// 记录一次工具调用。
// 它用于 trace、审计、评估和失败排查。
public class ToolCallRecord {

    // 工具名称。
    private final String toolName;

    // 工具参数，简化为 JSON 字符串。
    private final String argumentsJson;

    // 工具返回结果，简化为字符串。
    private final String result;

    // 工具调用是否成功。
    private final boolean success;

    // 创建工具调用记录。
    public ToolCallRecord(String toolName, String argumentsJson, String result, boolean success) {
        // 保存工具名称。
        this.toolName = toolName;
        // 保存调用参数。
        this.argumentsJson = argumentsJson;
        // 保存工具结果。
        this.result = result;
        // 保存成功标记。
        this.success = success;
    }

    // 返回工具名称。
    public String getToolName() {
        return toolName;
    }

    // 返回工具参数。
    public String getArgumentsJson() {
        return argumentsJson;
    }

    // 返回工具结果。
    public String getResult() {
        return result;
    }

    // 返回调用是否成功。
    public boolean isSuccess() {
        return success;
    }
}
```

### 3.4 AgentContext

```java
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// AgentContext 是 Agent 运行时的上下文对象。
// 它承载用户输入、对话历史、工具、任务状态和 trace 信息。
public class AgentContext {

    // 当前用户输入。
    private final String userInput;

    // 对话消息列表。
    private final List<Message> messages = new ArrayList<>();

    // 可调用工具列表。
    private final List<ToolDefinition> tools = new ArrayList<>();

    // 工作状态。真实项目中可替换为强类型 TaskState。
    private final Map<String, Object> state = new HashMap<>();

    // 工具调用记录。
    private final List<ToolCallRecord> toolCalls = new ArrayList<>();

    // 当前 traceId，用于串联一次 Agent 运行。
    private final String traceId;

    // 最大执行步数，防止无限循环。
    private final int maxSteps;

    // 构造 AgentContext。
    public AgentContext(String userInput, String traceId, int maxSteps) {
        // 保存用户输入。
        this.userInput = userInput;
        // 保存 traceId。
        this.traceId = traceId;
        // 保存最大步数。
        this.maxSteps = maxSteps;
        // 将用户输入加入消息列表。
        this.messages.add(new Message("user", userInput));
    }

    // 返回用户输入。
    public String getUserInput() {
        return userInput;
    }

    // 返回消息列表。
    public List<Message> getMessages() {
        return messages;
    }

    // 返回工具列表。
    public List<ToolDefinition> getTools() {
        return tools;
    }

    // 返回工作状态。
    public Map<String, Object> getState() {
        return state;
    }

    // 返回工具调用记录。
    public List<ToolCallRecord> getToolCalls() {
        return toolCalls;
    }

    // 返回 traceId。
    public String getTraceId() {
        return traceId;
    }

    // 返回最大步数。
    public int getMaxSteps() {
        return maxSteps;
    }

    // 添加工具定义。
    public void addTool(ToolDefinition tool) {
        // 将工具加入上下文。
        this.tools.add(tool);
    }

    // 添加工具调用记录。
    public void addToolCall(ToolCallRecord record) {
        // 将工具调用加入 trace。
        this.toolCalls.add(record);
    }

    // 添加一条消息。
    public void addMessage(String role, String content) {
        // 构造消息并加入消息列表。
        this.messages.add(new Message(role, content));
    }
}
```

【核心】`AgentContext` 是 Agent 的运行容器。不要把 Agent 写成“接收 String 返回 String”的普通函数，否则无法做状态管理、工具审计和错误恢复。

### 3.5 AgentResult

```java
import java.util.List;
import java.util.Map;

// AgentResult 表示一次 Agent 运行的结果。
public class AgentResult {

    // 任务是否完成。
    private final boolean completed;

    // 最终回答。如果未完成，可以是当前状态说明。
    private final String finalAnswer;

    // 工具调用轨迹。
    private final List<ToolCallRecord> toolCalls;

    // 更新后的状态快照。
    private final Map<String, Object> updatedState;

    // 构造 AgentResult。
    public AgentResult(
            boolean completed,
            String finalAnswer,
            List<ToolCallRecord> toolCalls,
            Map<String, Object> updatedState
    ) {
        // 保存完成标记。
        this.completed = completed;
        // 保存最终回答。
        this.finalAnswer = finalAnswer;
        // 保存工具调用轨迹。
        this.toolCalls = toolCalls;
        // 保存状态快照。
        this.updatedState = updatedState;
    }

    // 返回是否完成。
    public boolean isCompleted() {
        return completed;
    }

    // 返回最终回答。
    public String getFinalAnswer() {
        return finalAnswer;
    }

    // 返回工具调用轨迹。
    public List<ToolCallRecord> getToolCalls() {
        return toolCalls;
    }

    // 返回状态快照。
    public Map<String, Object> getUpdatedState() {
        return updatedState;
    }
}
```

### 3.6 Plan 与 PlanStep

```java
import java.util.ArrayList;
import java.util.List;

// 计划对象，用于 Plan-and-Execute 架构。
public class Plan {

    // 计划步骤列表。
    private final List<PlanStep> steps = new ArrayList<>();

    // 添加一个步骤。
    public void addStep(PlanStep step) {
        // 将步骤加入计划。
        this.steps.add(step);
    }

    // 返回全部步骤。
    public List<PlanStep> getSteps() {
        return steps;
    }

    // 查找第一个未完成步骤。
    public PlanStep nextPendingStep() {
        // 遍历所有步骤。
        for (PlanStep step : steps) {
            // 如果步骤状态是 PENDING，返回该步骤。
            if (step.getStatus() == StepStatus.PENDING) {
                return step;
            }
        }
        // 如果没有未完成步骤，返回 null。
        return null;
    }

    // 判断计划是否全部完成。
    public boolean isCompleted() {
        // 如果找不到未完成步骤，说明计划已完成。
        return nextPendingStep() == null;
    }
}
```

```java
// 步骤状态枚举。
public enum StepStatus {
    // 等待执行。
    PENDING,
    // 正在执行。
    RUNNING,
    // 已完成。
    COMPLETED,
    // 执行失败。
    FAILED
}
```

```java
// 计划中的单个步骤。
public class PlanStep {

    // 步骤唯一标识。
    private final String id;

    // 步骤目标。
    private final String goal;

    // 预期输出。
    private final String expectedOutput;

    // 建议使用的工具名称。
    private final String requiredTool;

    // 当前步骤状态。
    private StepStatus status = StepStatus.PENDING;

    // 步骤执行结果。
    private String result;

    // 构造计划步骤。
    public PlanStep(String id, String goal, String expectedOutput, String requiredTool) {
        // 保存步骤 ID。
        this.id = id;
        // 保存步骤目标。
        this.goal = goal;
        // 保存预期输出。
        this.expectedOutput = expectedOutput;
        // 保存建议工具。
        this.requiredTool = requiredTool;
    }

    // 返回步骤 ID。
    public String getId() {
        return id;
    }

    // 返回步骤目标。
    public String getGoal() {
        return goal;
    }

    // 返回预期输出。
    public String getExpectedOutput() {
        return expectedOutput;
    }

    // 返回建议工具。
    public String getRequiredTool() {
        return requiredTool;
    }

    // 返回状态。
    public StepStatus getStatus() {
        return status;
    }

    // 修改状态。
    public void setStatus(StepStatus status) {
        // 保存新状态。
        this.status = status;
    }

    // 返回步骤结果。
    public String getResult() {
        return result;
    }

    // 设置步骤结果。
    public void setResult(String result) {
        // 保存执行结果。
        this.result = result;
    }
}
```

## 4. ReAct 模式

### 4.1 ReAct 原理

ReAct = Reasoning + Acting。

它把 Agent 执行过程拆成：

```text
Thought：分析当前该做什么
Action：调用工具
Observation：读取工具结果
Thought：继续判断
Final：输出最终结果
```

ASCII 图：

```text
+-------------+
| User Goal   |
+------+------+ 
       |
       v
+------+------+
| Thought     |
+------+------+
       |
       v
+------+------+
| Action      |
| call tool   |
+------+------+
       |
       v
+------+------+
| Observation |
+------+------+
       |
       v
  continue?
   /     \
 yes     no
 /        \
v          v
Thought   Final Answer
```

### 4.2 ReAct 适用场景

适合：

- 查询型任务。
- 工具数量较少。
- 步骤不太长。
- 每步都依赖上一工具结果。

不适合：

- 超长任务。
- 强审批流程。
- 必须严格按固定流程执行的业务。
- 高风险写操作。

### 4.3 ReAct 工程坑

常见问题：

- 无限循环。
- 重复调用同一个工具。
- 工具结果污染后续判断。
- 模型编造工具结果。
- 没有最大步数限制。
- 工具失败后不退出。

防护：

- 设置 `maxSteps`。
- 记录已调用工具。
- 工具结果必须来自系统，不允许模型自己补。
- 每步都写 trace。
- 高风险工具必须审批。

## 5. 最小可运行 ReAct Agent 实验

这个实验不依赖真实大模型。我们用一个规则型 `MockReasoner` 模拟模型决策，重点学习 Agent 架构和工具循环。

### 5.1 实验目标

支持两个工具：

- `get_weather`：查询天气。
- `calculator`：计算简单加法。

用户示例：

```text
北京天气怎么样？
```

```text
计算 3 + 5
```

### 5.2 ToolExecutor 接口

```java
// 工具执行器接口。
// 每个具体工具都实现这个接口。
public interface ToolExecutor {

    // 返回工具名称。
    String name();

    // 执行工具。
    // argumentsJson 是模型生成的参数 JSON。
    String execute(String argumentsJson);
}
```

### 5.3 WeatherTool

```java
// 模拟天气查询工具。
public class WeatherTool implements ToolExecutor {

    // 返回工具名称。
    @Override
    public String name() {
        // 工具名必须和 Agent 决策中的 action 名称一致。
        return "get_weather";
    }

    // 执行天气查询。
    @Override
    public String execute(String argumentsJson) {
        // 为了保持实验简单，这里不解析 JSON。
        // 真实项目必须使用 Jackson 解析参数并校验字段。
        if (argumentsJson.contains("北京")) {
            // 返回模拟天气。
            return "北京今天晴，气温 18 到 26 摄氏度。";
        }
        // 返回默认天气。
        return "该城市天气未知。";
    }
}
```

### 5.4 CalculatorTool

```java
// 模拟计算器工具。
public class CalculatorTool implements ToolExecutor {

    // 返回工具名称。
    @Override
    public String name() {
        // 工具名称。
        return "calculator";
    }

    // 执行计算。
    @Override
    public String execute(String argumentsJson) {
        // 这是实验代码，仅处理固定示例。
        // 真实项目中不能用 contains 解析数学表达式。
        if (argumentsJson.contains("3") && argumentsJson.contains("5")) {
            // 返回计算结果。
            return "3 + 5 = 8";
        }
        // 返回不支持说明。
        return "只支持示例表达式 3 + 5。";
    }
}
```

### 5.5 ToolRegistry

```java
import java.util.HashMap;
import java.util.Map;

// 工具注册表。
// Agent 通过它找到工具执行器。
public class ToolRegistry {

    // 用 Map 保存工具名到执行器的映射。
    private final Map<String, ToolExecutor> executors = new HashMap<>();

    // 注册工具。
    public void register(ToolExecutor executor) {
        // 将工具执行器按名称放入 Map。
        executors.put(executor.name(), executor);
    }

    // 调用工具。
    public String call(String toolName, String argumentsJson) {
        // 根据工具名查找执行器。
        ToolExecutor executor = executors.get(toolName);
        // 如果工具不存在，返回错误。
        if (executor == null) {
            return "工具不存在：" + toolName;
        }
        // 调用工具并返回结果。
        return executor.execute(argumentsJson);
    }
}
```

### 5.6 AgentAction

```java
// Agent 下一步动作。
public class AgentAction {

    // 是否为最终回答。
    private final boolean finalAnswer;

    // 最终回答内容。
    private final String answer;

    // 要调用的工具名。
    private final String toolName;

    // 工具参数 JSON。
    private final String argumentsJson;

    // 私有构造方法。
    private AgentAction(boolean finalAnswer, String answer, String toolName, String argumentsJson) {
        // 保存是否最终回答。
        this.finalAnswer = finalAnswer;
        // 保存回答。
        this.answer = answer;
        // 保存工具名。
        this.toolName = toolName;
        // 保存工具参数。
        this.argumentsJson = argumentsJson;
    }

    // 创建最终回答动作。
    public static AgentAction finalAnswer(String answer) {
        // 返回最终回答对象。
        return new AgentAction(true, answer, null, null);
    }

    // 创建工具调用动作。
    public static AgentAction toolCall(String toolName, String argumentsJson) {
        // 返回工具调用对象。
        return new AgentAction(false, null, toolName, argumentsJson);
    }

    // 判断是否最终回答。
    public boolean isFinalAnswer() {
        return finalAnswer;
    }

    // 返回回答内容。
    public String getAnswer() {
        return answer;
    }

    // 返回工具名。
    public String getToolName() {
        return toolName;
    }

    // 返回工具参数。
    public String getArgumentsJson() {
        return argumentsJson;
    }
}
```

### 5.7 MockReasoner

```java
// 模拟大模型推理器。
// 真实项目中，这里会调用 ChatClient 或 LLM API。
public class MockReasoner {

    // 根据上下文决定下一步动作。
    public AgentAction decide(AgentContext context) {
        // 读取用户输入。
        String input = context.getUserInput();

        // 如果已经有工具调用结果，直接生成最终回答。
        if (!context.getToolCalls().isEmpty()) {
            // 取最后一次工具调用。
            ToolCallRecord last = context.getToolCalls().get(context.getToolCalls().size() - 1);
            // 把工具结果包装成最终回答。
            return AgentAction.finalAnswer("根据工具结果：" + last.getResult());
        }

        // 如果用户问天气，调用天气工具。
        if (input.contains("天气")) {
            // 构造工具调用参数。
            return AgentAction.toolCall("get_weather", "{\"city\":\"北京\"}");
        }

        // 如果用户要求计算，调用计算器。
        if (input.contains("计算") || input.contains("+")) {
            // 构造计算器参数。
            return AgentAction.toolCall("calculator", "{\"expression\":\"3+5\"}");
        }

        // 如果不需要工具，直接回答。
        return AgentAction.finalAnswer("这个问题不需要工具，我可以直接回答。");
    }
}
```

### 5.8 ReActAgent

```java
// ReAct Agent 实现。
public class ReActAgent {

    // 推理器。真实项目中可替换为 LLM Client。
    private final MockReasoner reasoner;

    // 工具注册表。
    private final ToolRegistry toolRegistry;

    // 构造 ReActAgent。
    public ReActAgent(MockReasoner reasoner, ToolRegistry toolRegistry) {
        // 保存推理器。
        this.reasoner = reasoner;
        // 保存工具注册表。
        this.toolRegistry = toolRegistry;
    }

    // 运行 Agent。
    public AgentResult run(AgentContext context) {
        // 从 0 开始计步。
        int step = 0;

        // 只要没超过最大步数，就继续循环。
        while (step < context.getMaxSteps()) {
            // 步数加一。
            step++;

            // 让推理器决定下一步动作。
            AgentAction action = reasoner.decide(context);

            // 如果动作是最终回答，结束循环。
            if (action.isFinalAnswer()) {
                // 将 assistant 消息写入上下文。
                context.addMessage("assistant", action.getAnswer());
                // 返回完成结果。
                return new AgentResult(true, action.getAnswer(), context.getToolCalls(), context.getState());
            }

            // 如果动作不是最终回答，就调用工具。
            String result = toolRegistry.call(action.getToolName(), action.getArgumentsJson());

            // 记录工具调用。
            ToolCallRecord record = new ToolCallRecord(
                    action.getToolName(),
                    action.getArgumentsJson(),
                    result,
                    true
            );

            // 将工具调用记录加入上下文。
            context.addToolCall(record);

            // 将工具结果作为 tool 消息加入上下文。
            context.addMessage("tool", result);
        }

        // 如果超过最大步数还没完成，返回失败结果。
        return new AgentResult(
                false,
                "Agent 超过最大步数，已停止，避免无限循环。",
                context.getToolCalls(),
                context.getState()
        );
    }
}
```

### 5.9 Main 方法运行实验

```java
import java.util.UUID;

// 实验入口。
public class ReActAgentDemo {

    // 主方法。
    public static void main(String[] args) {
        // 创建工具注册表。
        ToolRegistry registry = new ToolRegistry();

        // 注册天气工具。
        registry.register(new WeatherTool());

        // 注册计算器工具。
        registry.register(new CalculatorTool());

        // 创建模拟推理器。
        MockReasoner reasoner = new MockReasoner();

        // 创建 ReAct Agent。
        ReActAgent agent = new ReActAgent(reasoner, registry);

        // 创建上下文。最大步数设置为 5，防止无限循环。
        AgentContext context = new AgentContext(
                "北京天气怎么样？",
                UUID.randomUUID().toString(),
                5
        );

        // 运行 Agent。
        AgentResult result = agent.run(context);

        // 打印是否完成。
        System.out.println("completed = " + result.isCompleted());

        // 打印最终回答。
        System.out.println("answer = " + result.getFinalAnswer());

        // 打印工具调用次数。
        System.out.println("tool calls = " + result.getToolCalls().size());
    }
}
```

预期输出：

```text
completed = true
answer = 根据工具结果：北京今天晴，气温 18 到 26 摄氏度。
tool calls = 1
```

实验扩展：

- 把输入改成 `计算 3 + 5`。
- 把最大步数改成 1，观察是否还能完成。
- 故意让工具名写错，观察错误处理。

## 6. Plan-and-Execute 模式

### 6.1 原理

Plan-and-Execute 分成两个阶段：

```text
Planner：先生成计划
Executor：逐步执行计划
```

ASCII 图：

```text
+-------------+
| User Goal   |
+------+------+
       |
       v
+------+------+
| Planner     |
| create plan |
+------+------+
       |
       v
+------+------+
| Plan         |
| step 1       |
| step 2       |
| step 3       |
+------+------+
       |
       v
+------+------+
| Executor    |
| run steps   |
+------+------+
       |
       v
+------+------+
| Final Result|
+-------------+
```

### 6.2 适用场景

适合：

- 多步骤任务。
- 任务顺序明确。
- 每一步产物可检查。
- 需要恢复或审批。

示例：

```text
帮我分析一个线上报错：
1. 查询错误日志。
2. 查找相关代码。
3. 分析最近变更。
4. 输出修复建议。
```

### 6.3 Planner 示例

```java
// 简单规划器。
public class SimplePlanner {

    // 根据用户目标生成计划。
    public Plan createPlan(String userGoal) {
        // 创建空计划。
        Plan plan = new Plan();

        // 如果目标包含报错，生成排障计划。
        if (userGoal.contains("报错")) {
            // 添加查询日志步骤。
            plan.addStep(new PlanStep("step-1", "查询错误日志", "错误日志摘要", "search_logs"));
            // 添加查询代码步骤。
            plan.addStep(new PlanStep("step-2", "查找相关代码", "相关代码位置", "search_code"));
            // 添加分析步骤。
            plan.addStep(new PlanStep("step-3", "生成修复建议", "修复建议", "none"));
            // 返回计划。
            return plan;
        }

        // 默认生成单步计划。
        plan.addStep(new PlanStep("step-1", "直接回答用户问题", "最终回答", "none"));
        // 返回默认计划。
        return plan;
    }
}
```

### 6.4 Executor 示例

```java
// 计划执行器。
public class PlanExecutor {

    // 工具注册表。
    private final ToolRegistry toolRegistry;

    // 构造执行器。
    public PlanExecutor(ToolRegistry toolRegistry) {
        // 保存工具注册表。
        this.toolRegistry = toolRegistry;
    }

    // 执行计划。
    public String execute(Plan plan) {
        // 只要计划还没完成，就持续执行。
        while (!plan.isCompleted()) {
            // 找到下一个待执行步骤。
            PlanStep step = plan.nextPendingStep();

            // 将步骤标记为运行中。
            step.setStatus(StepStatus.RUNNING);

            // 如果步骤需要工具。
            if (!"none".equals(step.getRequiredTool())) {
                // 调用对应工具。这里用步骤目标作为简化参数。
                String result = toolRegistry.call(step.getRequiredTool(), "{\"query\":\"" + step.getGoal() + "\"}");
                // 保存步骤结果。
                step.setResult(result);
                // 标记完成。
                step.setStatus(StepStatus.COMPLETED);
            } else {
                // 不需要工具的步骤，直接生成模拟结果。
                step.setResult("已完成：" + step.getGoal());
                // 标记完成。
                step.setStatus(StepStatus.COMPLETED);
            }
        }

        // 返回汇总结果。
        return "计划执行完成，共 " + plan.getSteps().size() + " 个步骤。";
    }
}
```

### 6.5 Plan-and-Execute 工程坑

常见问题：

- 计划太粗，执行器无法执行。
- 计划太细，成本太高。
- 计划生成后不允许调整，遇到失败无法恢复。
- 计划状态没有持久化，服务重启后丢失。
- 每步没有验收标准，导致“看似完成”。

【工程经验】PlanStep 必须包含 `expectedOutput`。否则无法判断这一步是否真的完成。

## 7. Supervisor / Worker 多 Agent 协作

### 7.1 原理

Supervisor / Worker 模式中：

- Supervisor 负责理解任务、拆分任务、分配任务、汇总结果。
- Worker 负责执行某类具体任务。

ASCII 图：

```text
                 +----------------+
                 | User Goal      |
                 +--------+-------+
                          |
                          v
                 +--------+-------+
                 | Supervisor     |
                 | plan & assign  |
                 +---+--------+---+
                     |        |
       +-------------+        +--------------+
       v                                      v
+------+-------+                       +------+-------+
| Research     |                       | Code         |
| Worker       |                       | Worker       |
+------+-------+                       +------+-------+
       |                                      |
       +----------------+---------------------+
                        |
                        v
                 +------+-------+
                 | Final Merge  |
                 +--------------+
```

### 7.2 Worker 接口

```java
// Worker Agent 接口。
public interface WorkerAgent {

    // 返回 Worker 名称。
    String name();

    // 判断该 Worker 是否能处理任务。
    boolean canHandle(String task);

    // 执行任务。
    String handle(String task);
}
```

### 7.3 ResearchWorker

```java
// 研究型 Worker。
public class ResearchWorker implements WorkerAgent {

    // 返回名称。
    @Override
    public String name() {
        return "research-worker";
    }

    // 判断是否能处理研究任务。
    @Override
    public boolean canHandle(String task) {
        return task.contains("资料") || task.contains("文档") || task.contains("调研");
    }

    // 执行研究任务。
    @Override
    public String handle(String task) {
        return "研究结果：已整理相关资料。任务：" + task;
    }
}
```

### 7.4 CodeWorker

```java
// 代码型 Worker。
public class CodeWorker implements WorkerAgent {

    // 返回名称。
    @Override
    public String name() {
        return "code-worker";
    }

    // 判断是否能处理代码任务。
    @Override
    public boolean canHandle(String task) {
        return task.contains("代码") || task.contains("接口") || task.contains("测试");
    }

    // 执行代码任务。
    @Override
    public String handle(String task) {
        return "代码分析结果：已定位相关代码。任务：" + task;
    }
}
```

### 7.5 SupervisorAgent

```java
import java.util.ArrayList;
import java.util.List;

// Supervisor Agent。
public class SupervisorAgent {

    // Worker 列表。
    private final List<WorkerAgent> workers = new ArrayList<>();

    // 注册 Worker。
    public void registerWorker(WorkerAgent worker) {
        workers.add(worker);
    }

    // 处理用户任务。
    public String handle(String userGoal) {
        // 将用户目标拆成简单子任务。
        List<String> tasks = splitTasks(userGoal);

        // 保存所有 Worker 结果。
        List<String> results = new ArrayList<>();

        // 遍历子任务。
        for (String task : tasks) {
            // 找到能处理该任务的 Worker。
            WorkerAgent worker = selectWorker(task);

            // 如果没有 Worker 能处理，记录失败。
            if (worker == null) {
                results.add("没有合适的 Worker 处理任务：" + task);
                continue;
            }

            // 调用 Worker。
            String result = worker.handle(task);

            // 记录结果。
            results.add(worker.name() + " -> " + result);
        }

        // 汇总结果。
        return String.join("\n", results);
    }

    // 简化任务拆分。
    private List<String> splitTasks(String userGoal) {
        // 创建任务列表。
        List<String> tasks = new ArrayList<>();
        // 如果包含文档，添加调研任务。
        if (userGoal.contains("文档")) {
            tasks.add("调研相关文档资料");
        }
        // 如果包含代码，添加代码任务。
        if (userGoal.contains("代码")) {
            tasks.add("分析相关代码接口");
        }
        // 如果没有识别出任务，直接作为单任务。
        if (tasks.isEmpty()) {
            tasks.add(userGoal);
        }
        // 返回任务列表。
        return tasks;
    }

    // 选择 Worker。
    private WorkerAgent selectWorker(String task) {
        // 遍历所有 Worker。
        for (WorkerAgent worker : workers) {
            // 如果 Worker 能处理任务，返回它。
            if (worker.canHandle(task)) {
                return worker;
            }
        }
        // 没有合适 Worker。
        return null;
    }
}
```

### 7.6 多 Agent 工程坑

常见问题：

- Worker 职责重叠，互相抢任务。
- Supervisor 任务拆分不清楚。
- Worker 输出格式不统一。
- 多 Agent 成本过高。
- 状态同步复杂。
- 失败责任不清晰。

【重点】多 Agent 不是越多越好。先把单 Agent 做稳定，再引入 Supervisor / Worker。

## 8. 架构选型对照表

| 场景 | 推荐架构 | 原因 |
|---|---|---|
| 简单闲聊 | 普通 Chat | 不需要工具和状态 |
| 简单问答 | 单次 LLM 调用 | 成本低，延迟低 |
| 查资料回答 | RAG Agent | 需要外部知识 |
| 调 1-3 个工具 | ReAct | 工具调用路径短 |
| 多步骤业务流程 | Plan-and-Execute | 步骤可追踪、可恢复 |
| 高风险写操作 | 状态机 + HITL Agent | 必须审批和审计 |
| 多角色复杂任务 | Supervisor / Worker | 角色分工清晰 |
| 代码库分析 | Plan-and-Execute + Tools | 需要搜索、读取、测试 |
| 企业流程自动化 | 状态机 + Agent 辅助 | 业务规则必须确定 |

## 9. 架构选型决策树

```text
任务是否需要调用外部工具？
  否：
    是否只是简单问答？
      是 -> 单次 LLM 调用
      否 -> 普通 Chat + 上下文管理
  是：
    是否只有 1-3 个简单工具调用？
      是 -> ReAct
      否：
        是否步骤明确、需要恢复？
          是 -> Plan-and-Execute
          否：
            是否需要多个专业角色并行？
              是 -> Supervisor / Worker
              否 -> ReAct + 步数限制

任务是否包含高风险写操作？
  是 -> 必须加入 Human-in-the-loop 或确定性状态机
  否 -> 可自动执行，但仍需 trace
```

## 10. 常见坑与工程建议

### 10.1 无限循环

问题：

```text
Agent 不断调用同一个工具，无法停止。
```

解决：

- 设置 `maxSteps`。
- 记录重复工具调用。
- 连续失败时退出。
- 明确完成条件。

### 10.2 状态污染

问题：

```text
旧任务的工具结果影响新任务判断。
```

解决：

- 每个任务有独立 `taskId`。
- 区分 session state 和 task state。
- 工具结果带作用域。
- 完成任务后清理工作记忆。

### 10.3 工具结果不可信

问题：

```text
模型把用户输入或检索文档当成系统指令。
```

解决：

- 明确标记 tool observation。
- 检索内容标记为 untrusted context。
- 工具调用必须经过应用层校验。

### 10.4 计划不可执行

问题：

```text
Planner 生成“分析问题”这种空泛步骤。
```

解决：

- PlanStep 必须包含 expectedOutput。
- 每步最好绑定工具或验收条件。
- Executor 可以拒绝不可执行步骤。

### 10.5 多 Agent 过度设计

问题：

```text
简单任务也拆成多个 Agent，成本和延迟暴涨。
```

解决：

- 先评估单 Agent 是否足够。
- 多 Agent 必须有明确收益：并行、专业化、隔离权限。

## 11. 小练习

### 练习 1：扩展 ReAct 工具

在实验中新增一个工具：

```text
get_current_time
```

要求：

- 实现 `ToolExecutor`。
- 注册到 `ToolRegistry`。
- 修改 `MockReasoner`，当用户输入包含“现在几点”时调用该工具。

### 练习 2：增加重复调用保护

要求：

- 如果连续两次调用同一个工具且参数相同，停止 Agent。
- 返回错误说明：可能发生循环。

### 练习 3：把 Plan 持久化成 JSON

要求：

- 给 `Plan` 和 `PlanStep` 增加可序列化结构。
- 将计划保存为 JSON 字符串。
- 模拟服务重启后恢复计划。

### 练习 4：设计你自己的选型表

选择你所在业务中的 5 个场景，填写：

| 场景 | 是否需要工具 | 是否高风险 | 推荐架构 | 原因 |
|---|---|---|---|---|

## 12. 本课总结

本课你应该掌握：

- Agent 是多步任务执行系统，不是普通聊天机器人。
- Agent loop 必须包含观察、决策、工具调用、状态更新和停止条件。
- ReAct 适合短链路工具调用。
- Plan-and-Execute 适合多步骤、可恢复任务。
- Supervisor / Worker 适合多角色复杂任务，但成本和状态复杂度更高。
- 所有 Agent 架构都必须防止无限循环、状态污染、工具滥用和不可追踪。

最终判断标准：

```text
如果你的 Agent 每一步都能被解释、被追踪、被限制、被恢复，它才是工程系统。
如果它只是“让模型自己想办法”，那还不是可靠的 Agent 架构。
```

