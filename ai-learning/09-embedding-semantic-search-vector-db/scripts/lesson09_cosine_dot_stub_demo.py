# -*- coding: utf-8 -*-
"""
第 9 课 · 小节 0.1.7～0.1.9 配套：玩具向量上的 **点积** 与 **余弦相似度**

对应任务：
  - 建立 **「相似度 = 在向量几何里选一种度量」** 的直觉；线上须与 **Embedding 模型 / 向量库** 推荐保持一致。
  - 观察：**未单位化** 时，点积会受 **长度** 影响；余弦主要看 **方向**。

数据从哪读：
  - 写死的 3 组二维向量，仅为手算友好；真实维度通常是 **数百～数千**。

公式（本脚本直接实现）：
  - 点积：dot(a, b) = sum_i a_i * b_i
  - 余弦：cos(a, b) = dot(a, b) / (||a|| * ||b||)，分母为 0 时本脚本打印「未定义」
"""

from __future__ import print_function

import math
import sys


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(sum(x * x for x in a))


def cosine(a, b):
    na = norm(a)
    nb = norm(b)
    if na == 0.0 or nb == 0.0:
        return None
    return dot(a, b) / (na * nb)


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    pairs = (
        ('同向放大', [1.0, 0.0], [2.0, 0.0]),
        ('正交', [1.0, 0.0], [0.0, 1.0]),
        ('反向', [1.0, 0.0], [-1.0, 0.0]),
    )

    print('=== 玩具向量：点积 vs 余弦（二维；仅教学）===\n')
    for label, u, v in pairs:
        d = dot(u, v)
        c = cosine(u, v)
        c_str = '未定义（零向量）' if c is None else '{:.6f}'.format(c)
        print(label + '  u=' + str(u) + ' v=' + str(v))
        print('  dot=' + str(d) + '  cosine=' + c_str)
        print('')


if __name__ == '__main__':
    main()
