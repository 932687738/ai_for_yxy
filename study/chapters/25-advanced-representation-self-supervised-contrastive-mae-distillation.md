# 第 25 课：表示学习与自监督：对比学习、掩码建模、蒸馏与几何结构

## 0. 任务标识

任务名称：表示学习与自监督：对比学习、掩码建模、蒸馏与几何结构

预计学习时长：1.5 到 2 周

前置基础要求：

- 理解 embedding、相似度、交叉熵、Transformer encoder。
- 已完成第 9 课向量检索基础，以及第 19 课 Transformer 表示和残差流。
- 理解 KL、互信息、蒸馏、温度 softmax。

本课目标：

```text
理解无标签数据如何通过对比、重构、预测和蒸馏形成可迁移表示，并分析表示空间的几何结构。
```

你需要建立以下研究直觉：

- 自监督学习的核心是设计 pretext task，让模型从数据本身构造监督信号。
- 对比学习强调拉近正样本、推远负样本。
- 掩码建模强调从上下文恢复缺失信息。
- 自蒸馏强调 teacher-student 目标和防止表示坍缩。
- 表示空间质量可从 alignment、uniformity、collapse、isotropy 和线性可分性分析。

## 1. 本课阅读方式

建议学习顺序：

```text
表示学习目标
  -> InfoNCE
  -> alignment / uniformity
  -> BYOL / DINO 自蒸馏
  -> MAE 掩码重构
  -> hybrid distillation
  -> LLM 蒸馏
  -> 表示几何评估
```

【核心】好的表示不是简单压缩输入，而是保留对下游任务有用的变化因素，同时丢弃无关扰动。

## 2. 对比学习与 InfoNCE

### 2.1 正负样本

对输入 $x_i$ 做两种增强：

$$
z_i=f_\theta(\mathrm{aug}_1(x_i)),\quad
z_i^+=f_\theta(\mathrm{aug}_2(x_i))
$$

公式注释：

- $f_\theta$ 是 encoder。
- $z_i,z_i^+$ 是同一原始样本的两个视图表示。
- 它们构成正样本对。
- batch 中其他样本通常作为负样本。

理论注释：

数据增强定义了不变性。如果增强破坏任务语义，模型会学到错误不变性。自监督的关键不是无监督，而是通过增强、遮挡或预测任务注入先验。

### 2.2 InfoNCE 损失

$$
\mathcal{L}_i
=
-
\log
\frac{
\exp(\mathrm{sim}(z_i,z_i^+)/\tau)
}{
\sum_{j=1}^{N}
\exp(\mathrm{sim}(z_i,z_j)/\tau)
}
$$

公式注释：

- $\mathrm{sim}$ 通常是 cosine similarity。
- $\tau$ 是温度，控制 softmax 尖锐程度。
- 分子拉近正样本。
- 分母包含正样本和负样本，推远其他样本。

理论注释：

InfoNCE 可看作互信息下界，也可看作分类任务：给定一个 query，在 batch 中找出对应正样本。大 batch 或 memory bank 提供更多负样本，但也可能引入 false negatives。

## 3. Alignment 与 Uniformity

### 3.1 Alignment

$$
\mathcal{L}_{\text{align}}
=
\mathbb{E}_{(x,x^+)}
\|f(x)-f(x^+)\|_2^2
$$

公式注释：

- 衡量正样本表示距离。
- 越小表示同一语义样本的不同视图越接近。

理论注释：

过强 alignment 可能导致所有样本都聚到一起，产生表示坍缩。因此还需要 uniformity。

### 3.2 Uniformity

$$
\mathcal{L}_{\text{uniform}}
=
\log
\mathbb{E}_{x,y}
\exp
\left(
-2\|f(x)-f(y)\|_2^2
\right)
$$

公式注释：

- 随机样本对距离越大，指数项越小。
- 该目标鼓励表示分布在单位球上均匀铺开。

理论注释：

对比学习的表示质量可理解为 alignment 与 uniformity 的平衡。只对齐会坍缩，只均匀会丢失语义邻近结构。

## 4. 自蒸馏：BYOL、DINO 与防坍缩

### 4.1 Teacher-student 目标

$$
\mathcal{L}
=
\|q_\theta(z_s)-\mathrm{sg}(z_t)\|_2^2
$$

公式注释：

- $z_s$ 是 student view 表示。
- $z_t$ 是 teacher view 表示。
- $q_\theta$ 是 predictor。
- $\mathrm{sg}$ 是 stop-gradient，阻止 teacher 分支被该损失直接更新。

理论注释：

BYOL/DINO 等方法没有显式负样本，却能避免坍缩，依赖 stop-gradient、teacher EMA、centering、sharpening、predictor 等机制共同作用。

### 4.2 EMA teacher

$$
\theta_{\text{teacher}}
\leftarrow
m\theta_{\text{teacher}}
+
(1-m)\theta_{\text{student}}
$$

公式注释：

- $m$ 是动量系数，通常接近 1。
- teacher 是 student 的指数滑动平均。
- teacher 提供更平滑稳定的训练目标。

理论注释：

EMA teacher 类似时间集成，降低目标噪声。DINOv2 的成功说明大规模自蒸馏可以学习强通用视觉特征。

## 5. 掩码自编码 MAE

### 5.1 掩码重构

将输入 patch 分为可见和被 mask：

$$
x=(x_{\text{vis}},x_{\text{mask}})
$$

模型目标：

$$
\hat{x}_{\text{mask}}
=
g_\theta(f_\theta(x_{\text{vis}}))
$$

损失：

$$
\mathcal{L}_{\text{MAE}}
=
\|x_{\text{mask}}-\hat{x}_{\text{mask}}\|_2^2
$$

公式注释：

- encoder 只处理可见 patch。
- decoder 从 latent 表示重构被遮挡 patch。
- 高 mask ratio 迫使模型理解全局结构。

理论注释：

MAE 的目标偏向重构像素，可能学习更多低层细节；对比/蒸馏目标偏向语义不变性。2024-2025 年 hybrid 方法试图连接二者。

## 6. 知识蒸馏与 LLM 表示迁移

### 6.1 Logit distillation

$$
\mathcal{L}_{\text{KD}}
=
T^2
\mathrm{KL}
\left(
\mathrm{softmax}(z_T/T)
\|
\mathrm{softmax}(z_S/T)
\right)
$$

公式注释：

- $z_T$ 是 teacher logits。
- $z_S$ 是 student logits。
- $T$ 是温度。
- 高温 softmax 暴露类别间暗知识。

理论注释：

蒸馏不只是压缩模型，也是一种表示迁移。LLM 蒸馏可蒸馏 logits、hidden states、reasoning traces、preference behavior 或 tool-use trajectories。

### 6.2 Feature distillation

$$
\mathcal{L}_{\text{feat}}
=
\|P h_S-h_T\|_2^2
$$

公式注释：

- $h_S,h_T$ 是 student 和 teacher 的中间表示。
- $P$ 是投影层，用于匹配维度。
- 目标让 student 表示空间对齐 teacher。

理论注释：

Feature distillation 更直接控制表示空间，但也可能限制 student 形成自己的高效表示。对小模型来说，过强中间层约束可能损害最终任务表现。

## 7. 表示几何评估

### 7.1 Centered Kernel Alignment

CKA 衡量两个表示矩阵相似性：

$$
\mathrm{CKA}(X,Y)
=
\frac{\|Y^\top X\|_F^2}
{\|X^\top X\|_F\|Y^\top Y\|_F}
$$

公式注释：

- $X,Y$ 是两个模型或两层的表示矩阵。
- 分子衡量跨表示相关。
- 分母做尺度归一化。
- CKA 越高表示表示空间越相似。

理论注释：

CKA 常用于比较不同训练方法、不同层、teacher-student 表示是否对齐。它比逐神经元比较更稳健，因为表示空间可旋转。

### 7.2 Collapse 指标

表示协方差：

$$
\Sigma
=
\frac{1}{N}
\sum_i
(z_i-\bar{z})(z_i-\bar{z})^\top
$$

公式注释：

- $\Sigma$ 描述表示在各方向上的方差。
- 如果只有少数特征值非零，表示发生维度坍缩。
- 如果所有特征值接近 0，发生完全坍缩。

理论注释：

SSL 研究中，避免 collapse 是核心稳定性问题。Barlow Twins、VICReg、DINO 等都可以从方差、协方差和冗余消除角度解释。

## 8. 前沿研究进展：2024-2026 视角

### 8.1 Hybrid distillation

ICLR 2024 Hybrid Distillation 试图连接 Masked Autoencoder 和 Contrastive Learning，通过蒸馏目标弥合重构与语义表示之间的差距。

### 8.2 KDC-MAE

2024 年 KDC-MAE 将 contrastive learning、masked autoencoding 和 self-distillation 三类 SSL 目标组合，说明自监督范式正在走向混合目标。

### 8.3 表示学习走向跨模态和安全

2025 年 SSL 研究扩展到 EEG、医学、3D、LLM 安全和 citation attribution 等场景。表示学习从“预训练视觉 backbone”扩展为通用无标签结构发现方法。

## 9. 代码实验一：InfoNCE

```python
import torch
import torch.nn.functional as F

def info_nce(z1, z2, temperature=0.1):
    z1 = F.normalize(z1, dim=-1)
    z2 = F.normalize(z2, dim=-1)
    logits = z1 @ z2.T / temperature
    labels = torch.arange(z1.shape[0], device=z1.device)
    return F.cross_entropy(logits, labels)
```

实验要求：

- 用 MNIST/CIFAR 做两种增强。
- 训练 encoder。
- 用 frozen features 训练线性分类器。

## 10. 代码实验二：CKA

```python
def linear_cka(x, y):
    x = x - x.mean(dim=0, keepdim=True)
    y = y - y.mean(dim=0, keepdim=True)
    hsic = torch.norm(y.T @ x, p="fro") ** 2
    norm_x = torch.norm(x.T @ x, p="fro")
    norm_y = torch.norm(y.T @ y, p="fro")
    return hsic / (norm_x * norm_y + 1e-8)
```

实验要求：

- 比较随机初始化、监督训练、自监督训练的层表示。
- 绘制 layer-wise CKA heatmap。

## 11. MCP 调用点设计

### 11.1 MCP 调用点 A：最新自监督论文检索

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(\"self-supervised learning\" OR contrastive OR MAE OR distillation OR DINO OR \"representation learning\")",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 区分方法属于对比、掩码、蒸馏、聚类、预测 latent 还是混合目标。
- 记录是否评估 linear probing、fine-tuning、retrieval、OOD 和 robustness。

### 11.2 MCP 调用点 B：代码库检索

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "self supervised learning contrastive MAE DINO distillation representation PyTorch",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

## 12. 课后研究课题

### 课题 1：对比学习 alignment/uniformity 分析

要求：

- 训练 SimCLR 小模型。
- 计算 alignment 和 uniformity。
- 分析 temperature 和 batch size 的影响。

### 课题 2：MAE 与对比学习特征比较

要求：

- 训练或加载 MAE 和 contrastive encoder。
- 比较 linear probe、kNN、CKA、特征谱。

### 课题 3：蒸馏小模型

要求：

- 使用 teacher logits 或 hidden states 蒸馏 student。
- 比较只用 CE、logit KD、feature KD 的效果。

## 13. 推荐阅读与动态更新入口

基础阅读：

- SimCLR: A Simple Framework for Contrastive Learning of Visual Representations.
- MoCo: Momentum Contrast for Unsupervised Visual Representation Learning.
- BYOL: Bootstrap Your Own Latent.
- DINO: Emerging Properties in Self-Supervised Vision Transformers.
- MAE: Masked Autoencoders Are Scalable Vision Learners.
- VICReg, Barlow Twins.

近期阅读：

- DINOv2: Learning Robust Visual Features without Supervision, https://arxiv.org/abs/2304.07193
- Hybrid Distillation: Connecting Masked Autoencoders with Contrastive Learners, https://openreview.net/forum?id=5598cf1b2905a26ddb863e6705588327
- KDC-MAE: Knowledge Distilled Contrastive Mask Auto-Encoder, https://arxiv.org/abs/2411.12270
- Self-Supervised Representation Learning from Arbitrary Scenarios, https://openaccess.thecvf.com/content/CVPR2024/papers/Li_Self-Supervised_Representation_Learning_from_Arbitrary_Scenarios_CVPR_2024_paper.pdf
- A survey on design choices for self-supervised learning in computer vision, https://link.springer.com/article/10.1007/s10462-026-11506-9

动态阅读入口：

- Papers with Code SSL: https://paperswithcode.com/task/self-supervised-image-classification
- DINOv2: https://github.com/facebookresearch/dinov2
- MAE: https://github.com/facebookresearch/mae
- arXiv: https://arxiv.org

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 self-supervised learning、contrastive learning、MAE、distillation、representation geometry 相关论文。
