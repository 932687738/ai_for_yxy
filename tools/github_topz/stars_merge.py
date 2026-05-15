from __future__ import annotations

"""全局 Star Search API：前十名 + 与本文件 Stars 小节历史行合并。"""
import json
import os
import re
import ssl
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .display_zh import intro_display_zh_cn, normalize_description, repo_key_from_full


Entry = Tuple[int, str, str, str]


ROW_WITH_DESC_RE = re.compile(
    r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(https?://\S+)\s*\|\s*$"
)
ROW_LEGACY_RE = re.compile(
    r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*(https?://\S+)\s*\|\s*$"
)

STARS_MARKER = "## 全局 Star Search API（与文件历史合并）"


def _shanghai_tz():
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo("Asia/Shanghai")
    except Exception:
        return timezone(timedelta(hours=8))


def github_rest_headers(ssl_ctx: Optional[ssl.SSLContext], token: Optional[str]):
    ua = (
        os.environ.get("GITHUB_TOPZ_HTTP_USER_AGENT", "").strip()
        or "ai_for_learing-tools-update-github-topz"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": ua,
    }
    if token:
        headers["Authorization"] = "Bearer {}".format(token)
    return headers


def extract_stars_section_markdown(md_text: str) -> str:
    """仅解析 Stars 合并用表格：带小节标题时截取到下一个同级 ##；否则整张 MD（兼容旧版单文件）。"""
    if STARS_MARKER not in md_text:
        return md_text
    idx = md_text.find(STARS_MARKER)
    tail = md_text[idx:]
    other_h2 = list(re.finditer(r"^## [^\s#]", tail, flags=re.MULTILINE))
    if len(other_h2) <= 1:
        return tail.strip()
    second = other_h2[1]
    return tail[: second.start()].rstrip()


def parse_existing_table(md_blob: str) -> Dict[str, Entry]:
    """owner/repo 小写键 -> (stars, url, display_label, description)。"""
    out_dict: Dict[str, Entry] = {}
    for line in md_blob.splitlines():
        s = line.strip()
        matched = ROW_WITH_DESC_RE.match(s)
        if matched:
            full_raw = matched.group(1)
            stars_val = matched.group(2)
            desc_segment = matched.group(3).strip()
            url_val = matched.group(4)
            desc_keep = ""
            if desc_segment and desc_segment not in ("—", "-"):
                desc_keep = normalize_description(desc_segment)
        else:
            m2 = ROW_LEGACY_RE.match(s)
            if not m2:
                continue
            full_raw = m2.group(1)
            stars_val = m2.group(2)
            url_val = m2.group(3)
            desc_keep = ""
        key_use = repo_key_from_full(full_raw)
        if not key_use:
            continue
        star_int_loc = int(stars_val)
        label_use = full_raw.strip()
        out_dict[key_use] = (star_int_loc, url_val.strip(), label_use, desc_keep)
    return out_dict


def parse_stars_merge_state(md_text: str) -> Dict[str, Entry]:
    chunk = extract_stars_section_markdown(md_text)
    return parse_existing_table(chunk)


def github_repo_meta(ssl_ctx: Optional[ssl.SSLContext], token: Optional[str], owner_use: str, repo_use: str) -> Optional[dict]:
    repo_api_url = "https://api.github.com/repos/{}/{}".format(owner_use, repo_use)
    req_obj = Request(repo_api_url, headers=github_rest_headers(ssl_ctx, token), method="GET")
    try:
        with urlopen(req_obj, timeout=45, context=ssl_ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError:
        return None
    except URLError:
        return None


def enrich_missing_descriptions(
    ssl_ctx: Optional[ssl.SSLContext], token: Optional[str], merged: Dict[str, Entry]
) -> None:
    for key_nm, tup in list(merged.items()):
        stars_ct, pg_url, label_nm, brief_desc = tup
        if "{}".format(brief_desc).strip():
            continue
        parts_keys = key_nm.split("/", 1)
        if len(parts_keys) != 2:
            continue
        own_p, rp_n = parts_keys[0], parts_keys[1]
        blob = github_repo_meta(ssl_ctx, token, own_p, rp_n)
        if not blob:
            continue
        d_plain = normalize_description(blob.get("description"))
        if d_plain:
            merged[key_nm] = (stars_ct, pg_url, label_nm, d_plain)


def github_search_top10(ssl_ctx: Optional[ssl.SSLContext], token: Optional[str]) -> List[dict]:
    search_url_endpoint = (
        "https://api.github.com/search/repositories?q=stars:%3E0&sort=stars&order=desc&per_page=10"
    )
    req_obj = Request(
        search_url_endpoint,
        headers=github_rest_headers(ssl_ctx, token),
        method="GET",
    )
    with urlopen(req_obj, timeout=90, context=ssl_ctx) as resp_stream:
        data_raw = resp_stream.read().decode("utf-8")
    payload_outer = json.loads(data_raw)
    items_list_inner = payload_outer.get("items") or []
    return items_list_inner


def build_merged(existing_map_inner: Dict[str, Entry], fetch_items_top: List[dict]) -> Dict[str, Entry]:
    merged_outer: Dict[str, Entry] = dict(existing_map_inner)
    for one_item_loop in fetch_items_top:
        full_nm = one_item_loop.get("full_name") or ""
        st_ct = one_item_loop.get("stargazers_count")
        html_outer = one_item_loop.get("html_url") or ""
        key_loop = repo_key_from_full(full_nm)
        if not key_loop or st_ct is None:
            continue
        prior_tup_inner = merged_outer.get(key_loop)
        url_pick = "{}".format(html_outer).strip() if html_outer else (prior_tup_inner[1] if prior_tup_inner else "")
        label_pick = full_nm.strip() if full_nm.strip() else (prior_tup_inner[2] if prior_tup_inner else key_loop)
        desc_fetch = normalize_description(one_item_loop.get("description"))
        desc_prior_pick = prior_tup_inner[3] if prior_tup_inner else ""
        desc_out_pick = desc_fetch if desc_fetch else desc_prior_pick
        merged_outer[key_loop] = (int(st_ct), url_pick, label_pick, desc_out_pick)
    return merged_outer


def render_stars_section(ssl_ctx: ssl.SSLContext, merged_outer: Dict[str, Entry]) -> str:
    zone_now = datetime.now(tz=_shanghai_tz()).strftime("%Y-%m-%d %H:%M:%S")
    ranked_rows_ordered = sorted(
        merged_outer.items(),
        key=lambda kv_pair_ent: (-kv_pair_ent[1][0], kv_pair_ent[0]),
    )
    lines_buf = [
        STARS_MARKER,
        "",
        "- 数据源：[`dual-digest-on-pull`](../.cursor/rules/dual-digest-on-pull.mdc) 工作流程下配套的 GitHub Search API：`sort=stars` **全局前十名**（`/search/repositories`）。与本节历史行合并时：**已出现的仓库更新 Stars**，新仓库按 Star **降序** 参与整表排序。",
        "- **仓库简介**列：数据源为 GitHub `description`，**写入时为中文简述**——常见仓库内置固定中文提要；其余在渲染时尽力通过公开翻译接口转写，失败则回退英文摘录。表格中若为中文且无新的英文数据源，会直接沿用原有中文单元格。",
        "- **与 Trending 区别**：本节为全局累计 Star 排序快照；文末 Trending 为 GitHub「今日 / 本周 / 本月热度」榜单，数据源与口径均不同。",
        "",
        "**最近一次更新时间**（Asia/Shanghai）： {}".format(zone_now),
        "",
        "| 序号 | 仓库 | Stars | 仓库简介（中文） | 链接 |",
        "| --- | --- | ---:| --- | --- |",
    ]
    for idx_row, (_k_ent, tup_inner) in enumerate(ranked_rows_ordered, start=1):
        stars_ct, html_url_pick, label_pick, brief_raw = tup_inner
        fallback_url_piece = (
            "https://github.com/{}/{}".format(_k_ent.split("/")[0], _k_ent.split("/")[1])
            if "/" in _k_ent
            else ""
        )
        safe_url_piece = html_url_pick if html_url_pick else fallback_url_piece
        safe_intro_cell_piece = intro_display_zh_cn(ssl_ctx, _k_ent, brief_raw)
        lines_buf.append(
            "| {} | `{}` | {} | {} | {} |".format(
                idx_row, label_pick, stars_ct, safe_intro_cell_piece, safe_url_piece
            )
        )
    lines_buf.append("")
    return "\n".join(lines_buf)


def run_stars_pipeline(
    ssl_ctx: ssl.SSLContext, token_optional: Optional[str], full_existing_md_content: str
) -> Tuple[Dict[str, Entry], str]:
    hist_map_piece = parse_stars_merge_state(full_existing_md_content)
    fetched_top_list = github_search_top10(ssl_ctx, token_optional)
    if len(fetched_top_list) < 1:
        merged_only_hist = dict(hist_map_piece)
        enrich_missing_descriptions(ssl_ctx, token_optional, merged_only_hist)
        body_section_only = render_stars_section(ssl_ctx, merged_only_hist)
        return merged_only_hist, body_section_only
    merged_full_map = build_merged(hist_map_piece, fetched_top_list)
    enrich_missing_descriptions(ssl_ctx, token_optional, merged_full_map)
    body_section_piece = render_stars_section(ssl_ctx, merged_full_map)
    return merged_full_map, body_section_piece

