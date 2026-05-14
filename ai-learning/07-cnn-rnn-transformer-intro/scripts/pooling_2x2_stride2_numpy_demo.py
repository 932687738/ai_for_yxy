# -*- coding: utf-8 -*-
"""
第 7 课 · 小节 0.1.6 配套：单通道特征图上的 2×2 池化（max 与 average），stride=2

对应任务：建立「窗口内汇聚 → 空间分辨率下降」的数值直觉；与卷积的乘加区分开。

数据从哪读：
  - 不读外部文件。在代码里构造一个 4×4 的 ``float32`` 矩阵，当作单张特征图的响应强度。

张量 / 矩阵含义：
  - 输入 ``x``：形状 ``(4, 4)``，可理解为 **C=1** 时的一层特征图（去掉通道维以简化循环）。
  - 输出：在 ``padding=0``、``kernel=2``、``stride=2`` 且输入边长整除时，空间边长为 ``4/2=2``。

代码段说明：
  1) ``pool2d_max`` / ``pool2d_avg``：二重循环按窗口左上角步进，每窗 **4 个元素**做 max 或 mean。
  2) ``main``：打印输入与两种池化结果，便于对照「max 更尖、avg 更糊」的数值感。
"""

from __future__ import print_function

import numpy as np


def pool2d_max(x, kernel, stride):
    """单通道、无 padding 的二维 max pooling；``x`` 形状 ``(H, W)``，``kernel`` 正方形边长。"""
    h, w = x.shape
    if h % stride != 0 or w % stride != 0:
        raise ValueError(
            '本演示要求 H,W 能被 stride 整除，当前 ' + str((h, w, stride))
        )
    if kernel != stride:
        raise ValueError('本课演示固定 kernel==stride=' + str(stride) + '，避免重叠池化分岔')
    out_h = h // stride
    out_w = w // stride
    out = np.zeros((out_h, out_w), dtype=np.float32)
    for i in range(out_h):
        for j in range(out_w):
            sh = i * stride
            sw = j * stride
            patch = x[sh : sh + kernel, sw : sw + kernel]
            out[i, j] = np.max(patch)
    return out


def pool2d_avg(x, kernel, stride):
    """单通道 average pooling，规则与 ``pool2d_max`` 相同，只是把窗口内取平均。"""
    h, w = x.shape
    if h % stride != 0 or w % stride != 0:
        raise ValueError(
            '本演示要求 H,W 能被 stride 整除，当前 ' + str((h, w, stride))
        )
    if kernel != stride:
        raise ValueError('本课演示固定 kernel==stride=' + str(stride) + '，避免重叠池化分岔')
    out_h = h // stride
    out_w = w // stride
    out = np.zeros((out_h, out_w), dtype=np.float32)
    area = float(kernel * kernel)
    for i in range(out_h):
        for j in range(out_w):
            sh = i * stride
            sw = j * stride
            patch = x[sh : sh + kernel, sw : sw + kernel]
            out[i, j] = np.sum(patch) / area
    return out


def main():
    x = np.array(
        [
            [1.0, 3.0, 0.0, 2.0],
            [5.0, 6.0, 1.0, 1.0],
            [0.0, 2.0, 4.0, 3.0],
            [1.0, 1.0, 2.0, 0.0],
        ],
        dtype=np.float32,
    )
    k = 2
    s = 2
    mx = pool2d_max(x, k, s)
    av = pool2d_avg(x, k, s)

    np.set_printoptions(precision=2, suppress=True, linewidth=120)
    print('输入特征图 x，形状 ' + str(x.shape))
    print(x)
    print('')
    print('max pool 2x2 stride 2，输出形状 ' + str(mx.shape))
    print(mx)
    print('')
    print('avg pool 2x2 stride 2，输出形状 ' + str(av.shape))
    print(av)


if __name__ == '__main__':
    main()
