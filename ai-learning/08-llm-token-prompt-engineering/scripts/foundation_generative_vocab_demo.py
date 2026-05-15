# -*- coding: utf-8 -*-
"""
第 8 课 · 小节 0.1.3～0.1.4 配套：用字典罗列「基础模型之上」常见应用层适配与「生成式」形态（无 API、无第三方）

对应任务：
  - 把 **Foundation Model** 落到 **你日常写的工程**：多数时候不改底模权重，而是选一条或组合多条 **适配手段**。
  - 把 **Generative AI** 从 **市场营销词**还原成 **输出形态列表**：文本/代码/JSON/（本脚本不跑扩散模型，只列类）。

数据从哪读：
  - 无外部数据。``ADAPTATIONS`` 与 ``OUTPUT_KINDS`` 为教学用常量，可与产品例会白板对照。

代码段说明：
  1) ``print_adaptation_ladder``：四种典型路径（非互斥），便于评审时 **对齐词汇**。
  2) ``print_generative_kinds``：**生成式** 不等于 **只有 LLM**，但 LLM 是当前 **文本/代码** 主通路之一。
"""

from __future__ import print_function

import sys


ADAPTATIONS = (
    ('prompt_only', '仅通过 System/User 文本约束任务，不改模型权重'),
    ('rag', '检索文档片段写入上下文，再让模型基于片段生成/回答'),
    ('fine_tune', '用领域数据更新或注入适配器权重，成本与数据治理要求高'),
    ('tools', '通过 Function / Tool Calling 把计算与事实查询交给外部系统'),
)

OUTPUT_KINDS = (
    '自由文本',
    '结构化 JSON',
    '代码 patch / 全文件',
    '图像（扩散/编辑等）',
    '语音/音乐',
    '视频（生成或脚本级元数据）',
)


def print_adaptation_ladder():
    print('=== 基础模型（Foundation）之上的常见应用层手段（可组合）===')
    for key, desc in ADAPTATIONS:
        print('  • ' + key + ' — ' + desc)
    print('')


def print_generative_kinds():
    print('=== 生成式 AI 常见产出形态（LLM 主攻其中若干类）===')
    for k in OUTPUT_KINDS:
        print('  • ' + k)
    print('')
    print('说明：本演示不调用任何模型；上线时还要补 **校验、配额、审计、评测**')


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    print_adaptation_ladder()
    print_generative_kinds()


if __name__ == '__main__':
    main()
