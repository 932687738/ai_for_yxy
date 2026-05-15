from __future__ import annotations

import re
from typing import Dict
from urllib.parse import quote
from urllib.request import Request, urlopen
import json


def normalize_description(raw: object, max_len: int = 280) -> str:
    """GitHub 或页面的简介文本；表格防断列。"""
    if raw is None:
        return ""
    text = str(raw).strip().replace("\r\n", "\n")
    line = text.split("\n")[0].strip()
    if not line:
        return ""
    line = line.replace("|", "·")
    if len(line) > max_len:
        line = "{}…".format(line[: max_len - 1].rstrip())
    return line


def _looks_like_chinese(s: str) -> bool:
    for ch in s:
        if "\u4e00" <= ch <= "\u9fff":
            return True
    return False


_MANUAL_REPO_INTRO_ZH: Dict[str, str] = {
    "codecrafters-io/build-your-own-x": "通过从零重写各类代表性技术来学习编程与设计，加深对底层原理的理解。",
    "sindresorhus/awesome": "围绕多种主题整理的「Awesome」精品清单合集。",
    "freecodecamp/freecodecamp": "freeCodeCamp 官网开源代码与学习课程：可免费学习编程、数学与计算机科学。",
    "public-apis/public-apis": "免费可用的公共 API 资源汇总清单。",
    "ebookfoundation/free-programming-books": "可免费获取的编程与计算机类书籍书单汇总。",
    "openclaw/openclaw": "可在多系统运行的个人 AI 助手（吉祥物为龙虾图标）。",
    "nilbuild/developer-roadmap": "交互式开发者路线图、入门与进阶教程等学习资料合集。",
    "donnemartin/system-design-primer": "大厂级系统设计学习与面试备战材料（含 Anki 卡片范例）。",
    "jwasham/coding-interview-university": "面向软件工程师岗位的系统化计算机科学与面试自学路线图。",
    "vinta/awesome-python": "带选型倾向的 Python 框架、扩展库、工具与学习资源合集。",
    "awesome-selfhosted/awesome-selfhosted": "可自行部署的各类自由软件网络服务与 Web 应用清单。",
    "996icu/996.icu": "倡议关注「996」工作制、计数星标与交流的开发社区仓库（含网络迷因用语）。",
    "facebook/react": "用于构建 Web 与原生用户界面的 React 视图库（含多端生态）。",
}


def normalize_zh_line(raw: str, max_len: int = 280) -> str:
    line = str(raw).strip().replace("|", "·").replace("\r\n", "\n").split("\n")[0].strip()
    if not line:
        return ""
    if len(line) > max_len:
        line = "{}…".format(line[: max_len - 1].rstrip())
    return line


def mymemory_translate_to_zh(ssl_ctx, text: str) -> str:
    if not text.strip():
        return ""
    q = text.strip()
    if len(q) > 450:
        q = "{}…".format(q[:447].rstrip())
    endpoint = (
        "https://api.mymemory.translated.net/get?q={}&langpair=en|zh-CN".format(
            quote(q)
        )
    )
    headers = {"User-Agent": "ai_for_learing-tools-github-topz-translate"}
    req = Request(endpoint, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=25, context=ssl_ctx) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return ""
    data = payload.get("responseData") or {}
    out = str(data.get("translatedText") or "").strip().replace("|", "·")
    if not out.lower() or out.lower().startswith("my"):
        return ""
    return out


def repo_key_from_full(full_name_with_case: str) -> str:
    parts = [p for p in full_name_with_case.strip().strip("`").split("/") if p.strip()]
    if len(parts) != 2:
        return ""
    return "{}/{}".format(parts[0], parts[1]).lower()


def intro_display_zh_cn(ssl_ctx, repo_key_lower: str, stored_desc: str) -> str:
    """英文 description / 列表简介 → 表格用中文简述。"""
    cell = normalize_description(stored_desc)
    if not cell.strip():
        return "—"
    if _looks_like_chinese(cell):
        z = normalize_zh_line(cell)
        return z if z else "—"
    manual = _MANUAL_REPO_INTRO_ZH.get(repo_key_lower)
    if manual:
        z = normalize_zh_line(manual)
        return z if z else "—"
    z = normalize_zh_line(mymemory_translate_to_zh(ssl_ctx, cell))
    if z:
        return z
    return normalize_zh_line(cell) if normalize_zh_line(cell) else cell


def strip_simple_html(fragment: str) -> str:
    t = re.sub(r"<[^>]+>", "", fragment)
    t = re.sub(r"\s+", " ", t).strip()
    return normalize_description(t, max_len=400)
