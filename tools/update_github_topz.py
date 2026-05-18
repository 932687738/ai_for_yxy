#!/usr/bin/env python3
"""更新 dailyReport/github-topz.md：模块一 Stars Search API 合并 + 模块二 Trending HTML 抓取。"""
from __future__ import annotations

import argparse
import os
import ssl
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError


def _inject_tools_pkg_path():
    bundle_dir_piece = Path(__file__).resolve().parent
    if str(bundle_dir_piece) not in sys.path:
        sys.path.insert(0, str(bundle_dir_piece))


_inject_tools_pkg_path()

from github_topz import stars_merge, trending_fetch


def compose_full_markdown(ssl_ctx_inner: ssl.SSLContext, token_inner: str | None, existing_md_bulk: str) -> str:
    _hist_drop, stars_body_md = stars_merge.run_stars_pipeline(ssl_ctx_inner, token_inner, existing_md_bulk)
    trending_body_md = trending_fetch.render_trending_bundle(ssl_ctx_inner, existing_md_bulk)
    preamble_lines = [
        "# GitHub 快照（Stars Search API + Trending）",
        "",
        "本文件由 `tools/update_github_topz.py` 生成，两块内容独立编排：",
        "",
        "- **模块一**：`tools/github_topz/stars_merge.py` → GitHub REST `/search/repositories` 全局 Star 前十名，并按既有规则与本节历史 Markdown 表格合并（列结构与原 `github-topz.md` 一致）。",
        "- **模块二**：`tools/github_topz/trending_fetch.py` → 抓取 Trending 「今日 / 本周 / 本月」页面 HTML，`article.Box-row` 解析后与中文简介渲染。",
        "- **标记列**：各表相对**本次运行前**已保存的 `github-topz.md` 中对应表格出现过的 `owner/repo` 做差集；首次出现标 **新增**；再次运行会先清空上一轮「新增」后仅标记新一轮新增（详见 `.cursor/rules/dual-digest-on-pull.mdc`）。",
        "",
        "---",
        "",
    ]
    mid_separator = ["", "---", ""]
    return "\n".join(preamble_lines) + stars_body_md + "\n".join(mid_separator) + trending_body_md


def main() -> None:
    parser_obj = argparse.ArgumentParser(
        description="Merge GitHub top-10 snapshot + scrape Trending into github-topz.md"
    )
    parser_obj.add_argument(
        "--output",
        type=Path,
        default=Path("dailyReport/github-topz.md"),
        help="Markdown path (default: dailyReport/github-topz.md)",
    )
    cli_args_parse = parser_obj.parse_args()

    proj_root_piece = Path(__file__).resolve().parents[1]
    out_piece = cli_args_parse.output
    if not out_piece.is_absolute():
        out_piece = (proj_root_piece / out_piece).resolve()

    ssl_ctx_piece = ssl.create_default_context()
    token_piece = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    existed_full_text = ""
    if out_piece.is_file():
        existed_full_text = out_piece.read_text(encoding="utf-8")

    try:
        full_doc_text_piece = compose_full_markdown(ssl_ctx_piece, token_piece, existed_full_text)
    except HTTPError as er_http_outer:
        print("GitHub API 错误 HTTP {}： {}".format(er_http_outer.code, er_http_outer.reason))
        raise SystemExit(1) from er_http_outer
    except URLError as er_url_piece:
        print("请求失败： {}".format(er_url_piece.reason))
        raise SystemExit(1) from er_url_piece

    out_piece.parent.mkdir(parents=True, exist_ok=True)
    tmp_piece = out_piece.with_suffix(out_piece.suffix + ".tmp")
    tmp_piece.write_text(full_doc_text_piece, encoding="utf-8")
    tmp_piece.replace(out_piece)
    print("已写入 {}".format(out_piece))


if __name__ == "__main__":
    main()
