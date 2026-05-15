# -*- coding: utf-8 -*-
"""
第 8 课 · 小节 0.1.5～0.1.6 配套：粗粒度「长度」对比——强调真实 token 须用 **该模型** 的 tokenizer

对应任务：
  - 破除直觉：**汉字数**、**按空白切词数**、**字符数** 都不等于 **API 返回的 token 数**。
  - 与 **0.1.6** 衔接：**Tokenization** 是 **模型专属** 的前置步骤；换模型 = 换分词与词表。

数据从哪读：
  - 不读外部文件。``SAMPLES`` 为写死的中英文短句，仅作 **教学对比**。

输出含义：
  - 每行打印：**unicode 码点数**（近似「用户看到的字符数」）、**按空白切分词数**（英文友好，中文常失真）、**拆成单码点列表长度**（极端玩具「一字一 token」仅帮助建立 **「离散化」** 概念）。
  - **不是** OpenAI / Anthropic 等计费 token；上线请用 **官方 tokenizer 或 /usage**。

代码段说明：
  1) ``metrics_for``：对单条字符串算三种 **粗指标**，避免引入 **tiktoken**（若你本地已装，可自行对照真实值并写进学习笔记）。
  2) ``main``：逐条打印并 **重复声明** 「仅供参考」。
"""

from __future__ import print_function

import sys

# 教学样例：中英混排少量谐音字，便于看「空白切分」与「码点」差异
SAMPLES = (
    'Hello world, pricing API.',
    '大模型 按 token 计费，不是按「字数」计费。',
    'API rate=0.99 USD != 免费。',
)


def metrics_for(text):
    n_cp = len(text)
    n_ws_tokens = len(text.split())
    n_chars_as_list = len(list(text))
    return n_cp, n_ws_tokens, n_chars_as_list


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    print('=== 粗指标 vs 真实 token（本脚本仅为直觉课；计费以厂商 tokenizer 为准）===\n')
    for s in SAMPLES:
        a, b, c = metrics_for(s)
        print('句子：' + s)
        print('  unicode 码点数（len）=' + str(a))
        print('  按空白切分词数（split）=' + str(b) + '  （中文常切碎，不可当 token）')
        print('  单码点遍历长度=' + str(c) + '  （「一字一 id」只是玩具，不等价 BPE）')
        print('')


if __name__ == '__main__':
    main()
