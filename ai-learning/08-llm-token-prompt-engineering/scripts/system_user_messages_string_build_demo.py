# -*- coding: utf-8 -*-
"""
第 8 课 · 小节 0.1.1 配套：用纯字符串拼装「系统提示 + 用户载荷」——无 API、无第三方库

对应任务：
  - 体会 **工程化 Prompt** 与「随口一句」的差别：角色、任务、约束、输出格式、证据边界分块写清。
  - 为后续 **0.1.11～0.1.13**（System / Developer / User）埋伏笔：此处用 **system_block** 与 **user_block** 两段示意。

数据从哪读：
  - 不读外部文件。``contract_snippet`` 为写死在代码里的短合同片段，仅作占位。

输出含义：
  - 打印 **system**、**user** 全文及 **字符长度**；**不是** 真实 tokenizer 的 token 数（精确计费须调各模型 **tokenizer** 或 API）。

代码段说明：
  1) ``build_messages``：返回 (system_text, user_text)，便于单元测试里断言子串。
  2) ``main``：打印两段及 **合并预览**（真实 HTTP 请求常是 JSON 消息数组，这里只演示 **正文如何组织**）。
"""

from __future__ import print_function

import sys


def build_messages(contract_snippet):
    system_text = (
        '你是合同信息抽取助手。\n'
        '只能依据「合同片段」回答；做不到的事实请输出「原文未说明」。\n'
        '输出必须是单行 JSON，键为：payment_terms, delivery_date, liability_clause。\n'
        '不要输出 Markdown 代码围栏。'
    )
    user_text = (
        '合同片段：\n'
        '<<<BEGIN>>>\n'
        + contract_snippet.strip()
        + '\n<<<END>>>\n'
        '请抽取上述三字段。'
    )
    return system_text, user_text


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    snippet = (
        '甲方向乙方采购服务器一批。付款：签约后 30 日内付清全款。\n'
        '交付：乙方须在 2026-06-30 前发货至甲方仓库。\n'
        '若任一方迟延履行一日，应向对方支付合同金额千分之一的违约金。'
    )
    sys_m, usr_m = build_messages(snippet)
    print('--- system（' + str(len(sys_m)) + ' 字符）---')
    print(sys_m)
    print('')
    print('--- user（' + str(len(usr_m)) + ' 字符）---')
    print(usr_m)
    print('')
    print('说明：字符数 ≠ token 数；上线请用所选模型的 tokenizer / 用量 API 统计。')


if __name__ == '__main__':
    main()
