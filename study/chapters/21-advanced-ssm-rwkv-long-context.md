# 第 21 课：状态空间模型、RWKV 与长上下文建模

## 0. 任务标识

任务名称：状态空间模型、RWKV 与长上下文建模

预计学习时长：2 周

前置基础要求：

- 理解 RNN、Transformer attention、卷积、矩阵乘法和递推。
- 已完成第 15 课，理解线性系统、谱半径、稳定性和矩阵指数。
- 已完成第 19 课，理解 Transformer 长上下文瓶颈和注意力信息路由。
- 能阅读 PyTorch 中 scan、causal convolution 和 KV cache 相关代码。

本课目标：

```text
理解 SSM、Mamba、RWKV、RetNet 等线性复杂度架构如何试图绕开 Transformer 注意力的二次复杂度，并认识它们在长上下文记忆容量上的真实边界。
```

你需要建立以下研究直觉：

- Transformer attention 是无状态的内容寻址记忆，但 KV cache 随上下文线性增长。
- SSM/RWKV 是有状态递推模型，推理内存可近似常数，但状态容量有限。
- SSM 的数学根源是连续时间线性动力系统。
- Mamba 的 selective SSM 让状态更新依赖输入，从而增强内容选择能力。
- 长上下文不是只看复杂度 $O(n)$ 或 $O(n^2)$，还要看状态容量、检索能力、训练长度和外推机制。

## 1. 本课阅读方式

建议学习顺序：

```text
连续时间状态空间
  -> 离散化
  -> 卷积形式与递归形式
  -> S4 / DSS / LRU
  -> Mamba selective scan
  -> Mamba-2 与 State Space Duality
  -> RWKV 时间混合
  -> 长上下文 state capacity
  -> 混合架构与工程实现
```

【核心】线性复杂度架构不是“免费无限上下文”。它们把显式 KV 记忆压缩进固定或较小状态中，因此必须分析压缩后的状态能保留多少可检索信息。

## 2. Transformer 长上下文瓶颈

### 2.1 注意力复杂度

标准 causal self-attention：

$$
A
=
\mathrm{softmax}
\left(
\frac{QK^\top}{\sqrt{d_h}}
\right)
$$

其中：

$$
Q,K,V\in\mathbb{R}^{T\times d_h}
$$

计算复杂度为：

$$
O(T^2d_h)
$$

公式注释：

- $T$ 是上下文长度。
- $d_h$ 是单头维度。
- $QK^\top$ 产生 $T\times T$ 注意力矩阵。
- 当 $T$ 从 8K 增加到 128K，注意力矩阵大小按平方增长。

理论注释：

FlashAttention 可以降低显存和提升速度，但没有改变标准全注意力的二次计算本质。长上下文需要从架构上改变信息交互方式，例如滑动窗口、稀疏注意力、线性注意力、SSM、RWKV 或混合架构。

### 2.2 KV cache

自回归推理中，每步保存历史：

$$
K_{1:t},V_{1:t}
$$

KV cache 内存近似：

$$
O(LHTd_h)
$$

公式注释：

- $L$ 是层数。
- $H$ 是注意力头数。
- $T$ 是已生成或输入上下文长度。
- $d_h$ 是每头维度。
- KV cache 随上下文长度线性增长。

理论注释：

推理时 attention 每步只计算当前 query 对历史 KV 的注意力，但 KV cache 存储仍是长上下文部署的主要瓶颈。SSM/RWKV 的吸引力在于它们用固定状态替代不断增长的 KV cache。

## 3. 连续时间状态空间模型

### 3.1 线性状态空间方程

经典连续时间 SSM：

$$
\frac{dh(t)}{dt}
=
Ah(t)+Bx(t)
$$

$$
y(t)
=
Ch(t)+Dx(t)
$$

公式注释：

- $x(t)$ 是输入信号。
- $h(t)$ 是隐藏状态。
- $y(t)$ 是输出。
- $A$ 控制状态自身演化。
- $B$ 控制输入如何写入状态。
- $C$ 控制状态如何读出为输出。
- $D$ 是输入到输出的直通项。

理论注释：

这是控制论和信号处理中的基础模型。深度学习中的 SSM 把序列建模看成一个可学习动力系统：输入 token 驱动状态演化，状态压缩历史信息，输出从状态中读出。

### 3.2 稳定性

若没有输入：

$$
\frac{dh(t)}{dt}=Ah(t)
$$

解为：

$$
h(t)=\exp(At)h(0)
$$

公式注释：

- $\exp(At)$ 是矩阵指数。
- $h(0)$ 是初始状态。
- $A$ 的特征值决定状态随时间衰减、振荡或爆炸。

理论注释：

如果 $A$ 的特征值实部为负，状态会衰减，系统稳定；如果实部为正，状态可能爆炸。SSM 初始化和参数化必须控制谱性质，否则长序列递推会数值不稳定。

## 4. 离散化与递推

### 4.1 离散状态更新

对连续系统离散化后：

$$
h_t
=
\bar{A}h_{t-1}
+
\bar{B}x_t
$$

$$
y_t
=
Ch_t+Dx_t
$$

公式注释：

- $h_t$ 是第 $t$ 个 token 后的状态。
- $\bar{A}$ 是离散状态转移矩阵。
- $\bar{B}$ 是离散输入矩阵。
- 递推形式天然支持 streaming inference。

理论注释：

递推复杂度为 $O(T)$，每个 token 只更新一次状态。但所有历史信息都被压缩进 $h_t$，因此状态维度和更新机制决定了长期记忆容量。

### 4.2 卷积形式

展开递推：

$$
y_t
=
\sum_{i=0}^{t}
C\bar{A}^{i}\bar{B}x_{t-i}
$$

令：

$$
K_i=C\bar{A}^{i}\bar{B}
$$

得到：

$$
y_t=\sum_{i=0}^{t}K_i x_{t-i}
$$

公式注释：

- $K_i$ 是 SSM 的卷积核。
- $i$ 表示过去第 $i$ 步输入对当前输出的影响。
- $\bar{A}^i$ 控制记忆随距离衰减或振荡。
- 训练时可以用卷积并行计算，推理时可以用递推逐 token 更新。

理论注释：

SSM 的重要优势是“训练可并行、推理可递归”。这类似 attention 的训练并行性，但推理内存更接近 RNN。

## 5. Mamba：Selective State Space Model

### 5.1 输入依赖的选择机制

Mamba 的关键变化是让部分 SSM 参数依赖输入：

$$
h_t
=
\bar{A}(x_t)h_{t-1}
+
\bar{B}(x_t)x_t
$$

$$
y_t
=
C(x_t)h_t
$$

公式注释：

- $\bar{A}(x_t)$ 表示状态保留或遗忘程度可随当前 token 改变。
- $\bar{B}(x_t)$ 表示当前 token 写入状态的方式可变。
- $C(x_t)$ 表示读出方式可变。
- 这让模型具备内容选择能力，而不是固定卷积核。

理论注释：

传统 LTI SSM 使用固定核，适合信号处理，但对语言这种强内容依赖任务不足。Mamba 的 selective mechanism 使模型能根据 token 动态决定写入、保留和读出，从而更接近 attention 的内容选择能力。

### 5.2 Selective scan

递推可写成 scan：

$$
h_t=a_t\odot h_{t-1}+b_t
$$

其中：

$$
a_t=\bar{A}(x_t),\quad b_t=\bar{B}(x_t)x_t
$$

公式注释：

- $a_t$ 是逐 token 的遗忘或保留门。
- $b_t$ 是逐 token 的写入项。
- $\odot$ 是逐元素乘法。
- scan 算法可以并行化这类关联递推。

理论注释：

Mamba 的工程关键在于硬件感知 selective scan。它不是简单 Python for-loop，而是用并行 scan、kernel fusion 和内存布局优化实现高吞吐。

## 6. Mamba-2 与 State Space Duality

### 6.1 SSM 与 Attention 的对偶视角

Mamba-2 的 State Space Duality 提出：某些结构化 SSM 和注意力可以放进统一框架理解。

简化地看，attention 输出为：

$$
y_t
=
\sum_{i\le t}
\alpha_{ti}v_i
$$

SSM 输出为：

$$
y_t
=
\sum_{i\le t}
K_{t,i}x_i
$$

公式注释：

- attention 的权重 $\alpha_{ti}$ 依赖 query 和 key。
- SSM 的核 $K_{t,i}$ 由状态转移和选择机制决定。
- 两者都可以看作对历史 token 的加权聚合。

理论注释：

差异在于 memory representation：attention 显式保存所有 KV，SSM 将历史压缩进状态。SSD 的价值是帮助设计更快的 Mamba-2 层，并解释 attention 与 SSM 的共同结构。

## 7. RWKV：Transformer 训练范式与 RNN 推理形态

### 7.1 RWKV 时间混合

RWKV 可抽象为带指数衰减的加权历史聚合：

$$
s_t
=
\lambda s_{t-1}
+
k_t^\top v_t
$$

$$
z_t
=
\lambda z_{t-1}
+
k_t
$$

$$
y_t
=
\frac{s_t}{z_t}
$$

公式注释：

- $k_t$ 是当前 token 的 key-like 表示。
- $v_t$ 是 value-like 表示。
- $\lambda$ 是时间衰减因子。
- $s_t$ 累积加权 value。
- $z_t$ 累积归一化权重。
- $y_t$ 是归一化后的历史聚合。

理论注释：

RWKV 试图结合 Transformer 的并行训练和 RNN 的常数内存推理。它没有显式 $T\times T$ 注意力矩阵，而是通过递推状态聚合历史信息。

### 7.2 RWKV 与 Attention 的差异

Attention 对每个 query 重新计算对所有历史 token 的权重：

$$
\alpha_{ti}
=
\mathrm{softmax}(q_t^\top k_i)
$$

RWKV 类模型把历史压缩进递推状态：

$$
h_t=f(h_{t-1},x_t)
$$

公式注释：

- attention 是内容寻址，当前 query 可以直接选择历史任意 token。
- RWKV 是状态压缩，当前输出依赖压缩后的历史状态。
- 状态压缩带来效率，也带来信息瓶颈。

理论注释：

RWKV 的优势是推理内存和时间随上下文增长更友好。劣势是精确检索长距离细节可能不如 full attention，除非状态足够大或引入混合注意力机制。

## 8. 长上下文中的 State Capacity

### 8.1 状态容量问题

若模型状态维度为 $d_s$，历史长度为 $T$，则模型要把：

$$
x_1,\ldots,x_T
$$

压缩进：

$$
h_T\in\mathbb{R}^{d_s}
$$

公式注释：

- $T$ 可以是 32K、128K 甚至更长。
- $d_s$ 是固定状态大小。
- 历史信息量随 $T$ 增长，但状态容量固定。

理论注释：

这就是 Stuffed Mamba 等研究指出的 state collapse 问题：线性复杂度模型在极长上下文中可能无法保留足够可检索信息。上下文复杂度低不等于长程记忆能力强。

### 8.2 长上下文能力的三类指标

```text
perplexity：平均语言建模质量
needle retrieval：长上下文精确检索能力
state tracking：持续更新隐含状态的能力
```

理论注释：

一个模型可以在 perplexity 上表现不错，却在 needle-in-a-haystack 检索中失败；也可能能检索显式字符串，但无法维护复杂状态。长上下文评估必须覆盖多种能力。

## 9. 混合架构：Attention + SSM/RWKV

混合架构常见设计：

```text
部分层使用 attention，部分层使用 Mamba/RWKV
局部窗口 attention + 全局 SSM
短程 attention + 长程递推记忆
稀疏 attention + 线性 RNN 状态
```

理论注释：

混合架构承认两类机制互补：attention 擅长内容寻址和精确检索，SSM/RWKV 擅长流式处理和压缩记忆。Jamba、RWKV-X 等方向体现了这种折中。

## 10. 前沿研究进展：2024-2026 视角

### 10.1 Mamba-2 与 State Space Duality

2024 年 Mamba-2 提出 State Space Duality，把 SSM 与注意力放进统一结构，并报告核心层比 Mamba 更快，同时保持语言建模竞争力。

研究意义：

- 后 Transformer 架构不再是简单 RNN 回归。
- SSM 与 attention 的边界正在被重新刻画。
- 结构化矩阵、scan 算法和硬件实现成为架构设计核心。

### 10.2 Stuffed Mamba 与 state collapse

2024-2025 年 Stuffed Mamba 研究指出，RNN/SSM 类长上下文模型虽然复杂度线性，但存在状态容量和上下文召回边界。

研究意义：

- 长上下文评估不能只看可输入长度。
- 固定状态模型必须面对信息压缩瓶颈。
- 状态大小、训练长度和检索任务难度共同决定可用上下文。

### 10.3 RWKV-7 与混合线性复杂度模型

2025 年 RWKV-7、RWKV-X 等工作继续增强 RWKV 的动态状态演化，并通过混合稀疏注意力改善长距离建模。

研究意义：

- 纯状态压缩模型可能需要显式检索机制补强。
- 线性复杂度与精确记忆之间存在结构性折中。
- 未来长上下文架构可能是 hybrid，而非单一 attention 或单一 SSM。

## 11. 代码实验一：离散 SSM 递推与卷积等价

```python
import torch

def ssm_recurrent(x, a, b, c):
    # x: [T], scalar SSM for demonstration
    h = torch.tensor(0.0)
    ys = []
    for t in range(x.shape[0]):
        h = a * h + b * x[t]
        ys.append(c * h)
    return torch.stack(ys)

def ssm_convolution(x, a, b, c):
    t = x.shape[0]
    kernel = torch.stack([c * (a ** i) * b for i in range(t)])
    y = []
    for i in range(t):
        y.append((kernel[:i+1] * torch.flip(x[:i+1], dims=[0])).sum())
    return torch.stack(y)
```

实验要求：

- 验证递推和卷积输出一致。
- 改变 $a$，观察记忆衰减速度。
- 当 $|a|>1$ 时观察数值不稳定。

## 12. 代码实验二：简化 RWKV 时间混合

```python
def simple_rwkv(k, v, decay):
    # k, v: [T, D]
    s = torch.zeros_like(v[0])
    z = torch.zeros_like(k[0])
    ys = []
    for t in range(k.shape[0]):
        weight = torch.exp(k[t])
        s = decay * s + weight * v[t]
        z = decay * z + weight
        ys.append(s / (z + 1e-8))
    return torch.stack(ys)
```

实验要求：

- 改变 decay，观察模型偏向近期 token 还是长期平均。
- 构造 key-value recall toy task，测试固定状态的检索能力。
- 与简化 attention 对比精确检索效果。

## 13. MCP 调用点设计

### 13.1 MCP 调用点 A：最新 SSM/RWKV 论文检索

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(Mamba OR \"state space model\" OR RWKV OR RetNet OR \"linear attention\" OR \"long context\") AND (LLM OR language)",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 区分 SSM、gated linear RNN、linear attention、hybrid model。
- 提取复杂度、状态大小、训练长度、评估上下文长度。
- 判断论文是否评估了真实长程检索，而不只是 perplexity。

### 13.2 MCP 调用点 B：代码库检索

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "Mamba Mamba2 RWKV RetNet state space model long context PyTorch",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

预期学习收获：

- 学习 selective scan 的高性能实现接口。
- 对比 Mamba、RWKV、RetNet 的缓存状态。
- 理解训练并行和推理递归之间的实现差异。

## 14. 课后研究课题

### 课题 1：SSM 记忆衰减实验

要求：

- 实现标量和向量 SSM。
- 改变 $\bar{A}$ 的谱半径。
- 测试不同距离 token 对当前输出的影响。

### 课题 2：Mamba/RWKV 与 Attention 的检索对比

要求：

- 构造 needle retrieval toy dataset。
- 比较简化 attention、简化 RWKV、简化 SSM。
- 分析固定状态模型在哪些场景失败。

### 课题 3：阅读 Mamba-2 或 Stuffed Mamba

要求：

- 总结论文中的核心数学对象。
- 说明它如何定义长上下文能力。
- 分析其结论对 LLM 架构选择的影响。

开放问题：

- 线性复杂度架构能否完全替代 attention？
- state capacity 是否可以通过外部记忆、稀疏注意力或动态状态扩展解决？

## 15. 推荐阅读与动态更新入口

基础阅读：

- Gu et al., Efficiently Modeling Long Sequences with Structured State Spaces.
- Gu and Dao, Mamba: Linear-Time Sequence Modeling with Selective State Spaces.
- Peng et al., RWKV: Reinventing RNNs for the Transformer Era.
- Sun et al., Retentive Network: A Successor to Transformer for Large Language Models.

近期阅读：

- Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality, https://arxiv.org/abs/2405.21060
- Stuffed Mamba: State Collapse and State Capacity of RNN-Based Long-Context Modeling, https://openreview.net/forum?id=cu2CT2VAvs
- Enhancing RWKV-based Language Models for Long-Sequence Text Generation, https://arxiv.org/abs/2502.15485
- RWKV-X: A Linear Complexity Hybrid Language Model, https://arxiv.org/abs/2504.21463
- RWKV-7 "Goose" with Expressive Dynamic State Evolution, https://arxiv.org/abs/2503.14456
- Scaling up the State Size of RNN LLMs for Long-Context Scenarios, https://aclanthology.org/2025.acl-long.564/
- State Space Models are Strong Text Rerankers, https://aclanthology.org/2025.repl4nlp-1.12/

动态阅读入口：

- Mamba GitHub: https://github.com/state-spaces/mamba
- RWKV GitHub: https://github.com/BlinkDL/RWKV-LM
- arXiv: https://arxiv.org
- OpenReview: https://openreview.net

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 Mamba、Mamba-2、RWKV、RetNet、linear attention、long-context state capacity 相关论文。
