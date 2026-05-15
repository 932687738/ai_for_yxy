#!/usr/bin/env python3
"""更新 dailyReport/github-topz.md：拉取 GitHub 按 Star 全局排序前十名，与文件中已有条目合并。"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from typing import Dict, List, Tuple, Optional

# 新版：序号 | 仓库 | Stars | 说明 | 链接；旧版无「说明」列时解析为 description 空串以便兼容
ROW_WITH_DESC_RE = re.compile(
    r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(https?://\S+)\s*\|\s*$"
)
ROW_LEGACY_RE = re.compile(
    r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*(https?://\S+)\s*\|\s*$"
)

# (stars, url, label, description) — description 空则渲染为「—」
Entry = Tuple[int, str, str, str]


def normalize_description(raw: object, max_len: int = 280) -> str:
    """GitHub REST 的 description；去掉换行，避免 Markdown 表格竖线打散列。"""
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


# 常客仓库的高质量中文一句话（不按英文 description 随 GitHub 改文案而漂移）
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


def mymemory_translate_to_zh(ssl_ctx: ssl.SSLContext, text: str) -> str:
    """MyMemory 免费翻译（无密钥）；失败则退回空串。"""
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
    headers = {"User-Agent": "ai_for_learing-tools-update-github-topz-translate"}
    req = Request(endpoint, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=25, context=ssl_ctx) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return ""
    data = payload.get("responseData") or {}
    out = data.get("translatedText") or ""
    out = str(out).strip().replace("|", "·")
    if not out.lower() or out.lower().startswith("my"):
        # 常见于配额或无匹配时的占位串
        return ""
    return out


def intro_display_zh_cn(ssl_ctx: ssl.SSLContext, repo_key_lower: str, stored_desc: str) -> str:
    """表格「简介」栏：合并数据里常为英文 GitHub description；落地 Markdown 时用中文更易读。"""
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


def repo_key(full_name: str) -> str:
    parts = [p for p in full_name.strip().strip("`").split("/") if p.strip()]
    if len(parts) != 2:
        return ""
    return "{}/{}".format(parts[0], parts[1]).lower()


def parse_existing_table(md_text: str) -> Dict[str, Entry]:
    """owner/repo 小写键 -> (stars, url, display_label, description)。"""
    out: Dict[str, Entry] = {}
    for line in md_text.splitlines():
        s = line.strip()
        m = ROW_WITH_DESC_RE.match(s)
        if m:
            full_raw, stars_str, desc_cell, url = m.group(1), m.group(2), m.group(3).strip(), m.group(4)
            desc_stored = ""
            if desc_cell and desc_cell not in ("—", "-"):
                desc_stored = normalize_description(desc_cell)
        else:
            m2 = ROW_LEGACY_RE.match(s)
            if not m2:
                continue
            full_raw, stars_str, url = m2.group(1), m2.group(2), m2.group(3)
            desc_stored = ""
        key = repo_key(full_raw)
        if not key:
            continue
        stars = int(stars_str)
        label = full_raw.strip()
        out[key] = (stars, url.strip(), label, desc_stored)
    return out


def github_repo_meta(ssl_ctx: ssl.SSLContext | None, token: str | None, owner: str, repo: str) -> Optional[dict]:
    url = "https://api.github.com/repos/{}/{}".format(owner, repo)
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai_for_learing-tools-update-github-topz",
    }
    if token:
        headers["Authorization"] = "Bearer {}".format(token)
    req = Request(url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=45, context=ssl_ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError:
        return None
    except URLError:
        return None


def enrich_missing_descriptions(ssl_ctx: ssl.SSLContext | None, token: str | None, merged: Dict[str, Entry]) -> None:
    """仅当简介为空时补打一枪 GET /repos，避免整张表长尾全是「—」。"""
    for key, (stars, url, label, desc) in list(merged.items()):
        if desc.strip():
            continue
        parts = key.split("/", 1)
        if len(parts) != 2:
            continue
        owner, repo_name = parts[0], parts[1]
        meta = github_repo_meta(ssl_ctx, token, owner, repo_name)
        if not meta:
            continue
        d = normalize_description(meta.get("description"))
        if d:
            merged[key] = (stars, url, label, d)


def github_search_top10(ssl_ctx: ssl.SSLContext | None, token: str | None) -> List[dict]:
    url = "https://api.github.com/search/repositories?q=stars:%3E0&sort=stars&order=desc&per_page=10"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai_for_learing-tools-update-github-topz",
    }
    if token:
        headers["Authorization"] = "Bearer {}".format(token)
    req = Request(url, headers=headers, method="GET")
    with urlopen(req, timeout=90, context=ssl_ctx) as resp:
        data = resp.read().decode("utf-8")
    payload = json.loads(data)
    items = payload.get("items") or []
    return items


def build_merged(existing: Dict[str, Entry], fetch_items: List[dict]) -> Dict[str, Entry]:
    merged: Dict[str, Entry] = dict(existing)
    for item in fetch_items:
        full = item.get("full_name") or ""
        stars = item.get("stargazers_count")
        html_url = item.get("html_url") or ""
        key = repo_key(full)
        if not key or stars is None:
            continue
        prior = merged.get(key)
        url = html_url.strip() if html_url else (prior[1] if prior else "")
        label = full.strip() if full.strip() else (prior[2] if prior else key)
        desc_api = normalize_description(item.get("description"))
        desc_prior = prior[3] if prior else ""
        desc_final = desc_api if desc_api else desc_prior
        merged[key] = (int(stars), url, label, desc_final)
    return merged


def render_md(ssl_ctx: ssl.SSLContext, merged: Dict[str, Entry]) -> str:
    zone = datetime.now(tz=_shanghai_tz()).strftime("%Y-%m-%d %H:%M:%S")
    rows = sorted(
        merged.items(),
        key=lambda kv: (-kv[1][0], kv[0]),
    )
    lines = [
        "# GitHub star 前十名（快照合并）",
        "",
        "- 数据源：[`dual-digest-on-pull`](../.cursor/rules/dual-digest-on-pull.mdc) 工作流程下，Knowledge Base Digest 配套的 GitHub Search API：`sort=stars` 前十名。",
        "- 与本文件已有仓库合并：**已出现的仓库更新 Stars**，新增的按 Star **降序** 插入整表排序。",
        "- **仓库简介**列：数据源为 GitHub `description`，**写入时为中文简述**——常见仓库内置固定中文提要；其余在渲染时尽力通过公开翻译接口转写，失败则回退英文摘录。表格中若为中文且无新的英文数据源，会直接沿用原有中文单元格。",
        "",
        "**最近一次更新时间**（Asia/Shanghai）： {}".format(zone),
        "",
        "| 序号 | 仓库 | Stars | 仓库简介（中文） | 链接 |",
        "| --- | --- | ---:| --- | --- |",
    ]
    for i, (_key, (stars, html_url, label, description)) in enumerate(rows, start=1):
        safe_url = html_url if html_url else "https://github.com/{}/{}".format(_key.split("/")[0], _key.split("/")[1])
        safe_desc = intro_display_zh_cn(ssl_ctx, _key, description)
        lines.append("| {} | `{}` | {} | {} | {} |".format(i, label, stars, safe_desc, safe_url))
    lines.append("")
    return "\n".join(lines)


def _shanghai_tz():
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo("Asia/Shanghai")
    except Exception:
        return timezone(timedelta(hours=8))


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge GitHub top-10-by-stars snapshot into github-topz.md")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dailyReport/github-topz.md"),
        help="Path to markdown file (default: dailyReport/github-topz.md)",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out_path = args.output
    if not out_path.is_absolute():
        out_path = (root / out_path).resolve()
    else:
        out_path = out_path.resolve()

    ssl_ctx = ssl.create_default_context()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    existing: Dict[str, Entry] = {}
    if out_path.is_file():
        existing = parse_existing_table(out_path.read_text(encoding="utf-8"))

    try:
        items = github_search_top10(ssl_ctx, token)
    except HTTPError as e:
        print("GitHub API 错误 HTTP {}： {}".format(e.code, e.reason))
        raise SystemExit(1) from e
    except URLError as e:
        print("请求失败： {}".format(e.reason))
        raise SystemExit(1) from e

    if len(items) < 1:
        print("GitHub API 返回空结果，跳过写入")
        raise SystemExit(2)

    merged = build_merged(existing, items)
    enrich_missing_descriptions(ssl_ctx, token, merged)
    text = render_md(ssl_ctx, merged)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(out_path)
    print("已写入 {}".format(out_path))


if __name__ == "__main__":
    main()
