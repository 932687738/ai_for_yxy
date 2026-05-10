# 第 15 课：数值线性代数、随机矩阵理论与深度网络谱分析

## 0. 任务标识

任务名称：数值线性代数、随机矩阵理论与深度网络谱分析

预计学习时长：1.5 到 2 周

前置基础要求：

- 已掌握向量、矩阵、特征值、奇异值、范数、梯度、反向传播。
- 能使用 PyTorch 或 NumPy 完成基本模型训练。
- 理解深度学习中的损失函数、优化器、过拟合、泛化与正则化。
- 建议能阅读基础英文论文摘要与算法伪代码。

本课目标：

```text
从“矩阵怎么计算”上升到“谱结构如何支配深度网络训练行为”。
```

你需要建立以下研究直觉：

- 条件数决定数值问题对扰动的放大程度。
- 奇异值谱决定信号在网络层间传播时是否爆炸、衰减或保持稳定。
- Hessian 谱揭示损失地形的曲率、尖锐极小值、鞍点和训练稳定性。
- 随机矩阵理论给出了“大宽度随机网络”中谱分布的基准模型。
- 大模型训练中的低秩、谱裁剪、归一化、初始化和优化器，本质上都在调控谱结构。

## 1. 本课阅读方式

本课不是复习线性代数公式，而是把线性代数当成研究深度网络的显微镜。

建议学习顺序：

```text
条件数与数值稳定性
  -> SVD 与低秩近似
  -> 随机矩阵谱分布
  -> Jacobian 与信号传播
  -> Hessian 谱与损失地形
  -> PyTorch 谱实验
  -> 前沿论文阅读与复现
```

【核心】深度网络不是普通函数，它是大量矩阵乘法、非线性门控和随机优化共同作用形成的高维动力系统。谱分析是理解这个系统稳定性和泛化行为的重要入口。

## 2. 条件数：数值稳定性的第一性指标

### 2.1 向量范数与算子范数

对向量 $x \in \mathbb{R}^n$，常见范数包括：

$$
\|x\|_2 = \sqrt{\sum_{i=1}^n x_i^2}, \quad
\|x\|_1 = \sum_{i=1}^n |x_i|, \quad
\|x\|_\infty = \max_i |x_i|
$$

公式注释：

- $\|x\|_2$ 是欧氏长度，衡量向量在几何空间中的实际距离。在深度学习中，embedding 相似度、梯度裁剪、权重衰减经常默认使用 2-范数。
- $\|x\|_1$ 衡量绝对值总量，容易诱导稀疏性。L1 正则化能够让部分参数变成 0，就是因为它对每个坐标施加线性惩罚。
- $\|x\|_\infty$ 只关心最大坐标幅度，适合分析最坏坐标扰动。例如对抗样本中的 $L_\infty$ 攻击限制每个像素最多改多少。
- 三种范数不是谁更“正确”，而是观察同一个向量的三种尺度。研究中必须说明使用哪种范数，因为不同范数给出的稳定性结论可能不同。

矩阵 $A \in \mathbb{R}^{m \times n}$ 的诱导 2-范数定义为：

$$
\|A\|_2 = \max_{x \ne 0} \frac{\|Ax\|_2}{\|x\|_2}
$$

公式注释：

- 分子 $\|Ax\|_2$ 是输入 $x$ 被矩阵 $A$ 变换后的长度。
- 分母 $\|x\|_2$ 是输入原始长度，用它归一化后，结果只表示“放大倍数”，不受输入本身大小影响。
- $\max_{x \ne 0}$ 表示在所有非零输入方向中寻找最容易被放大的方向。
- 这一定义把矩阵看成一个算子，而不是一张数字表。它回答的问题是：这个线性层最坏情况下能把信号放大多少倍？

它等于最大奇异值：

$$
\|A\|_2 = \sigma_{\max}(A)
$$

理论注释：

- 最大奇异值 $\sigma_{\max}(A)$ 对应矩阵最强的拉伸方向。
- 如果某层权重矩阵的最大奇异值远大于 1，沿某些方向的激活或梯度可能被放大。
- 如果最大奇异值远小于 1，该层可能压缩信息，使梯度在深层网络中衰减。
- 谱归一化的基本思想就是直接控制 $\sigma_{\max}(A)$，让网络 Lipschitz 常数不要失控。

这说明矩阵的最大奇异值刻画了它对输入向量长度的最大放大能力。

### 2.2 条件数与扰动放大

对可逆矩阵 $A$，2-范数条件数为：

$$
\kappa_2(A) = \|A\|_2 \|A^{-1}\|_2 = \frac{\sigma_{\max}(A)}{\sigma_{\min}(A)}
$$

公式注释：

- $\sigma_{\max}(A)$ 表示矩阵最强放大方向。
- $\sigma_{\min}(A)$ 表示矩阵最弱放大方向。
- 两者比值越大，说明矩阵在不同方向上的缩放越不均匀。
- 当 $\sigma_{\min}(A)$ 接近 0 时，某些方向几乎被压扁，反向恢复这些方向会极度放大噪声。
- 条件数 $\kappa_2(A)$ 至少为 1。等于 1 时表示所有方向缩放一致，例如正交矩阵或等比例缩放矩阵。

如果求解线性系统：

$$
Ax = b
$$

公式注释：

- $A$ 是已知系数矩阵。
- $b$ 是观测到的右侧向量，可以理解为数据或约束。
- $x$ 是要求解的未知量。
- 在机器学习里，最小二乘、二阶优化、自然梯度和核方法都会隐含类似线性系统。

当 $b$ 受到扰动 $\Delta b$ 时，解的相对误差满足：

$$
\frac{\|\Delta x\|}{\|x\|}
\le
\kappa(A)
\frac{\|\Delta b\|}{\|b\|}
$$

公式注释：

- 左侧 $\frac{\|\Delta x\|}{\|x\|}$ 是解的相对误差。
- 右侧 $\frac{\|\Delta b\|}{\|b\|}$ 是输入或观测的相对误差。
- $\kappa(A)$ 是误差放大因子。它说明即使数据误差只有 0.1%，当条件数为 $10^4$ 时，解误差也可能被放大到不可接受的程度。
- 这是上界，不是精确等式。实际误差是否达到上界取决于扰动方向是否对齐最坏奇异向量。

【重点】条件数不是误差本身，而是误差放大器。条件数越大，同样的浮点舍入、梯度噪声、数据扰动越容易被放大。

### 2.3 深度网络中的条件数

深度网络的一层可以写成：

$$
h_{l+1} = \phi(W_l h_l + b_l)
$$

公式注释：

- $h_l$ 是第 $l$ 层输入激活。
- $W_l$ 是第 $l$ 层权重矩阵。
- $b_l$ 是偏置。
- $\phi$ 是非线性激活函数，例如 ReLU、GELU、SiLU。
- 对 Transformer 来说，单层不只是一个矩阵乘法，但注意力投影、MLP 投影、输出投影都可以局部写成类似形式。

忽略非线性时，$L$ 层网络近似为：

$$
h_L = W_{L-1} W_{L-2} \cdots W_0 x
$$

公式注释：

- 这个式子不是说真实网络没有非线性，而是用线性化模型分析层间信号传播。
- 矩阵乘积顺序从右向左作用：输入 $x$ 先经过 $W_0$，再经过 $W_1$，直到 $W_{L-1}$。
- 深度网络的稳定性难点来自“很多矩阵连续相乘”。即使每个矩阵看起来正常，乘积的谱也可能变得很极端。

整体线性映射的范数满足：

$$
\|W_{L-1} \cdots W_0\|_2
\le
\prod_{l=0}^{L-1} \|W_l\|_2
$$

公式注释：

- 这是矩阵范数的次乘性：$\|AB\| \le \|A\|\|B\|$。
- 右侧是每层最大放大倍数的乘积，给出整体最大放大的上界。
- 如果每层平均放大 $1.05$ 倍，100 层后上界约为 $1.05^{100}$，已经超过 100 倍。
- 如果每层平均缩小 $0.95$ 倍，100 层后约为 $0.95^{100}$，信号会明显衰减。

因此只要每一层有轻微放大，深层乘积也可能指数级爆炸。反向传播中梯度同样经过 Jacobian 连乘：

$$
\frac{\partial \mathcal{L}}{\partial h_l}
=
\left(
\prod_{k=l}^{L-1}
\frac{\partial h_{k+1}}{\partial h_k}
\right)^\top
\frac{\partial \mathcal{L}}{\partial h_L}
$$

公式注释：

- $\mathcal{L}$ 是损失函数。
- $\frac{\partial \mathcal{L}}{\partial h_l}$ 是损失对第 $l$ 层激活的梯度。
- $\frac{\partial h_{k+1}}{\partial h_k}$ 是第 $k$ 层到下一层的 Jacobian。
- 连乘来自链式法则。反向传播本质上就是不断乘以局部 Jacobian 的转置。
- 如果这些 Jacobian 的奇异值长期大于 1，梯度爆炸；长期小于 1，梯度消失。
- 残差连接、LayerNorm、合适初始化和学习率 warmup 都是在工程上缓解这个连乘问题。

这就是梯度爆炸、梯度消失和初始化理论的线性代数根源。

## 3. SVD：低秩结构与参数高效训练的数学基础

### 3.1 奇异值分解

任意矩阵 $A \in \mathbb{R}^{m \times n}$ 都可以分解为：

$$
A = U \Sigma V^\top
$$

公式注释：

- $V^\top$ 把输入向量投影到右奇异向量构成的坐标系。
- $\Sigma$ 对每个主方向进行缩放，缩放倍数就是奇异值。
- $U$ 把缩放后的结果旋转到输出空间。
- 如果某些奇异值很小，说明对应方向几乎不影响输出；如果只有少数奇异值很大，说明矩阵具有近似低秩结构。

其中：

- $U$ 和 $V$ 是正交矩阵。
- $\Sigma$ 是非负对角矩阵。
- 对角元素 $\sigma_1 \ge \sigma_2 \ge \cdots \ge 0$ 是奇异值。

矩阵作用可以理解为三步：

```text
V^T：旋转输入坐标
Sigma：沿主方向缩放
U：旋转到输出坐标
```

### 3.2 Eckart-Young 定理

保留前 $r$ 个奇异值可得到最优秩 $r$ 近似：

$$
A_r = \sum_{i=1}^{r} \sigma_i u_i v_i^\top
$$

公式注释：

- $u_i v_i^\top$ 是一个秩 1 矩阵，表示第 $i$ 个主方向的外积结构。
- $\sigma_i$ 是该方向的重要性权重。
- $A_r$ 只保留前 $r$ 个最重要方向，丢弃后面的弱方向。
- 这可以理解为矩阵版本的“主成分保留”。

并且：

$$
A_r =
\arg\min_{\operatorname{rank}(B) \le r}
\|A-B\|_F
$$

公式注释：

- $\operatorname{rank}(B) \le r$ 表示候选矩阵 $B$ 的秩最多为 $r$。
- $\|A-B\|_F$ 是 Frobenius 范数误差，即所有元素平方误差之和再开方。
- $\arg\min$ 表示使误差最小的那个矩阵。
- Eckart-Young 定理说明：如果你只能用秩 $r$ 矩阵近似 $A$，截断 SVD 是全局最优解，不是启发式方法。

误差为：

$$
\|A-A_r\|_F^2 = \sum_{i=r+1}^{\min(m,n)} \sigma_i^2
$$

公式注释：

- 近似误差正好等于被丢弃奇异值的平方和。
- 如果奇异值衰减很快，低秩近似损失很小。
- 如果奇异值衰减很慢，说明信息分散在许多方向上，低秩压缩会明显损失表达能力。
- 这给 LoRA rank 选择提供了理论判断：rank 不是越小越好，而要看任务更新矩阵的奇异值能量集中程度。

【核心】如果一个权重更新 $\Delta W$ 的有效奇异值只有少数几个显著方向，那么低秩适配不是工程技巧，而是谱结构允许的压缩。

### 3.3 与 LoRA 的连接

LoRA 将权重更新写成：

$$
W' = W + \Delta W,\quad
\Delta W = BA
$$

公式注释：

- $W$ 是预训练权重，通常冻结不更新。
- $\Delta W$ 是下游任务需要学习的权重改变量。
- $B$ 和 $A$ 是可训练低秩因子。
- 训练时不直接学习完整 $\Delta W$，而是学习两个小矩阵的乘积。

其中：

$$
B \in \mathbb{R}^{d_{\text{out}} \times r}, \quad
A \in \mathbb{R}^{r \times d_{\text{in}}}
$$

公式注释：

- $d_{\text{in}}$ 是线性层输入维度。
- $d_{\text{out}}$ 是线性层输出维度。
- $r$ 是 LoRA rank，控制可学习更新子空间的维度。
- 原始全量更新需要 $d_{\text{out}}d_{\text{in}}$ 个参数，LoRA 只需要 $r(d_{\text{out}}+d_{\text{in}})$ 个参数。

因此：

$$
\operatorname{rank}(\Delta W) \le r
$$

公式注释：

- 矩阵乘积 $BA$ 的秩不会超过中间维度 $r$。
- 这意味着 LoRA 更新只能改变最多 $r$ 个独立方向。
- 如果任务需要的更新本来就是低维的，LoRA 会高效；如果任务需要大范围改变模型能力，过小的 $r$ 会限制性能。

从 SVD 角度看，LoRA 假设微调任务只需要改变权重空间中的少数主方向。

这为下一课“张量分解、低秩结构与大模型参数高效训练”埋下基础。

## 4. 随机矩阵理论：深度网络谱分布的基线模型

### 4.1 为什么需要随机矩阵理论

深度网络权重矩阵通常巨大，逐个分析元素没有意义。随机矩阵理论关心的是：

```text
当矩阵维度趋近无穷时，特征值或奇异值整体分布会收敛到什么形状？
```

这提供了判断网络谱结构是否异常的基线。

### 4.2 Wishart 矩阵与 Marchenko-Pastur 分布

设：

$$
X \in \mathbb{R}^{n \times p}, \quad
X_{ij} \sim \mathcal{N}(0, \sigma^2)
$$

公式注释：

- $X$ 可以看成一个数据矩阵，$n$ 是特征维度或神经元数量，$p$ 是样本数。
- $X_{ij}$ 表示第 $i$ 个特征在第 $j$ 个样本上的数值。
- $\mathcal{N}(0,\sigma^2)$ 表示每个元素来自均值为 0、方差为 $\sigma^2$ 的高斯分布。
- 这个设定是“纯随机无结构数据”的基准模型。真实深度网络不完全满足独立高斯假设，但它提供了判断结构信号是否显著的参照。

样本协方差矩阵为：

$$
S = \frac{1}{p}XX^\top
$$

公式注释：

- $XX^\top$ 衡量不同特征维度之间的相关性。
- 除以 $p$ 是样本平均，使矩阵尺度不会随样本数线性增长。
- $S$ 是半正定矩阵，因此特征值非负。
- 在神经网络中，激活协方差、梯度协方差、embedding 协方差都可以用类似矩阵描述。

当 $n,p \to \infty$ 且：

$$
\frac{n}{p} \to \gamma
$$

公式注释：

- $\gamma$ 是维度与样本数的比例。
- 经典低维统计通常假设 $p \gg n$，但现代深度学习经常处于 $n$ 和 $p$ 同阶甚至 $n > p$ 的高维环境。
- Marchenko-Pastur 分布描述的是这种高维比例极限，而不是固定维度下的精确分布。

特征值分布趋近 Marchenko-Pastur 分布，其支撑区间为：

$$
\lambda_{\pm}
=
\sigma^2(1 \pm \sqrt{\gamma})^2
$$

公式注释：

- $\lambda_-$ 和 $\lambda_+$ 是随机协方差特征值 bulk 的理论左右边界。
- 当 $\gamma$ 越大，特征值分布越宽，说明高维噪声本身就会制造明显的谱扩散。
- 如果观测到的最大特征值远超 $\lambda_+$，它可能不是纯噪声，而是低秩信号或训练结构造成的 outlier。

密度为：

$$
\rho(\lambda)
=
\frac{1}{2\pi \sigma^2 \gamma \lambda}
\sqrt{(\lambda_+ - \lambda)(\lambda - \lambda_-)}
$$

公式注释：

- $\rho(\lambda)$ 表示特征值落在 $\lambda$ 附近的密度。
- 根号项保证密度只在 $[\lambda_-,\lambda_+]$ 内有意义。
- 分母中的 $\lambda$ 使小特征值区域的形状更敏感，这也是高维协方差矩阵经常病态的原因之一。
- 研究中常把经验谱直方图和 MP 理论边界叠加，判断矩阵是否存在非随机结构。

其中 $\lambda \in [\lambda_-, \lambda_+]$。

【重点】如果训练后权重或 Hessian 的谱只有一个随机矩阵 bulk，而没有明显 outlier，说明模型可能没有形成强任务方向；如果出现少量 outlier，通常意味着模型学习到了低维结构化方向。

### 4.3 Wigner 半圆律

若对称随机矩阵：

$$
H = \frac{1}{\sqrt{n}}G,\quad G_{ij}=G_{ji},\quad G_{ij}\sim \mathcal{N}(0,\sigma^2)
$$

公式注释：

- $G_{ij}=G_{ji}$ 表示矩阵对称，因此特征值都是实数。
- $\frac{1}{\sqrt{n}}$ 是关键缩放。如果没有这个缩放，特征值会随矩阵维度变大而发散。
- 这个模型刻画“随机对称相互作用”。在 Hessian 分析中，它可作为随机曲率背景的粗略基线。

其特征值分布在极限下趋近半圆律：

$$
\rho(\lambda)
=
\frac{1}{2\pi\sigma^2}
\sqrt{4\sigma^2 - \lambda^2}
$$

公式注释：

- 特征值主要落在 $[-2\sigma,2\sigma]$。
- 分布形状像半圆，因此称为 Wigner 半圆律。
- 与 MP 分布不同，Wigner 矩阵可以有正负特征值；这更像非凸损失地形中的曲率，正特征值对应上凸方向，负特征值对应下坡或鞍点方向。
- 深度网络 Hessian 通常不是纯 Wigner 矩阵，因为它包含数据、模型结构和损失函数诱导的相关性。

深度网络 Hessian 不是简单 Wigner 矩阵，但半圆律提供了理解“高维随机曲率背景”的基本参照。

## 5. Jacobian 谱：信号传播与动态等距

### 5.1 层间 Jacobian

对一层：

$$
h_{l+1} = \phi(W_l h_l)
$$

公式注释：

- 这里暂时省略偏置，是为了让 Jacobian 表达更清晰。
- $W_l h_l$ 是线性预激活，$\phi$ 决定哪些坐标被放大、压缩或置零。
- 对 ReLU 来说，$\phi'$ 只取 0 或 1；对 GELU/SiLU 来说，$\phi'$ 是连续门控。

Jacobian 为：

$$
J_l =
\frac{\partial h_{l+1}}{\partial h_l}
=
D_l W_l
$$

公式注释：

- $J_l$ 描述第 $l$ 层输入发生微小变化时，输出如何变化。
- $D_l$ 来自激活函数导数，是一个对角门控矩阵。
- $W_l$ 来自线性变换。
- 乘积 $D_l W_l$ 表示“先经过线性方向混合，再被非线性导数按坐标门控”。
- 如果很多 ReLU 单元导数为 0，$D_l$ 会屏蔽大量梯度路径。

其中：

$$
D_l = \operatorname{diag}(\phi'(W_l h_l))
$$

公式注释：

- $\operatorname{diag}(\cdot)$ 把向量放到对角线上形成对角矩阵。
- $\phi'(W_lh_l)$ 是每个神经元在当前输入上的局部斜率。
- 这说明 Jacobian 不是固定矩阵，而是依赖当前输入样本。不同样本会激活不同的局部线性区域。

整个网络的输入输出 Jacobian：

$$
J = J_{L-1}J_{L-2}\cdots J_0
$$

公式注释：

- $J$ 描述输入 $x$ 的微小变化最终如何影响输出 $h_L$。
- 它也是研究鲁棒性、对抗扰动、梯度传播和表示稳定性的核心对象。
- 如果 $J$ 的最大奇异值很大，输入微扰可能被放大，模型更脆弱。
- 如果 $J$ 的很多奇异值接近 0，模型可能丢失输入中的部分信息。

如果 $J$ 的奇异值大多接近 1，则信号和梯度可以稳定传播。这种性质称为动态等距。

### 5.2 残差连接的谱意义

残差层：

$$
h_{l+1}=h_l + F_l(h_l)
$$

公式注释：

- $h_l$ 是恒等路径，保证信息可以直接跨层传递。
- $F_l(h_l)$ 是残差分支，只学习对当前表示的修正。
- 这种结构让网络更像逐步修正的动力系统，而不是每层都完全重写表示。

Jacobian 为：

$$
J_l = I + \frac{\partial F_l}{\partial h_l}
$$

公式注释：

- $I$ 来自恒等路径，特征值全部为 1。
- $\frac{\partial F_l}{\partial h_l}$ 来自残差分支。
- 当残差分支的 Jacobian 较小，整体 Jacobian 会围绕单位矩阵波动，信号传播更稳定。
- Transformer 中的残差流可以理解为高维表示在多个子模块作用下不断累积微小更新。

如果 $\left\|\frac{\partial F_l}{\partial h_l}\right\|_2$ 较小，则 $J_l$ 的特征值围绕 1 波动。这解释了残差网络和 Transformer 残差流为什么有利于深层训练。

## 6. Hessian 谱：损失地形、曲率与泛化

### 6.1 Hessian 定义

模型参数为 $\theta \in \mathbb{R}^d$，损失函数为 $\mathcal{L}(\theta)$，Hessian 为：

$$
H(\theta)
=
\nabla_\theta^2 \mathcal{L}(\theta)
$$

公式注释：

- $\theta$ 是把所有模型参数展平后得到的高维向量。
- $\nabla_\theta^2$ 表示对参数做二阶偏导。
- Hessian 的第 $(i,j)$ 个元素是：

$$
H_{ij}
=
\frac{\partial^2 \mathcal{L}}
{\partial \theta_i \partial \theta_j}
$$

- 对角元素表示单个参数方向的曲率。
- 非对角元素表示两个参数方向之间的耦合关系。
- 现代大模型参数量巨大，Hessian 无法显式存储，只能通过 Hessian-vector product、Lanczos、随机迹估计等方法间接分析。

二阶 Taylor 展开：

$$
\mathcal{L}(\theta + \Delta)
\approx
\mathcal{L}(\theta)
+
\nabla \mathcal{L}(\theta)^\top \Delta
+
\frac{1}{2}\Delta^\top H(\theta)\Delta
$$

公式注释：

- $\Delta$ 是参数扰动，表示从当前参数点移动一小步。
- 第一项 $\mathcal{L}(\theta)$ 是当前位置的损失。
- 第二项 $\nabla \mathcal{L}(\theta)^\top \Delta$ 是一阶线性变化，由梯度决定。
- 第三项 $\frac{1}{2}\Delta^\top H(\theta)\Delta$ 是二阶曲率修正。
- 如果只看梯度，就只能知道“往哪里下降”；加入 Hessian 后，才能知道“这个方向是陡峭还是平坦”。

在局部极小值附近，梯度项接近 0，损失变化由二次型控制：

$$
\Delta \mathcal{L}
\approx
\frac{1}{2}\Delta^\top H \Delta
$$

公式注释：

- 局部极小值附近 $\nabla \mathcal{L}(\theta) \approx 0$，所以一阶项消失。
- 二次型 $\Delta^\top H\Delta$ 描述沿扰动方向 $\Delta$ 的曲率。
- 如果 $\Delta$ 与 Hessian 最大特征向量对齐，损失上升最快。
- 如果 $\Delta$ 落在 Hessian 小特征值方向，损失变化很小，说明存在平坦谷地。

如果 $H$ 的最大特征值很大，则某些方向非常尖锐。

### 6.2 梯度下降稳定性

对二次损失：

$$
\mathcal{L}(\theta)=\frac{1}{2}\theta^\top H\theta
$$

公式注释：

- 这是二次型损失，是分析优化器稳定性的标准局部模型。
- 在任意光滑损失函数的局部，Taylor 展开都可以近似成二次型。
- $H$ 在这里假设为对称正定矩阵，因此所有特征值为正，损失地形像高维碗。

梯度下降：

$$
\theta_{t+1} = \theta_t - \eta H\theta_t
=
(I-\eta H)\theta_t
$$

公式注释：

- $\eta$ 是学习率。
- $\nabla \mathcal{L}(\theta_t)=H\theta_t$，所以更新式变成 $\theta_t-\eta H\theta_t$。
- $I-\eta H$ 是每一步对参数误差的线性变换。
- 如果沿某个特征方向 $q_i$ 分解参数，更新会变成：

$$
\alpha_{i,t+1}
=
(1-\eta\lambda_i)\alpha_{i,t}
$$

- 其中 $\lambda_i$ 是 Hessian 第 $i$ 个特征值，$\alpha_i$ 是该特征方向上的坐标。
- 因此不同曲率方向的收敛速度不同。大特征值方向收敛快但容易震荡，小特征值方向收敛慢。

若 $H$ 对称正定，收敛需要：

$$
0 < \eta < \frac{2}{\lambda_{\max}(H)}
$$

公式注释：

- 收敛要求所有方向都满足 $|1-\eta\lambda_i|<1$。
- 最严格的约束来自最大特征值 $\lambda_{\max}(H)$。
- 当 $\eta\lambda_{\max}(H)>2$，最大曲率方向会发散。
- 当 $\eta$ 接近边界时，训练可能进入 edge of stability：loss 震荡但不立即崩溃。
- 实际深度网络不是固定二次函数，但这个条件解释了为什么学习率、warmup、梯度裁剪和归一化会显著影响稳定性。

【核心】最大 Hessian 特征值决定了学习率上界。训练中 loss 突然震荡，常常对应局部曲率过大或优化器有效步长过大。

### 6.3 Sharpness 与 flat minima

一种局部 sharpness 可定义为：

$$
\max_{\|\epsilon\|_2 \le \rho}
\mathcal{L}(\theta+\epsilon)-\mathcal{L}(\theta)
$$

公式注释：

- $\epsilon$ 是对参数的扰动。
- $\rho$ 是扰动半径，限制扰动不能太大。
- 这个定义问的是：在当前参数附近半径为 $\rho$ 的小球内，损失最多会升高多少？
- 如果最大升高很大，说明当前位置尖锐；如果最大升高很小，说明当前位置平坦。

二阶近似下：

$$
\max_{\|\epsilon\|_2 \le \rho}
\frac{1}{2}\epsilon^\top H\epsilon
=
\frac{1}{2}\rho^2 \lambda_{\max}(H)
$$

公式注释：

- 对称矩阵二次型的最大值由最大特征值决定。
- 当 $\epsilon$ 与最大特征向量方向一致时，$\epsilon^\top H\epsilon$ 最大。
- 因此 sharpness 在局部二阶近似下等价于控制 $\lambda_{\max}(H)$。
- 这也是为什么很多 sharpness 指标、本征谱分析和 SAM 会联系在一起。

这解释了 Sharpness-Aware Minimization 的目标：

$$
\min_\theta
\max_{\|\epsilon\|_2 \le \rho}
\mathcal{L}(\theta+\epsilon)
$$

公式注释：

- 内层 $\max$ 寻找当前参数附近最坏扰动。
- 外层 $\min$ 寻找即使被最坏扰动后损失仍然低的参数。
- 普通经验风险最小化只要求 $\mathcal{L}(\theta)$ 小，SAM 要求邻域内都小。
- 这会偏向更平坦的解，但计算成本更高，因为每一步需要近似求一次内层扰动。

SAM 不是简单正则化，而是显式惩罚局部高曲率区域。

## 7. 前沿研究进展：2024-2026 视角

### 7.1 研究进展一：随机矩阵理论正在从线性模型扩展到深度非线性模型

近期代表：

- Zhenyu Liao 和 Michael W. Mahoney, Random Matrix Theory for Deep Learning: Beyond Eigenvalues of Linear Models, arXiv:2506.13139，初版 2025-06-16，arXiv 页面显示最新版更新于 2026-04-16。

这类工作的重要变化是：传统随机矩阵理论主要分析线性模型、样本协方差、核矩阵和确定性等价形式，而深度学习需要处理非线性、高维比例极限和一般谱函数。其核心目标不只是给出某个矩阵的特征值分布，而是解释：

```text
高维非线性网络中的 scaling law、double descent、训练动力学和泛化误差是否可以被统一到一个谱分析框架中。
```

研究启发：

- 不要只问“这个矩阵的最大特征值是多少”，还要问“哪些谱函数和泛化、训练速度、表示质量相关”。
- 对深度网络来说，线性等价、确定性等价和高维等价是连接随机矩阵理论与神经网络行为的桥。
- 当模型参数量、样本数、数据维度同时很大时，低维统计直觉经常失效，必须使用高维极限理论。

### 7.2 研究进展二：权重矩阵训练动力学可用 Dyson Brownian Motion 描述

近期代表：

- Gert Aarts, Biagio Lucini, Chanju Park, Stochastic weight matrix dynamics during learning and Dyson Brownian motion, arXiv:2407.16427，2024-07-23。
- Gert Aarts, Ouraman Hajizadeh, Biagio Lucini, Chanju Park, Dyson Brownian motion and random matrix dynamics of weight matrices during learning, arXiv:2411.13512，2024-11-20。

这条线索把 SGD 更新后的权重矩阵看成随机矩阵过程。若权重矩阵 $W_t$ 随训练演化，谱不再只是静态分布，而是随机动力学：

$$
dW_t = -\nabla_W \mathcal{L}(W_t)dt + \sqrt{2T}\,dB_t
$$

公式注释：

- $W_t$ 表示时间 $t$ 时的权重矩阵。
- $-\nabla_W \mathcal{L}(W_t)dt$ 是确定性下降项，推动权重降低损失。
- $dB_t$ 是 Brownian motion 噪声项，用来近似 mini-batch SGD 中的随机扰动。
- $\sqrt{2T}$ 控制噪声强度，$T$ 可理解为有效温度。
- 这个式子把训练过程从离散迭代近似成连续随机微分方程，便于使用统计物理和随机过程工具分析谱演化。

其中有效温度 $T$ 与学习率和 batch size 有关。谱层面会出现类似 Dyson Brownian Motion 的特征，例如 eigenvalue repulsion。

研究启发：

- batch size 和 learning rate 不只是工程超参数，也控制权重谱动力学中的噪声强度。
- 初始权重常接近 Marchenko-Pastur 型随机谱，训练后可能形成 bulk 加结构化 outlier。
- 统计物理中的 Coulomb gas、Dyson Brownian Motion 和有效温度可以帮助解释 SGD 的隐式正则化。

### 7.3 研究进展三：Hessian 谱正在进入优化稳定性理论

近期代表：

- Minhak Song 等，Zeroth-Order Optimization at the Edge of Stability, arXiv:2604.14669，2026-04-16。
- Sidak Pal Singh, Weronika Ormaniec, Thomas Hofmann, Cracking the Hessian: Closed-Form Hessian Spectra for Fundamental Neural Networks, OpenReview ICLR 2026 submission，2025-09-20，2026-02-11 修改。

过去常见的稳定性结论是：一阶梯度下降的局部稳定性主要由 $\lambda_{\max}(H)$ 控制。但最新研究开始追问：

```text
如果优化器不是标准一阶梯度下降，而是零阶优化、动量、自适应优化或大模型低精度训练，稳定性是否仍然只由最大特征值决定？
```

零阶优化研究显示，均方稳定性可能依赖整个 Hessian 谱，而不仅是最大特征值。闭式 Hessian 谱研究则试图在简单但非平凡的网络中推导全部特征值和特征向量，从而解释 outlier、condition number、注意力结构和权重谱范数之间的关系。

研究启发：

- 大模型微调、黑盒优化和 memory-efficient fine-tuning 中，Hessian trace、top eigenvalue 和谱尾部都可能影响稳定性。
- 如果只监控 loss，可能已经太晚；谱指标有机会作为训练预警信号。
- Hessian 的闭式结果虽然只覆盖简化网络，但能提供构造新优化器和正则项的理论基准。

## 8. MCP 调用点设计

本课要求动态获取最新论文、代码库或数据集。由于课程会持续迭代，不能把论文列表写死在教材里。

### 8.1 MCP 调用点 A：最新论文检索

调用目的：获取最近 24 个月内关于 deep learning Hessian spectrum、random matrix theory、loss landscape 的论文。

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(\"Hessian spectrum\" OR \"loss landscape\" OR \"random matrix theory\") AND (\"deep learning\" OR \"neural networks\")",
  "max_results": 10,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 学会从标题和摘要判断论文是否研究谱结构。
- 提取论文中的核心数学对象，例如 Hessian、Jacobian、Fisher、NTK、Gram matrix。
- 识别论文是理论推导、经验观测还是工程方法。

### 8.2 MCP 调用点 B：代码库检索

调用目的：查找 Hessian top eigenvalue、Lanczos、stochastic trace estimation 的开源实现。

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "PyTorch Hessian spectrum Lanczos neural network",
  "language": "Python",
  "sort": "updated",
  "max_results": 5
}
```

预期学习收获：

- 对比显式构造 Hessian 与 Hessian-vector product 的复杂度差异。
- 学习 Lanczos 如何在不构造完整矩阵时估计主特征值。
- 找到可复现实验的工程模板。

### 8.3 MCP 调用点 C：课程运行时论文卡片生成

调用目的：把 MCP 检索到的论文转为结构化阅读卡片。

建议输出字段：

```json
{
  "title": "...",
  "year": 2025,
  "problem": "...",
  "math_objects": ["Hessian", "Jacobian", "random matrix"],
  "main_claim": "...",
  "experiment": "...",
  "reproducibility_score": "high | medium | low"
}
```

预期学习收获：

- 把论文阅读从“看热闹”变成“提取研究变量”。
- 为课后项目形成可跟踪的论文复现清单。

## 9. 代码实验一：Marchenko-Pastur 分布模拟

实验目标：观察随机高维矩阵的协方差特征值分布。

```python
import numpy as np
import matplotlib.pyplot as plt

def simulate_mp(n=800, p=1200, sigma=1.0):
    x = np.random.normal(0, sigma, size=(n, p))
    s = (x @ x.T) / p
    eigvals = np.linalg.eigvalsh(s)

    gamma = n / p
    lam_minus = sigma**2 * (1 - np.sqrt(gamma))**2
    lam_plus = sigma**2 * (1 + np.sqrt(gamma))**2
    return eigvals, lam_minus, lam_plus

eigvals, lo, hi = simulate_mp()

plt.hist(eigvals, bins=80, density=True, alpha=0.7)
plt.axvline(lo, color="red", linestyle="--", label="MP lower")
plt.axvline(hi, color="red", linestyle="--", label="MP upper")
plt.title("Eigenvalue distribution of random covariance matrix")
plt.legend()
plt.show()
```

观察问题：

- 大部分特征值是否落在 $[\lambda_-, \lambda_+]$？
- 如果人为加入低秩信号，是否会出现超出 bulk 的 outlier？

加入低秩信号：

```python
n, p = 800, 1200
x = np.random.randn(n, p)

u = np.random.randn(n, 1)
v = np.random.randn(1, p)
signal = 3.0 * (u @ v) / np.sqrt(n * p)

x_spiked = x + signal
s = (x_spiked @ x_spiked.T) / p
eigvals = np.linalg.eigvalsh(s)

plt.hist(eigvals, bins=80, density=True, alpha=0.7)
plt.title("Spiked covariance: bulk plus outlier")
plt.show()
```

研究解释：

```text
bulk 像随机背景，outlier 像任务结构。
```

## 10. 代码实验二：PyTorch Hessian-vector product 与主特征值

完整 Hessian 对现代网络不可显式构造，因为参数量 $d$ 很大，Hessian 大小是 $d \times d$。但可以计算 Hessian-vector product：

$$
Hv = \nabla_\theta \left(\nabla_\theta \mathcal{L}(\theta)^\top v\right)
$$

PyTorch 实现：

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SmallMLP(nn.Module):
    def __init__(self, d_in=20, d_hidden=64, d_out=2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, d_hidden),
            nn.ReLU(),
            nn.Linear(d_hidden, d_hidden),
            nn.ReLU(),
            nn.Linear(d_hidden, d_out),
        )

    def forward(self, x):
        return self.net(x)

def flatten_tensors(tensors):
    return torch.cat([t.reshape(-1) for t in tensors])

def unflatten_like(vector, tensors):
    outputs = []
    offset = 0
    for t in tensors:
        numel = t.numel()
        outputs.append(vector[offset:offset + numel].view_as(t))
        offset += numel
    return outputs

def hessian_vector_product(model, loss, vector):
    params = [p for p in model.parameters() if p.requires_grad]
    grads = torch.autograd.grad(loss, params, create_graph=True)
    flat_grads = flatten_tensors(grads)
    grad_v = torch.dot(flat_grads, vector)
    hvp = torch.autograd.grad(grad_v, params, retain_graph=True)
    return flatten_tensors(hvp).detach()

def power_iteration_top_eigenvalue(model, x, y, steps=30):
    logits = model(x)
    loss = F.cross_entropy(logits, y)
    params = [p for p in model.parameters() if p.requires_grad]
    n_params = sum(p.numel() for p in params)

    v = torch.randn(n_params)
    v = v / v.norm()

    for _ in range(steps):
        hv = hessian_vector_product(model, loss, v)
        v = hv / (hv.norm() + 1e-12)

    hv = hessian_vector_product(model, loss, v)
    rayleigh = torch.dot(v, hv)
    return rayleigh.item()

torch.manual_seed(0)
model = SmallMLP()
x = torch.randn(128, 20)
y = torch.randint(0, 2, (128,))

top_lambda = power_iteration_top_eigenvalue(model, x, y)
print("estimated top Hessian eigenvalue:", top_lambda)
```

实验扩展：

- 训练模型 0、10、100、1000 步后分别估计 $\lambda_{\max}(H)$。
- 改变学习率，观察 loss 震荡是否与 $\lambda_{\max}(H)$ 增大相关。
- 加入 weight decay、gradient clipping、SAM，比较 Hessian top eigenvalue。

## 11. 代码实验三：条件数与梯度下降速度

实验目标：验证条件数越大，梯度下降越慢。

```python
import numpy as np
import matplotlib.pyplot as plt

def make_quadratic(dim=50, condition_number=1000):
    eigvals = np.logspace(0, np.log10(condition_number), dim)
    q, _ = np.linalg.qr(np.random.randn(dim, dim))
    h = q @ np.diag(eigvals) @ q.T
    return h

def gd_on_quadratic(h, steps=300):
    lam_max = np.linalg.eigvalsh(h).max()
    eta = 1.8 / lam_max
    theta = np.random.randn(h.shape[0])
    losses = []

    for _ in range(steps):
        loss = 0.5 * theta @ h @ theta
        grad = h @ theta
        theta = theta - eta * grad
        losses.append(loss)

    return np.array(losses)

for kappa in [10, 100, 1000, 10000]:
    h = make_quadratic(condition_number=kappa)
    losses = gd_on_quadratic(h)
    plt.semilogy(losses, label=f"kappa={kappa}")

plt.title("Condition number controls optimization speed")
plt.xlabel("step")
plt.ylabel("loss")
plt.legend()
plt.show()
```

理论解释：

对二次问题，梯度下降收敛速度与：

$$
\frac{\kappa - 1}{\kappa + 1}
$$

相关。$\kappa$ 越大，狭长谷地越明显，优化越慢。

## 12. 跨学科连接

### 12.1 统计物理

高维损失地形常被类比为 spin glass。大量局部极值、鞍点和平坦方向共同构成复杂能量景观。SGD 类似带噪声的动力系统：

$$
d\theta_t =
-\nabla \mathcal{L}(\theta_t)dt
+
\sqrt{2T}\,dW_t
$$

其中 $T$ 可被理解为由 batch noise 诱导的有效温度。

### 12.2 控制论

训练过程可以看成离散控制系统：

$$
\theta_{t+1}=f(\theta_t, u_t)
$$

其中 $u_t$ 是学习率、batch size、梯度裁剪、权重衰减等控制变量。Hessian 最大特征值给出局部稳定性约束。

### 12.3 神经科学

表示学习中的主方向、低维流形和谱 outlier，与神经群体活动中的低维动态结构有相似性。两者都关注高维观测背后的少数主导因子。

## 13. 本课小结

本课形成的研究主线：

```text
矩阵条件数
  -> 奇异值谱
  -> 随机矩阵 bulk
  -> 低秩 outlier
  -> Jacobian 信号传播
  -> Hessian 曲率
  -> 优化稳定性与泛化
```

你应掌握的核心判断：

- 训练不稳定时，优先检查有效步长和局部曲率。
- 网络太深时，检查 Jacobian 奇异值是否远离 1。
- 权重更新呈低秩时，可考虑 LoRA、谱截断或子空间训练。
- 看到大矩阵谱分布时，先区分 bulk 和 outlier。
- 谱分析不是替代实验，而是让实验结果有可解释的数学坐标。

## 14. 课后研究课题

### 课题 1：Hessian 谱随训练阶段的演化

要求：

- 选择 MNIST、CIFAR-10 或一个小型文本分类任务。
- 训练 MLP 或小型 Transformer。
- 每隔固定 step 估计 Hessian top eigenvalue 和 trace。
- 分析训练初期、中期、收敛期的曲率变化。

必须查阅论文：

- 至少 1 篇 Hessian spectrum 或 loss landscape 相关论文。
- 至少 1 篇 sharpness 或 SAM 相关论文。

输出：

- 一份图表报告。
- 一段解释：谱变化是否能预测训练不稳定或泛化差异。

### 课题 2：随机矩阵 bulk 与低秩信号 outlier

要求：

- 构造纯随机矩阵和 spiked covariance 矩阵。
- 绘制特征值分布。
- 改变 signal strength，观察 outlier 从 bulk 中分离的阈值。

开放问题：

```text
神经网络训练出的特征方向，是否可以看成从随机背景中冒出的 outlier？
```

输出：

- Python 实验代码。
- 一页理论解释，说明 Marchenko-Pastur 分布和 outlier 的关系。

### 课题 3：LoRA 更新的奇异值谱分析

要求：

- 微调一个小型语言模型或文本分类 Transformer。
- 保存全量微调更新 $\Delta W$ 或 LoRA 更新矩阵。
- 对不同层的 $\Delta W$ 做 SVD。
- 比较前 $r$ 个奇异值解释的能量比例：

$$
E(r)=
\frac{\sum_{i=1}^r \sigma_i^2}
{\sum_{i=1}^{k} \sigma_i^2}
$$

开放问题：

- 哪些层更低秩？
- 注意力层和 MLP 层的谱结构是否不同？
- 低秩是否来自任务简单，还是来自预训练模型已经提供了良好基底？

## 15. 推荐阅读与动态更新入口

固定基础阅读：

- Gene H. Golub, Charles F. Van Loan, Matrix Computations.
- Terence Tao, Topics in Random Matrix Theory.
- Pennington, Schoenholz, Ganguli, Resurrecting the sigmoid in deep learning through dynamical isometry.
- Ghorbani, Krishnan, Xiao, An Investigation into Neural Net Optimization via Hessian Eigenvalue Density.
- Foret et al., Sharpness-Aware Minimization for Efficiently Improving Generalization.

近期阅读：

- Liao, Mahoney, Random Matrix Theory for Deep Learning: Beyond Eigenvalues of Linear Models, arXiv:2506.13139, https://arxiv.org/abs/2506.13139
- Aarts, Lucini, Park, Stochastic weight matrix dynamics during learning and Dyson Brownian motion, arXiv:2407.16427, https://arxiv.org/abs/2407.16427
- Aarts, Hajizadeh, Lucini, Park, Dyson Brownian motion and random matrix dynamics of weight matrices during learning, arXiv:2411.13512, https://arxiv.org/abs/2411.13512
- Song et al., Zeroth-Order Optimization at the Edge of Stability, arXiv:2604.14669, https://arxiv.org/abs/2604.14669
- Singh, Ormaniec, Hofmann, Cracking the Hessian: Closed-Form Hessian Spectra for Fundamental Neural Networks, OpenReview ICLR 2026 submission, https://openreview.net/forum?id=XfO8npR1fb

动态阅读入口：

- arXiv: https://arxiv.org
- Papers with Code: https://paperswithcode.com
- OpenReview: https://openreview.net

本课生成时参考的最新检索方向：

- 2024-2025 年关于 deep neural network Hessian spectrum、loss landscape、random matrix theory 的 arXiv 论文。
- 2024-2026 年关于低秩微调、谱结构、优化稳定性和大模型训练动力学的研究趋势。

后续更新本课时，优先通过 MCP 调用点 A 重新检索论文，并替换本节动态阅读条目。
