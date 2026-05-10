# 第 20 课：稀疏专家模型 MoE：路由、负载均衡、容量因子与系统实现

## 0. 任务标识

任务名称：稀疏专家模型 MoE：路由、负载均衡、容量因子与系统实现

预计学习时长：1.5 到 2 周

前置基础要求：

- 理解 Transformer FFN、softmax、top-k、交叉熵和分布式训练。
- 已完成第 16 课，理解低秩、稀疏和参数高效扩展。
- 已完成第 18 课，理解大规模优化、batch、分布式同步和通信成本。
- 能读懂 PyTorch 中 `topk`、scatter/gather 和 all-to-all 通信的基本逻辑。

本课目标：

```text
理解 MoE 如何通过稀疏激活扩展总参数量，同时保持每个 token 的计算量近似可控。
```

你需要建立以下研究直觉：

- MoE 的核心不是“多个模型投票”，而是 token 级动态路由。
- 路由器决定每个 token 送到哪些专家，专家通常是 FFN 子网络。
- MoE 的难点不是公式本身，而是负载均衡、通信、专家塌缩、训练稳定性和推理调度。
- 总参数量大不等于每 token 计算量大；activated parameters 才决定实际前向计算。
- MoE 是算法、优化和系统工程强耦合的架构。

## 1. 本课阅读方式

建议学习顺序：

```text
Dense FFN
  -> MoE FFN 替换
  -> Router / Gate
  -> Top-k routing
  -> Load balancing loss
  -> Capacity factor 与 token dropping
  -> Expert parallelism 与 all-to-all
  -> Auxiliary-loss-free load balancing
  -> 推理缓存与专家调度
```

【核心】MoE 的研究问题不是“怎么堆更多专家”，而是“如何让路由、专家、负载、通信和训练目标共同稳定工作”。

## 2. 从 Dense FFN 到 MoE 层

### 2.1 Dense FFN

Transformer 中标准 FFN 为：

$$
\mathrm{FFN}(x)
=
W_2 \phi(W_1x)
$$

公式注释：

- $x\in\mathbb{R}^{d_{\text{model}}}$ 是单个 token 的隐藏状态。
- $W_1\in\mathbb{R}^{d_{\text{ff}}\times d_{\text{model}}}$ 是升维矩阵。
- $W_2\in\mathbb{R}^{d_{\text{model}}\times d_{\text{ff}}}$ 是降维矩阵。
- $\phi$ 通常是 GELU、SwiGLU 或 ReLU。
- 所有 token 都经过同一个 FFN 参数。

理论注释：

Dense FFN 的计算量随参数量增长。如果想扩大 FFN 容量，每个 token 的计算也随之增加。MoE 的想法是扩大总专家参数，但每个 token 只激活少数专家。

### 2.2 MoE FFN

MoE 层包含 $E$ 个专家：

$$
\mathrm{Expert}_e(x)
=
W_{2,e}\phi(W_{1,e}x)
$$

MoE 输出为：

$$
y
=
\sum_{e=1}^{E}
g_e(x)\mathrm{Expert}_e(x)
$$

公式注释：

- $E$ 是专家总数。
- $\mathrm{Expert}_e$ 是第 $e$ 个专家，通常结构与 FFN 类似。
- $g_e(x)$ 是路由器给第 $e$ 个专家的权重。
- 若采用稀疏 top-k routing，大多数 $g_e(x)=0$。

理论注释：

MoE 将参数容量和计算量部分解耦。总参数量约随 $E$ 增长，但每个 token 只经过 $k$ 个专家，计算量约与 $k$ 成正比，而不是与 $E$ 成正比。

## 3. Router 与 Top-k Routing

### 3.1 路由概率

路由器通常是一个线性分类器：

$$
s(x)=W_rx
$$

$$
p_e(x)
=
\frac{\exp(s_e(x))}
{\sum_{j=1}^{E}\exp(s_j(x))}
$$

公式注释：

- $W_r\in\mathbb{R}^{E\times d_{\text{model}}}$ 是路由器权重。
- $s_e(x)$ 是 token $x$ 分配给专家 $e$ 的 logit。
- $p_e(x)$ 是 softmax 后的路由概率。
- 路由器本身参数很少，但对训练稳定性影响巨大。

理论注释：

路由器是 MoE 的瓶颈之一。它需要同时学习语义分工和负载均衡。如果只按任务最优路由，可能所有 token 都挤到少数强专家；如果过度均衡，可能损害专家 specialization。

### 3.2 Top-k routing

选取概率最高的 $k$ 个专家：

$$
\mathcal{T}(x)
=
\operatorname{TopK}(p(x),k)
$$

输出为：

$$
y
=
\sum_{e\in\mathcal{T}(x)}
\tilde{p}_e(x)\mathrm{Expert}_e(x)
$$

其中：

$$
\tilde{p}_e(x)
=
\frac{p_e(x)}
{\sum_{j\in\mathcal{T}(x)}p_j(x)}
$$

公式注释：

- $\mathcal{T}(x)$ 是被选中的专家集合。
- $k=1$ 时是 Switch Transformer 风格 top-1 routing。
- $k=2$ 或更大时，每个 token 可混合多个专家输出。
- $\tilde{p}_e$ 是在选中专家上重新归一化的权重。

理论注释：

Top-k 带来稀疏计算，但也带来不可导选择。实际训练中，专家选择路径对未选中专家没有梯度，可能导致专家利用不均衡。常见解决方案包括加噪路由、负载均衡损失、expert choice 和 auxiliary-loss-free 方法。

## 4. 负载均衡与专家塌缩

### 4.1 负载定义

一个 batch 中专家 $e$ 的 token 负载可写为：

$$
L_e
=
\sum_{i=1}^{N}
\mathbf{1}[e\in\mathcal{T}(x_i)]
$$

公式注释：

- $N$ 是 batch 内 token 数。
- $\mathbf{1}[\cdot]$ 是指示函数，条件成立为 1，否则为 0。
- $L_e$ 表示专家 $e$ 实际处理了多少 token。
- 理想情况下，各专家负载接近 $N k / E$。

理论注释：

负载不均衡会造成两个问题：第一，热门专家过载，导致 token dropping 或延迟；第二，冷门专家训练不足，能力退化。专家塌缩是 MoE 训练失败的常见原因。

### 4.2 辅助负载均衡损失

常见负载均衡损失可抽象为：

$$
\mathcal{L}_{\text{aux}}
=
E
\sum_{e=1}^{E}
f_e P_e
$$

其中：

$$
f_e=\frac{L_e}{N},\quad
P_e=\frac{1}{N}\sum_{i=1}^{N}p_e(x_i)
$$

公式注释：

- $f_e$ 是专家 $e$ 实际接收 token 的比例。
- $P_e$ 是路由器给专家 $e$ 的平均概率。
- 如果某个专家既被高概率选择又实际负载高，损失会推动路由器调整。
- 前面的 $E$ 用于尺度归一化。

理论注释：

辅助损失能缓解负载不均衡，但它也会和主语言建模损失竞争。过强的负载均衡会迫使 token 去不合适的专家，损害模型质量。DeepSeek-V3 的 auxiliary-loss-free load balancing 正是为了降低这种目标冲突。

## 5. Capacity Factor 与 Token Dropping

### 5.1 专家容量

每个专家容量常设为：

$$
C
=
\left\lceil
\frac{N k}{E}
\cdot
\alpha
\right\rceil
$$

公式注释：

- $C$ 是每个专家最多处理的 token 数。
- $N$ 是 batch token 数。
- $k$ 是每个 token 激活专家数。
- $E$ 是专家数。
- $\alpha$ 是 capacity factor，通常大于 1。

理论注释：

容量因子越大，token dropping 越少，但 padding 和无效计算越多。容量因子越小，计算更紧凑，但热门专家更容易溢出。它是吞吐和质量之间的系统超参数。

### 5.2 Token dropping

当专家 $e$ 的分配 token 超过 $C$：

$$
L_e > C
$$

超出的 token 可能被丢弃、转发到备选专家或走残差路径。

公式注释：

- token dropping 是系统层面的近似，不是模型语义上的理想操作。
- 被丢弃 token 无法经过目标专家，可能造成训练噪声和质量下降。
- 推理时 dropping 更敏感，因为它直接影响输出质量。

理论注释：

MoE 训练中的很多“模型问题”实际是容量和调度问题。路由策略必须和硬件拓扑、batch 组织、专家并行方式一起设计。

## 6. Expert Parallelism 与 All-to-All

### 6.1 专家并行

专家并行把不同专家放在不同设备上。token 需要被发送到对应专家：

```text
tokens on each GPU
  -> router
  -> all-to-all dispatch
  -> expert computation
  -> all-to-all combine
```

通信量近似与：

$$
O(Nkd_{\text{model}})
$$

相关。

公式注释：

- $N$ 是全局 token 数。
- $k$ 是每个 token 路由到的专家数。
- $d_{\text{model}}$ 是 token hidden size。
- All-to-all 通信需要跨设备交换 token 激活。

理论注释：

MoE 的瓶颈常常不是 FLOPs，而是通信和调度。专家越多、top-k 越大、跨节点专家越分散，all-to-all 成本越高。LocMoE 这类方法试图利用 locality 把跨节点通信转为节点内通信。

## 7. DeepSeek-MoE 与 Auxiliary-Loss-Free 负载均衡

### 7.1 细粒度专家与共享专家

DeepSeek-MoE 系列使用细粒度专家和共享专家思想：

```text
shared experts：所有 token 都可访问的通用能力
routed experts：由路由器选择的专业能力
```

理论注释：

共享专家缓解路由错误带来的基础能力损失；细粒度专家让专家分工更细，提高稀疏激活的组合灵活性。

### 7.2 Auxiliary-loss-free 直觉

传统方法把负载均衡写成额外损失。Auxiliary-loss-free 方法更像对路由偏置做动态调节：

$$
s_e'(x)
=
s_e(x)+b_e
$$

公式注释：

- $s_e(x)$ 是原始路由 logit。
- $b_e$ 是专家 $e$ 的动态偏置。
- 如果专家过载，可以降低其偏置；如果专家利用不足，可以提高其偏置。
- 调整发生在路由层面，而不是直接给主损失加辅助项。

理论注释：

这类方法试图把负载均衡看成约束优化或分配问题，而不是多目标损失加权问题。2025 年理论工作将其解释为 assignment problem 的 primal-dual 近似，为 MoE 负载均衡提供了更清晰的优化视角。

## 8. 前沿研究进展：2024-2026 视角

### 8.1 DeepSeek-V3 的 MoE 工程化

DeepSeek-V3 报告了 671B 总参数、每 token 激活约 37B 参数的 MoE 架构，并使用 auxiliary-loss-free load balancing。

研究意义：

- 证明稀疏激活可以支撑极大总参数模型。
- 负载均衡从辅助损失走向路由机制设计。
- activated parameters 成为评估 MoE 成本的关键指标。

### 8.2 LocMoE：通信局部性

LocMoE 关注 MoE 训练中的 all-to-all 通信瓶颈，通过结合负载均衡和 locality，将部分跨节点通信转为节点内通信。

研究意义：

- MoE 扩展不只是算法问题，还是网络拓扑问题。
- 路由器需要考虑专家语义，也需要考虑物理位置。
- 未来 MoE 可能会出现 topology-aware routing。

### 8.3 MoE 系统综述与部署

2025 年 MoE in LLMs 综述总结了 expert gating、routing、hierarchical MoE、多模态 MoE、部署和挑战。

研究意义：

- MoE 已从单点架构技巧变为 LLM 扩展主线。
- 专家 specialization、routing collapse、inference serving 和 expert caching 是核心开放问题。

## 9. 代码实验一：最小 Top-k MoE 层

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class Expert(nn.Module):
    def __init__(self, d_model, d_ff):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )

    def forward(self, x):
        return self.net(x)

class TopKMoE(nn.Module):
    def __init__(self, d_model, d_ff, num_experts=4, k=2):
        super().__init__()
        self.router = nn.Linear(d_model, num_experts)
        self.experts = nn.ModuleList([Expert(d_model, d_ff) for _ in range(num_experts)])
        self.k = k

    def forward(self, x):
        # x: [batch, tokens, d_model]
        scores = self.router(x)
        probs = F.softmax(scores, dim=-1)
        top_prob, top_idx = torch.topk(probs, self.k, dim=-1)
        top_prob = top_prob / top_prob.sum(dim=-1, keepdim=True)

        out = torch.zeros_like(x)
        for expert_id, expert in enumerate(self.experts):
            mask = top_idx == expert_id
            if not mask.any():
                continue
            token_mask = mask.any(dim=-1)
            selected = x[token_mask]
            expert_out = expert(selected)
            weights = (top_prob * mask.float()).sum(dim=-1)[token_mask].unsqueeze(-1)
            out[token_mask] += expert_out * weights
        return out, probs, top_idx
```

代码注释：

- 该实现便于理解，不适合高性能训练。
- 真实 MoE 需要按专家聚合 token，避免逐专家 Python loop。
- 分布式版本需要 dispatch/combine 和 all-to-all。

## 10. 代码实验二：负载均衡指标

```python
def expert_load(top_idx, num_experts):
    # top_idx: [batch, tokens, k]
    flat = top_idx.reshape(-1)
    return torch.bincount(flat, minlength=num_experts).float()

def load_balance_loss(probs, top_idx, num_experts):
    # probs: [batch, tokens, experts]
    n = probs.shape[0] * probs.shape[1]
    load = expert_load(top_idx, num_experts) / n
    prob_mean = probs.mean(dim=(0, 1))
    return num_experts * torch.sum(load * prob_mean)
```

实验要求：

- 训练 toy MoE 分类模型。
- 观察无辅助损失时是否出现专家塌缩。
- 加入负载均衡损失后比较专家使用率和验证性能。

## 11. MCP 调用点设计

### 11.1 MCP 调用点 A：最新 MoE 论文检索

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(\"Mixture of Experts\" OR MoE OR \"sparse experts\") AND (LLM OR \"large language model\" OR routing OR \"load balancing\")",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 区分 routing、load balancing、expert specialization、expert parallelism 和 serving。
- 识别论文关注训练、推理还是理论分析。
- 提取 top-k、专家数、activated parameters、通信策略和负载指标。

### 11.2 MCP 调用点 B：代码库检索

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "Mixture of Experts MoE routing load balancing expert parallelism PyTorch LLM",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

预期学习收获：

- 学习高性能 MoE 的 token dispatch/combine。
- 对比 DeepSpeed-MoE、Megablocks、ScatterMoE、Tutel 等实现。
- 理解专家并行与张量并行、数据并行如何组合。

## 12. 课后研究课题

### 课题 1：专家塌缩实验

要求：

- 实现 Top-k MoE toy model。
- 比较无负载均衡、辅助负载均衡、动态路由偏置三种策略。
- 绘制专家负载随训练变化曲线。

### 课题 2：容量因子与 token dropping

要求：

- 固定专家数和 top-k。
- 改变 capacity factor。
- 记录 token dropping 率、训练 loss 和吞吐。

开放问题：

- 更大的 capacity factor 是否总是更好？
- token dropping 对训练和推理的影响是否一致？

### 课题 3：MoE 系统瓶颈分析

要求：

- 阅读 LocMoE 或 MegaScale-MoE。
- 分析 all-to-all 通信量。
- 设计一个 topology-aware routing 的简化方案。

## 13. 推荐阅读与动态更新入口

基础阅读：

- Shazeer et al., Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer.
- Fedus et al., Switch Transformers.
- Zhou et al., Mixture-of-Experts with Expert Choice Routing.
- Lepikhin et al., GShard.

近期阅读：

- DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models, https://arxiv.org/abs/2401.06066
- DeepSeek-V3 Technical Report, https://arxiv.org/abs/2412.19437
- Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts, https://arxiv.org/abs/2408.15664
- A Theoretical Framework for Auxiliary-Loss-Free Load Balancing of Sparse Mixture-of-Experts in Large-Scale AI Models, https://arxiv.org/abs/2512.03915
- LocMoE: A Low-Overhead MoE for Large Language Model Training, https://arxiv.org/abs/2401.13920
- Mixture of Experts in Large Language Models, https://arxiv.org/abs/2507.11181
- Scaling Laws for Fine-Grained Mixture of Experts, https://arxiv.org/abs/2402.07871

动态阅读入口：

- arXiv: https://arxiv.org
- DeepSpeed-MoE: https://www.deepspeed.ai/tutorials/mixture-of-experts/
- Megablocks: https://github.com/stanford-futuredata/megablocks
- Tutel: https://github.com/microsoft/tutel

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 MoE routing、load balancing、expert parallelism、MoE serving 相关论文。
