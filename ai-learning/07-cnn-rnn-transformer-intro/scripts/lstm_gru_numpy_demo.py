# -*- coding: utf-8 -*-
"""
第 7 课 · 小节 0.1.9 配套：LSTM 与 GRU 单步更新，仅用 NumPy（对照上一节的 vanilla RNN）

对应任务：
  - 看清「门控」在数值上做了什么：LSTM 拆成 **细胞状态 c** 与 **隐藏状态 h**；GRU 用 **复位门 r**、**更新门 z** 把参数收紧到更少矩阵。
  - 同一随机种子、同一输入序列下，对比三类单元（若后续扩展）或至少跑通 LSTM 与 GRU 的前向轨迹。

数据从哪读：
  - 不读外部文件。构造长度 T=5、每步 input_dim 维的 x_seq；权重用固定随机种子初始化，便于复现。

张量含义：
  - x_t：(input_dim,) 当前步输入，可理解为 embedding 后的 token。
  - h：(hidden_dim,) 隐藏状态；LSTM 另需 c：(hidden_dim,) **细胞状态**（长期记忆槽，与 h 分离）。
  - 拼接向量 hx = concat(h, x)，形状 (hidden_dim + input_dim,)，一次线性层吃完整「旧状态 + 新输入」。

代码段说明：
  1) sigmoid / lstm_step / gru_step：标准向量式前向（与 PyTorch 默认公式同族，细节以本文件为准）。
  2) main：先 lstm 再 gru，各自从 h=0、c=0 起步，逐步打印 h 的 L2 范数。
"""

from __future__ import print_function

import sys

import numpy as np


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def lstm_step(x_t, h_prev, c_prev, w_i, w_f, w_o, w_g, b_i, b_f, b_o, b_g):
    """
    单步 LSTM。``w_*`` 形状均为 (hidden_dim, hidden_dim + input_dim)；
    hx = concat(h_prev, x_t)，列向量语义在 numpy 里为 1d。
    i,f,o 经 sigmoid；g 经 tanh；c_new = f*c_prev + i*g；h_new = o*tanh(c_new)。
    """
    hx = np.concatenate([h_prev, x_t])
    i_gate = sigmoid(np.dot(w_i, hx) + b_i)
    f_gate = sigmoid(np.dot(w_f, hx) + b_f)
    o_gate = sigmoid(np.dot(w_o, hx) + b_o)
    g_gate = np.tanh(np.dot(w_g, hx) + b_g)
    c_new = f_gate * c_prev + i_gate * g_gate
    h_new = o_gate * np.tanh(c_new)
    return h_new, c_new


def gru_step(x_t, h_prev, w_z, w_r, w_n, b_z, b_r, b_n):
    """
    单步 GRU（与常见「concat(h,x) 算门，n 用 r*h 与 x 拼接」写法一致）。
    z,r：sigmoid；n：tanh；h_new = (1-z)*h_prev + z*n。
    ``w_z`` ``w_r``：(hidden_dim, hidden_dim + input_dim)；
    ``w_n``：(hidden_dim, hidden_dim + input_dim)，输入为 concat(r*h_prev, x_t)。
    """
    hx = np.concatenate([h_prev, x_t])
    z_gate = sigmoid(np.dot(w_z, hx) + b_z)
    r_gate = sigmoid(np.dot(w_r, hx) + b_r)
    rx = np.concatenate([r_gate * h_prev, x_t])
    n_gate = np.tanh(np.dot(w_n, rx) + b_n)
    h_new = (1.0 - z_gate) * h_prev + z_gate * n_gate
    return h_new


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    np.random.seed(11)
    input_dim = 4
    hidden_dim = 5
    t_len = 5
    dim_hx = hidden_dim + input_dim

    x_seq = np.random.randn(t_len, input_dim).astype(np.float32) * 0.4

    scale = 0.25
    w_i = np.random.randn(hidden_dim, dim_hx).astype(np.float32) * scale
    w_f = np.random.randn(hidden_dim, dim_hx).astype(np.float32) * scale
    w_o = np.random.randn(hidden_dim, dim_hx).astype(np.float32) * scale
    w_g = np.random.randn(hidden_dim, dim_hx).astype(np.float32) * scale
    b_i = np.zeros(hidden_dim, dtype=np.float32)
    b_f = np.ones(hidden_dim, dtype=np.float32) * 0.5
    b_o = np.zeros(hidden_dim, dtype=np.float32)
    b_g = np.zeros(hidden_dim, dtype=np.float32)

    w_z = np.random.randn(hidden_dim, dim_hx).astype(np.float32) * scale
    w_r = np.random.randn(hidden_dim, dim_hx).astype(np.float32) * scale
    w_n = np.random.randn(hidden_dim, dim_hx).astype(np.float32) * scale
    b_z = np.zeros(hidden_dim, dtype=np.float32)
    b_r = np.zeros(hidden_dim, dtype=np.float32)
    b_n = np.zeros(hidden_dim, dtype=np.float32)

    np.set_printoptions(precision=4, suppress=True, linewidth=120)
    print('==== LSTM：c 与 h 分离；f 门保留旧 c，i 门写入新内容 ====')
    h = np.zeros(hidden_dim, dtype=np.float32)
    c = np.zeros(hidden_dim, dtype=np.float32)
    for t in range(t_len):
        x_t = x_seq[t]
        h, c = lstm_step(x_t, h, c, w_i, w_f, w_o, w_g, b_i, b_f, b_o, b_g)
        print(
            't=%d | h L2=%.4f | c L2=%.4f | h=%s'
            % (t, float(np.linalg.norm(h)), float(np.linalg.norm(c)), str(h))
        )

    print('')
    print('==== GRU：无单独 c；z 在「旧 h」与「候选 n」之间插值 ====')
    h2 = np.zeros(hidden_dim, dtype=np.float32)
    for t in range(t_len):
        x_t = x_seq[t]
        h2 = gru_step(x_t, h2, w_z, w_r, w_n, b_z, b_r, b_n)
        print('t=%d | h L2=%.4f | h=%s' % (t, float(np.linalg.norm(h2)), str(h2)))


if __name__ == '__main__':
    main()
