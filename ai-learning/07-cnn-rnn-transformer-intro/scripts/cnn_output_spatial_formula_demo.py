# -*- coding: utf-8 -*-
"""
第 7 课 · 小节 0.1.3 配套：卷积在空间维「输出边长」的整数公式演示（不涉及矩阵乘加）

只回答一件事：给定输入边长 L、正方形核边长 K、对称 padding=P、stride=S（dilation=1），
单层卷积在空间一条边上的输出个数是多少？

与本课其它素材的关系：
  - ``cnn_valid_conv_numpy_demo.py`` 固定了 ``P=0, S=1`` 的 ``valid`` 情形，你看到输出从 8 变为 6。
  - 本脚本用同一公式套几组教材式数字：例如 ``P=1`` 可把 ``valid`` 缩水补回，
    ``S>1`` 会下采样特征图宽度/高度。

张量形状的直觉（本节只算长度，不向量化整张图）：
  - Conv2d 时 **高、宽两条边各自**套下面公式即可；通道数与本脚本无关。
"""

from __future__ import print_function


def conv_out_length(length_in, kernel, stride, padding):
    """单条空间边上：假设 dilation=1，与课上写的 floor((L+2P-K)/S)+1 等价（整数 //）。"""
    if length_in <= 0 or kernel <= 0 or stride <= 0 or padding < 0:
        raise ValueError(
            'length_in,kernel,stride,padding 需满足 L,K,S>0 且 P>=0，当前 '
            + str((length_in, kernel, stride, padding))
        )
    n = length_in + 2 * padding - kernel
    if n < 0:
        raise ValueError(
            '无法在 L=' + str(length_in) + ', K=' + str(kernel)
            + ', P=' + str(padding)
            + ' 下对齐核：核对输入（含膨胀为 1 的常见设定）太大了'
        )
    return n // stride + 1


def main():
    demos = [
        ('与 valid 脚本一致：8→6', dict(L=8, K=3, P=0, S=1)),
        ('仅加对称 pad=1，仍 K=3,S=1，常用来保持空间尺寸', dict(L=8, K=3, P=1, S=1)),
        ('下采样：stride=2', dict(L=8, K=3, P=1, S=2)),
        ('稍大一些的输入自检', dict(L=32, K=3, P=1, S=2)),
    ]

    for title, kw in demos:
        L = kw['L']
        K = kw['K']
        P = kw['P']
        S = kw['S']
        out = conv_out_length(L, K, S, P)
        formula = '(' + str(L) + '+2*' + str(P) + '-' + str(K) + ')/' + str(S) + '+1'

        inner = L + 2 * P - K
        ok_mod = inner % S == 0

        print('---')
        print(title)
        print('输入边长 L=' + str(L) + ', 核边长 K=' + str(K) + ', pad P=' + str(P) + ', stride S=' + str(S))
        print('内层括号 L+2P-K = ' + str(inner) + '；是否整除 stride：' + str(ok_mod) + '')
        print('输出边长 floor(' + formula + ') 的整数版 => ' + str(out))


if __name__ == '__main__':
    main()
