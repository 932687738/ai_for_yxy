from __future__ import annotations

"""抓取 github.com/trending 静态 HTML（今日/本周/本月），解析后与中文简介列写入 Markdown。"""
import re
import ssl
from dataclasses import dataclass
from typing import List, Optional, Set
from urllib.request import Request, urlopen

from .display_zh import intro_display_zh_cn, repo_key_from_full, strip_simple_html


TRENDING_DOC_MARKER = "## Trending 页面快照（HTML 抓取）"
TRENDING_SINCE_HEADINGS = {
    "daily": "### 今日 trending（since=daily）",
    "weekly": "### 本周 trending（since=weekly）",
    "monthly": "### 本月 trending（since=monthly）",
}
TRENDING_BASE = "https://github.com/trending"
USER_AGENT_FALLBACK = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ai_for_learing-tools-github_topz "
    "(+https://github.com/) Python-urllib-compatible"
)


def trending_doc_portion(md_text: str) -> str:
    if TRENDING_DOC_MARKER not in md_text:
        return ""
    return md_text[md_text.find(TRENDING_DOC_MARKER):]


def extract_trending_subsection_for_since(portion_md: str, since_value: str) -> str:
    heading = TRENDING_SINCE_HEADINGS.get(since_value)
    if not heading or heading not in portion_md:
        return ""
    idx = portion_md.find(heading)
    tail = portion_md[idx:]
    inner_rest = tail[len(heading):]
    next_h3 = re.search(r"^### ", inner_rest, flags=re.MULTILINE)
    if next_h3:
        return tail[: len(heading) + next_h3.start()]
    return tail


def parse_trending_existing_repo_keys(section_md: str) -> Set[str]:
    keys_out: Set[str] = set()
    for line in section_md.splitlines():
        line_s = line.strip()
        matched_row = re.match(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|", line_s)
        if not matched_row:
            continue
        k_loc = repo_key_from_full(matched_row.group(1))
        if k_loc:
            keys_out.add(k_loc)
    return keys_out


@dataclass
class TrendingRepo:
    owner_nm: str
    repo_nm: str
    stars_tot: int
    forks_tot: int
    language_txt: str
    trending_txt: str
    description_txt: str

    @property
    def repo_key_lc(self) -> str:
        return "{}/{}".format(self.owner_nm, self.repo_nm).lower()

    @property
    def canonical_url(self) -> str:
        return "https://github.com/{}/{}".format(self.owner_nm, self.repo_nm)


def _compact_count_to_int(fragment: str) -> int:
    compact = "{}".format(fragment).strip().replace(",", "").replace(" ", "").replace("\xa0", "").lower()
    if compact.isdigit():
        return int(compact)
    m_k = re.match(r"^([\d]+(?:\.[\d]+)?)(k)$", compact)
    if m_k:
        return int(round(float(m_k.group(1)) * 1000))
    m_m = re.match(r"^([\d]+(?:\.[\d]+)?)(m)$", compact)
    if m_m:
        return int(round(float(m_m.group(1)) * 1000000))
    m_num = re.search(r"([\d][\d,]*)", compact)
    if m_num:
        return int(m_num.group(1).replace(",", ""))
    return 0


def fetch_trending_html(ssl_ctx: ssl.SSLContext, since_param: str) -> str:
    url_piece = "{}?since={}".format(TRENDING_BASE, since_param)
    ua_header = USER_AGENT_FALLBACK
    req_obj = Request(
        url_piece,
        headers={"User-Agent": ua_header, "Accept-Language": "en-US,en;q=0.9"},
        method="GET",
    )
    with urlopen(req_obj, timeout=60, context=ssl_ctx) as resp_stream:
        raw_bytes = resp_stream.read()
    return raw_bytes.decode("utf-8", errors="replace")


def _split_article_chunks(html_bulk: str) -> List[str]:
    split_blocks = html_bulk.split('<article class="Box-row"', maxsplit=-1)[1:]
    bodies_out: List[str] = []
    for raw_tail in split_blocks:
        anchor_idx = raw_tail.find("</article>")
        if anchor_idx < 0:
            continue
        bodies_out.append(raw_tail[:anchor_idx])
    return bodies_out


def parse_one_article_block(ssl_ctx_ignore: ssl.SSLContext, block_inner: str) -> Optional[TrendingRepo]:
    heading_outer = re.search(
        r'REPOSITORY_NAME_HEADING.*?href="/([^/\s"#]+)/([^/\s"#]+)"',
        block_inner,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not heading_outer:
        return None
    owner_loc = heading_outer.group(1)
    repo_loc = heading_outer.group(2)
    if "{}".format(owner_loc).strip().lower() == "sponsors":
        return None
    slug_path_piece = "/{}/{}".format(owner_loc, repo_loc)

    lang_slot = ""
    lang_m = re.search(r'itemprop="programmingLanguage">([^<]+)<', block_inner)
    if lang_m:
        lang_slot = strip_simple_html(lang_m.group(1))

    trending_slot = ""
    trend_m = re.search(
        r"([\d,]+\s+stars\s+(?:today|this\s+week|this\s+month))",
        block_inner,
        flags=re.IGNORECASE,
    )
    if trend_m:
        trending_slot = trend_m.group(1).strip()
    desc_slot = ""
    desc_m = re.search(
        r'<p class="col-9 color-fg-muted[^"]*"[^>]*>([\s\S]*?)</p>',
        block_inner,
    )
    if desc_m:
        desc_slot = strip_simple_html(desc_m.group(1))

    stars_pick = 0
    forks_pick = 0
    sg_m_loc = re.search(
        (
            r'href="%s/stargazers"[^>]*>[\s\S]*?</svg>\s*([\d,\.\sKm]+)\s*</a>'
            % re.escape(slug_path_piece)
        ),
        block_inner,
    )
    if sg_m_loc:
        stars_pick = _compact_count_to_int(sg_m_loc.group(1))
    fk_m_loc = re.search(
        (
            r'href="%s/forks"[^>]*>[\s\S]*?</svg>\s*([\d,\.\sKm]+)\s*</a>'
            % re.escape(slug_path_piece)
        ),
        block_inner,
    )
    if fk_m_loc:
        forks_pick = _compact_count_to_int(fk_m_loc.group(1))

    return TrendingRepo(
        owner_nm=owner_loc,
        repo_nm=repo_loc,
        stars_tot=stars_pick,
        forks_tot=forks_pick,
        language_txt=lang_slot if lang_slot else "—",
        trending_txt=trending_slot if trending_slot else "—",
        description_txt=desc_slot,
    )


def parse_trending_page(ssl_ctx_piece: ssl.SSLContext, html_bulk: str) -> List[TrendingRepo]:
    ordered_list: List[TrendingRepo] = []
    for chunk_body_loop in _split_article_chunks(html_bulk):
        parsed_one = parse_one_article_block(ssl_ctx_piece, chunk_body_loop)
        if parsed_one:
            ordered_list.append(parsed_one)
    return ordered_list


def render_trending_section(
    ssl_ctx_loc: ssl.SSLContext,
    heading_title_cn: str,
    since_value: str,
    prev_repo_keys_before: Set[str],
) -> str:
    """返回「### …」一段 Markdown（含表格）。"""
    try:
        html_loc = fetch_trending_html(ssl_ctx_loc, since_value)
        repo_collected = parse_trending_page(ssl_ctx_loc, html_loc)
    except Exception as exc_err:
        return (
            "### {}\n\n"
            "> Trending HTML 抓取或解析失败： `{}`。**since**=`{}`。\n".format(
                heading_title_cn, exc_err, since_value
            )
        )

    if not repo_collected:
        return (
            "### {}\n\n"
            "> 未解析到任何 `article.Box-row`，可能是 GitHub 页面结构变更，需要更新 `{}`。\n".format(
                heading_title_cn, __name__
            )
        )

    rows_lines = [
        "",
        "**页面**： `{}?since={}`".format(TRENDING_BASE, since_value),
        "",
        "| # | 仓库 | Stars | Forks | 语言 | 周期动向 | 仓库简介（中文） | 链接 | 标记 |",
        "| ---: | --- | ---:| ---:| --- | --- | --- | --- | --- |",
    ]
    for ix_row_rep, rp_it in enumerate(repo_collected[:25], start=1):
        intro_zh_cell = intro_display_zh_cn(ssl_ctx_loc, rp_it.repo_key_lc, rp_it.description_txt)
        mark_cell_loc = "新增" if rp_it.repo_key_lc not in prev_repo_keys_before else ""
        rows_lines.append(
            "| {} | `{}` | {} | {} | {} | {} | {} | {} | {} |".format(
                ix_row_rep,
                "{}/{}".format(rp_it.owner_nm, rp_it.repo_nm),
                rp_it.stars_tot,
                rp_it.forks_tot,
                rp_it.language_txt,
                rp_it.trending_txt,
                intro_zh_cell,
                rp_it.canonical_url,
                mark_cell_loc,
            )
        )
    rows_lines.append("")
    return "### {}\n".format(heading_title_cn) + "\n".join(rows_lines)


def render_trending_bundle(ssl_ctx_piece: ssl.SSLContext, existing_full_md: str = "") -> str:
    trend_blob = trending_doc_portion(existing_full_md)
    keys_daily = parse_trending_existing_repo_keys(extract_trending_subsection_for_since(trend_blob, "daily"))
    keys_weekly = parse_trending_existing_repo_keys(extract_trending_subsection_for_since(trend_blob, "weekly"))
    keys_monthly = parse_trending_existing_repo_keys(extract_trending_subsection_for_since(trend_blob, "monthly"))
    section_parts = [
        TRENDING_DOC_MARKER,
        "",
        "**说明**：与上方「全局 Star Search」数据源不同；本段按 GitHub trending 页的 **daily / weekly / monthly** 各拉一页并解析。**若前端改版导致选择器失效，需更新解析逻辑。**",
        "",
        "- **标记**列：三个 `since` 子表**各自独立**对照本次拉取前文件中该小节表格已出现的 `owner/repo`；新出现的行标 **新增**。下次拉取会先清空上一轮「新增」再重算（只保留相对**上一版文件**的新仓库）。",
        "",
        render_trending_section(
            ssl_ctx_piece, "今日 trending（since=daily）", "daily", keys_daily
        ),
        "",
        render_trending_section(
            ssl_ctx_piece, "本周 trending（since=weekly）", "weekly", keys_weekly
        ),
        "",
        render_trending_section(
            ssl_ctx_piece, "本月 trending（since=monthly）", "monthly", keys_monthly
        ),
        "",
    ]
    return "\n".join(section_parts)

