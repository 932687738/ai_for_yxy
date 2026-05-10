# 第 7 课：CNN、RNN 与 Transformer 入门

## 0. 本课阅读方式

本课介绍三类重要神经网络结构：

```text
CNN：擅长处理局部空间结构，常见于图像。
RNN：擅长处理序列，早期常用于文本和时间序列。
Transformer：擅长并行建模序列关系，是现代大模型基础。
```

本课不要求你从零实现复杂网络，而是理解：

```text
它们分别解决什么问题？
输入数据长什么样？
核心结构是什么？
为什么 Transformer 取代 RNN 成为大模型主流？
```

【核心】CNN、RNN、Transformer 是深度学习中的三种重要结构思想，不只是三个 API 名称。

## 0.1 概念讲义：CNN、RNN、Transformer 术语详解

### 0.1.1 第 7 课到底在学什么

第 6 课讲了 PyTorch 基础训练流程，第 7 课讲不同神经网络结构如何适配不同类型的数据。

数据类型不同，模型结构也不同：

| 数据 | 常见结构 |
|---|---|
| 图像 | CNN |
| 文本序列 | RNN、Transformer |
| 时间序列 | RNN、Transformer、TCN |
| 大模型 | Transformer |

【重点】模型结构本质上是对数据结构的归纳偏置。

### 0.1.2 CNN

CNN 是 Convolutional Neural Network，卷积神经网络。

它擅长处理图像，因为图像具有局部空间结构：

```text
相邻像素之间关系很重要。
局部纹理可以组合成更高级图案。
```

【核心】CNN 通过卷积核提取局部特征。

### 0.1.3 Convolution 卷积

卷积是用一个小窗口在图像上滑动，提取局部模式。

卷积核可以学习：

- 边缘。
- 纹理。
- 角点。
- 局部形状。

【重点】卷积层不是手写边缘检测规则，而是通过训练学习卷积核参数。

### 0.1.4 Kernel / Filter 卷积核

卷积核是一个小矩阵。

例如：

```text
3 x 3
5 x 5
```

它在图像上滑动，对局部区域做加权计算。

【核心】卷积核是 CNN 中可学习的局部特征检测器。

### 0.1.5 Feature Map 特征图

卷积层输出的结果叫特征图。

低层特征图可能表示：

- 边缘。
- 颜色变化。
- 纹理。

高层特征图可能表示：

- 眼睛。
- 轮廓。
- 物体部件。

### 0.1.6 Pooling 池化

池化用于压缩特征图大小。

常见：

- Max Pooling
- Average Pooling

作用：

- 降低计算量。
- 提高对小范围位置变化的鲁棒性。
- 保留重要特征。

### 0.1.7 RNN

RNN 是 Recurrent Neural Network，循环神经网络。

它用于处理序列数据。

序列数据特点：

```text
当前元素的含义和前后顺序有关。
```

例如：

- 文本。
- 时间序列。
- 语音。
- 用户行为序列。

【核心】RNN 通过隐藏状态保存历史信息。

### 0.1.8 Hidden State 隐藏状态

隐藏状态是 RNN 记忆历史信息的向量。

每一步输入后，RNN 更新隐藏状态：

```text
当前输入 + 上一步隐藏状态 -> 新隐藏状态
```

【重点】隐藏状态是 RNN 处理序列的核心。

### 0.1.9 LSTM / GRU

普通 RNN 容易遇到长距离依赖问题。

LSTM 和 GRU 是改进结构，用门控机制控制信息保留和遗忘。

适合：

- 较长文本。
- 时间序列。
- 需要记忆历史上下文的任务。

【重点】LSTM/GRU 曾是 NLP 主流结构，但大模型时代主要由 Transformer 接替。

### 0.1.10 Transformer

Transformer 是现代大模型的核心结构。

它不依赖循环逐步处理序列，而是通过 Attention 机制直接建模序列中任意位置之间的关系。

【核心】Transformer 是大模型的基础架构。

### 0.1.11 Attention 注意力机制

Attention 的直觉是：

```text
处理当前位置时，模型应该关注序列中哪些其他位置？
```

例如句子：

```text
小明把书放进书包，因为它很重。
```

模型需要判断“它”指什么。

Attention 可以让模型在处理“它”时关注“书”。

### 0.1.12 Self-Attention 自注意力

Self-Attention 是序列内部各位置之间互相关注。

每个 token 都可以看其他 token，并计算相关性。

【核心】Self-Attention 让 Transformer 能建模长距离依赖。

### 0.1.13 Token

Token 是文本被模型处理的基本单位。

它可能是：

- 一个词。
- 一个子词。
- 一个字符片段。
- 一个标点。

【重点】大模型不是直接处理原始字符串，而是先把文本切成 token。

### 0.1.14 Embedding

Embedding 把 token 转成向量。

Transformer 处理的是向量序列，不是原始文本。

```text
文本 -> token -> embedding -> Transformer
```

### 0.1.15 Positional Encoding 位置编码

Transformer 本身没有 RNN 的顺序处理机制，因此需要位置编码告诉模型 token 顺序。

【重点】没有位置信息，Transformer 很难区分词序。

### 0.1.16 Encoder / Decoder

Transformer 常见结构包括：

- Encoder：理解输入。
- Decoder：生成输出。

模型类型：

| 类型 | 示例任务 |
|---|---|
| Encoder-only | 文本分类、理解 |
| Decoder-only | 文本生成、大语言模型 |
| Encoder-Decoder | 翻译、摘要 |

【核心】GPT 类模型通常是 Decoder-only Transformer。

### 0.1.17 本课重点标注汇总

【核心】CNN 擅长局部空间特征，典型用于图像。

【核心】RNN 擅长序列建模，通过隐藏状态传递历史信息。

【核心】Transformer 通过 Self-Attention 建模序列中任意位置关系，是大模型基础。

【重点】卷积核是可学习的局部特征检测器。

【重点】Attention 解决的是“当前处理位置应该关注哪里”的问题。

【重点】Token 和 Embedding 是文本进入模型前的关键转换。

【易错】Transformer 不是只用于文本，也可扩展到图像、语音、多模态。

### 0.1.18 自我检查问题

1. CNN 为什么适合图像？
2. 卷积核做什么？
3. 特征图是什么？
4. RNN 为什么适合序列？
5. 隐藏状态是什么？
6. LSTM/GRU 解决什么问题？
7. Transformer 为什么适合大模型？
8. Attention 的直觉是什么？
9. Self-Attention 和普通 Attention 有什么关系？
10. Token、Embedding、位置编码分别解决什么问题？

## 1. 本课目标

学完本课后，你应该能够：

1. 解释 CNN、RNN、Transformer 分别适合什么数据。
2. 理解卷积、卷积核、特征图、池化。
3. 理解序列、隐藏状态、LSTM/GRU。
4. 理解 Attention、Self-Attention、Token、Embedding、位置编码。
5. 解释为什么 Transformer 是现代大模型基础。

## 2. 三类结构对比

| 结构 | 擅长数据 | 核心思想 | 典型应用 |
|---|---|---|---|
| CNN | 图像、局部空间结构 | 卷积提取局部特征 | 图像分类、目标检测 |
| RNN | 序列 | 隐藏状态传递历史 | 文本、语音、时间序列 |
| Transformer | 序列和多模态 | Attention 建模全局关系 | 大模型、翻译、摘要 |

## 3. CNN 详解

CNN 利用图像的局部性：

```text
边缘 -> 纹理 -> 部件 -> 物体
```

网络越深，特征越抽象。

【工程经验】CNN 仍然是很多视觉任务的重要基础，即使现在视觉 Transformer 也很流行。

## 4. RNN 详解

RNN 逐步读取序列：

```text
x1 -> h1
x2 + h1 -> h2
x3 + h2 -> h3
```

问题：

- 训练难。
- 长距离依赖弱。
- 难以并行。

这些问题推动了 Transformer 的流行。

## 5. Transformer 详解

Transformer 用 Self-Attention 让每个 token 直接关注其他 token。

优势：

- 并行能力强。
- 长距离依赖更好。
- 可扩展到大规模数据和参数。

【核心】大语言模型的核心能力建立在 Transformer 可扩展性上。

## 6. 从文本到 Transformer

流程：

```text
原始文本
  -> Tokenization
  -> Token IDs
  -> Embedding
  -> Positional Encoding
  -> Transformer Blocks
  -> 输出概率或表示
```

【重点】模型真正处理的是数字向量，不是原始文字。

## 7. 常见误区

1. 以为 CNN 只能用于图片。它也可用于一维信号。
2. 以为 RNN 已经完全没用。它仍可用于小型序列任务。
3. 以为 Transformer 不需要位置信息。
4. 以为 Attention 就是简单关键词匹配。
5. 以为大模型只靠结构，忽略数据和训练规模。

## 8. 代码辅助示例

### 8.1 CNN 层形状直觉

```python
import torch
from torch import nn

x = torch.randn(8, 3, 32, 32)
conv = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3)
y = conv(x)

print(y.shape)
```

含义：

```text
8：batch size
3：输入通道
32x32：图像大小
16：输出特征图通道数
```

### 8.2 Transformer 输入直觉

```python
import torch
from torch import nn

embedding = nn.Embedding(num_embeddings=10000, embedding_dim=128)
token_ids = torch.tensor([[1, 23, 456, 78]])
x = embedding(token_ids)

print(x.shape)
```

含义：

```text
token id -> embedding 向量
```

## 9. 本课实践任务

1. 用自己的话解释 CNN、RNN、Transformer。
2. 画出 CNN 从图像到特征图的流程。
3. 画出 RNN 隐藏状态传递流程。
4. 画出文本进入 Transformer 的流程。
5. 解释为什么 Transformer 成为大模型主流。

## 10. 自测题

1. CNN 为什么适合图像？
2. Pooling 有什么作用？
3. RNN 的隐藏状态是什么？
4. LSTM/GRU 为什么出现？
5. Self-Attention 解决什么问题？
6. Token 和 Embedding 有什么区别？
7. 位置编码为什么重要？
8. GPT 类模型通常属于哪种 Transformer 结构？

## 11. 阶段验收标准

完成本课后，你应该能做到：

1. 能区分 CNN、RNN、Transformer。
2. 能解释卷积、池化、特征图。
3. 能解释隐藏状态和序列建模。
4. 能解释 Attention 和 Self-Attention。
5. 能说明 Transformer 和大模型的关系。

## 12. 本课使用的信息源

- PyTorch Neural Networks Tutorial：神经网络层、CNN 基础。
- PyTorch Sequence Models and LSTM Tutorial：RNN/LSTM、序列建模。
- PyTorch Transformer 文档：Transformer API 和结构。
- Hugging Face LLM Course：Transformer 和大模型学习路径。
- The Illustrated Transformer：Transformer 和 Self-Attention 直觉解释。

