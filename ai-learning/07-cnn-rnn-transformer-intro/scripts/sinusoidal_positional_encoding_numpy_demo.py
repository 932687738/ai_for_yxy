# -*- coding: utf-8 -*-
"""
第 7 课 · 小节 0.1.15 配套：《Attention Is All You Need》正弦位置编码，并与 token embedding 相加

对应任务：
  - 看清「无 RNN 即无内置顺序」时，如何用 **仅依赖位置下标 pos、维度下标 i** 的函数生成 **PE(pos, :)**，再与 **X_emb** 相加进入第一层注意力。
  - 与 **0.1.14** 衔接：本脚本前半构造玩具 **X_emb**；后半构造 **PE**，输出 **X = X_emb + PE**（与常见实现一致；RoPE、ALiBi 等是另一族，本课不立项）。

数据从哪读：
  - 不读外部文件。``T``、``d_model`` 在代码里给定；``X_emb`` 用固定种子随机，模拟已查表得到的 token 向量序列。

张量含义：
  - ``X_emb``：形状 (T, d_model)，第 t 行为第 t 个 token 的嵌入（未加位置）。
  - ``PE``：形状 (T, d_model) 或预先算 ``max_len`` 再截取前 T 行；第 t 行只依赖于 **整数位置 t**。
  - ``X``：``X_emb + PE``，作为「带序信息的输入」进入后续 **W_Q/W_K/W_V**（演示略）。

代码段说明：
  1) ``sinusoidal_pe_matrix``：对 pos=0..max_len-1、维 0..d_model-1 填充 sin/cos 公式（偶维 sin，奇维 cos，底数 10000）。
  2) ``main``：打印 ``PE`` 两行与 ``X`` 与 ``X_emb`` 的差（应等于对应 ``PE``）。
"""

from __future__ import print_function

import math
import sys

import numpy as np


def sinusoidal_pe_matrix(max_len, d_model):
    """
    形状 (max_len, d_model) 的正弦位置编码矩阵，与论文表述一致（偶列 sin，奇列 cos）。
    """
    pe = np.zeros((max_len, d_model), dtype=np.float64)
    position = np.arange(max_len, dtype=np.float64).reshape(max_len, 1)
    div_term = np.exp(
        np.arange(0, d_model, 2, dtype=np.float64) * (-math.log(10000.0) / float(d_model))
    )
    pe[:, 0::2] = np.sin(position * div_term)
    pe[:, 1::2] = np.cos(position * div_term)
    return pe.astype(np.float32)


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    t_len = 5
    d_model = 8
    max_len = 32

    np.random.seed(31)
    x_emb = np.random.randn(t_len, d_model).astype(np.float32) * 0.15
    pe = sinusoidal_pe_matrix(max_len, d_model)[:t_len, :]
    x_in = x_emb + pe

    np.set_printoptions(precision=4, suppress=True, linewidth=120)
    print('正弦位置编码：max_len=%d（截取前 T=%d）, d_model=%d' % (max_len, t_len, d_model))
    print('PE[0] = ' + str(pe[0]))
    print('PE[1] = ' + str(pe[1]))
    print('')
    print('X_emb[0] L2=%.4f | X_in[0] L2=%.4f（加 PE 后一般变化）' % (
        float(np.linalg.norm(x_emb[0])),
        float(np.linalg.norm(x_in[0])),
    ))
    print('验证：(X_in - X_emb)[0] ≈ PE[0] ：差 L2=%.6f' % float(np.linalg.norm(x_in[0] - x_emb[0] - pe[0])))


if __name__ == '__main__':
    main()
