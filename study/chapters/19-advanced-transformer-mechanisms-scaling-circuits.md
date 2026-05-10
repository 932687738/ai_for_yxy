# 第 19 课：Transformer 深层机理：注意力信息瓶颈、缩放定律与电路理论

## 0. 任务标识

任务名称：Transformer 深层机理：注意力信息瓶颈、缩放定律与电路理论

预计学习时长：2 到 2.5 周

前置基础要求：

- 理解 Transformer、Self-Attention、残差连接、LayerNorm、MLP、位置编码。
- 已完成第 15 课，理解谱、Jacobian、Hessian 和线性化分析。
- 已完成第 18 课，理解大规模优化、训练动力学和 scaling law 的优化背景。
- 能读懂 attention 权重、activation patching 和简单 PyTorch hook。

本课目标：

```text
从“Transformer 是注意力模型”上升到“Transformer 是由残差流、注意力头、MLP 特征和可组合电路构成的高维计算系统”。
```

你需要建立以下研究直觉：

- 残差流是 Transformer 内部信息传递的主干通道。
- 注意力头可拆分为 QK 电路和 OV 电路：一个决定看哪里，一个决定写什么。
- MLP 不只是非线性层，而是特征读取、特征写入和记忆展开的重要模块。
- scaling law 描述能力随参数、数据和计算量变化的统计规律，但不直接解释具体能力如何在电路中形成。
- 机制可解释性试图把模型行为分解为可验证、可干预的计算子图。

## 1. 本课阅读方式

建议学习顺序：

```text
残差流视角
  -> 单头注意力的 QK/OV 分解
  -> 多头注意力与 superposition
  -> MLP 特征与稀疏表示
  -> 归纳头和复制电路
  -> 信息瓶颈与注意力压缩
  -> scaling law
  -> 自动电路发现与 attribution patching
```

【核心】Transformer 的研究不能停留在“attention 权重可视化”。真正的机制分析要回答：哪个组件在什么输入上通过什么路径写入了什么信息，并且删除或替换它会不会改变输出。

## 2. 残差流：Transformer 的通信总线

### 2.1 残差更新形式

第 $l$ 层 Transformer 可抽象为：

$$
x_{l+1}
=
x_l
+
\mathrm{Attn}_l(\mathrm{LN}(x_l))
+
\mathrm{MLP}_l(\mathrm{LN}(x_l+\mathrm{Attn}_l(\mathrm{LN}(x_l))))
$$

公式注释：

- $x_l$ 是第 $l$ 层残差流状态，形状通常为 $[T,d_{\text{model}}]$。
- $T$ 是序列长度，$d_{\text{model}}$ 是隐藏维度。
- $\mathrm{Attn}_l$ 是第 $l$ 层多头注意力。
- $\mathrm{MLP}_l$ 是前馈网络。
- $\mathrm{LN}$ 是 LayerNorm，控制激活尺度。
- 加号表示每个模块不是替换状态，而是向残差流写入增量。

理论注释：

残差流视角非常重要。每个 attention head 和 MLP block 都像一个读写模块：从残差流读取信息，计算后把结果写回残差流。机制可解释性通常沿着残差流追踪信息如何被写入、保留、组合和读出。

### 2.2 Logit lens

输出 logits 可写为：

$$
\mathrm{logits}
=
x_L W_U
$$

也可对中间层残差流做投影：

$$
\mathrm{logits}_l
=
x_l W_U
$$

公式注释：

- $W_U$ 是 unembedding 矩阵，把隐藏状态映射到词表 logits。
- $x_L$ 是最后一层残差流。
- $x_lW_U$ 用同一个输出头读取中间层表示。
- 如果某个中间层已经强烈支持正确 token，说明答案相关信息较早写入残差流。

理论注释：

Logit lens 是粗粒度工具。它假设中间层表示和最终层表示处于相同可读空间，但 LayerNorm、非线性和后续层会改变语义。因此它适合探索，不足以单独证明机制。

## 3. 单头注意力的 QK/OV 电路分解

### 3.1 Attention 公式

对单个注意力头：

$$
Q=XW_Q,\quad
K=XW_K,\quad
V=XW_V
$$

$$
A=\mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_h}}\right)
$$

$$
O=AVW_O
$$

公式注释：

- $X\in\mathbb{R}^{T\times d_{\text{model}}}$ 是输入残差流。
- $W_Q,W_K,W_V$ 是 query、key、value 投影矩阵。
- $d_h$ 是单头维度。
- $A\in\mathbb{R}^{T\times T}$ 是注意力模式，表示每个位置看哪些位置。
- $W_O$ 把头输出写回残差流。

理论注释：

注意力头可以拆成两个相对独立的计算：

```text
QK 电路：决定从哪里读取。
OV 电路：决定读取后写入什么。
```

仅看 attention pattern 只能看到 QK 部分，无法知道 value 信息被写成了什么方向。因此“attention 权重高”不等于“该 token 对输出贡献大”。

### 3.2 QK 电路

注意力 score 为：

$$
S_{ij}
=
\frac{(x_iW_Q)(x_jW_K)^\top}{\sqrt{d_h}}
=
\frac{x_i W_Q W_K^\top x_j^\top}{\sqrt{d_h}}
$$

公式注释：

- $S_{ij}$ 是位置 $i$ 对位置 $j$ 的注意力打分。
- $x_i$ 是当前位置表示。
- $x_j$ 是被查看位置表示。
- $W_QW_K^\top$ 是 QK 矩阵，决定什么类型的 query 会匹配什么类型的 key。
- 除以 $\sqrt{d_h}$ 是缩放，防止维度变大时 dot product 过大导致 softmax 饱和。

理论注释：

QK 电路学习的是“寻址规则”。例如 induction head 的 QK 部分会学习：如果当前 token 与前文某 token 相同，就去看该 token 后面的下一个位置。

### 3.3 OV 电路

若某个位置 $j$ 被 attend，写入方向近似由：

$$
x_j W_V W_O
$$

决定。

公式注释：

- $W_VW_O$ 是 OV 矩阵。
- $W_V$ 从被查看 token 中提取 value 信息。
- $W_O$ 将该信息写回残差流。
- 这个写入方向最终可能通过 unembedding 增加某些 token 的 logits。

理论注释：

OV 电路学习的是“写入语义”。复制头的 OV 电路可能把被 attend token 的身份写入残差流；语法头可能写入实体、数、位置或依存关系相关方向。

## 4. 信息瓶颈与注意力压缩

### 4.1 信息瓶颈目标

信息瓶颈经典形式为：

$$
\min_{p(z\mid x)}
I(X;Z)-\beta I(Z;Y)
$$

公式注释：

- $X$ 是输入。
- $Y$ 是任务标签或预测目标。
- $Z$ 是压缩表示。
- $I(X;Z)$ 衡量表示保留了多少输入信息。
- $I(Z;Y)$ 衡量表示保留了多少任务相关信息。
- $\beta$ 控制压缩与预测之间的权衡。

理论注释：

在 Transformer 中，注意力本身可看作选择性信息路由。每个 token 无法无限制地保留所有上下文细节，模型必须在残差维度、注意力模式和 MLP 特征中压缩任务相关信息。长上下文模型尤其明显：注意力预算和 KV cache 成本迫使模型学习信息选择。

### 4.2 Attention entropy

一个头在位置 $i$ 的注意力熵：

$$
H_i
=
-
\sum_{j=1}^{T}
A_{ij}\log A_{ij}
$$

公式注释：

- $A_{ij}$ 是位置 $i$ 对位置 $j$ 的注意力权重。
- $H_i$ 越低，注意力越集中。
- $H_i$ 越高，注意力越分散。
- 平均注意力熵可作为头是否选择性路由信息的粗略指标。

理论注释：

低熵不一定表示头重要，高熵也不一定表示头无用。有些头需要广泛聚合信息，有些头需要精确复制。注意力熵只能作为候选信号，必须结合 ablation、patching 和 logit attribution 验证。

## 5. 归纳头与可组合电路

### 5.1 归纳头任务

给定序列：

```text
A B ... A
```

模型需要预测下一个 token 为：

```text
B
```

归纳头学习的机制是：

```text
当前看到 A -> 找到前文 A -> 关注前文 A 后面的 token B -> 提升 B 的 logit
```

### 5.2 归纳头的两步电路

可以抽象为：

$$
\text{previous-token head}
\to
\text{induction head}
\to
W_U
$$

公式注释：

- previous-token head 把前一个 token 的信息移动到当前位置。
- induction head 用当前 token 匹配过去相同 token，并读取其后继信息。
- $W_U$ 将残差流中的后继 token 方向读出为 logits。

理论注释：

归纳头是 mechanistic interpretability 的经典例子，因为它展示了 Transformer 可以形成跨层可组合算法，而不是只做浅层统计匹配。

## 6. 缩放定律：能力随规模的统计规律

### 6.1 幂律形式

语言模型 loss 常被经验拟合为：

$$
L(N,D,C)
\approx
L_\infty
+
aN^{-\alpha}
+
bD^{-\beta}
+
cC^{-\gamma}
$$

公式注释：

- $N$ 是模型参数量。
- $D$ 是训练 token 数。
- $C$ 是训练计算量。
- $L_\infty$ 是不可约损失。
- $\alpha,\beta,\gamma$ 是缩放指数。
- $a,b,c$ 是数据集和架构相关常数。

理论注释：

缩放定律告诉我们“增加资源平均会带来多少 loss 改善”，但不告诉我们“模型内部形成了哪个算法”。它是宏观统计规律，电路理论是微观机制解释，两者互补。

### 6.2 Compute-optimal 训练

在固定计算预算 $C$ 下，需要在参数量和数据量之间分配：

$$
C \propto ND
$$

公式注释：

- 这是简化估计，实际计算还受序列长度、层数、attention 复杂度和硬件效率影响。
- 如果 $N$ 太大而 $D$ 太小，模型欠训练。
- 如果 $D$ 太大而 $N$ 太小，模型容量不足。

理论注释：

Chinchilla 风格结论说明，很多早期大模型相对参数过大、训练 token 不足。后续 LLM 训练越来越强调数据规模、数据质量和训练计算的匹配。

## 7. 自动电路发现与因果干预

### 7.1 Activation patching

给定 clean 输入和 corrupted 输入，替换某层激活：

$$
x_l^{\text{corr}}
\leftarrow
x_l^{\text{clean}}
$$

观察目标 logit 是否恢复：

$$
\Delta
=
\mathrm{logit}_{\text{target}}^{\text{patched}}
-
\mathrm{logit}_{\text{target}}^{\text{corr}}
$$

公式注释：

- clean 输入是模型能正确回答的样本。
- corrupted 输入破坏关键信息，使模型答错。
- patching 把 clean 的某个内部激活替换到 corrupted 运行中。
- $\Delta$ 衡量该激活对恢复正确行为的因果贡献。

理论注释：

Activation patching 是因果工具，不只是相关性分析。但它依赖实验设计：corruption 是否只破坏目标特征，patch 的粒度是否合适，指标是否能代表目标行为。

### 7.2 Logit attribution

某个组件输出 $h_c$ 对目标 logit 的线性贡献可近似为：

$$
\mathrm{attr}_c
=
h_c^\top
(W_U[:,y^+]-W_U[:,y^-])
$$

公式注释：

- $h_c$ 是组件写入残差流的向量。
- $y^+$ 是正确 token。
- $y^-$ 是对比 token。
- $W_U[:,y^+]-W_U[:,y^-]$ 是 logit difference 方向。
- 内积越大，说明该组件越支持正确 token 相对对比 token。

理论注释：

Logit attribution 利用残差流加性结构，是快速定位候选组件的工具。但非线性后续层会改变贡献，因此仍需 patching 或 ablation 验证。

## 8. 前沿研究进展：2024-2026 视角

### 8.1 自动化电路发现走向大模型

2024-2025 年，机制可解释性从手工分析小模型逐步转向自动电路发现、contextual decomposition、transcoder 和 sparse autoencoder。

研究意义：

- 手工找电路无法扩展到百亿参数模型。
- 自动方法试图把组件、特征和路径组织成可验证子图。
- 关键挑战从“能否找到相关组件”变为“电路是否 faithful、minimal、causal”。

### 8.2 全局层面的模块化电路

2025 年 ICML 的 global-level mechanistic interpretability 研究强调：LLM 行为可能由多个模块化电路组合完成，而不是单个头或单个 neuron 决定。

研究意义：

- 复杂任务需要跨层、跨头、跨 MLP 的协同。
- 电路应从局部组件分析扩展到模块级和任务级。
- 这和软件工程中的调用图类似，但组件是分布式表示而非显式函数。

### 8.3 稀疏权重 Transformer 与可解释性-能力权衡

2025 年关于 weight-sparse transformers 的研究表明，稀疏权重可能提升电路可解释性，但会与模型能力产生权衡；扩大模型规模可能改善能力-可解释性边界。

研究意义：

- 可解释性不只是后处理，也可以通过架构和训练约束影响。
- 稀疏性、模块化、低秩和可解释性之间存在深层联系。
- 未来可解释模型可能需要训练时就引入结构偏置。

## 9. 代码实验一：Attention Head Ablation

```python
import torch

def ablate_head_output(head_outputs, head_index):
    patched = head_outputs.clone()
    patched[:, :, head_index, :] = 0.0
    return patched
```

实验要求：

- 在小型 Transformer 上注册 hook，记录每个 attention head 输出。
- 对单个头置零，观察目标 token logit 变化。
- 找出对复制、括号匹配或简单算法任务最关键的头。

指标：

$$
\Delta \ell
=
\ell_{\text{original}}(y)
-
\ell_{\text{ablated}}(y)
$$

公式注释：

- $\ell_{\text{original}}(y)$ 是原模型对正确 token 的 logit。
- $\ell_{\text{ablated}}(y)$ 是删除某个头后的 logit。
- $\Delta \ell$ 越大，该头对正确输出越重要。

## 10. 代码实验二：Attention Entropy

```python
def attention_entropy(attn):
    # attn: [batch, heads, query_pos, key_pos]
    eps = 1e-12
    return -(attn * (attn + eps).log()).sum(dim=-1)
```

实验要求：

- 比较不同层、不同头的平均 attention entropy。
- 找出低熵头，并检查它是否对应复制、定位或特殊 token。
- 结合 ablation 判断低熵头是否真的重要。

## 11. MCP 调用点设计

### 11.1 MCP 调用点 A：最新机制可解释性论文检索

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(\"mechanistic interpretability\" OR \"transformer circuits\" OR \"circuit discovery\" OR \"scaling laws\") AND (Transformer OR LLM)",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 区分 attribution、patching、SAE、transcoder、自动电路发现和理论 scaling law。
- 提取论文中的因果验证方法。
- 判断电路发现是否只做相关性，还是做了干预验证。

### 11.2 MCP 调用点 B：代码库检索

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "TransformerLens mechanistic interpretability activation patching sparse autoencoder transformer circuits",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

预期学习收获：

- 学习 hook residual stream、attention pattern、head output。
- 复现 induction head 和 activation patching 实验。
- 对比手工电路分析和自动电路发现工具。

## 12. 课后研究课题

### 课题 1：复现归纳头

要求：

- 构造重复 token 序列任务。
- 训练或加载小型 Transformer。
- 分析哪些头关注前文相同 token 后的位置。
- 用 ablation 验证该头对预测下一个 token 的贡献。

### 课题 2：Logit lens 与 activation patching 对比

要求：

- 选择一个简单问答或复制任务。
- 用 logit lens 找出答案出现的层。
- 用 activation patching 验证关键层和关键头。

开放问题：

- Logit lens 定位和 patching 定位是否一致？
- 哪些情况下 logit lens 会误导？

### 课题 3：小模型 scaling law 实验

要求：

- 训练 3 到 5 个不同宽度或层数的小 Transformer。
- 固定数据分布，记录 loss 与参数量。
- 拟合幂律指数。

开放问题：

- 小模型实验是否呈现稳定 scaling law？
- 数据质量变化是否改变缩放指数？

## 13. 推荐阅读与动态更新入口

基础阅读：

- Vaswani et al., Attention Is All You Need.
- Kaplan et al., Scaling Laws for Neural Language Models.
- Hoffmann et al., Training Compute-Optimal Large Language Models.
- Elhage et al., A Mathematical Framework for Transformer Circuits.
- Olsson et al., In-context Learning and Induction Heads.

近期阅读：

- Mechanistically Interpreting a Transformer-based 2-SAT Solver: An Axiomatic Approach, https://arxiv.org/abs/2407.13594
- Towards Global-level Mechanistic Interpretability: A Perspective of Modular Circuits of Large Language Models, https://proceedings.mlr.press/v267/he25x.html
- Weight-sparse transformers have interpretable circuits, https://arxiv.org/abs/2511.13653
- Unifying Learning Dynamics and Generalization in Transformers Scaling Law, https://arxiv.org/abs/2512.22088
- TransformerLens: https://github.com/TransformerLensOrg/TransformerLens

动态阅读入口：

- Transformer Circuits Thread: https://transformer-circuits.pub
- Neel Nanda mechanistic interpretability resources: https://www.neelnanda.io/mechanistic-interpretability
- OpenReview: https://openreview.net
- arXiv: https://arxiv.org

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 mechanistic interpretability、transformer circuits、scaling laws、automatic circuit discovery 相关论文。
