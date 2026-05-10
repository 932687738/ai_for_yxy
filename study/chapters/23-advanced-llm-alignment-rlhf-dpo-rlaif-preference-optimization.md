# 第 23 课：大模型对齐：RLHF、DPO、RLAIF 与偏好优化理论

## 0. 任务标识

任务名称：大模型对齐：RLHF、DPO、RLAIF 与偏好优化理论

预计学习时长：2 周

前置基础要求：

- 理解监督微调、交叉熵、KL 散度、策略梯度和基本强化学习。
- 已完成第 17 课，理解概率模型、KL 和后验近似。
- 已完成第 18 课，理解优化稳定性、PPO/SAM 类约束优化思想。
- 能阅读偏好数据格式：prompt、chosen response、rejected response。

本课目标：

```text
从“让模型更听话”上升到“把人类偏好、AI 反馈、奖励建模和 KL 约束策略优化放进统一数学框架”。
```

你需要建立以下研究直觉：

- 对齐不是单一算法，而是数据、奖励、优化和评估共同构成的训练阶段。
- RLHF 用奖励模型近似人类偏好，再用 KL 约束优化策略。
- DPO 把奖励模型隐式消去，将偏好学习转化为直接监督式目标。
- RLAIF 用 AI 反馈扩展偏好标注，但会引入模型偏见自循环风险。
- 2025 年推理模型中的 GRPO/RLVR 把对齐问题扩展到可验证奖励和长链推理优化。

## 1. 本课阅读方式

建议学习顺序：

```text
SFT
  -> 偏好数据
  -> 奖励模型 Bradley-Terry
  -> KL 约束 RLHF
  -> PPO
  -> DPO 推导
  -> IPO/KTO/ORPO/SimPO
  -> RLAIF / Constitutional AI
  -> GRPO / RLVR
```

【核心】对齐目标不是让模型最大化某个绝对正确的 reward，而是在有限、噪声、偏差明显的反馈信号下，让策略朝更符合人类或任务偏好的方向移动，同时避免 reward hacking 和能力坍缩。

## 2. 偏好数据与奖励建模

### 2.1 偏好样本

偏好数据通常写成：

$$
(x,y_w,y_l)
$$

公式注释：

- $x$ 是 prompt。
- $y_w$ 是 preferred 或 chosen response。
- $y_l$ 是 rejected response。
- 偏好只说明 $y_w$ 相对 $y_l$ 更好，不给绝对分数。

理论注释：

偏好数据比人工写标准答案更便宜，尤其适合开放式回答。但偏好具有主观性、上下文依赖和标注者偏差，不能视作真实价值函数。

### 2.2 Bradley-Terry 奖励模型

设奖励模型为 $r_\phi(x,y)$，偏好概率为：

$$
P(y_w\succ y_l\mid x)
=
\sigma
\left(
r_\phi(x,y_w)-r_\phi(x,y_l)
\right)
$$

训练损失：

$$
\mathcal{L}_{\text{RM}}
=
-
\mathbb{E}
\log
\sigma
\left(
r_\phi(x,y_w)-r_\phi(x,y_l)
\right)
$$

公式注释：

- $r_\phi$ 是奖励模型，输入 prompt 和 response，输出标量。
- $\sigma$ 是 sigmoid 函数。
- 如果 chosen 的奖励比 rejected 高很多，loss 较小。
- 该模型只学习奖励差异，不学习绝对奖励标尺。

理论注释：

奖励模型是 RLHF 的关键瓶颈。它可能被策略模型利用，产生 reward hacking：奖励高但人类实际不喜欢的输出。因此 RLHF 通常加入 KL 约束，让新策略不要偏离 SFT 模型太远。

## 3. KL 约束 RLHF

### 3.1 策略优化目标

RLHF 常用目标：

$$
\max_{\pi_\theta}
\mathbb{E}_{x\sim D,y\sim\pi_\theta(\cdot\mid x)}
\left[
r_\phi(x,y)
-
\beta
\mathrm{KL}
\left(
\pi_\theta(\cdot\mid x)
\|
\pi_{\text{ref}}(\cdot\mid x)
\right)
\right]
$$

公式注释：

- $\pi_\theta$ 是当前待优化语言模型。
- $\pi_{\text{ref}}$ 是参考模型，通常是 SFT 模型。
- $r_\phi$ 是奖励模型。
- $\beta$ 控制 KL 惩罚强度。
- KL 项限制策略不要远离参考模型。

理论注释：

这个目标体现了对齐中的核心张力：提高 reward 与保持语言质量/安全边界。$\beta$ 过小容易 reward hacking，$\beta$ 过大则模型几乎不学习偏好。

### 3.2 token 级 KL

语言模型序列概率分解为：

$$
\pi_\theta(y\mid x)
=
\prod_{t=1}^{T}
\pi_\theta(y_t\mid x,y_{<t})
$$

log 概率为：

$$
\log \pi_\theta(y\mid x)
=
\sum_{t=1}^{T}
\log \pi_\theta(y_t\mid x,y_{<t})
$$

公式注释：

- 每个 token 的 log probability 累加成整段回答的 log probability。
- KL 惩罚通常也可按 token 近似计算。
- 长回答天然有更多 log 概率项，因此长度归一化和 reward 设计很重要。

理论注释：

对齐训练中常见的长度偏置、啰嗦回答和 reward overoptimization，都与序列级 reward 和 token 级概率分解有关。

## 4. PPO 在 RLHF 中的作用

### 4.1 PPO clipped objective

PPO 使用概率比：

$$
\rho_t(\theta)
=
\frac{\pi_\theta(a_t\mid s_t)}
{\pi_{\theta_{\text{old}}}(a_t\mid s_t)}
$$

目标：

$$
\mathcal{L}_{\text{PPO}}
=
\mathbb{E}
\left[
\min
\left(
\rho_t A_t,
\operatorname{clip}(\rho_t,1-\epsilon,1+\epsilon)A_t
\right)
\right]
$$

公式注释：

- $a_t$ 是生成的 token。
- $s_t$ 是当前上下文状态。
- $A_t$ 是 advantage，表示该 token 相对基线有多好。
- $\rho_t$ 衡量新旧策略概率变化。
- clip 防止单步更新过大。

理论注释：

PPO 的价值在于稳定策略更新。但在 LLM 上，PPO 训练复杂、显存高、需要 reward model 和 value model，且对超参数敏感。这推动了 DPO 等直接偏好优化方法。

## 5. DPO：直接偏好优化

### 5.1 隐式奖励

KL 约束最优策略满足：

$$
r(x,y)
=
\beta
\log
\frac{\pi^\star(y\mid x)}
{\pi_{\text{ref}}(y\mid x)}
+
\beta\log Z(x)
$$

公式注释：

- $\pi^\star$ 是理想最优策略。
- $\pi_{\text{ref}}$ 是参考策略。
- $Z(x)$ 是归一化常数，只依赖 prompt。
- 奖励可以由策略相对参考模型的 log probability ratio 表示。

理论注释：

DPO 的关键洞察是：如果奖励可以由最优策略隐式表示，就不必显式训练奖励模型再跑 PPO。可以直接用偏好对训练策略。

### 5.2 DPO 损失

DPO 目标：

$$
\mathcal{L}_{\text{DPO}}
=
-
\mathbb{E}
\log
\sigma
\left(
\beta
\left[
\log
\frac{\pi_\theta(y_w\mid x)}
{\pi_{\text{ref}}(y_w\mid x)}
-
\log
\frac{\pi_\theta(y_l\mid x)}
{\pi_{\text{ref}}(y_l\mid x)}
\right]
\right)
$$

公式注释：

- chosen response 的相对 log 概率应高于 rejected response。
- 参考模型用于校正原本就容易生成的回答。
- $\beta$ 控制偏好优化强度。
- 不需要单独 reward model，也不需要 rollout/value model。

理论注释：

DPO 简化了 RLHF pipeline，但不是免费午餐。它依赖离线偏好数据，容易受数据分布限制；如果偏好数据噪声大或 chosen/rejected 差异弱，DPO 可能过拟合。

## 6. IPO、KTO、ORPO 与 SimPO

### 6.1 IPO

IPO 修改 DPO 的过强分类倾向，目标更像回归偏好 margin：

$$
\left(
h_\theta(x,y_w,y_l)
-
\frac{1}{2\beta}
\right)^2
$$

公式注释：

- $h_\theta$ 表示 chosen 和 rejected 的 log-ratio 差。
- 目标不是无限拉大偏好差距，而是接近合适 margin。

理论注释：

IPO 试图缓解 DPO 在可分偏好数据上的过拟合和 reward overoptimization。

### 6.2 KTO

KTO 使用人类效用中的损失厌恶思想，不要求严格成对偏好，而可使用 desirable/undesirable 样本。

理论注释：

KTO 适合偏好数据不是成对比较，而是单条反馈的场景。它把偏好优化从 pairwise 扩展到更灵活的数据格式。

### 6.3 ORPO / SimPO

ORPO 将 SFT 和偏好优化合并，SimPO 去掉 reference model 并使用长度归一化 reward。

理论注释：

这些方法共同趋势是降低 RLHF pipeline 复杂度：更少模型、更少阶段、更低显存、更容易复现。但简单方法是否能替代 PPO/RLVR，取决于任务是否需要在线探索和可验证奖励。

## 7. RLAIF 与 Constitutional AI

RLAIF 使用 AI 反馈替代或补充人类反馈：

```text
模型生成多个回答
  -> 强模型或规则系统评价偏好
  -> 训练 reward model 或直接偏好优化
```

理论注释：

RLAIF 可以放大标注规模，但风险是评审模型的偏见、盲点和风格偏好会传递给被训练模型。Constitutional AI 通过显式原则约束 AI 反馈，降低纯黑箱偏好带来的不可控性。

## 8. GRPO、RLVR 与推理模型

### 8.1 GRPO

GRPO 对同一 prompt 采样一组回答，并用组内相对奖励构造 advantage：

$$
A_i
=
\frac{r_i-\mathrm{mean}(r)}
{\mathrm{std}(r)+\epsilon}
$$

公式注释：

- $r_i$ 是第 $i$ 个回答的奖励。
- 组内均值和标准差用于归一化。
- 不需要单独训练 value model。
- 适合数学、代码等可验证任务。

理论注释：

GRPO/RLVR 在 2025 年推理模型训练中受到关注，因为它降低了 PPO 的 critic 成本，并能利用规则奖励、单元测试、数学答案验证器等可扩展反馈。

### 8.2 Verifiable Reward

可验证奖励：

$$
r(x,y)
=
\mathbf{1}[\mathrm{verify}(x,y)=\text{correct}]
$$

公式注释：

- verifier 可以是数学答案检查器、代码测试、格式校验或规则系统。
- 奖励稀疏但客观。
- 适合训练推理、代码和工具调用能力。

理论注释：

RLVR 的优势是减少主观标注，劣势是覆盖面有限。它可能鼓励模型优化可验证任务，而不是全面对齐人类偏好。

## 9. 前沿研究进展：2024-2026 视角

### 9.1 DPO 方法族快速扩展

2024-2025 年 DPO survey、ORPO、SimPO、KTO、CPO 等方法把偏好优化从 RL pipeline 转向 supervised-like pipeline。

研究意义：

- 对齐训练门槛降低。
- 研究重点转向偏好数据质量、reference model、长度偏置和过优化。

### 9.2 DeepSeek-R1 与 GRPO/RLVR

2025 年推理模型展示了基于可验证奖励的大规模 RL 能显著提升数学和代码推理能力，GRPO 成为关键技术之一。

研究意义：

- 对齐和能力训练边界变模糊。
- RL 不只是“安全对齐”，也成为推理能力放大的训练阶段。

### 9.3 统一奖励-策略优化

2025 年 URPO、EM Policy Gradient、Group Preference Reward Shaping 等工作试图统一偏好、可验证奖励和开放式指令数据。

研究意义：

- 未来 pipeline 可能不再清晰区分 SFT、RM、PPO、DPO。
- 不同反馈信号会被放进统一生成式或组相对优化框架。

## 10. 代码实验一：DPO 损失

```python
import torch
import torch.nn.functional as F

def dpo_loss(policy_chosen, policy_rejected, ref_chosen, ref_rejected, beta=0.1):
    chosen_logratio = policy_chosen - ref_chosen
    rejected_logratio = policy_rejected - ref_rejected
    logits = beta * (chosen_logratio - rejected_logratio)
    return -F.logsigmoid(logits).mean()
```

实验要求：

- 用小型 causal LM 计算 chosen/rejected 序列 log probability。
- 实现 DPO loss。
- 比较不同 beta 下训练稳定性和回答长度。

## 11. 代码实验二：GRPO 组内 advantage

```python
def grpo_advantages(rewards, eps=1e-8):
    # rewards: [batch, group_size]
    mean = rewards.mean(dim=1, keepdim=True)
    std = rewards.std(dim=1, keepdim=True)
    return (rewards - mean) / (std + eps)
```

实验要求：

- 对同一数学题采样多个答案。
- 用规则 verifier 给出 0/1 reward。
- 计算组内 advantage 并分析奖励方差。

## 12. MCP 调用点设计

### 12.1 MCP 调用点 A：最新对齐论文检索

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(RLHF OR DPO OR RLAIF OR GRPO OR RLVR OR \"preference optimization\") AND (LLM OR \"large language model\")",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 区分方法使用 human preference、AI feedback、reward model、verifier 还是 self-reward。
- 提取 KL 约束、reference model、advantage 构造和数据格式。

### 12.2 MCP 调用点 B：代码库检索

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "DPO ORPO KTO GRPO RLHF TRL preference optimization LLM",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

预期学习收获：

- 学习 Hugging Face TRL 中 DPO/ORPO/PPO Trainer。
- 对比 sequence logprob、mask、长度归一化的实现细节。

## 13. 课后研究课题

### 课题 1：DPO 与 SFT 对比

要求：

- 使用同一小型偏好数据集。
- 训练 SFT 与 DPO。
- 比较 win rate、长度、重复率和 KL drift。

### 课题 2：偏好数据噪声实验

要求：

- 人为翻转部分 chosen/rejected 标签。
- 比较 DPO 与 IPO 的鲁棒性。
- 分析噪声对 reward margin 的影响。

### 课题 3：规则奖励训练推理小任务

要求：

- 构造可验证数学或代码任务。
- 采样多个答案，使用 verifier 打分。
- 实现简化 GRPO 或 reward-weighted SFT。

## 14. 推荐阅读与动态更新入口

基础阅读：

- Christiano et al., Deep Reinforcement Learning from Human Preferences.
- Ouyang et al., Training language models to follow instructions with human feedback.
- Rafailov et al., Direct Preference Optimization.
- Bai et al., Constitutional AI.
- Schulman et al., Proximal Policy Optimization Algorithms.

近期阅读：

- A Survey of Direct Preference Optimization, https://arxiv.org/abs/2503.11701
- SimPO: Simple Preference Optimization, https://papers.nips.cc/paper/2024/hash/e099c1c9699814af0be873a175361713-Abstract-Conference.html
- DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning, https://arxiv.org/abs/2501.12948
- URPO: A Unified Reward & Policy Optimization Framework for Large Language Models, https://arxiv.org/abs/2507.17515
- Predictive Scaling Laws for Efficient GRPO Training of Large Reasoning Models, https://arxiv.org/abs/2507.18014
- Training Large Language Models to Reason via EM Policy Gradient, https://arxiv.org/abs/2504.18587
- Reinforcement Learning for Large Language Models via Group Preference Reward Shaping, https://aclanthology.org/2025.emnlp-main.1085/

动态阅读入口：

- Hugging Face TRL: https://github.com/huggingface/trl
- OpenRLHF: https://github.com/OpenRLHF/OpenRLHF
- arXiv: https://arxiv.org
- OpenReview: https://openreview.net

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 RLHF、DPO、RLAIF、GRPO、RLVR、preference optimization 相关论文。
