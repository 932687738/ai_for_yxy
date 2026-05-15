# -*- coding: utf-8 -*-
"""
第 8 课 · ## 0.2 练习 B-1 参考实现（单一可行解，非标答唯一）

对应任务：
  - 与教材 **练习 B-1** 对照：System / User 分块、定界符、JSON 约束、「无则 null」。

数据从哪读：
  - 内嵌字符串 **SAMPLE_LOG** 为演示聊天；真实系统从 DB/队列读入后填入 user 模板。

说明：
  - **不调 API**；仅 ``print`` 便于 diff 与代码评审。
"""

from __future__ import print_function

import sys

SAMPLE_LOG = (
    '客户：我上周买的耳机订单还能改地址吗？\n'
    '客服：请您提供订单号。\n'
    '客户：找不到了，单号好像是 OW-xxxxx 那个。\n'
)


def build_customer_log_extraction_prompts(log_text):
    system_text = (
        '你是客服质检与信息抽取助手。\n'
        '只能在 <<<LOG_BEGIN>>> 与 <<<LOG_END>>> 之间的「聊天正文」中取证；不得编造订单号或情绪。\n'
        '若订单号无法从正文可靠识别，order_id 必须为 null；sentiment 允许 unknown。\n'
        'need_human：若客户明确要求人工、或纠纷/退款/辱骂等需升级，则为 true，否则 false。\n'
        '只输出一行紧凑 JSON，键：order_id, sentiment, need_human。不要 Markdown 代码围栏，不要复述日志。\n'
        'sentiment 取值限定：positive, neutral, negative, unknown。'
    )
    user_text = (
        '请从下列聊天中抽取字段。\n'
        '<<<LOG_BEGIN>>>\n'
        + log_text.strip()
        + '\n<<<LOG_END>>>'
    )
    return system_text, user_text


def main():
    if getattr(sys.stdout, 'reconfigure', None):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass

    s, u = build_customer_log_extraction_prompts(SAMPLE_LOG)
    print('=== System ===')
    print(s)
    print('')
    print('=== User ===')
    print(u)


if __name__ == '__main__':
    main()
