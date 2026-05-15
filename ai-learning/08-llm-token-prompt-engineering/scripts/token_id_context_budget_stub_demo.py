# -*- coding: utf-8 -*-
"""
第 8 课 · 小节 0.1.7～0.1.8 配套：玩具「整数 token ID」+ 上下文 **预算表**（无真实 tokenizer）

对应任务：
  - **0.1.7**：看清 **token id** 就是 **整型下标**；同一 **token 字符串** 在 **固定词表** 里映射到 **唯一 id**（版本不变前提下）。
  - **0.1.8**：把 **上下文窗口** 当成 **硬预算**：**输入侧各块之和 + 预留给模型输出的 token** 不得超过 **厂商上限**（数值为教学假设）。

数据从哪读：
  - 不读外部文件。``TOY_CHAR_IDS`` 为极小玩具映射；``BUDGET_ROWS`` 为假设的每条占用 token 数。

代码段说明：
  1) ``demo_toy_ids``：展示 Python 列表里的 **整数** 即可代表「已离散化」序列；**勿**与真实 LLM 词表对号入座。
  2) ``demo_context_budget``：把教材 **0.1.8** 列举的块落成 **一行行假计数**，再与 ``CONTEXT_LIMIT``、``RESERVED_FOR_COMPLETION`` 比较。
"""

from __future__ import print_function

import sys

# 极小玩具表：仅用于对照「字符 -> 整数 id」，不等价任何真实模型词表
TOY_CHAR_IDS = {
    'a': 10,
    'b': 11,
    'c': 12,
}

# 假设一次请求里各段占用（token 数 —— 教学用常数；真实须 encode）
BUDGET_ROWS = (
    ('system 指令', 180),
    ('developer 指令', 120),
    ('当前 user', 650),
    ('多轮 history', 2200),
    ('RAG 检索片段', 4200),
    ('工具返回 JSON', 480),
)

CONTEXT_LIMIT = 8192
RESERVED_FOR_COMPLETION = 1024


def encode_toy_word(word):
    """把 ``word`` 中每个字符映射为玩具 id；未知字符记 -1。"""
    return [TOY_CHAR_IDS.get(ch, -1) for ch in word]


def demo_toy_ids():
    print('=== 玩具 Token ID：字符串已消失，只剩整数序列 ===')
    w = 'abc'
    ids = encode_toy_word(w)
    print('词（玩具）：' + w + ' -> ids=' + str(ids))
    print('说明：真实系统里是几万～几十万维词表；这里只有 3 个 id。\n')


def demo_context_budget():
    print('=== 上下文窗口：各段假设计费 token + 预留生成长度 ===')
    used = 0
    for name, n in BUDGET_ROWS:
        print('  ' + name + ': ' + str(n))
        used = used + n
    need = used + RESERVED_FOR_COMPLETION
    print('')
    print('输入段合计（假设）=' + str(used))
    print('预留生成长度=' + str(RESERVED_FOR_COMPLETION))
    print('本例总需求=' + str(need) + '  |  窗口上限=' + str(CONTEXT_LIMIT))
    if need <= CONTEXT_LIMIT:
        print('结论：数值意义上「未爆仓」（真实还要扣特殊 token、模板开销等）。')
    else:
        print('结论：已超窗口 —— 需截断 history / 压缩 RAG / 换长窗口模型 / 分多轮。')
    print('')


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    demo_toy_ids()
    demo_context_budget()


if __name__ == '__main__':
    main()
