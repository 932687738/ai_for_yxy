# 第 22 课：扩散模型、Score-based SDE 与 Flow Matching

## 0. 任务标识

任务名称：扩散模型、Score-based SDE 与 Flow Matching

预计学习时长：2 到 2.5 周

前置基础要求：

- 理解概率分布、高斯噪声、KL 散度、ELBO、重参数化。
- 已完成第 17 课，理解变分推断、归一化流和概率生成建模。
- 已完成第 18 课，理解 SDE/ODE 视角下的优化动力学。
- 能用 PyTorch 训练简单 U-Net 或 MLP，并理解时间步 embedding。

本课目标：

```text
从 DDPM 的加噪去噪算法，上升到 SDE、probability flow ODE、score matching 和 flow matching 的统一生成建模框架。
```

你需要建立以下研究直觉：

- 扩散模型学习的是从噪声分布回到数据分布的反向过程。
- Score-based model 学习的是 $\nabla_x \log p_t(x)$，即每个噪声尺度下密度上升最快方向。
- 反向 SDE 和 probability flow ODE 给出采样过程的连续时间解释。
- Flow Matching 不必显式模拟扩散反向过程，而是直接学习连接噪声和数据的速度场。
- 现代图像、视频、音频和 3D 生成模型正在从纯 diffusion 向 diffusion/flow/consistency 混合框架演化。

## 1. 本课阅读方式

建议学习顺序：

```text
DDPM 前向加噪
  -> 反向去噪
  -> 变分目标与噪声预测
  -> Score matching
  -> Score-based SDE
  -> Probability flow ODE
  -> Classifier-free guidance
  -> Flow Matching / Rectified Flow
  -> Consistency / Transition Matching
```

【核心】扩散、score SDE、flow matching 不是互不相关的技巧，它们都在学习一个从简单分布到数据分布的传输过程。

## 2. DDPM 前向过程

### 2.1 逐步加噪

DDPM 定义前向马尔可夫过程：

$$
q(x_t\mid x_{t-1})
=
\mathcal{N}
\left(
x_t;
\sqrt{1-\beta_t}x_{t-1},
\beta_t I
\right)
$$

公式注释：

- $x_0$ 是真实数据样本，例如图像 latent。
- $x_t$ 是第 $t$ 步加噪后的样本。
- $\beta_t$ 是噪声调度，控制每一步加入多少高斯噪声。
- 均值 $\sqrt{1-\beta_t}x_{t-1}$ 表示保留上一时刻的大部分信号。
- 方差 $\beta_t I$ 表示加入各向同性高斯噪声。

理论注释：

前向过程不是要学习的部分，而是人为设计的破坏过程。它把复杂数据分布逐步推向简单高斯分布，使反向生成可以从高斯噪声开始。

### 2.2 闭式采样

定义：

$$
\alpha_t=1-\beta_t,\quad
\bar{\alpha}_t=\prod_{s=1}^{t}\alpha_s
$$

则：

$$
q(x_t\mid x_0)
=
\mathcal{N}
\left(
x_t;
\sqrt{\bar{\alpha}_t}x_0,
(1-\bar{\alpha}_t)I
\right)
$$

等价采样：

$$
x_t
=
\sqrt{\bar{\alpha}_t}x_0
+
\sqrt{1-\bar{\alpha}_t}\epsilon,\quad
\epsilon\sim\mathcal{N}(0,I)
$$

公式注释：

- $\bar{\alpha}_t$ 是从 0 到 $t$ 的累计信号保留比例。
- $1-\bar{\alpha}_t$ 是累计噪声比例。
- 这个闭式公式允许训练时直接从 $x_0$ 跳到任意噪声步 $t$，无需逐步模拟。

理论注释：

DDPM 训练高效的关键之一就是该闭式加噪公式。模型可以随机采样时间步 $t$，学习在任意噪声强度下恢复信号。

## 3. 反向过程与噪声预测

### 3.1 反向去噪分布

生成过程学习：

$$
p_\theta(x_{t-1}\mid x_t)
=
\mathcal{N}
\left(
x_{t-1};
\mu_\theta(x_t,t),
\Sigma_\theta(x_t,t)
\right)
$$

公式注释：

- $p_\theta$ 是神经网络参数化的反向转移分布。
- 输入是带噪样本 $x_t$ 和时间步 $t$。
- 输出均值 $\mu_\theta$ 或等价的噪声预测、数据预测、velocity prediction。
- $\Sigma_\theta$ 可固定或学习。

理论注释：

反向过程本质上是在学习每个噪声尺度下如何把样本往数据流形方向推回去。图像生成中的 U-Net 或 DiT 就是这个去噪网络。

### 3.2 噪声预测目标

常用训练目标：

$$
\mathcal{L}_{\epsilon}
=
\mathbb{E}_{x_0,\epsilon,t}
\left[
\left\|
\epsilon
-
\epsilon_\theta(x_t,t)
\right\|_2^2
\right]
$$

公式注释：

- $\epsilon$ 是真实加入的高斯噪声。
- $\epsilon_\theta(x_t,t)$ 是模型预测噪声。
- 损失要求模型从带噪图像中识别噪声成分。
- 一旦知道噪声，就可以估计干净样本 $x_0$。

理论注释：

噪声预测目标可由变分下界简化而来，也可理解为 denoising score matching。它比直接预测 $x_0$ 在不同噪声尺度下更稳定。

## 4. Score Matching 与 Score-based Model

### 4.1 Score 函数

分布 $p_t(x)$ 的 score 定义为：

$$
s_t(x)
=
\nabla_x \log p_t(x)
$$

公式注释：

- $p_t(x)$ 是第 $t$ 个噪声尺度下的样本分布。
- $\nabla_x$ 表示对输入样本求梯度，而不是对模型参数求梯度。
- score 指向数据密度上升最快的方向。
- 在高噪声区域，score 告诉样本如何向更可能的数据区域移动。

理论注释：

生成模型不一定需要知道归一化密度 $p_t(x)$，只要知道 score，就可以用 Langevin dynamics 或反向 SDE 从噪声采样到数据。

### 4.2 噪声预测与 score 的关系

对 DDPM 闭式加噪：

$$
x_t
=
\sqrt{\bar{\alpha}_t}x_0
+
\sigma_t\epsilon
$$

其中：

$$
\sigma_t=\sqrt{1-\bar{\alpha}_t}
$$

score 近似与噪声预测关系为：

$$
s_t(x_t)
\approx
-
\frac{1}{\sigma_t}
\epsilon_\theta(x_t,t)
$$

公式注释：

- $\sigma_t$ 是噪声标准差。
- 模型预测噪声越准确，就越能估计 score。
- 负号表示去噪方向与噪声方向相反。

理论注释：

这条关系连接了 DDPM 和 score-based generative modeling。看似不同的噪声预测网络，实际在学习每个时间边际分布的 score。

## 5. Score-based SDE

### 5.1 前向 SDE

连续时间扩散可写为：

$$
dx
=
f(x,t)dt
+
g(t)dW_t
$$

公式注释：

- $x$ 是随时间演化的样本。
- $f(x,t)$ 是 drift，控制确定性漂移。
- $g(t)$ 是 diffusion coefficient，控制噪声强度。
- $dW_t$ 是 Brownian motion 增量。

理论注释：

DDPM 是离散时间扩散，SDE 是连续时间极限。不同 SDE 选择对应 VP、VE、sub-VP 等扩散族。

### 5.2 反向 SDE

反向时间 SDE 为：

$$
dx
=
\left[
f(x,t)
-
g(t)^2
\nabla_x \log p_t(x)
\right]dt
+
g(t)d\bar{W}_t
$$

公式注释：

- $\nabla_x\log p_t(x)$ 是 score。
- $d\bar{W}_t$ 是反向时间 Brownian motion。
- $-g(t)^2\nabla_x\log p_t(x)$ 修正漂移，使过程从噪声回到数据。

理论注释：

反向 SDE 是 score-based 生成的核心定理：只要学会所有时间的 score，就可以从先验噪声分布反向采样生成数据。

## 6. Probability Flow ODE

与反向 SDE 共享同样边际分布的 ODE 为：

$$
dx
=
\left[
f(x,t)
-
\frac{1}{2}g(t)^2
\nabla_x \log p_t(x)
\right]dt
$$

公式注释：

- 该方程没有随机噪声项。
- drift 中 score 系数为反向 SDE 的一半。
- 采样轨迹确定，给定初始噪声后输出确定。

理论注释：

Probability flow ODE 让扩散模型可以使用 ODE solver 采样，并支持精确 likelihood 估计。DDIM、DPM-Solver、flow matching 与 rectified flow 都与 ODE 采样思想密切相关。

## 7. Classifier-free Guidance

CFG 使用条件和无条件预测组合：

$$
\epsilon_{\text{cfg}}
=
\epsilon_\theta(x_t,t,\emptyset)
+
w
\left(
\epsilon_\theta(x_t,t,c)
-
\epsilon_\theta(x_t,t,\emptyset)
\right)
$$

公式注释：

- $c$ 是文本、类别或其他条件。
- $\emptyset$ 表示无条件输入。
- $w$ 是 guidance scale。
- 第二项增强条件方向，使生成更符合提示词。

理论注释：

CFG 提升条件一致性，但过大 $w$ 会降低多样性、引入过饱和或失真。它体现了生成质量、多样性和条件遵循之间的权衡。

## 8. Flow Matching 与 Rectified Flow

### 8.1 速度场学习

Flow Matching 直接学习 ODE：

$$
\frac{dx_t}{dt}
=
v_\theta(x_t,t)
$$

将噪声 $x_0\sim p_0$ 传输到数据 $x_1\sim p_{\text{data}}$。

公式注释：

- $v_\theta$ 是神经网络预测的速度场。
- $t\in[0,1]$ 是连续时间。
- 采样时从噪声初值积分 ODE 到 $t=1$。

理论注释：

Flow Matching 不需要模拟扩散反向链，也不需要显式 score。它把生成建模看成学习概率路径上的速度场。

### 8.2 线性插值路径

常见路径：

$$
x_t
=
(1-t)x_0+tx_1
$$

目标速度：

$$
u_t
=
x_1-x_0
$$

训练目标：

$$
\mathcal{L}_{\text{FM}}
=
\mathbb{E}
\left[
\|v_\theta(x_t,t)-u_t\|_2^2
\right]
$$

公式注释：

- $x_0$ 是噪声样本。
- $x_1$ 是数据样本。
- $x_t$ 是二者之间的插值点。
- $u_t$ 是从噪声指向数据的真实速度。
- 模型学习在任意中间点应该朝哪个方向移动。

理论注释：

Rectified Flow 追求更直的生成轨迹，从而减少 ODE 采样步数。2024-2025 年研究进一步指出，直线性、匹配对构造、重训练和 consistency 约束共同影响效果。

## 9. 前沿研究进展：2024-2026 视角

### 9.1 Flow Matching 成为统一教学框架

MIT 2025/2026 Flow Matching and Diffusion Models 课程将 ODE、SDE、score、flow matching、CFG 和现代图像/视频模型放入统一框架。

研究意义：

- 扩散与流模型边界正在变模糊。
- 研究重点从单一采样公式转向概率路径和向量场设计。

### 9.2 Consistency Flow Matching 与少步生成

2024 年 Consistency Flow Matching 显式约束速度场自一致性，目标是在保持质量的同时提升训练和采样效率。

研究意义：

- 少步甚至一步生成是扩散模型落地的关键。
- consistency 约束让模型学习更稳定的全局流，而不是只拟合局部速度。

### 9.3 Transition Matching

2025 年 Transition Matching 提出离散时间、连续状态的统一生成范式，试图同时覆盖 diffusion、flow 和 continuous autoregressive generation。

研究意义：

- 生成模型正在从“扩散 vs 流 vs 自回归”的分类，转向统一转移算子视角。
- 文生图、视频和连续域自回归可能共享同一数学框架。

## 10. 代码实验一：最小 DDPM 噪声预测

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

def q_sample(x0, t, alpha_bar):
    noise = torch.randn_like(x0)
    a = alpha_bar[t].view(-1, *([1] * (x0.ndim - 1)))
    xt = a.sqrt() * x0 + (1 - a).sqrt() * noise
    return xt, noise

def diffusion_loss(model, x0, t, alpha_bar):
    xt, noise = q_sample(x0, t, alpha_bar)
    pred = model(xt, t)
    return F.mse_loss(pred, noise)
```

实验要求：

- 在二维 toy data 上训练 MLP 去噪网络。
- 可视化不同 $t$ 下的带噪样本。
- 比较线性 beta schedule 和 cosine schedule。

## 11. 代码实验二：Flow Matching Toy Model

```python
def flow_matching_loss(model, x0_noise, x1_data):
    batch = x0_noise.shape[0]
    t = torch.rand(batch, 1, device=x0_noise.device)
    xt = (1 - t) * x0_noise + t * x1_data
    target_v = x1_data - x0_noise
    pred_v = model(xt, t)
    return F.mse_loss(pred_v, target_v)
```

实验要求：

- 用 two moons 数据训练 flow matching。
- 从高斯噪声积分 ODE 生成样本。
- 比较不同 ODE step 数下样本质量。

## 12. MCP 调用点设计

### 12.1 MCP 调用点 A：最新生成模型论文检索

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(diffusion OR \"score-based\" OR \"flow matching\" OR \"rectified flow\" OR \"consistency model\") AND (generative OR video OR image)",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 区分论文改进的是概率路径、速度场、score 网络、采样器、蒸馏还是架构。
- 记录采样步数、FID、训练成本和模型规模。
- 判断方法是否适合图像、视频、音频、3D 或分子生成。

### 12.2 MCP 调用点 B：代码库检索

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "diffusion flow matching rectified flow score SDE PyTorch",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

预期学习收获：

- 对比 DDPM、DDIM、DPM-Solver、flow matching 的实现差异。
- 学习时间 embedding、noise schedule、CFG 和 ODE solver。

## 13. 课后研究课题

### 课题 1：DDPM 与 Flow Matching 在二维数据上的对比

要求：

- 使用同一 MLP 架构。
- 训练 DDPM 和 Flow Matching。
- 比较训练稳定性、采样步数和样本质量。

### 课题 2：CFG scale 的质量-多样性权衡

要求：

- 使用一个小型条件扩散模型。
- 改变 guidance scale。
- 记录条件准确率、多样性和样本失真。

### 课题 3：阅读 Rectified Flow 或 Transition Matching

要求：

- 提取论文中的概率路径定义。
- 说明其与 DDPM、score SDE 的差异。
- 分析它是否真正降低采样成本。

## 14. 推荐阅读与动态更新入口

基础阅读：

- Ho et al., Denoising Diffusion Probabilistic Models.
- Song et al., Score-Based Generative Modeling through Stochastic Differential Equations.
- Song et al., Denoising Diffusion Implicit Models.
- Lipman et al., Flow Matching for Generative Modeling.
- Liu et al., Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow.

近期阅读：

- An Introduction to Flow Matching and Diffusion Models, https://arxiv.org/abs/2506.02070
- Flow Matching and Diffusion Models 2026, https://diffusion.csail.mit.edu/2026/
- Consistency Flow Matching, https://arxiv.org/abs/2407.02398
- Rectified Diffusion, https://arxiv.org/abs/2410.07303
- Transition Matching, https://openreview.net/forum?id=An0ePypuOJ
- Diffusion Bridge or Flow Matching?, https://arxiv.org/abs/2509.24531

动态阅读入口：

- MIT diffusion course: https://diffusion.csail.mit.edu
- Papers with Code diffusion models: https://paperswithcode.com/methods/category/diffusion-models
- arXiv: https://arxiv.org

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 diffusion、score SDE、flow matching、rectified flow、consistency model 相关论文。
