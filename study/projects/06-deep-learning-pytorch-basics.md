# 项目 06：PyTorch 基础概念验收

对应课程：第 6 课《深度学习与 PyTorch 基础》

## 1. 项目目标

本项目验证你是否理解 PyTorch 训练的基本组成，而不是追求复杂模型效果。

## 2. 术语报告

创建：

```text
reports/pytorch_basics_concepts.md
```

解释：

- 深度学习
- 神经网络
- Tensor
- shape
- dtype
- device
- batch
- forward pass
- loss
- backward pass
- autograd
- computational graph
- optimizer
- nn.Module
- activation function
- epoch
- state_dict

## 3. 训练循环复述

用自己的话解释：

```python
optimizer.zero_grad()
loss.backward()
optimizer.step()
```

必须说明：

1. 为什么要清空梯度。
2. 反向传播计算什么。
3. 优化器更新什么。

## 4. 常见错误分析

说明下面错误分别可能是什么原因：

1. shape 不匹配。
2. dtype 不匹配。
3. CPU Tensor 和 GPU Tensor 混用。
4. loss 不下降。
5. 训练正常但推理结果不稳定。

## 5. 验收清单

- [ ] 能解释 Tensor。
- [ ] 能解释计算图。
- [ ] 能解释自动求导。
- [ ] 能解释 `nn.Module`。
- [ ] 能解释训练循环五步。
- [ ] 能解释 `model.train()` 和 `model.eval()`。

