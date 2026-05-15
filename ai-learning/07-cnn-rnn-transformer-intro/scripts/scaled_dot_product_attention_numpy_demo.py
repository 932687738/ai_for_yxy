# -*- coding: utf-8 -*-
"""
第 7 课 · 小节 0.1.10（并指向 0.1.11～0.1.12）配套：单头缩放点积注意力，仅用 NumPy

对应任务：
  - 用一个小矩阵算清：Attention 本质是「加权求和」，权重由 Q 与 K 的相似度经 softmax 得到，再乘 V。
  - 与 RNN 对照：一步内 **所有位置** 可互看（本演示长度为 T 的全连接注意力），无 h_{t-1} 递推。

数据从哪读：
  - 不读外部文件。固定 T=4、d_k=3，随机 Q、K、V（可改为手写小数以手算核对）。

张量含义：
  - Q, K, V：形状均为 (T, d_k)，行 t 表示第 t 个位置的查询 / 键 / 值（本演示直接用随机矩阵占位）。
  - scores：Q @ K^T，形状 (T, T)，scores[i,j] 表示位置 i 对位置 j 的未归一化相关度。
  - weights：对 scores 的每一行做 softmax，再除以 sqrt(d_k) 的缩放已在 softmax 前完成（标准 Transformer 写法）。

代码段说明：
  1) softmax_rows：数值稳定版 row-wise softmax。
  2) attention：返回 context（每行一个输出向量）与 weights 供打印。
"""

from __future__ import print_function

import math
import sys

import numpy as np


def softmax_rows(mat):
    """对二维 ``mat`` 按行做 softmax，`mat` 形状 (T, T)。"""
    shifted = mat - np.max(mat, axis=1, keepdims=True)
    ex = np.exp(shifted)
    return ex / np.sum(ex, axis=1, keepdims=True)


def attention(q, k, v):
    """缩放点积注意力，``q,k,v`` 均为 (T, d_k)，返回 (context, weights)。"""
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

    np.random.seed(3)
    t_len = 4
    d_k = 3
    q = np.random.randn(t_len, d_k).astype(np.float32) * 0.5
    k = np.random.randn(t_len, d_k).astype(np.float32) * 0.5
    v = np.random.randn(t_len, d_k).astype(np.float32) * 0.5

    ctx, w = attention(q, k, v)
    np.set_printoptions(precision=4, suppress=True, linewidth=120)
    print('单头缩放点积注意力：T=%d, d_k=%d' % (t_len, d_k))
    print('权重矩阵（每行和为 1，行 i 表示位置 i 对各位置的注意力）：')
    print(w)
    print('')
    print('输出 context（形状与 Q 相同，每行是 V 行的凸组合）：')
    print(ctx)


if __name__ == '__main__':
    main()
