# -*- coding: utf-8 -*-
"""
第 7 课 · 小节 0.1.7～0.1.8 配套：香草 RNN（vanilla RNN）逐步更新隐藏状态，仅用 NumPy

对应任务：
  - 把「序列 + 循环」落成一行公式：每一步用当前输入 x_t 与上一步隐藏向量 h_{t-1} 算出新的 h_t。
  - 与 0.1.8 勾连：打印每一步的 h_t 范数，直观看到「状态在随时间携带信息」。

数据从哪读：
  - 不读外部文件。构造长度 T=5 的输入序列，每步一个 input_dim 维向量（可理解为已 embedding 后的 token 向量）。

张量 / 向量含义：
  - x_seq：形状 (T, input_dim)，时间维在第 0 轴；x_seq[t] 即第 t 步的 x_t。
  - h：形状 (hidden_dim,)，每一步会被覆盖更新为新的隐藏状态 h_t。
  - W_xh：形状 (hidden_dim, input_dim)，把当前输入线性变到「隐藏空间」。
  - W_hh：形状 (hidden_dim, hidden_dim)，把上一步隐藏状态线性变换后与当前输入分支相加。
  - b：形状 (hidden_dim,)，偏置。
  - 更新式（本演示用的最常见标式之一）：
        h_t = tanh(W_xh @ x_t + W_hh @ h_{t-1} + b)
    其中 @ 为矩阵向量乘（NumPy 里 dot）。

代码段说明：
  1) rnn_step：单步前向，返回新的 h 与 tanh 前的 pre_activation（便于观察饱和程度）。
  2) main：h_0 取全零；对 t=0..T-1 顺序调用 rnn_step，逐步打印 h 的 L2 范数与向量本身。
"""

from __future__ import print_function

import sys

import numpy as np


def rnn_step(x_t, h_prev, w_xh, w_hh, b_vec):
    """
    单步香草 RNN：``x_t`` (input_dim,) ，``h_prev`` (hidden_dim,) ，返回 (h_new, pre_tanh)。
    pre_tanh 为进入 tanh 之前的加权和，用于教学观察（非训练回放不必保存）。
    """
    pre = np.dot(w_xh, x_t) + np.dot(w_hh, h_prev) + b_vec
    h_new = np.tanh(pre)
    return h_new, pre


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    np.random.seed(7)
    input_dim = 4
    hidden_dim = 5
    t_len = 5

    w_xh = np.random.randn(hidden_dim, input_dim).astype(np.float32) * 0.3
    w_hh = np.random.randn(hidden_dim, hidden_dim).astype(np.float32) * 0.3
    b_vec = np.zeros(hidden_dim, dtype=np.float32)

    x_seq = np.random.randn(t_len, input_dim).astype(np.float32) * 0.5
    h = np.zeros(hidden_dim, dtype=np.float32)

    np.set_printoptions(precision=4, suppress=True, linewidth=120)
    print(' Vanilla RNN demo: input_dim=' + str(input_dim) + ', hidden_dim=' + str(hidden_dim) + ', T=' + str(t_len))
    print(' 更新式: h_t = tanh(W_xh @ x_t + W_hh @ h_{t-1} + b)')
    print('')

    for t in range(t_len):
        x_t = x_seq[t]
        h, pre = rnn_step(x_t, h, w_xh, w_hh, b_vec)
        norm = float(np.linalg.norm(h))
        print('--- step t=' + str(t) + ' ---')
        print('x_t = ' + str(x_t))
        print('pre_tanh L2 = ' + str(float(np.linalg.norm(pre))) + ' | h_t L2 = ' + str(norm))
        print('h_t = ' + str(h))
        print('')


if __name__ == '__main__':
    main()
