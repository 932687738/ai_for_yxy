# -*- coding: utf-8 -*-
"""
第 7 课 · 小节 0.1.11～0.1.12 配套：自注意力（单头）——从同一序列 X 学出 Q、K、V，再缩放点积注意力

对应任务：
  - 把「注意力权重」与 **0.1.10** 的 demo 接上：此处 Q、K、V 不是随机矩阵，而是由 **X (T, d_model)** 经三个线性层 **W_Q、W_K、W_V** 映射得到（形状统一到 d_k，便于点积）。
  - 体会 **Self-Attention**：三个投影矩阵作用在 **同一批 token 向量** 上，相关性由 **Q 与 K** 决定，**聚合内容**来自 **V**。

数据从哪读：
  - 不读外部文件。构造 X 为 (T, d_model) 的随机矩阵，模拟已 embedding 并叠过位置信息后的输入（本脚本不单独实现位置编码）。

张量含义：
  - X：行 t 为第 t 个位置的 d_model 维向量。
  - Q = X @ W_Q，K = X @ W_K，V = X @ W_V；W_* 形状 (d_model, d_k)，故 Q、K、V 均为 (T, d_k)。
  - 之后与 ``scaled_dot_product_attention_numpy_demo.py`` 相同：scores = Q K^T / sqrt(d_k)，行 softmax，乘 V 得 context (T, d_k)。

代码段说明：
  1) softmax_rows / attention：与前一脚本一致，避免复制可 import——为单文件可运行，少量重复保留。
  2) main：打印 X 一行范数、权重矩阵、context 形状。
"""

from __future__ import print_function

import math
import sys

import numpy as np


def softmax_rows(mat):
    shifted = mat - np.max(mat, axis=1, keepdims=True)
    ex = np.exp(shifted)
    return ex / np.sum(ex, axis=1, keepdims=True)


def attention(q, k, v):
    d_k = q.shape[1]
    scores = np.dot(q, k.T) / math.sqrt(float(d_k))
    weights = softmax_rows(scores)
    context = np.dot(weights, v)
    return context, weights


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    np.random.seed(17)
    t_len = 4
    d_model = 6
    d_k = 4

    x = np.random.randn(t_len, d_model).astype(np.float32) * 0.35
    w_q = np.random.randn(d_model, d_k).astype(np.float32) * 0.3
    w_k = np.random.randn(d_model, d_k).astype(np.float32) * 0.3
    w_v = np.random.randn(d_model, d_k).astype(np.float32) * 0.3

    q = np.dot(x, w_q)
    k = np.dot(x, w_k)
    v = np.dot(x, w_v)

    ctx, w = attention(q, k, v)

    np.set_printoptions(precision=4, suppress=True, linewidth=120)
    print('自注意力（单头）：T=%d, d_model=%d, d_k=%d' % (t_len, d_model, d_k))
    print('X 各行 L2 范数：' + str(np.linalg.norm(x, axis=1)))
    print('')
    print('注意力权重（行 softmax，和为 1）：')
    print(w)
    print('')
    print('context 形状 ' + str(ctx.shape) + '（与 Q、K、V 行数一致）：')
    print(ctx)


if __name__ == '__main__':
    main()
