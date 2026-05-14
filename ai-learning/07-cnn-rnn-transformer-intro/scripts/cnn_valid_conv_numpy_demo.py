# -*- coding: utf-8 -*-
"""
第 7 课 · 小节 0.1.2～0.1.4 配套脚本：单通道二维「有效卷积」（valid convolution）演示

教学目标（只听课也能对照代码跟上）：
  - 弄清 CNN 里最核心的运算：用小窗口（卷积核 / kernel）在图上滑动，
    对每个局部做「对应位置乘加」得到一个新的输出格子（得到一个特征图的单元）。

数据从哪读：
  - 本脚本不读外部文件。
  - ``image``：在代码里构造的 8x8「灰度图」（float32），中间的亮块近似一个方块。
  - ``kernel``：在代码里写死的 3x3「竖边强化」核对（不是训练学出来的，
    只用来让你看到输出的形态变化）。

张量含义（本课用词）：
  - ``image``：形状 ``(h, w)``，可以理解为单通道高度 h、宽度 w 的灰度图。
  - ``kernel``：形状 ``(kh, kw)``，卷积核，每个元素是一个可学习权重；
    这里是手工固定的一组数，等价于演示「某一种局部模式被放大或被抑制」。

代码段在做什么（阅读顺序从上到下）：
  1) ``make_demo_image()``：构造带明显边缘/块状区域的小图，便于肉眼对比卷积前后的样子。
  2) ``conv2d_valid_np()``：
     - 「valid」指不做边缘补零 padding，输出的高宽变小：
       公式 ``out_h = h - kh + 1``、``out_w = w - kw + 1``
     - 两重循环逐个输出位置：每次切出局部 ``patch``，做 ``np.sum(patch * kernel)``
  3) ``main()``：打印输入、核对、输出三块矩阵；数字范围不同很正常（卷积本质是线性加权）。
"""

from __future__ import print_function

import numpy as np


def make_demo_image():
    """构造 8x8 的简单灰度图：背景略暗，中心偏右一块更亮"""
    img = np.zeros((8, 8), dtype=np.float32)
    img[2:6, 4:8] = 1.0
    img[:, :] = img[:, :] * 0.6 + 0.1
    img[2:6, 4:8] = 0.9
    return img


def conv2d_valid_np(image, kernel):
    """
    单通道二维有效卷积：stride=1, padding=0

    Args:
      image (ndarray): 形状 ``(h, w)``
      kernel (ndarray): 形状 ``(kh, kw)``
    Returns:
      ndarray: 形状 ``(h-kh+1, w-kw+1)``
    """
    h, w = image.shape
    kh, kw = kernel.shape
    out_h = h - kh + 1
    out_w = w - kw + 1
    if out_h <= 0 or out_w <= 0:
        raise ValueError(
            '卷积核不能比图像还大：图像(' + str(h) + ',' + str(w) + ') '
            '核(' + str(kh) + ',' + str(kw) + ')'
        )
    out = np.zeros((out_h, out_w), dtype=np.float32)
    for i in range(out_h):
        for j in range(out_w):
            patch = image[i : i + kh, j : j + kw]
            out[i, j] = np.sum(patch * kernel)
    return out


def main():
    image = make_demo_image()
    # 简化的 Sobel-ish 纵向差分近似：左侧正、右侧负，利于突出竖向边界响应
    kernel = np.array(
        [
            [1.0, 0.0, -1.0],
            [2.0, 0.0, -2.0],
            [1.0, 0.0, -1.0],
        ],
        dtype=np.float32,
    )

    out = conv2d_valid_np(image, kernel)

    np.set_printoptions(precision=2, suppress=True, linewidth=120)
    print('输入图像 image (8x8)')
    print(image)
    print('')
    print('卷积核 kernel (3x3)，本示例为手写固定核对，训练中由损失反传更新')
    print(kernel)
    print('')
    print('输出特征图 conv2d_valid output (6x6) = height 8-3+1, width 8-3+1')
    print(out)
    print('')
    print('形状核对：输入', image.shape, ' -> 输出', out.shape)


if __name__ == '__main__':
    main()
