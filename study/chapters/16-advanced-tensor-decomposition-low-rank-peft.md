# 第 16 课：张量分解、低秩结构与大模型参数高效训练

## 0. 任务标识

任务名称：张量分解、低秩结构与大模型参数高效训练

预计学习时长：1 到 1.5 周

前置基础要求：

- 已完成第 15 课，理解 SVD、奇异值谱、条件数、Hessian 谱和低秩近似。
- 理解 Transformer 中的线性投影矩阵，例如 $W_Q,W_K,W_V,W_O$ 和 MLP 中的 up/down projection。
- 能使用 PyTorch 完成基础微调，了解 LoRA、QLoRA 或 PEFT 的基本使用方式。
- 能阅读 arXiv 论文中的方法章节和算法伪代码。

本课目标：

```text
把“低秩矩阵近似”扩展到“张量结构、Kronecker 结构、子空间训练和大模型参数高效适配”。
```

你需要形成以下研究直觉：

- 大模型微调不是必须更新全量参数，很多任务更新集中在低维子空间。
- LoRA 的数学本质是限制权重更新矩阵的秩。
- 张量分解进一步利用多维结构，比普通矩阵低秩更强地压缩参数。
- GaLore 这类方法不是低秩参数化权重，而是低秩投影梯度。
- DoRA、PiSSA、LoRA+、LoRTA 等方法都可以放进“更新空间如何选择、分解、初始化和优化”的统一框架中。

## 1. 本课阅读方式

建议学习顺序：

```text
矩阵低秩复习
  -> LoRA 的秩约束与梯度结构
  -> Kronecker 分解
  -> CP/Tucker/TT 张量分解
  -> 低秩初始化与谱对齐
  -> 低秩梯度投影
  -> 量化与低秩适配结合
  -> 论文复现与实验诊断
```

【核心】参数高效训练不是简单“少训点参数”，而是在高维参数空间中选择一个可训练子流形。研究问题是：这个子流形是否足够表达任务更新，同时是否足够低维以降低显存、通信和过拟合。

## 2. 从矩阵低秩到权重更新子空间

### 2.1 全量微调的参数更新

设预训练线性层权重为：

$$
W_0 \in \mathbb{R}^{d_{\text{out}}\times d_{\text{in}}}
$$

全量微调学习：

$$
W = W_0 + \Delta W
$$

其中：

$$
\Delta W \in \mathbb{R}^{d_{\text{out}}\times d_{\text{in}}}
$$

公式注释：

- $W_0$ 是预训练模型已经学到的通用表示基底。
- $\Delta W$ 是下游任务需要新增或修正的方向。
- 全量微调允许 $\Delta W$ 占据整个矩阵空间，自由度为 $d_{\text{out}}d_{\text{in}}$。
- 对大模型来说，这意味着优化器状态、梯度、参数副本都会成倍增加显存。

### 2.2 LoRA 的低秩约束

LoRA 将更新限制为：

$$
\Delta W = BA
$$

其中：

$$
B \in \mathbb{R}^{d_{\text{out}}\times r},\quad
A \in \mathbb{R}^{r\times d_{\text{in}}}
$$

因此：

$$
\operatorname{rank}(\Delta W) \le r
$$

可训练参数量从：

$$
d_{\text{out}}d_{\text{in}}
$$

下降为：

$$
r(d_{\text{out}}+d_{\text{in}})
$$

公式注释：

- $r$ 是低秩瓶颈维度。它控制更新空间大小，不直接等于模型表达能力上限，但会强烈影响适配能力。
- $A$ 可理解为把输入投影到 $r$ 维任务子空间。
- $B$ 可理解为把任务子空间映射回输出空间。
- 当 $r \ll \min(d_{\text{in}},d_{\text{out}})$ 时，参数和优化器显存显著下降。

理论注释：

LoRA 的核心假设是：

```text
下游任务需要的参数改变量，主要集中在少数主方向。
```

这个假设可以从三个角度理解：

- 谱角度：$\Delta W$ 的奇异值快速衰减。
- 优化角度：有效梯度位于低维子空间。
- 表示角度：预训练模型已提供大部分通用特征，下游任务只需重新组合。

## 3. 低秩更新的优化动力学

### 3.1 LoRA 参数的梯度

设损失为 $\mathcal{L}(W_0 + BA)$，记：

$$
G =
\frac{\partial \mathcal{L}}{\partial \Delta W}
\in \mathbb{R}^{d_{\text{out}}\times d_{\text{in}}}
$$

由链式法则：

$$
\frac{\partial \mathcal{L}}{\partial B}
=
GA^\top
$$

$$
\frac{\partial \mathcal{L}}{\partial A}
=
B^\top G
$$

公式注释：

- $G$ 是如果直接训练完整 $\Delta W$ 时会得到的全量梯度。
- $GA^\top$ 把全量梯度投影到 $B$ 的参数空间。
- $B^\top G$ 把全量梯度投影到 $A$ 的参数空间。
- 因此 LoRA 不是简单删除梯度，而是把梯度限制在由 $A$ 和 $B$ 决定的低秩流形上。

### 3.2 低秩流形的切空间

对于：

$$
\Delta W = BA
$$

微小变化为：

$$
d(\Delta W)=dB\,A+B\,dA
$$

公式注释：

- $dB\,A$ 表示改变输出方向。
- $B\,dA$ 表示改变输入投影方向。
- 所有可能的 $d(\Delta W)$ 构成低秩矩阵流形附近的切空间。
- 优化器每一步实际只能在这个切空间里移动。

理论注释：

如果最优全量更新 $\Delta W^\star$ 不在这个低秩流形附近，LoRA 会产生结构性欠拟合。提高 rank、选择更多注入层、使用更好的初始化或采用 DoRA/PiSSA 等方法，都是在改善这个子空间匹配问题。

## 4. Kronecker 分解：利用双线性结构压缩矩阵

### 4.1 Kronecker 积

给定：

$$
A \in \mathbb{R}^{m\times n},\quad
B \in \mathbb{R}^{p\times q}
$$

Kronecker 积定义为：

$$
A\otimes B =
\begin{bmatrix}
a_{11}B & a_{12}B & \cdots & a_{1n}B\\
a_{21}B & a_{22}B & \cdots & a_{2n}B\\
\vdots & \vdots & \ddots & \vdots\\
a_{m1}B & a_{m2}B & \cdots & a_{mn}B
\end{bmatrix}
$$

公式注释：

- $A\otimes B$ 把 $A$ 的每个元素替换为该元素乘以整个矩阵 $B$。
- 输出矩阵大小为 $mp \times nq$。
- Kronecker 结构适合表达“粗粒度模式”和“细粒度模式”的组合。

### 4.2 Kronecker 低秩近似

可以用若干 Kronecker 项近似权重：

$$
W \approx \sum_{i=1}^{R} A_i \otimes B_i
$$

公式注释：

- $R$ 是 Kronecker rank。
- 每一项 $A_i\otimes B_i$ 表示一个可分离结构。
- 这种分解比普通低秩矩阵更强调二维网格或块结构。

工程意义：

- 对卷积核、注意力投影矩阵、embedding 压缩都有潜在价值。
- Kronecker 因子可以减少参数和矩阵乘法成本。
- 缺点是形状约束较强，需要合理 reshape 原始权重。

## 5. 张量分解：从二维矩阵到多维结构

### 5.1 为什么需要张量

矩阵是二阶张量。很多模型参数天然具有多维结构：

- 卷积核：$\mathcal{W}\in\mathbb{R}^{C_{\text{out}}\times C_{\text{in}}\times k_h\times k_w}$
- 多头注意力：可以重排为 $\mathcal{W}\in\mathbb{R}^{n_{\text{head}}\times d_{\text{head}}\times d_{\text{model}}}$
- FFN 权重：可按通道组、专家、层、秩维度重排。

把这些结构直接展平成矩阵会丢失模式信息。张量分解试图利用多维相关性。

### 5.2 CP 分解

CP 分解把三阶张量写成若干秩 1 张量之和：

$$
\mathcal{X}
\approx
\sum_{r=1}^{R}
\lambda_r
a_r \otimes b_r \otimes c_r
$$

其中：

$$
a_r\in\mathbb{R}^{I},\quad
b_r\in\mathbb{R}^{J},\quad
c_r\in\mathbb{R}^{K}
$$

公式注释：

- $\mathcal{X}\in\mathbb{R}^{I\times J\times K}$ 是三阶张量。
- $a_r\otimes b_r\otimes c_r$ 是三维外积，对应一个秩 1 模式。
- $R$ 是 CP rank，控制保留多少模式。
- $\lambda_r$ 是第 $r$ 个模式的强度。

优点：

- 参数量低。
- 结构清晰。
- 适合强可分离模式。

缺点：

- CP rank 难以稳定估计。
- 优化可能病态。
- 对复杂相关结构表达能力有限。

### 5.3 Tucker 分解

Tucker 分解写成：

$$
\mathcal{X}
\approx
\mathcal{G}
\times_1 A
\times_2 B
\times_3 C
$$

其中：

$$
\mathcal{G}\in\mathbb{R}^{R_1\times R_2\times R_3}
$$

公式注释：

- $\mathcal{G}$ 是核心张量，表示低维子空间中的交互关系。
- $A,B,C$ 是三个模态上的因子矩阵。
- $\times_n$ 表示 mode-$n$ tensor-matrix product。
- Tucker 分解比 CP 更灵活，因为核心张量允许不同模态之间发生复杂交互。

参数量从：

$$
IJK
$$

变为：

$$
IR_1 + JR_2 + KR_3 + R_1R_2R_3
$$

理论注释：

Tucker 分解类似“多维 PCA”。它为每个模态学习一个低维子空间，再用核心张量描述这些子空间之间的耦合。

### 5.4 Tensor Train 分解

Tensor Train 将高阶张量写成一串三阶核心：

$$
\mathcal{X}(i_1,i_2,\ldots,i_d)
=
G_1(i_1)G_2(i_2)\cdots G_d(i_d)
$$

更完整地写：

$$
G_k \in \mathbb{R}^{r_{k-1}\times n_k\times r_k},\quad
r_0=r_d=1
$$

公式注释：

- $d$ 是张量阶数。
- $n_k$ 是第 $k$ 个维度大小。
- $r_k$ 是 TT rank，控制相邻维度之间传递多少信息。
- 每个 $G_k(i_k)$ 是固定索引 $i_k$ 后得到的矩阵。
- 整体元素值由一串矩阵乘积得到。

工程意义：

- TT 适合压缩 embedding、全连接层和高阶重排后的权重。
- 参数量从 $\prod_k n_k$ 降低到约 $\sum_k r_{k-1}n_kr_k$。
- 但 TT 的实际速度收益依赖内核实现，参数少不等于推理一定快。

## 6. 低秩适配的前沿方法

### 6.1 LoRA+：区分两个低秩因子的学习率

LoRA+ 观察到 $A$ 和 $B$ 在优化中承担不同角色，因此可以设置不同学习率：

$$
\eta_A \ne \eta_B
$$

理论直觉：

- $A$ 决定输入侧投影子空间。
- $B$ 决定输出侧重构方向。
- 两者梯度尺度和收敛速度可能不同。

研究意义：

```text
低秩分解不是唯一确定的，优化器超参数会影响分解因子的有效学习动态。
```

### 6.2 DoRA：权重方向与幅值解耦

DoRA 将权重分解为幅值和方向：

$$
W = m \frac{V}{\|V\|}
$$

然后对方向部分使用低秩更新：

$$
V = V_0 + BA
$$

公式注释：

- $m$ 控制权重范数或幅值。
- $\frac{V}{\|V\|}$ 控制方向。
- LoRA 直接加性更新权重；DoRA 认为方向和幅值应分开适配。

研究意义：

- 在低 rank 时，DoRA 往往比普通 LoRA 更接近全量微调行为。
- 它把 weight normalization 的思想引入 PEFT。
- 这说明低秩结构不只可以作用在权重本身，也可以作用在权重方向空间。

### 6.3 PiSSA：用主奇异方向初始化适配空间

PiSSA 的核心思想是利用预训练权重的主奇异向量初始化适配模块，而不是随机初始化。

设：

$$
W_0 \approx U_r\Sigma_r V_r^\top
$$

可以让低秩适配从主谱方向开始：

$$
B_0 = U_r\Sigma_r^{1/2},\quad
A_0 = \Sigma_r^{1/2}V_r^\top
$$

公式注释：

- $U_r,\Sigma_r,V_r$ 是 $W_0$ 的前 $r$ 个奇异方向。
- 这种初始化让适配空间一开始就对齐预训练权重的高能方向。
- 相比随机 LoRA，PiSSA 更强调“谱对齐”和“快速收敛”。

研究意义：

- 初始化不只是工程细节，它决定低秩子空间的起点。
- 当 rank 很小时，起点是否贴近有效方向会显著影响最终性能。

### 6.4 GaLore：低秩梯度投影

GaLore 不一定把权重更新写成 $BA$，而是在训练过程中对梯度做低秩投影。

设全量梯度：

$$
G_t =
\frac{\partial \mathcal{L}}{\partial W_t}
$$

对其做 SVD 近似：

$$
G_t \approx U_r\Sigma_rV_r^\top
$$

然后在低秩子空间内更新优化器状态。

公式注释：

- $G_t$ 是当前 step 的梯度矩阵。
- $U_r,V_r$ 给出梯度变化最快或最重要的方向。
- GaLore 压缩的是梯度和优化器状态，而不是直接限制权重必须低秩。

研究意义：

```text
LoRA 是低秩参数化，GaLore 是低秩优化过程。
```

这一区别很重要：低秩参数化节省可训练参数；低秩梯度投影则试图让全参数训练也具有更低的显存占用。

### 6.5 LoRTA：张量化低秩适配

LoRTA 一类方法把多个 LoRA 模块或多个权重更新组织成张量，并使用张量分解共享结构。

可以抽象为：

$$
\Delta \mathcal{W}
\approx
\mathcal{G}
\times_1 A_{\text{layer}}
\times_2 A_{\text{module}}
\times_3 A_{\text{rank}}
$$

公式注释：

- $\Delta \mathcal{W}$ 表示跨层、跨模块收集到的权重更新张量。
- $A_{\text{layer}}$ 捕捉层间共享结构。
- $A_{\text{module}}$ 捕捉注意力、MLP 等模块类型差异。
- $A_{\text{rank}}$ 捕捉低秩方向。

研究意义：

- 普通 LoRA 对每一层独立建模。
- 张量化 LoRA 允许层与层之间共享适配模式。
- 这适合多任务、多层、多专家或多模态模型的压缩适配。

### 6.6 QA-BLoRA：量化与低秩适配联合设计

量化低秩适配关注：

```text
如何在低 bit 权重和低秩更新同时存在时，保持训练和推理质量？
```

可抽象为：

$$
W' = Q(W_0) + BA
$$

其中 $Q(\cdot)$ 是量化算子。

公式注释：

- $Q(W_0)$ 是量化后的预训练权重，例如 4-bit 或 8-bit。
- $BA$ 是高精度或混合精度的低秩适配更新。
- 量化误差和低秩近似误差会同时影响模型输出。

理论注释：

量化后的误差可写为：

$$
W_0 - Q(W_0) = E_q
$$

最终权重误差来自：

$$
E_{\text{total}}
=
E_q + (\Delta W^\star - BA)
$$

这说明低秩 rank、量化 bit、量化分组大小不是独立超参数，而是在共同分配误差预算。

## 7. 工程实现：一个最小 LoRA 线性层

下面代码用于理解底层逻辑，不依赖 PEFT 框架。

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class LoRALinear(nn.Module):
    def __init__(self, in_features, out_features, rank=8, alpha=16, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank

        self.weight = nn.Parameter(torch.empty(out_features, in_features))
        self.weight.requires_grad_(False)

        self.lora_a = nn.Parameter(torch.empty(rank, in_features))
        self.lora_b = nn.Parameter(torch.zeros(out_features, rank))
        self.bias = nn.Parameter(torch.zeros(out_features)) if bias else None

        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        nn.init.kaiming_uniform_(self.lora_a, a=math.sqrt(5))

    def forward(self, x):
        base = F.linear(x, self.weight, self.bias)
        update = F.linear(F.linear(x, self.lora_a), self.lora_b)
        return base + self.scaling * update
```

代码注释：

- `self.weight.requires_grad_(False)` 冻结预训练权重。
- `lora_a` 对应公式中的 $A$。
- `lora_b` 对应公式中的 $B$。
- `lora_b` 初始化为 0，使训练开始时 LoRA 分支不改变原模型输出。
- `alpha / rank` 是缩放系数，避免 rank 改变时更新幅度失控。

实验要求：

- 分别设置 rank 为 2、4、8、16。
- 记录训练 loss、验证准确率、显存占用和可训练参数量。
- 对训练后的 $BA$ 做 SVD，观察真实有效秩。

## 8. 实验：低秩更新的奇异值能量

训练结束后分析：

$$
\Delta W = BA
$$

做 SVD：

$$
\Delta W = U\Sigma V^\top
$$

定义前 $k$ 个奇异值的能量占比：

$$
E(k)
=
\frac{\sum_{i=1}^{k}\sigma_i^2}
{\sum_{i=1}^{r}\sigma_i^2}
$$

代码：

```python
import torch

def lora_spectral_energy(lora_a, lora_b):
    delta = lora_b @ lora_a
    singular_values = torch.linalg.svdvals(delta)
    energy = singular_values.square()
    ratio = torch.cumsum(energy, dim=0) / energy.sum()
    return singular_values.detach().cpu(), ratio.detach().cpu()
```

分析问题：

- 是否前 1 到 2 个奇异值已经解释大部分能量？
- 不同层的 LoRA 更新谱是否不同？
- 注意力层和 MLP 层的更新是否呈现不同秩结构？
- 提高 rank 后，新增奇异值是否真正被使用？

## 9. 实验：张量分解压缩一个线性层

以 Tucker 为例，可以把权重 reshape 为三阶张量：

$$
W \in \mathbb{R}^{d_{\text{out}}\times d_{\text{in}}}
\to
\mathcal{W}\in\mathbb{R}^{I\times J\times K}
$$

然后学习：

$$
\mathcal{W}
\approx
\mathcal{G}
\times_1 A
\times_2 B
\times_3 C
$$

实验流程：

```text
1. 选择一个训练好的小型 MLP 或 Transformer 线性层。
2. 将权重 reshape 为三阶张量。
3. 使用 tensorly 做 Tucker 分解。
4. 用分解后的权重替代原权重。
5. 比较压缩率、推理延迟、验证集性能下降。
```

示例代码骨架：

```python
import torch
import tensorly as tl
from tensorly.decomposition import tucker

tl.set_backend("pytorch")

def tucker_compress_weight(weight, shape, ranks):
    tensor = weight.reshape(shape)
    core, factors = tucker(tensor, rank=ranks)
    reconstructed = tl.tucker_to_tensor((core, factors))
    return reconstructed.reshape_as(weight), core, factors
```

注意：

- 低参数量不必然带来低延迟。
- 如果分解后需要多个小矩阵乘法，GPU 利用率可能下降。
- 真正工程落地要结合 Triton、自定义 CUDA 或库级 kernel fusion。

## 10. MCP 调用点设计

### 10.1 MCP 调用点 A：最新 PEFT 论文检索

调用目的：获取 2024-2026 年关于 LoRA 变体、低秩微调、张量化适配、量化适配的最新论文。

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(LoRA OR \"low-rank adaptation\" OR PEFT OR \"tensor decomposition\") AND (\"large language model\" OR LLM)",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 学会区分低秩参数化、低秩梯度投影、低秩初始化和张量化共享。
- 建立 PEFT 方法谱系，而不是把每篇论文当成孤立技巧。
- 提取实验设置：base model、rank、数据集、显存、训练 token、评价指标。

### 10.2 MCP 调用点 B：代码库检索

调用目的：查找 PEFT、GaLore、DoRA、PiSSA、Tensor Train compression 的可复现实验代码。

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "LoRA DoRA PiSSA GaLore tensor decomposition LLM",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

预期学习收获：

- 比较论文公式和真实代码之间的差异。
- 学习如何在 Hugging Face Transformers 中替换 attention projection。
- 学习如何记录可训练参数、显存峰值和吞吐量。

### 10.3 MCP 调用点 C：自动生成方法对比表

调用目的：把检索到的论文转为结构化方法表。

建议输出字段：

```json
{
  "method": "DoRA",
  "year": 2024,
  "core_decomposition": "weight magnitude-direction decomposition",
  "trainable_object": "direction low-rank update + magnitude",
  "memory_saving": "medium",
  "main_risk": "extra computation and implementation complexity",
  "best_use_case": "low-rank fine-tuning close to full fine-tuning"
}
```

预期学习收获：

- 能把论文转化为可比较的研究变量。
- 能判断一个新 PEFT 方法到底改变了参数化、初始化、优化器还是量化方式。

## 11. 课后研究课题

### 课题 1：LoRA rank 与真实有效秩

要求：

- 选择一个小型文本分类或指令微调任务。
- 分别设置 rank 为 2、4、8、16、32。
- 保存每层 LoRA 更新矩阵 $BA$。
- 计算奇异值能量 $E(k)$。

开放问题：

- 高 rank 是否真的被模型使用？
- 哪些层的有效秩更高？
- 任务难度是否改变更新谱分布？

输出：

- 每层奇异值谱图。
- rank 与验证性能曲线。
- 一段关于“rank 选择是否可以自适应”的分析。

### 课题 2：DoRA、PiSSA 与普通 LoRA 的对比复现

要求：

- 至少阅读 DoRA 和 PiSSA 原论文。
- 在同一 base model、同一数据集、同一训练预算下比较三种方法。
- 记录收敛速度、最终性能、显存占用和更新矩阵谱。

开放问题：

- 改善来自更好的初始化，还是来自更好的参数化？
- 当 rank 很大时，方法差异是否缩小？
- 哪种方法对学习率最敏感？

输出：

- 实验表格。
- 训练曲线。
- 方法差异的数学解释。

### 课题 3：张量分解压缩 Transformer 线性层

要求：

- 选择一个小型 Transformer。
- 对 attention output projection 或 MLP down projection 做 Tucker 或 Tensor Train 分解。
- 比较压缩前后困惑度、准确率、推理延迟和参数量。

开放问题：

- 参数压缩率与真实延迟收益是否一致？
- 张量分解更适合哪些层？
- 是否需要分解后微调恢复性能？

输出：

- 压缩率和性能下降曲线。
- 对失败案例的分析，而不是只报告成功结果。

## 12. 推荐阅读与动态更新入口

基础阅读：

- Hu et al., LoRA: Low-Rank Adaptation of Large Language Models.
- Kolda and Bader, Tensor Decompositions and Applications.
- Oseledets, Tensor-Train Decomposition.
- Novikov et al., Tensorizing Neural Networks.

近期阅读：

- Hayou et al., LoRA+: Efficient Low Rank Adaptation of Large Models, arXiv:2402.12354, https://arxiv.org/abs/2402.12354
- Liu et al., DoRA: Weight-Decomposed Low-Rank Adaptation, arXiv:2402.09353, https://arxiv.org/abs/2402.09353
- Zhao et al., GaLore: Memory-Efficient LLM Training by Gradient Low-Rank Projection, arXiv:2403.03507, https://arxiv.org/abs/2403.03507
- Meng et al., PiSSA: Principal Singular Values and Singular Vectors Adaptation of Large Language Models, arXiv:2404.02948, https://arxiv.org/abs/2404.02948
- Wang et al., LoRTA: Low Rank Tensor Adaptation of Large Language Models, arXiv:2402.11417, https://arxiv.org/abs/2402.11417
- Xu et al., QA-BLoRA: Quantization-Aware Blockwise Low-Rank Adaptation of Large Language Models, arXiv:2404.03665, https://arxiv.org/abs/2404.03665

动态阅读入口：

- arXiv: https://arxiv.org
- Papers with Code: https://paperswithcode.com
- Hugging Face PEFT: https://github.com/huggingface/peft
- Microsoft LoRA: https://github.com/microsoft/LoRA

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 PEFT、low-rank adaptation、tensor decomposition、quantization-aware adaptation 相关论文，并更新“近期阅读”和“前沿方法”两节。
