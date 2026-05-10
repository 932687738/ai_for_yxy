# 第 6 课：深度学习与 PyTorch 基础

## 0. 本课阅读方式

本课开始进入深度学习。你不需要一开始就掌握复杂网络结构，而要先理解深度学习训练的基本部件：

```text
Tensor
神经网络层
前向传播
损失函数
反向传播
梯度
优化器
训练循环
```

建议学习顺序：

```text
先理解深度学习和传统机器学习的区别
  -> 理解 PyTorch Tensor
  -> 理解计算图和自动求导
  -> 理解 nn.Module
  -> 理解训练循环
  -> 最后运行一个最小神经网络
```

【核心】PyTorch 不是“高级 NumPy”，它的关键价值是张量计算 + 自动求导 + 神经网络组件。

## 0.1 概念讲义：深度学习与 PyTorch 术语详解

### 0.1.1 第 6 课到底在学什么

深度学习是使用多层神经网络从数据中学习复杂规律。

和传统机器学习相比：

```text
传统机器学习：
  更依赖人工特征工程。

深度学习：
  可以从原始或低层特征中逐层学习更复杂表示。
```

【重点】深度学习不是完全不需要特征工程，而是把大量表示学习交给神经网络完成。

### 0.1.2 Deep Learning 深度学习

深度学习是机器学习的一个分支，核心是多层神经网络。

适合：

- 图像识别。
- 语音识别。
- 自然语言处理。
- 大模型。
- 多模态理解。

【核心】大模型本质上也是深度学习模型，只是规模更大、数据更多、结构更复杂。

### 0.1.3 Neural Network 神经网络

神经网络由层组成，每一层对输入做变换。

简化结构：

```text
输入层 -> 隐藏层 -> 输出层
```

每一层通常包含：

- 权重。
- 偏置。
- 激活函数。

【核心】神经网络通过多层变换学习复杂函数。

### 0.1.4 Tensor 张量

Tensor 是 PyTorch 中最核心的数据结构。

它可以表示：

```text
标量
向量
矩阵
高维数组
```

在深度学习中：

- 输入数据是 Tensor。
- 模型参数是 Tensor。
- 中间结果是 Tensor。
- 梯度也是 Tensor。

【核心】PyTorch 中几乎所有计算都围绕 Tensor 进行。

### 0.1.5 shape、dtype、device

Tensor 有三个重要属性：

| 属性 | 含义 |
|---|---|
| shape | 形状，例如 `(batch_size, features)` |
| dtype | 数据类型，例如 `float32`、`int64` |
| device | 计算设备，例如 CPU、CUDA GPU |

【易错】深度学习报错最常见原因之一是 shape、dtype 或 device 不匹配。

### 0.1.6 Batch

Batch 是一次送入模型的一批样本。

为什么不用所有数据一次训练？

- 数据太大。
- 内存不够。
- 小批量训练更高效。
- 梯度更新更频繁。

【重点】训练循环通常按 batch 迭代，而不是一次处理全部数据。

### 0.1.7 Forward Pass 前向传播

前向传播是输入经过模型得到预测结果的过程。

```text
X -> model -> y_pred
```

【核心】前向传播回答“当前参数下，模型预测什么”。

### 0.1.8 Loss 损失

损失衡量预测值和真实值之间的差距。

例如：

- 回归常用 MSELoss。
- 分类常用 CrossEntropyLoss。

【核心】训练目标是降低损失。

### 0.1.9 Backward Pass 反向传播

反向传播根据损失计算每个参数的梯度。

```python
loss.backward()
```

【核心】反向传播回答“每个参数应该如何调整才能降低损失”。

### 0.1.10 Autograd 自动求导

Autograd 是 PyTorch 自动计算梯度的机制。

你只需要定义前向计算和损失，PyTorch 会根据计算图自动计算梯度。

【重点】PyTorch 训练代码中通常不手写复杂导数。

### 0.1.11 Computational Graph 计算图

计算图记录 Tensor 运算之间的依赖关系。

例如：

```text
x -> w*x + b -> loss
```

PyTorch 根据计算图反向传播梯度。

【核心】自动求导依赖计算图。

### 0.1.12 Parameter 参数

参数是模型需要学习的 Tensor。

在 PyTorch 中，`nn.Linear` 内部有：

- weight
- bias

这些就是可训练参数。

### 0.1.13 Optimizer 优化器

优化器根据梯度更新参数。

常见优化器：

- SGD
- Adam

训练中常见步骤：

```python
optimizer.zero_grad()
loss.backward()
optimizer.step()
```

【核心】优化器负责真正修改模型参数。

### 0.1.14 nn.Module

`nn.Module` 是 PyTorch 中定义模型的基础类。

一个模型通常继承 `nn.Module`，并实现 `forward` 方法。

【重点】模型结构定义在 `__init__` 中，前向计算定义在 `forward` 中。

### 0.1.15 Activation Function 激活函数

激活函数给神经网络引入非线性。

常见激活函数：

- ReLU
- Sigmoid
- Tanh

【核心】如果没有非线性激活，多层线性层仍然等价于一个线性变换。

### 0.1.16 Epoch

Epoch 表示完整遍历训练集一次。

例如：

```text
训练 10 个 epoch = 模型完整看训练集 10 遍
```

### 0.1.17 Learning Rate

学习率控制每次参数更新步长。

【易错】学习率太大可能发散，太小训练很慢。

### 0.1.18 state_dict

`state_dict` 是 PyTorch 保存模型参数的常用方式。

它包含模型中可学习参数的名称和值。

【工程经验】通常保存 `state_dict`，而不是直接保存整个模型对象。

### 0.1.19 本课重点标注汇总

【核心】Tensor 是 PyTorch 的基本数据结构。

【核心】前向传播产生预测，损失函数衡量错误，反向传播计算梯度，优化器更新参数。

【核心】自动求导是 PyTorch 的关键能力。

【核心】`nn.Module` 是定义神经网络模型的基础。

【重点】训练循环的顺序不能乱：清梯度、前向、算损失、反向、更新。

【易错】shape、dtype、device 不匹配是 PyTorch 常见错误。

### 0.1.20 自我检查问题

1. 深度学习和传统机器学习有什么区别？
2. Tensor 是什么？
3. shape、dtype、device 分别代表什么？
4. 前向传播做什么？
5. 损失函数做什么？
6. 反向传播做什么？
7. Autograd 解决什么问题？
8. 优化器做什么？
9. `nn.Module` 的作用是什么？
10. 为什么训练前要 `optimizer.zero_grad()`？

## 1. 本课目标

学完本课后，你应该能够：

1. 解释深度学习和神经网络的基本思想。
2. 理解 PyTorch Tensor、shape、dtype、device。
3. 理解自动求导、计算图、梯度。
4. 理解 `nn.Module`、层、前向传播。
5. 理解损失函数和优化器。
6. 能读懂 PyTorch 基础训练循环。
7. 能保存和加载模型参数。

## 2. PyTorch 训练主线

```text
准备数据
  -> 转成 Tensor
  -> 定义模型 nn.Module
  -> 定义损失函数
  -> 定义优化器
  -> for epoch:
       for batch:
         前向传播
         计算 loss
         清空梯度
         反向传播
         更新参数
```

【核心】所有 PyTorch 训练代码都可以先按这条主线理解。

## 3. Tensor 基础

Tensor 类似 NumPy 数组，但支持 GPU 计算和自动求导。

最重要的不是记 API，而是随时检查：

```python
print(x.shape)
print(x.dtype)
print(x.device)
```

【重点】深度学习中，数据格式正确比模型复杂更优先。

## 4. 自动求导

PyTorch 可以自动计算梯度。

简化理解：

```text
你定义计算过程
PyTorch 记录计算图
调用 backward
PyTorch 自动计算每个参数的梯度
```

【易错】只有参与计算图且需要梯度的 Tensor 才会有 `.grad`。

## 5. 神经网络模型

使用 `nn.Module` 定义模型。

```python
import torch
from torch import nn


class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(3, 1)

    def forward(self, x):
        return self.linear(x)
```

你要理解：

```text
__init__ 定义层。
forward 定义数据如何流动。
nn.Linear(3, 1) 表示 3 个输入特征，1 个输出。
```

## 6. 训练循环

典型训练循环：

```python
for epoch in range(epochs):
    y_pred = model(X)
    loss = loss_fn(y_pred, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

顺序解释：

1. 前向传播得到预测。
2. 计算损失。
3. 清空上一轮梯度。
4. 反向传播计算新梯度。
5. 优化器更新参数。

【核心】这五步是 PyTorch 训练代码的骨架。

## 7. 模型保存

常见保存方式：

```python
torch.save(model.state_dict(), "model.pth")
```

加载：

```python
model.load_state_dict(torch.load("model.pth"))
model.eval()
```

【工程经验】推理前使用 `model.eval()`，训练前使用 `model.train()`。

## 8. 常见误区

1. 不检查 shape。
2. 标签 dtype 错误。
3. 输入和模型不在同一 device。
4. 忘记清空梯度。
5. 训练和推理模式混用。
6. 以为 loss 下降就一定业务效果好。

## 9. 代码辅助示例

```python
import torch
from torch import nn

X = torch.tensor([
    [80.0, 2.0, 10.0],
    [100.0, 3.0, 8.0],
    [120.0, 3.0, 5.0],
])
y = torch.tensor([[120.0], [150.0], [180.0]])

model = nn.Linear(3, 1)
loss_fn = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.00001)

for epoch in range(100):
    y_pred = model(X)
    loss = loss_fn(y_pred, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

print(model(X))
```

这段代码验证的是训练循环，不是推荐的生产模型写法。

## 10. 自测题

1. Tensor 和 NumPy 数组有什么不同？
2. 计算图有什么作用？
3. `loss.backward()` 做了什么？
4. `optimizer.step()` 做了什么？
5. 为什么要清空梯度？
6. `model.train()` 和 `model.eval()` 有什么区别？

## 11. 阶段验收标准

完成本课后，你应该能做到：

1. 能解释深度学习训练流程。
2. 能解释 Tensor、Autograd、nn.Module。
3. 能读懂基础 PyTorch 训练循环。
4. 能说明损失函数和优化器作用。
5. 能识别 shape、dtype、device 常见错误。

## 12. 本课使用的信息源

- PyTorch Beginner Basics：入门整体结构。
- PyTorch Tensors Tutorial：Tensor、shape、dtype、device。
- PyTorch Autograd Tutorial：自动求导和计算图。
- PyTorch Build Model Tutorial：`nn.Module` 和模型定义。
- PyTorch Optimization Tutorial：损失函数、优化器、训练循环。
- PyTorch Saving and Loading Models：`state_dict`、保存和加载模型。

