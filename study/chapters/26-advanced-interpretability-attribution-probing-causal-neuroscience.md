# 第 26 课：可解释性与模型行为分析：归因、探针、因果干预与神经科学连接

## 0. 任务标识

任务名称：可解释性与模型行为分析：归因、探针、因果干预与神经科学连接

预计学习时长：2 周

前置基础要求：

- 理解 Transformer 残差流、attention head、MLP 和 logits。
- 已完成第 19 课，理解 QK/OV 电路、activation patching、logit attribution。
- 已完成第 25 课，理解表示空间、CKA、自监督特征和表示几何。
- 能使用 PyTorch hook 读取中间激活。

本课目标：

```text
从“模型为什么这么答”上升到“用归因、探针、因果干预和表示工程验证模型内部机制”。
```

你需要建立以下研究直觉：

- 可解释性分为事后解释、表示分析、机制解释和可干预控制。
- 相关性解释不足以证明机制，必须做因果干预。
- 探针能发现信息是否存在，但不一定说明模型是否使用该信息。
- Sparse Autoencoder 试图把 polysemantic 神经元分解为更可解释特征。
- Activation steering 说明解释变量也可用于行为控制，但带来安全风险。
- 神经科学与 LLM 可解释性共享“从高维活动中寻找可验证机制”的方法论。

## 1. 本课阅读方式

建议学习顺序：

```text
归因方法
  -> 梯度与集成梯度
  -> 探针与控制任务
  -> causal tracing / activation patching
  -> Sparse Autoencoder
  -> representation engineering
  -> activation steering
  -> 神经科学 decoding / encoding
  -> 安全与评估
```

【核心】可解释性研究的标准不是“解释听起来合理”，而是“解释对应的内部变量被干预后，模型行为按预测改变”。

## 2. 归因方法

### 2.1 梯度归因

对输入 embedding $x$ 和目标 logit $S_c(x)$：

$$
\mathrm{Attr}_i
=
\left|
\frac{\partial S_c(x)}
{\partial x_i}
\right|
$$

公式注释：

- $S_c(x)$ 是类别或 token $c$ 的 logit。
- $x_i$ 是输入第 $i$ 个维度或 token embedding。
- 梯度表示该维度微小变化对目标 logit 的局部影响。

理论注释：

梯度归因是局部线性解释。它计算便宜，但容易受梯度饱和、噪声和输入缩放影响。它说明“如果微小改变会怎样”，不一定说明“模型实际如何计算”。

### 2.2 Integrated Gradients

$$
\mathrm{IG}_i(x)
=
(x_i-x_i')
\int_{\alpha=0}^{1}
\frac{\partial F(x'+\alpha(x-x'))}
{\partial x_i}
d\alpha
$$

公式注释：

- $x'$ 是 baseline 输入。
- $x$ 是真实输入。
- 积分沿 baseline 到输入的路径累计梯度。
- 相比普通梯度，IG 缓解局部梯度不稳定问题。

理论注释：

IG 满足 completeness：所有特征归因之和等于输出差异 $F(x)-F(x')$。但 baseline 选择会显著影响解释，文本模型中的 baseline 尤其困难。

## 3. 探针与控制任务

### 3.1 线性探针

给定隐藏表示 $h$，训练探针：

$$
\hat{y}
=
\mathrm{softmax}(Wh+b)
$$

公式注释：

- $h$ 是某层隐藏状态。
- $W,b$ 是探针参数。
- $\hat{y}$ 是被探测属性，例如词性、实体、真假、情绪。

理论注释：

探针回答的是“表示中是否线性可读出某信息”。它不回答模型在生成时是否使用了该信息。高探针准确率可能来自探针自己学到了任务，而不是模型内部机制。

### 3.2 控制任务

控制任务要求在随机标签或无关标签上训练探针，比较真实任务提升：

$$
\Delta
=
\mathrm{Acc}_{\text{real}}
-
\mathrm{Acc}_{\text{control}}
$$

公式注释：

- $\mathrm{Acc}_{\text{real}}$ 是真实属性探针准确率。
- $\mathrm{Acc}_{\text{control}}$ 是控制标签探针准确率。
- 差值越大，说明表示更可能真的编码目标属性。

理论注释：

控制任务帮助避免过度解释高容量探针。现代 LLM 表示分析更偏向简单线性探针、因果干预和 OOD 验证结合。

## 4. 因果干预：Causal Tracing 与 Activation Patching

### 4.1 Activation patching

对 corrupted run 注入 clean activation：

$$
h_l^{\text{corr}}
\leftarrow
h_l^{\text{clean}}
$$

衡量输出恢复：

$$
\Delta
=
S_{\text{target}}^{\text{patched}}
-
S_{\text{target}}^{\text{corr}}
$$

公式注释：

- clean run 是正确输入运行。
- corrupted run 是破坏关键信息后的运行。
- patching 替换某层、某头或某 token 的激活。
- $\Delta$ 衡量该激活对目标行为的因果贡献。

理论注释：

Activation patching 是机制可解释性的核心工具。它比 attention 可视化更强，因为它直接改变模型内部变量并观察行为变化。

### 4.2 Attribution patching

Attribution patching 用一阶近似估计 patching 效果：

$$
\Delta F
\approx
\nabla_h F^\top
(h^{\text{clean}}-h^{\text{corr}})
$$

公式注释：

- $F$ 是目标指标，例如 logit difference。
- $h$ 是待分析激活。
- 梯度项衡量指标对激活的敏感度。
- 激活差值衡量 clean 和 corrupted 的内部差异。

理论注释：

Attribution patching 比完整 patching 便宜，适合扫描大量组件。但它是一阶近似，遇到强非线性或大扰动时可能不准确。2024 年 AtP* 等工作专门研究其效率和可靠性。

## 5. Sparse Autoencoder 与特征分解

### 5.1 SAE 目标

给定激活 $h$，SAE 学习：

$$
z
=
\sigma(W_{\text{enc}}h+b)
$$

$$
\hat{h}
=
W_{\text{dec}}z
$$

损失：

$$
\mathcal{L}
=
\|h-\hat{h}\|_2^2
+
\lambda\|z\|_1
$$

公式注释：

- $h$ 是模型中间激活。
- $z$ 是稀疏特征表示。
- $\hat{h}$ 是重构激活。
- 重构项保证 SAE 保留原激活信息。
- L1 项鼓励每个样本只激活少数特征。

理论注释：

SAE 的目标是把 polysemantic 神经元分解成更 monosemantic 的特征。它建立在 linear representation hypothesis 上：许多概念可由激活空间中的方向表示。

### 5.2 Feature intervention

若某个 SAE feature $z_j$ 对应概念，可干预：

$$
z_j
\leftarrow
z_j+\alpha
$$

再解码回激活：

$$
h'
=
W_{\text{dec}}z'
$$

公式注释：

- $\alpha$ 是干预强度。
- $z_j$ 是待增强或抑制的特征。
- $h'$ 是修改后的激活。

理论注释：

如果增强特征会按预期改变模型行为，说明该特征具有因果作用。否则它可能只是相关特征或解释标签错误。

## 6. Representation Engineering 与 Activation Steering

### 6.1 Steering vector

给定正负样本激活均值：

$$
v
=
\mathbb{E}[h\mid \text{positive}]
-
\mathbb{E}[h\mid \text{negative}]
$$

推理时干预：

$$
h'
=
h+\alpha v
$$

公式注释：

- $v$ 是行为方向，例如诚实、有害、拒答、情绪。
- $\alpha$ 控制干预强度。
- 干预通常发生在某层残差流。

理论注释：

Activation steering 是一种无需改权重的行为控制方法。它也说明 LLM 内部存在可线性操控的行为方向。但 steering 可能被攻击者用于绕过安全边界，是 2025 年安全研究关注点。

## 7. 神经科学连接

### 7.1 Encoding model

神经科学中 encoding model 预测神经响应：

$$
\hat{r}
=
f_\theta(s)
$$

公式注释：

- $s$ 是刺激，例如图像、文本或声音。
- $r$ 是脑区响应，例如 fMRI、ECoG、spike rate。
- 模型学习刺激到神经活动的映射。

理论注释：

这和 AI 表示分析中的“输入到中间激活”类似。两者都试图解释高维系统如何编码外界信息。

### 7.2 Decoding model

解码模型从神经活动恢复刺激或意图：

$$
\hat{s}
=
g_\phi(r)
$$

理论注释：

脑解码与模型 probing 类似：都从内部活动读出外部变量。但可读出不等于因果使用。神经科学和 AI 可解释性都需要干预实验验证机制。

## 8. 前沿研究进展：2024-2026 视角

### 8.1 SAE 与 CoT 机制分析

2025 年 CoT mechanistic interpretability with sparse autoencoding 将 SAE 和 activation patching 用于分析链式思考，研究 CoT 信息是否真实存在于内部表示。

### 8.2 Activation steering 安全化与攻击化

2025 年 activation steering 同时用于 bias mitigation 和攻击放大。它既是安全工具，也是供应链和白盒模型风险。

### 8.3 Mechanistic data attribution

2026 年 mechanistic data attribution 试图追踪可解释单元来自哪些训练数据，把机制解释连接到数据来源。

### 8.4 神经科学与 AI 可解释性融合

2024 年 neuroscience decoding 综述强调，机制可解释性和神经解码都在从相关读出走向可干预、闭环实验。

## 9. 代码实验一：Integrated Gradients

```python
import torch

def integrated_gradients(model, x, baseline, target_idx, steps=50):
    total_grad = torch.zeros_like(x)
    for alpha in torch.linspace(0, 1, steps, device=x.device):
        x_alpha = baseline + alpha * (x - baseline)
        x_alpha.requires_grad_(True)
        logits = model(x_alpha)
        score = logits[..., target_idx].sum()
        grad = torch.autograd.grad(score, x_alpha)[0]
        total_grad += grad
    return (x - baseline) * total_grad / steps
```

实验要求：

- 对文本分类模型做 token embedding 归因。
- 比较不同 baseline 的解释差异。

## 10. 代码实验二：Activation patching 骨架

```python
def patch_activation(module, clean_cache, name):
    def hook(mod, inp, out):
        return clean_cache[name]
    return module.register_forward_hook(hook)
```

实验要求：

- 构造 clean/corrupted prompt。
- 缓存 clean run 某层激活。
- patch 到 corrupted run。
- 观察目标 logit 是否恢复。

## 11. MCP 调用点设计

### 11.1 MCP 调用点 A：最新可解释性论文检索

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(\"mechanistic interpretability\" OR \"activation patching\" OR \"sparse autoencoder\" OR \"activation steering\" OR \"causal tracing\" OR probing) AND (LLM OR Transformer)",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 区分归因、探针、因果干预、SAE、steering 和数据归因。
- 提取论文是否进行了 causal intervention。

### 11.2 MCP 调用点 B：代码库检索

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "mechanistic interpretability sparse autoencoder activation patching transformer lens steering",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

预期学习收获：

- 学习 TransformerLens、SAELens、Captum、baukit 等工具。
- 复现 patching、SAE feature visualization、activation steering。

## 12. 课后研究课题

### 课题 1：探针是否说明模型使用了信息

要求：

- 对某层表示训练线性探针。
- 再用 activation patching 验证该信息是否影响输出。
- 比较探针准确率和因果贡献。

### 课题 2：SAE feature 解释与干预

要求：

- 使用开源 SAE 或训练小型 SAE。
- 找到一个可解释 feature。
- 增强/抑制该 feature，观察输出变化。

### 课题 3：Activation steering 安全实验

要求：

- 构造 positive/negative 样本得到 steering vector。
- 在不同层和不同强度下干预。
- 分析效果、泛化和副作用。

## 13. 推荐阅读与动态更新入口

基础阅读：

- Sundararajan et al., Axiomatic Attribution for Deep Networks.
- Alain and Bengio, Understanding intermediate layers using linear classifier probes.
- Meng et al., Locating and Editing Factual Associations in GPT.
- Elhage et al., A Mathematical Framework for Transformer Circuits.
- Anthropic, Towards Monosemanticity.
- Representation Engineering: A Top-Down Approach to AI Transparency.

近期阅读：

- AtP*: An efficient and scalable method for localizing LLM behaviour to components, https://arxiv.org/abs/2403.00745
- Scaling and evaluating sparse autoencoders, https://arxiv.org/abs/2406.04093
- How does Chain of Thought Think? Mechanistic Interpretability of Chain-of-Thought Reasoning with Sparse Autoencoding, https://arxiv.org/abs/2507.22928
- Activation Steering for Bias Mitigation, https://arxiv.org/abs/2508.09019
- Steering in the Shadows: Causal Amplification for Activation Space Attacks in Large Language Models, https://arxiv.org/abs/2511.17194
- Mechanistic Data Attribution: Tracing the Training Origins of Interpretable LLM Units, https://arxiv.org/abs/2601.21996
- Decoding the brain: From neural representations to mechanistic models, https://doi.org/10.1016/j.cell.2024.08.051

动态阅读入口：

- TransformerLens: https://github.com/TransformerLensOrg/TransformerLens
- SAELens: https://github.com/jbloomAus/SAELens
- Captum: https://captum.ai
- Transformer Circuits: https://transformer-circuits.pub
- arXiv: https://arxiv.org

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 mechanistic interpretability、SAE、activation patching、activation steering、causal tracing、probing 相关论文。
