# -*- coding: utf-8 -*-
"""
第 7 课 · 小节 0.1.13～0.1.14 配套：极简「按空白切词」→ token id → 查表得到 Embedding 矩阵 X

对应任务：
  - 看清链路：原始字符串 **不是** Transformer 的直接输入；要先 **离散化**（token id），再 **嵌入**（连续向量）。
  - 与 **`self_attention_numpy_demo.py`** 衔接：本脚本输出的 **X (T, d_embed)** 即为后续自注意力里的 **X**（再加位置编码等，本演示略）。

数据从哪读：
  - 不读外部文件。在代码里写死一句示例中文句；用 **str.split()** 做玩具级分词（**非** BPE/SentencePiece，仅供形状直觉）。

张量含义：
  - token_ids：长度 T 的整型列表，元素范围 [0, vocab_size)。
  - embedding_table：形状 (vocab_size, d_embed)，第 i 行是 id 为 i 的 token 的向量（类比 PyTorch ``nn.Embedding`` 权重）。
  - X：形状 (T, d_embed)，第 t 行是第 t 个 token 的 embedding；即 stacking embedding_table[token_ids[t]]。

代码段说明：
  1) word_tokenize Toy：空白分词 + 建 ``token2id``；``<UNK>`` 仅占位，本句无未知词。
  2) main：固定随机种子，打印词表、ids、X 前两行的 L2 范数。
"""

from __future__ import print_function

import sys

import numpy as np


def build_vocab_and_tokenize(sentence):
    """
    按空白切词，稳定排序得到词表；返回 (tokens, token2id)。
    """
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


def token_ids_from_tokens(tokens, token2id, unk_id):
    ids = []
    for w in tokens:
        if w in token2id:
            ids.append(token2id[w])
        else:
            ids.append(unk_id)
    return ids


def embed_ids(ids, embedding_table):
    """``ids`` 为 list of int；返回 (T, d_embed)。"""
    rows = [embedding_table[i] for i in ids]
    return np.stack(rows, axis=0)


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    sentence = '小明 把 书 放进 书包 因为 它 很重'
    tokens, token2id, unk_id = build_vocab_and_tokenize(sentence)
    ids = token_ids_from_tokens(tokens, token2id, unk_id)

    np.random.seed(23)
    vocab_size = len(token2id)
    d_embed = 8
    embedding_table = np.random.randn(vocab_size, d_embed).astype(np.float32) * 0.2
    x = embed_ids(ids, embedding_table)

    np.set_printoptions(precision=4, suppress=True, linewidth=120)
    print('玩具分词（仅按空白切；真实大模型用 BPE 等）')
    print('句子：' + sentence)
    print('tokens (%d): ' % len(tokens) + str(tokens))
    print('词表大小（含 <UNK>）=%d' % vocab_size)
    print('token_ids: ' + str(ids))
    print('')
    print('X 形状 (T, d_embed) = ' + str(x.shape))
    print('第 0、2 行 L2 范数：' + str(float(np.linalg.norm(x[0]))) + ', ' + str(float(np.linalg.norm(x[2]))))
    print('X[0] = ' + str(x[0]))


if __name__ == '__main__':
    main()
