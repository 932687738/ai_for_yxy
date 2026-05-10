# 第 17 课：变分推断、归一化流与贝叶斯深度学习

## 0. 任务标识

任务名称：变分推断、归一化流与贝叶斯深度学习

预计学习时长：2 周

前置基础要求：

- 理解概率、条件概率、贝叶斯公式、最大似然估计、交叉熵。
- 理解深度神经网络训练、梯度下降、反向传播和重参数化 trick 的基本代码实现。
- 已完成第 15 课和第 16 课，能理解高维参数空间、Hessian、低秩子空间与模型不确定性的关系。

本课目标：

```text
从“神经网络给出一个点预测”上升到“模型应该表达后验分布、预测不确定性和可信度边界”。
```

你需要建立以下研究直觉：

- 贝叶斯学习不是只寻找一个最优参数，而是推断参数后验分布。
- 精确后验通常不可解，变分推断用可优化分布族近似后验。
- ELBO 是“可计算优化目标”，它同时包含数据拟合项和复杂度约束项。
- 归一化流用可逆变换构造复杂分布，是提升变分后验表达能力的重要工具。
- 贝叶斯深度学习关注 epistemic uncertainty 和 aleatoric uncertainty，在医疗、自动驾驶、金融和 LLM 可靠性评估中尤其关键。

## 1. 本课阅读方式

建议学习顺序：

```text
贝叶斯公式
  -> 后验不可解问题
  -> KL 散度与 ELBO
  -> 均值场变分推断
  -> 重参数化梯度
  -> 贝叶斯神经网络
  -> 归一化流
  -> LLM 不确定性与校准
  -> PyTorch 实验
```

【核心】本课不是学习“多输出一个方差”，而是学习如何把模型参数、预测结果和认知不确定性放进同一个概率推断框架。

## 2. 贝叶斯学习：从点估计到后验分布

### 2.1 贝叶斯公式

给定数据 $D=\{(x_i,y_i)\}_{i=1}^N$ 和模型参数 $\theta$，贝叶斯公式为：

$$
p(\theta\mid D)
=
\frac{p(D\mid \theta)p(\theta)}{p(D)}
$$

公式注释：

- $\theta$ 是模型参数。对神经网络来说，它包含所有权重和偏置。
- $D$ 是观测数据集。
- $p(\theta)$ 是先验分布，表示看见数据前对参数的假设。
- $p(D\mid\theta)$ 是似然，表示给定参数后生成数据的概率。
- $p(\theta\mid D)$ 是后验分布，表示看见数据后参数可能取值的分布。
- $p(D)$ 是证据或边际似然，用来归一化后验分布。

理论注释：

- 频率派点估计通常寻找一个最优 $\theta^\star$。
- 贝叶斯推断保留一整个分布 $p(\theta\mid D)$，因此可以表达“模型知道自己不确定”。
- 在大模型中，完整参数后验几乎无法直接表示，但贝叶斯思想仍可用于 LoRA 后验、最后一层后验、ensemble、校准和不确定性估计。

### 2.2 证据项为什么难

证据项为：

$$
p(D)
=
\int p(D\mid\theta)p(\theta)d\theta
$$

公式注释：

- 该积分需要在所有可能参数 $\theta$ 上求和或积分。
- 神经网络参数维度可能达到百万、十亿甚至万亿级。
- 积分区域高维且非凸，后验可能多峰、强相关、长尾。
- 这正是贝叶斯深度学习困难的根源。

理论注释：

如果 $p(D)$ 可精确计算，后验就能精确归一化。但深度网络中该积分不可行，所以需要近似推断：

- MCMC：用采样逼近后验。
- Laplace approximation：用局部高斯近似后验。
- Variational inference：用可优化分布族近似后验。
- Ensemble：用多个模型近似部分后验多样性。

## 3. KL 散度：分布之间的非对称距离

### 3.1 KL 散度定义

两个分布 $q(z)$ 和 $p(z)$ 的 KL 散度为：

$$
\mathrm{KL}(q(z)\|p(z))
=
\int q(z)\log\frac{q(z)}{p(z)}dz
$$

公式注释：

- $z$ 是随机变量，可以是隐变量、参数或潜在表示。
- $q(z)$ 是近似分布。
- $p(z)$ 是目标分布。
- 积分对 $q(z)$ 加权，因此 KL 主要惩罚 $q$ 把概率质量放在 $p$ 很小的地方。
- KL 散度非负，但不是对称距离，通常 $\mathrm{KL}(q\|p)\ne\mathrm{KL}(p\|q)$。

理论注释：

- 最小化 $\mathrm{KL}(q\|p)$ 常称为 reverse KL，倾向 mode-seeking，容易选择目标分布的某个峰。
- 最小化 $\mathrm{KL}(p\|q)$ 常称为 forward KL，倾向 mass-covering，更愿意覆盖多个模式。
- 变分推断常最小化 $\mathrm{KL}(q(\theta)\|p(\theta\mid D))$，这会带来低估不确定性的风险。

## 4. 变分推断与 ELBO

### 4.1 变分推断目标

选择一个可处理的分布族 $q_\phi(\theta)$，用它近似真实后验：

$$
q_\phi(\theta) \approx p(\theta\mid D)
$$

目标是：

$$
\phi^\star
=
\arg\min_\phi
\mathrm{KL}\left(q_\phi(\theta)\|p(\theta\mid D)\right)
$$

公式注释：

- $\phi$ 是变分分布的参数，例如均值和方差。
- $q_\phi(\theta)$ 是我们能采样、能计算密度、能优化的近似后验。
- $p(\theta\mid D)$ 是真实后验，通常不可直接计算。
- 目标表示寻找最接近真实后验的近似分布。

理论注释：

这个目标看起来合理，但不能直接优化，因为 $p(\theta\mid D)$ 包含不可计算的 $p(D)$。ELBO 的作用就是把不可解目标转化为可优化下界。

### 4.2 ELBO 推导

从边际似然开始：

$$
\log p(D)
=
\log \int p(D,\theta)d\theta
$$

引入任意分布 $q_\phi(\theta)$：

$$
\log p(D)
=
\log \int q_\phi(\theta)
\frac{p(D,\theta)}{q_\phi(\theta)}
d\theta
$$

由 Jensen 不等式：

$$
\log p(D)
\ge
\mathbb{E}_{q_\phi(\theta)}
\left[
\log
\frac{p(D,\theta)}{q_\phi(\theta)}
\right]
$$

右侧称为 ELBO：

$$
\mathcal{L}_{\mathrm{ELBO}}(\phi)
=
\mathbb{E}_{q_\phi(\theta)}
[\log p(D\mid\theta)]
-
\mathrm{KL}(q_\phi(\theta)\|p(\theta))
$$

公式注释：

- $\log p(D)$ 是模型证据，直接最大化它可以做贝叶斯模型选择。
- 引入 $q_\phi(\theta)$ 是为了把不可解积分变成对可采样分布的期望。
- Jensen 不等式说明“log 的期望小于等于期望的 log”，因此得到下界。
- 第一项 $\mathbb{E}_{q_\phi}[\log p(D\mid\theta)]$ 是数据拟合项，鼓励后验样本解释数据。
- 第二项 $\mathrm{KL}(q_\phi(\theta)\|p(\theta))$ 是复杂度惩罚，鼓励近似后验不要偏离先验太远。

理论注释：

最大化 ELBO 等价于最小化近似后验和真实后验之间的 KL：

$$
\log p(D)
=
\mathcal{L}_{\mathrm{ELBO}}(\phi)
+
\mathrm{KL}(q_\phi(\theta)\|p(\theta\mid D))
$$

因为左侧与 $\phi$ 无关，最大化 ELBO 会压低后面的 KL 项。

【核心】ELBO 是贝叶斯深度学习中最重要的桥：它把不可计算的后验推断转化为随机梯度优化。

### 4.3 均值场近似

最常见的变分分布是假设参数独立：

$$
q_\phi(\theta)
=
\prod_{j=1}^{d}
q_{\phi_j}(\theta_j)
$$

若每个参数使用高斯：

$$
q_{\phi_j}(\theta_j)
=
\mathcal{N}(\mu_j,\sigma_j^2)
$$

公式注释：

- $d$ 是参数总数。
- $\theta_j$ 是第 $j$ 个参数。
- $\mu_j$ 和 $\sigma_j$ 分别表示该参数后验均值和不确定性。
- 独立性假设让计算变简单，但忽略参数之间的相关性。

理论注释：

- 均值场适合规模较大的模型，因为参数量线性增长。
- 它容易低估后验方差，尤其在参数强相关或后验多峰时。
- 对大模型而言，完整均值场 BNN 仍然昂贵，因此常用于最后一层、Adapter、LoRA 或小模型。

## 5. 重参数化梯度

### 5.1 为什么需要重参数化

如果：

$$
\theta \sim q_\phi(\theta)
$$

我们要优化：

$$
\nabla_\phi
\mathbb{E}_{q_\phi(\theta)}[f(\theta)]
$$

直接对采样操作求梯度困难。重参数化 trick 将随机性移到与 $\phi$ 无关的噪声：

$$
\theta = \mu + \sigma \odot \epsilon,\quad
\epsilon\sim\mathcal{N}(0,I)
$$

公式注释：

- $\mu$ 是变分后验均值。
- $\sigma$ 是标准差，通常通过 $\rho$ 参数化为 $\sigma=\log(1+\exp(\rho))$ 保证为正。
- $\epsilon$ 是标准高斯噪声，不依赖 $\phi$。
- $\odot$ 是逐元素乘法。
- 采样参数 $\theta$ 变成确定性函数 $g_\phi(\epsilon)$，因此可以反向传播。

理论注释：

重参数化降低了梯度估计方差，是 VAE、Bayes by Backprop、连续归一化流训练的基础。离散变量无法直接使用普通重参数化，需要 Gumbel-Softmax、score function estimator 或其他松弛方法。

## 6. 贝叶斯神经网络

### 6.1 权重后验

普通神经网络学习一个权重点估计：

$$
y = f(x;\theta^\star)
$$

贝叶斯神经网络学习权重分布：

$$
\theta \sim q_\phi(\theta),\quad
y = f(x;\theta)
$$

预测分布为：

$$
p(y^\star\mid x^\star,D)
=
\int p(y^\star\mid x^\star,\theta)
p(\theta\mid D)d\theta
$$

用变分后验近似：

$$
p(y^\star\mid x^\star,D)
\approx
\frac{1}{S}
\sum_{s=1}^{S}
p(y^\star\mid x^\star,\theta_s),
\quad
\theta_s\sim q_\phi(\theta)
$$

公式注释：

- $x^\star$ 是测试输入。
- $y^\star$ 是未知标签。
- 积分表示对所有可能参数进行贝叶斯模型平均。
- $\theta_s$ 是从近似后验采样得到的第 $s$ 个权重样本。
- $S$ 是 Monte Carlo 样本数。

理论注释：

贝叶斯模型平均通常比单个点估计更稳健，因为它把参数不确定性传播到预测分布中。代价是推理需要多次采样前向传播，计算成本更高。

### 6.2 不确定性分解

预测不确定性通常分为：

```text
aleatoric uncertainty：数据本身噪声，更多数据也无法完全消除。
epistemic uncertainty：模型认知不足，更多相关数据可以降低。
```

对于分类任务，可用预测熵衡量总不确定性：

$$
H[y\mid x,D]
=
-
\sum_c
p(y=c\mid x,D)
\log p(y=c\mid x,D)
$$

公式注释：

- $c$ 是类别索引。
- $p(y=c\mid x,D)$ 是贝叶斯模型平均后的类别概率。
- 熵越大，说明预测分布越分散，模型越不确定。
- 熵无法单独区分 aleatoric 和 epistemic，需要结合互信息或 ensemble 分歧。

互信息可用于衡量 epistemic uncertainty：

$$
I[y,\theta\mid x,D]
=
H[y\mid x,D]
-
\mathbb{E}_{p(\theta\mid D)}
H[y\mid x,\theta]
$$

公式注释：

- 第一项是整体预测熵。
- 第二项是固定某个模型参数后的平均预测熵。
- 如果不同参数样本给出差异很大，互信息会高，说明模型认知不确定性强。
- 如果每个参数样本都同样不确定，更多是数据噪声或类别本身模糊。

## 7. 归一化流：用可逆变换构造复杂后验

### 7.1 变量变换公式

设基础变量：

$$
z_0\sim p_0(z_0)
$$

通过可逆变换：

$$
z_K = f_K\circ f_{K-1}\circ\cdots\circ f_1(z_0)
$$

则密度满足：

$$
\log p_K(z_K)
=
\log p_0(z_0)
-
\sum_{k=1}^{K}
\log
\left|
\det
\frac{\partial f_k}{\partial z_{k-1}}
\right|
$$

公式注释：

- $z_0$ 是简单基础分布样本，例如标准高斯。
- $f_k$ 是第 $k$ 个可逆变换。
- $z_K$ 是经过多层变换后的复杂样本。
- Jacobian 行列式衡量体积缩放。变换压缩体积会提高密度，扩张体积会降低密度。
- 对数形式便于数值稳定计算。

理论注释：

归一化流的关键要求是：

- 变换可逆。
- Jacobian determinant 可高效计算。
- 采样和密度评估都可行。

这使它适合提升变分后验表达能力，也适合密度估计、生成模型和不确定性建模。

### 7.2 平面流示例

一种简单流为：

$$
f(z)=z+u h(w^\top z+b)
$$

公式注释：

- $z$ 是输入隐变量。
- $u$ 控制变换方向。
- $w^\top z+b$ 是一维投影。
- $h$ 是非线性函数，例如 $\tanh$。
- 该变换在一个方向上弯曲基础分布。

理论注释：

单个平面流表达能力有限，但多个流叠加可以把简单高斯逐步变成复杂多峰或弯曲分布。现代 flow 更常用 coupling layer、autoregressive flow、continuous normalizing flow 等结构。

## 8. 前沿研究进展：2024-2026 视角

### 8.1 贝叶斯 LLM 与不确定性估计

2024-2026 年的重要趋势是把贝叶斯不确定性引入大语言模型可靠性评估：

- 用 Bayesian LoRA 或 Adapter 后验替代全参数后验。
- 用 ensemble、MC dropout、Laplace、SWAG 或最后一层 BNN 估计 epistemic uncertainty。
- 将不确定性用于拒答、风险分级、主动学习和工具调用置信度控制。

研究问题：

```text
LLM 的概率输出并不等价于真实置信度。如何校准模型，让“不确定”真正可用？
```

### 8.2 归一化流与扩散/流匹配的交叉

归一化流强调可逆变换和精确似然，扩散模型强调逐步去噪，flow matching 则把生成过程写成向量场学习。2024-2026 年生成模型研究中，这三类方法正在互相靠近：

- continuous normalizing flow 使用 ODE 描述密度变换。
- score-based model 使用 SDE 描述噪声到数据的反向过程。
- flow matching 直接学习从简单分布到数据分布的速度场。

这为第 22 课“扩散模型、Score-based SDE 与 Flow Matching”打基础。

### 8.3 变分推断进入参数高效微调

与第 16 课连接，近期研究越来越关注：

$$
q_\phi(\Delta W)
$$

而不是：

$$
q_\phi(W)
$$

公式注释：

- $W$ 是全量大模型权重，维度极高。
- $\Delta W$ 是 LoRA、Adapter 或 prefix-tuning 产生的小规模更新。
- 对 $\Delta W$ 做后验推断比对全量 $W$ 做后验推断更现实。

理论注释：

这相当于在低维任务子空间内做贝叶斯推断。它牺牲了完整后验表达能力，但显著降低计算和存储成本，适合真实大模型场景。

## 9. 代码实验一：Bayes by Backprop 线性层

下面实现一个最小贝叶斯线性层，用高斯后验近似权重。

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class BayesianLinear(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.weight_mu = nn.Parameter(torch.empty(out_features, in_features))
        self.weight_rho = nn.Parameter(torch.empty(out_features, in_features))
        self.bias_mu = nn.Parameter(torch.empty(out_features))
        self.bias_rho = nn.Parameter(torch.empty(out_features))
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight_mu, a=math.sqrt(5))
        nn.init.constant_(self.weight_rho, -5.0)
        nn.init.zeros_(self.bias_mu)
        nn.init.constant_(self.bias_rho, -5.0)

    def sample_param(self, mu, rho):
        sigma = F.softplus(rho)
        eps = torch.randn_like(mu)
        return mu + sigma * eps, sigma

    def forward(self, x):
        weight, weight_sigma = self.sample_param(self.weight_mu, self.weight_rho)
        bias, bias_sigma = self.sample_param(self.bias_mu, self.bias_rho)
        out = F.linear(x, weight, bias)
        return out, (weight, weight_sigma, bias, bias_sigma)
```

代码注释：

- `mu` 表示后验均值。
- `rho` 通过 `softplus` 转成正标准差。
- 每次前向传播都会采样一组权重。
- 训练时需要额外加入 KL 项，不能只优化交叉熵。

## 10. 代码实验二：ELBO 损失

设先验为标准高斯：

$$
p(w)=\mathcal{N}(0,1)
$$

近似后验为：

$$
q(w)=\mathcal{N}(\mu,\sigma^2)
$$

两个一维高斯的 KL 为：

$$
\mathrm{KL}(q\|p)
=
\frac{1}{2}
\left(
\mu^2+\sigma^2-\log\sigma^2-1
\right)
$$

公式注释：

- $\mu^2$ 惩罚后验均值偏离先验中心。
- $\sigma^2$ 惩罚后验方差过大。
- $-\log\sigma^2$ 防止方差塌缩到 0。
- 该 KL 项让模型不要用过度确定的参数解释有限数据。

PyTorch 实现：

```python
def gaussian_kl_to_standard_normal(mu, sigma):
    return 0.5 * torch.sum(mu.pow(2) + sigma.pow(2) - torch.log(sigma.pow(2) + 1e-8) - 1.0)

def elbo_loss(logits, targets, kl, num_batches, beta=1.0):
    nll = F.cross_entropy(logits, targets)
    return nll + beta * kl / num_batches
```

实验要求：

- 在二分类 toy dataset 上训练普通 MLP 和 Bayesian MLP。
- 比较测试集 accuracy、NLL、ECE 和预测熵。
- 对分布外输入画出 epistemic uncertainty 热力图。

## 11. 代码实验三：一个最小 RealNVP coupling layer

RealNVP 使用可逆 coupling 结构：

$$
y_a=x_a
$$

$$
y_b=x_b\odot \exp(s(x_a))+t(x_a)
$$

log determinant 为：

$$
\log
\left|
\det
\frac{\partial y}{\partial x}
\right|
=
\sum_j s_j(x_a)
$$

公式注释：

- 输入 $x$ 被分成两部分 $x_a,x_b$。
- $x_a$ 保持不变，用来生成缩放 $s(x_a)$ 和平移 $t(x_a)$。
- $x_b$ 经过仿射变换。
- Jacobian 是三角矩阵，因此 log determinant 只需要求缩放项之和。

代码骨架：

```python
class CouplingLayer(nn.Module):
    def __init__(self, dim, hidden):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim // 2, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, dim)
        )

    def forward(self, x):
        xa, xb = x.chunk(2, dim=-1)
        st = self.net(xa)
        s, t = st.chunk(2, dim=-1)
        s = torch.tanh(s)
        yb = xb * torch.exp(s) + t
        y = torch.cat([xa, yb], dim=-1)
        log_det = s.sum(dim=-1)
        return y, log_det
```

实验要求：

- 用二维 moon dataset 训练 flow 密度模型。
- 可视化基础高斯经过 flow 后的样本分布。
- 分析 coupling layer 为什么能高效计算 determinant。

## 12. MCP 调用点设计

### 12.1 MCP 调用点 A：最新论文检索

调用目的：检索 2024-2026 年关于 Bayesian deep learning、LLM uncertainty、variational inference、normalizing flow 的最新论文。

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(\"Bayesian deep learning\" OR \"variational inference\" OR \"normalizing flow\" OR \"LLM uncertainty\")",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 区分论文是在做后验推断、校准、OOD 检测、生成建模还是理论分析。
- 提取论文中的概率对象：prior、posterior、likelihood、latent variable、flow transform。
- 识别方法是否能扩展到大模型。

### 12.2 MCP 调用点 B：代码库检索

调用目的：查找 PyTorch/Pyro/NumPyro 中可复现的 BNN、VAE、normalizing flow 实现。

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "Bayesian neural network variational inference normalizing flow PyTorch Pyro",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

预期学习收获：

- 学会对照论文公式和概率编程实现。
- 理解手写 ELBO 与 Pyro 自动变分推断的差异。
- 找到不确定性可视化和校准评估代码。

### 12.3 MCP 调用点 C：论文阅读卡片

建议输出字段：

```json
{
  "title": "...",
  "year": 2025,
  "problem": "LLM uncertainty calibration",
  "probabilistic_object": ["posterior", "predictive entropy", "mutual information"],
  "method_type": "variational | ensemble | flow | Laplace | calibration",
  "scalability": "small model | adapter | LoRA | full LLM",
  "main_limitation": "..."
}
```

## 13. 课后研究课题

### 课题 1：BNN 与普通 MLP 的不确定性对比

要求：

- 构造二维分类数据集。
- 训练普通 MLP、MC Dropout MLP、Bayesian MLP。
- 可视化分类边界和预测熵。
- 在分布外区域比较 epistemic uncertainty。

输出：

- 三种方法的 accuracy、NLL、ECE。
- 一张 uncertainty heatmap。
- 一段解释：哪种方法更能表达“没见过的数据”。

### 课题 2：用归一化流增强变分后验

要求：

- 实现一个基础 VAE。
- 将标准高斯后验替换为 flow posterior。
- 对比 ELBO、重构质量和 latent space 分布。

开放问题：

- 更复杂的后验是否一定提升生成质量？
- Flow 的 expressiveness 和训练稳定性之间有什么权衡？

### 课题 3：LLM 答案置信度校准分析

要求：

- 选择一个问答数据集。
- 收集 LLM 输出概率、self-consistency 分歧或多个采样答案。
- 计算 ECE、Brier score、预测熵。
- 分析模型高置信错误样本。

开放问题：

- LLM 的 token probability 是否能代表答案正确概率？
- self-consistency 能否作为 epistemic uncertainty 的近似？
- 哪些问题类型最容易高置信错误？

## 14. 推荐阅读与动态更新入口

基础阅读：

- David MacKay, Information Theory, Inference, and Learning Algorithms.
- Bishop, Pattern Recognition and Machine Learning.
- Blundell et al., Weight Uncertainty in Neural Networks.
- Kingma and Welling, Auto-Encoding Variational Bayes.
- Rezende and Mohamed, Variational Inference with Normalizing Flows.
- Papamakarios et al., Normalizing Flows for Probabilistic Modeling and Inference.

近期阅读方向：

- Bayesian deep learning for large language models.
- Uncertainty estimation and calibration for LLMs.
- Variational inference with expressive posterior families.
- Normalizing flows, continuous flows and flow matching.
- Bayesian PEFT, Bayesian LoRA and uncertainty-aware adapters.

动态阅读入口：

- arXiv: https://arxiv.org
- OpenReview: https://openreview.net
- Pyro: https://pyro.ai
- NumPyro: https://num.pyro.ai
- Papers with Code: https://paperswithcode.com

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 Bayesian deep learning、variational inference、normalizing flow、LLM uncertainty 相关论文，并更新前沿研究进展。
