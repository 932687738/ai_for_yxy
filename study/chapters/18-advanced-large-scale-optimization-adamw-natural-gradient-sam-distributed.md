# 第 18 课：大规模优化：AdamW、自然梯度、SAM 与分布式优化动力学

## 0. 任务标识

任务名称：大规模优化：AdamW、自然梯度、SAM 与分布式优化动力学

预计学习时长：2 周

前置基础要求：

- 理解梯度下降、动量、学习率、batch size、loss landscape。
- 已完成第 15 课，理解 Hessian、曲率、条件数、sharpness。
- 已完成第 17 课，理解 KL、Fisher 信息和概率分布视角。
- 能读懂 PyTorch optimizer 的 `step()` 实现。

本课目标：

```text
从“调优化器超参数”上升到“理解优化器如何改变参数空间几何、噪声动力学和泛化偏置”。
```

你需要建立以下研究直觉：

- SGD、AdamW、自然梯度、SAM、Muon 不是简单更新公式不同，而是在不同度量下移动参数。
- AdamW 的核心是自适应预条件和解耦权重衰减。
- 自然梯度使用 Fisher 信息矩阵修正参数空间几何。
- SAM 通过优化邻域最坏损失偏向平坦解。
- 分布式训练中的 batch size、梯度同步、通信压缩和延迟会改变优化噪声结构。

## 1. 本课阅读方式

建议学习顺序：

```text
梯度流
  -> 动量与 Adam
  -> AdamW 解耦权重衰减
  -> 预条件与自然梯度
  -> SAM 与 sharpness
  -> Muon / Shampoo / Sophia 等结构化优化器
  -> 分布式优化动力学
  -> PyTorch 实验
```

【核心】优化器不是训练过程的附属组件。对大模型而言，优化器决定显存、吞吐、稳定性、泛化、训练预算和最终能力边界。

## 2. 梯度下降与连续时间梯度流

### 2.1 离散梯度下降

标准梯度下降为：

$$
\theta_{t+1}
=
\theta_t
-
\eta \nabla_\theta \mathcal{L}(\theta_t)
$$

公式注释：

- $\theta_t$ 是第 $t$ 步模型参数。
- $\eta$ 是学习率。
- $\nabla_\theta \mathcal{L}(\theta_t)$ 是当前损失对参数的梯度。
- 更新方向是最陡下降方向，但这是在欧氏几何下成立的。

理论注释：

该公式隐含一个假设：所有参数坐标具有相同尺度和相同几何意义。深度网络中这个假设经常不成立，例如 LayerNorm scale、attention projection、embedding 参数的梯度尺度差异很大。

### 2.2 梯度流

当学习率很小，离散更新可近似为 ODE：

$$
\frac{d\theta(t)}{dt}
=
-
\nabla_\theta \mathcal{L}(\theta(t))
$$

公式注释：

- $\theta(t)$ 是连续时间参数轨迹。
- 左侧是参数随时间变化的速度。
- 右侧是负梯度方向。
- 该方程把训练看成动力系统，便于分析稳定性、收敛速度和噪声扰动。

理论注释：

真实训练是离散、随机、非凸的。梯度流不是精确描述，而是理论近似。它适合解释学习率较小、batch 较大时的平均运动；当学习率大或 batch noise 强时，需要随机微分方程视角。

## 3. 动量、Adam 与 AdamW

### 3.1 动量法

动量更新为：

$$
m_t
=
\beta m_{t-1}
+
(1-\beta)g_t
$$

$$
\theta_{t+1}
=
\theta_t-\eta m_t
$$

其中：

$$
g_t=\nabla_\theta \mathcal{L}(\theta_t)
$$

公式注释：

- $g_t$ 是当前 mini-batch 梯度。
- $m_t$ 是梯度的一阶指数滑动平均。
- $\beta$ 控制历史梯度保留程度，常见值为 0.9。
- 动量会增强持续一致的方向，削弱来回震荡的方向。

理论注释：

在狭长谷地中，普通梯度下降会横向震荡、纵向缓慢前进。动量通过累积历史方向加速低曲率方向的运动，但过大动量也可能越过稳定区域。

### 3.2 Adam

Adam 同时估计一阶矩和二阶矩：

$$
m_t=\beta_1m_{t-1}+(1-\beta_1)g_t
$$

$$
v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2
$$

偏差修正：

$$
\hat{m}_t=\frac{m_t}{1-\beta_1^t},\quad
\hat{v}_t=\frac{v_t}{1-\beta_2^t}
$$

更新：

$$
\theta_{t+1}
=
\theta_t
-
\eta
\frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\epsilon}
$$

公式注释：

- $m_t$ 是梯度方向的平滑估计。
- $v_t$ 是梯度平方的平滑估计，近似每个坐标的尺度。
- $\hat{m}_t,\hat{v}_t$ 修正初始阶段滑动平均偏向 0 的问题。
- 分母 $\sqrt{\hat{v}_t}+\epsilon$ 让梯度大的坐标步长变小，梯度小的坐标步长变大。
- 所有运算是逐坐标的，因此 Adam 是对角预条件方法。

理论注释：

Adam 的优势是对梯度尺度不敏感，适合稀疏梯度和大模型训练。风险是逐坐标自适应可能改变隐式正则化，使泛化行为不同于 SGD。

### 3.3 AdamW

传统 Adam 中的 L2 正则会混入自适应梯度缩放。AdamW 将权重衰减解耦：

$$
\theta_{t+1}
=
\theta_t
-
\eta
\frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\epsilon}
-
\eta\lambda\theta_t
$$

公式注释：

- 前半部分是 Adam 的自适应梯度更新。
- $-\eta\lambda\theta_t$ 是独立的权重衰减项。
- $\lambda$ 是 weight decay 系数。
- 解耦后，权重衰减不再被 $\sqrt{\hat{v}_t}$ 按坐标扭曲。

理论注释：

AdamW 是现代 Transformer 和 LLM 训练的默认基线之一。它的成功不是因为它“更贝叶斯”或“更二阶”，而是因为它在高维非平稳训练中足够稳健，并且权重衰减行为更可控。

## 4. 预条件与自然梯度

### 4.1 预条件梯度下降

一般预条件更新写成：

$$
\theta_{t+1}
=
\theta_t
-
\eta P_t^{-1}g_t
$$

公式注释：

- $P_t$ 是预条件矩阵。
- $P_t^{-1}g_t$ 是被重新缩放和旋转后的梯度。
- 如果 $P_t=I$，退化为普通梯度下降。
- 如果 $P_t$ 近似 Hessian，则接近 Newton 方法。

理论注释：

预条件的目标是改善条件数。好的预条件器会把狭长谷地变得更圆，使不同曲率方向以更接近的速度收敛。问题是完整矩阵 $P_t$ 太大，必须使用对角、块对角、Kronecker 或低秩近似。

### 4.2 自然梯度

自然梯度使用 Fisher 信息矩阵：

$$
F(\theta)
=
\mathbb{E}_{x,y\sim p_\theta}
\left[
\nabla_\theta \log p_\theta(y\mid x)
\nabla_\theta \log p_\theta(y\mid x)^\top
\right]
$$

自然梯度更新：

$$
\theta_{t+1}
=
\theta_t
-
\eta F(\theta_t)^{-1}
\nabla_\theta\mathcal{L}(\theta_t)
$$

公式注释：

- $F(\theta)$ 衡量模型输出分布对参数变化的敏感程度。
- 如果某个参数方向对输出分布影响很大，Fisher 对应方向数值大，更新会被压小。
- 如果某个方向对输出影响小，更新可以更大。
- 自然梯度不是在欧氏距离下走最陡下降，而是在分布空间 KL 几何下走最陡下降。

理论注释：

自然梯度具有重参数化不变性：如果两个参数化表示同一个概率模型，自然梯度方向在分布空间中一致。大模型中完整 Fisher 不可逆也不可存储，因此 K-FAC、Shampoo、AdaFactor、Sophia 等方法都可看作不同形式的可扩展近似。

## 5. Sharpness-Aware Minimization

### 5.1 SAM 目标

SAM 优化邻域最坏损失：

$$
\min_\theta
\max_{\|\epsilon\|_2\le\rho}
\mathcal{L}(\theta+\epsilon)
$$

公式注释：

- $\epsilon$ 是参数扰动。
- $\rho$ 是扰动半径。
- 内层最大化寻找当前参数附近最坏方向。
- 外层最小化让模型偏向邻域内都低损失的平坦区域。

理论注释：

SAM 的直觉来自泛化：如果参数稍微扰动就损失暴涨，说明解依赖精细调参，泛化可能较差。平坦解对量化、低精度训练、分布偏移也更稳健。

### 5.2 一阶近似扰动

内层最坏扰动可用一阶近似：

$$
\epsilon^\star
\approx
\rho
\frac{\nabla_\theta\mathcal{L}(\theta)}
{\|\nabla_\theta\mathcal{L}(\theta)\|_2}
$$

公式注释：

- 梯度方向是一阶近似下损失增长最快的方向。
- 归一化让扰动长度等于 $\rho$。
- 实际 SAM 通常先计算梯度，扰动参数，再在扰动点计算用于更新的梯度。

理论注释：

SAM 计算成本约为普通训练的两次 forward/backward。大规模分布式训练中，这个额外成本和同步依赖很重，因此 2024-2025 年出现了异步 SAM、低成本 SAM 和 late-phase SAM 等变体。

## 6. 结构化优化器：Shampoo、Sophia 与 Muon

### 6.1 Shampoo 的矩阵预条件

对矩阵参数 $W\in\mathbb{R}^{m\times n}$ 和梯度 $G_t$，Shampoo 维护左右二阶统计：

$$
L_t=\sum_{\tau=1}^{t}G_\tau G_\tau^\top,\quad
R_t=\sum_{\tau=1}^{t}G_\tau^\top G_\tau
$$

更新近似为：

$$
W_{t+1}
=
W_t
-
\eta
L_t^{-1/4}
G_t
R_t^{-1/4}
$$

公式注释：

- $L_t$ 捕捉输出维度上的梯度相关性。
- $R_t$ 捕捉输入维度上的梯度相关性。
- 左右预条件比 Adam 的逐元素缩放更能利用矩阵结构。
- $-1/4$ 幂来自 Kronecker 分解下对完整二阶预条件的近似。

理论注释：

Shampoo 更接近矩阵几何，但矩阵开方和逆开方代价高。实际大模型训练需要块化、低频更新、近似 eigendecomposition 或 Adam 稳定化。

### 6.2 Sophia 的轻量二阶思想

Sophia 使用对角 Hessian 或 Gauss-Newton 估计作为预条件，并对更新做 clipping：

$$
\Delta\theta_t
=
\operatorname{clip}
\left(
\frac{m_t}{\hat{h}_t+\epsilon},
c
\right)
$$

公式注释：

- $m_t$ 是一阶动量。
- $\hat{h}_t$ 是轻量二阶曲率估计。
- $c$ 是裁剪阈值，防止二阶估计不稳定导致过大更新。
- 该方法试图在 AdamW 和完整二阶方法之间取折中。

理论注释：

Sophia 的核心问题是如何低成本估计曲率。它适合解释一个重要趋势：LLM 优化器正在从纯逐坐标一阶方法，转向轻量曲率和结构化预条件。

### 6.3 Muon 的矩阵正交化更新

Muon 对矩阵动量做正交化，简化表示为：

$$
M_t=\beta M_{t-1}+(1-\beta)G_t
$$

$$
U_t\approx \operatorname{orthogonalize}(M_t)
$$

$$
W_{t+1}=W_t-\eta U_t
$$

公式注释：

- $M_t$ 是矩阵参数的动量。
- $\operatorname{orthogonalize}$ 通常通过 Newton-Schulz 迭代近似矩阵极分解中的正交因子。
- $U_t$ 不是逐元素缩放后的梯度，而是谱结构被重整化后的矩阵方向。
- Muon 主要适用于二维权重矩阵，对 bias、embedding、norm 参数通常仍需 AdamW 或其他规则。

理论注释：

Muon 的思想是让更新矩阵在谱上更均衡，避免某些奇异方向支配训练。2025 年“Muon is Scalable for LLM Training”显示矩阵正交化优化器可扩展到 LLM 训练，是 2024-2026 年优化器研究的重要方向。

## 7. 分布式优化动力学

### 7.1 数据并行梯度平均

有 $K$ 个 worker 时，同步数据并行梯度为：

$$
g_t
=
\frac{1}{K}
\sum_{k=1}^{K}
g_t^{(k)}
$$

公式注释：

- $g_t^{(k)}$ 是第 $k$ 个 worker 在本地 mini-batch 上计算的梯度。
- 平均后等价于更大 batch 的梯度估计。
- $K$ 增大通常降低梯度噪声，但也可能削弱 SGD 的隐式正则化。

理论注释：

大 batch 训练并不只是吞吐优化。它改变噪声尺度，可能需要学习率 scaling、warmup、更强正则或 sharpness 控制。训练不稳定时，问题可能来自优化动力学，而不是模型容量不足。

### 7.2 梯度噪声尺度

mini-batch 梯度可写为：

$$
g_B(\theta)
=
\nabla\mathcal{L}(\theta)
+
\xi_B
$$

其中：

$$
\mathbb{E}[\xi_B]=0,\quad
\operatorname{Var}(\xi_B)\propto \frac{1}{B}
$$

公式注释：

- $g_B$ 是 batch size 为 $B$ 的随机梯度。
- $\nabla\mathcal{L}$ 是全数据梯度。
- $\xi_B$ 是采样噪声。
- batch 越大，噪声方差越小。

理论注释：

噪声不是纯坏事。适当噪声可以帮助逃离尖锐极小值或鞍点。大模型训练中的 batch size 选择是在吞吐、稳定性、泛化和硬件效率之间折中。

## 8. 前沿研究进展：2024-2026 视角

### 8.1 Schedule-Free AdamW

2024 年 Schedule-Free AdamW 试图减少对手工学习率 schedule 的依赖，用插值和平均机制替代预先设定的训练步数规划。

研究意义：

- 大规模训练中 schedule 错误会浪费大量算力。
- schedule-free 方法让优化器对训练长度更鲁棒。
- 它改变的是训练轨迹管理，而不是模型结构。

### 8.2 Muon 可扩展到 LLM 训练

2025 年 “Muon is Scalable for LLM Training” 把矩阵正交化优化器推进到大语言模型训练场景。

研究意义：

- AdamW 不再是唯一稳妥默认项。
- 矩阵化优化器利用权重的二维结构，而不是把参数当成无结构向量。
- 优化器设计开始与谱几何、矩阵计算和系统实现深度耦合。

### 8.3 异步与分布式 SAM

2025 年的异步 SAM、LSAM 等工作关注 SAM 在分布式大 batch 训练中的效率瓶颈。

研究意义：

- SAM 的最坏扰动步骤带来额外同步依赖。
- 异步设计试图减少 wall-clock 成本，同时保留 flat minima 偏置。
- 这说明泛化优化方法必须与分布式系统共同设计。

## 9. 代码实验一：从零实现 AdamW

```python
import torch

class MiniAdamW(torch.optim.Optimizer):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.01):
        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self):
        for group in self.param_groups:
            beta1, beta2 = group["betas"]
            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad
                state = self.state[p]
                if len(state) == 0:
                    state["step"] = 0
                    state["m"] = torch.zeros_like(p)
                    state["v"] = torch.zeros_like(p)
                state["step"] += 1
                m, v = state["m"], state["v"]
                m.mul_(beta1).add_(grad, alpha=1 - beta1)
                v.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)
                m_hat = m / (1 - beta1 ** state["step"])
                v_hat = v / (1 - beta2 ** state["step"])
                p.addcdiv_(m_hat, v_hat.sqrt().add(group["eps"]), value=-group["lr"])
                p.add_(p, alpha=-group["lr"] * group["weight_decay"])
```

实验要求：

- 与 `torch.optim.AdamW` 对比 loss 曲线。
- 关闭 bias correction，观察早期训练变化。
- 将解耦 weight decay 改成 L2 正则，比较参数范数。

## 10. 代码实验二：SAM 训练步骤

```python
def sam_step(model, loss_fn, x, y, base_optimizer, rho=0.05):
    logits = model(x)
    loss = loss_fn(logits, y)
    loss.backward()

    grad_norm = torch.norm(torch.stack([
        p.grad.norm() for p in model.parameters() if p.grad is not None
    ]))

    eps_list = []
    with torch.no_grad():
        for p in model.parameters():
            if p.grad is None:
                eps_list.append(None)
                continue
            eps = rho * p.grad / (grad_norm + 1e-12)
            p.add_(eps)
            eps_list.append(eps)

    base_optimizer.zero_grad()
    loss_perturbed = loss_fn(model(x), y)
    loss_perturbed.backward()

    with torch.no_grad():
        for p, eps in zip(model.parameters(), eps_list):
            if eps is not None:
                p.sub_(eps)

    base_optimizer.step()
    base_optimizer.zero_grad()
    return loss.item(), loss_perturbed.item()
```

实验要求：

- 比较 SGD、AdamW、SAM-AdamW 的验证集泛化差距。
- 估计训练后 Hessian top eigenvalue。
- 分析 SAM 是否真的降低 sharpness。

## 11. MCP 调用点设计

### 11.1 MCP 调用点 A：最新优化器论文检索

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(AdamW OR SAM OR Muon OR Shampoo OR Sophia OR \"natural gradient\" OR \"distributed optimization\") AND (LLM OR \"large language model\" OR \"deep learning\")",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 判断新优化器改动的是预条件、动量、曲率估计、schedule、sharpness 还是系统通信。
- 提取内存成本、通信成本、额外 forward/backward 次数。
- 识别实验是否达到 LLM 规模，而不只是小模型验证。

### 11.2 MCP 调用点 B：代码库检索

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "Muon optimizer AdamW SAM Shampoo Sophia PyTorch distributed LLM",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

预期学习收获：

- 对比论文伪代码和真实训练框架实现。
- 学习如何处理不同参数组：matrix weights、embedding、bias、norm。
- 学习分布式场景下 optimizer state sharding。

## 12. 课后研究课题

### 课题 1：AdamW 的解耦权重衰减实验

要求：

- 实现 Adam、AdamW、Adam + L2。
- 在同一模型上比较训练 loss、验证 loss、参数范数。
- 分析解耦 weight decay 对泛化的影响。

### 课题 2：SAM 是否真的降低 sharpness

要求：

- 训练普通 AdamW 和 SAM-AdamW。
- 使用 power iteration 估计 Hessian top eigenvalue。
- 对比验证集性能和 sharpness。

### 课题 3：Muon / Shampoo / AdamW 的矩阵结构比较

要求：

- 阅读 Muon 或 Shampoo 近期论文。
- 对一个小型 Transformer 的二维权重参数单独应用矩阵优化器。
- 记录显存、吞吐、loss 曲线和验证指标。

开放问题：

- 矩阵化优化器是否对所有层都有效？
- 为什么 norm、bias、embedding 通常需要单独处理？
- 谱正交化是否改变更新矩阵的有效秩？

## 13. 推荐阅读与动态更新入口

基础阅读：

- Kingma and Ba, Adam: A Method for Stochastic Optimization.
- Loshchilov and Hutter, Decoupled Weight Decay Regularization.
- Amari, Natural Gradient Works Efficiently in Learning.
- Foret et al., Sharpness-Aware Minimization for Efficiently Improving Generalization.
- Martens and Grosse, Optimizing Neural Networks with Kronecker-factored Approximate Curvature.

近期阅读：

- Defazio et al., The Road Less Scheduled, Schedule-Free Learning, 2024.
- Liu et al., Sophia: A Scalable Stochastic Second-order Optimizer for Language Model Pre-training, https://arxiv.org/abs/2305.14342
- Moonshot AI, Muon is Scalable for LLM Training, https://arxiv.org/abs/2502.16982
- Sharpness-Aware Minimization Efficiently Selects Flatter Minima Late in Training, https://arxiv.org/abs/2410.10373
- Asynchronous Sharpness-Aware Minimization For Fast and Accurate Deep Learning, https://arxiv.org/abs/2503.11147
- LSAM: Asynchronous Distributed Training with Landscape-Smoothed Sharpness-Aware Minimization, https://arxiv.org/abs/2509.03110
- Understanding and Improving the Shampoo Optimizer via Kullback-Leibler Minimization, https://arxiv.org/abs/2509.03378
- NuMuon: Nuclear-Norm-Constrained Muon for Compressible LLM Training, https://arxiv.org/abs/2603.03597

动态阅读入口：

- arXiv: https://arxiv.org
- OpenReview: https://openreview.net
- PyTorch Optimizers: https://pytorch.org/docs/stable/optim.html
- DeepSpeed ZeRO: https://www.deepspeed.ai/tutorials/zero/

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 optimizer、SAM、Muon、Shampoo、distributed optimization 相关论文，并更新前沿研究进展。
