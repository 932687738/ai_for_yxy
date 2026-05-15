# -*- coding: utf-8 -*-
"""
第 7 课 · 小节 0.1.17～0.1.18 配套收官：从「按空白切词」到「一层自注意力输出」的迷你流水线（NumPy）

对应任务：
  - 把 **`token_embedding_lookup_numpy_demo.py`**、**`sinusoidal_positional_encoding_numpy_demo.py`**、**`self_attention_numpy_demo.py`** 三条链路 **串成一条**，在单一脚本里跑通 **形状与数据流**。
  - 适合作为 **0.1.18** 自测前的「整图复习」，不包含训练、不含 PyTorch。

数据从哪读：
  - 不读外部文件。示例句写死在 ``main``；词表由句中首次出现顺序构造；``<UNK>`` 仅占位。

张量流转（每步形状在注释中标明）：
  1) tokens -> token_ids：长度 T 的 int 列表。
  2) X_emb = E[token_ids]：(T, d_model)。
  3) PE = sinusoidal_pe[:T, :]：(T, d_model)；X = X_emb + PE。
  4) Q = X @ W_Q，K = X @ W_K，V = X @ W_V；(T, d_k)。
  5) softmax(Q K^T / sqrt(d_k)) @ V -> context：(T, d_k)。

代码段说明：
  - 为减少跨文件依赖，本文件 **内联** 最小子函数（与前几脚本公式一致）。
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


def build_vocab_tokenize(sentence):
    tokens = sentence.split()
    unique = []
    seen = set()
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    token2id = {}
    for i, w in enumerate(unique):
        token2id[w] = i
    unk_id = len(unique)
    token2id['<UNK>'] = unk_id
    return tokens, token2id, unk_id


def to_ids(tokens, token2id, unk_id):
    return [token2id[w] if w in token2id else unk_id for w in tokens]


def sinusoidal_pe(max_len, d_model):
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

    sentence = '小明 把 书 放进 书包'
    tokens, token2id, unk_id = build_vocab_tokenize(sentence)
    ids = to_ids(tokens, token2id, unk_id)

    np.random.seed(41)
    t_len = len(ids)
    d_model = 8
    d_k = 6
    vocab_size = len(token2id)

    e_mat = np.random.randn(vocab_size, d_model).astype(np.float32) * 0.2
    x_emb = np.stack([e_mat[i] for i in ids], axis=0)
    pe = sinusoidal_pe(32, d_model)[:t_len, :]
    x = x_emb + pe

    w_q = np.random.randn(d_model, d_k).astype(np.float32) * 0.25
    w_k = np.random.randn(d_model, d_k).astype(np.float32) * 0.25
    w_v = np.random.randn(d_model, d_k).astype(np.float32) * 0.25

    q = np.dot(x, w_q)
    k_mat = np.dot(x, w_k)
    v_mat = np.dot(x, w_v)
    ctx, wgt = attention(q, k_mat, v_mat)

    np.set_printoptions(precision=3, suppress=True, linewidth=120)
    print('第 7 课 · 0.1 收官流水线：「分词→id→E→+PE→QKV→Attention」')
    print('句子：' + sentence)
    print('T=%d | d_model=%d | d_k=%d' % (t_len, d_model, d_k))
    print('注意力权重第一行（应和为 1）：' + str(wgt[0]))
    print('context 形状 ' + str(ctx.shape))


if __name__ == '__main__':
    main()
