#!/usr/bin/env python3
"""本地 ChromaDB CRUD 命令行工具。

支持两种连接方式：
1) 持久化目录（PersistentClient）：与 project_graphrag 脚本相同的本地落盘模式
2) HTTP 客户端（HttpClient）：连接本机或局域网已启动的 Chroma Server

依赖：pip install -r project_graphrag/requirements-chroma.txt

示例：
  python tools/chroma_crud.py --persist ./chroma_store list-collections
  python tools/chroma_crud.py --http localhost 8000 count --collection my_coll
  python tools/chroma_crud.py --persist ./chroma_store query --collection my_coll --text "hello" --n 5

写入负载 JSON（add / upsert 共用）：
  {"ids": ["a","b"], "documents": ["...","..."], "metadatas": [{}, {}], "embeddings": [[...], [...]]}
  embeddings / documents / metadatas 均可选，但与集合维度及 Chroma 校验规则一致（见官方文档）。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _preset_hub_timeouts_before_chroma() -> None:
    """首次使用默认嵌入器时可能下载模型；放宽 HF 超时，减少弱网失败。"""
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "900")
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "120")


def _load_json_file(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def _parse_json_inline(raw: str) -> Any:
    return json.loads(raw)


def _require_chroma():
    try:
        import chromadb  # type: ignore

        return chromadb
    except ImportError:
        print(
            "未安装 chromadb。请执行: pip install -r project_graphrag/requirements-chroma.txt",
            file=sys.stderr,
        )
        raise SystemExit(2)


def build_client(args: argparse.Namespace):
    chromadb = _require_chroma()
    if getattr(args, "persist_dir", None):
        p = Path(args.persist_dir).resolve()
        return chromadb.PersistentClient(path=str(p))
    host = args.http_host
    port = int(args.http_port)
    ssl = bool(getattr(args, "http_ssl", False))
    return chromadb.HttpClient(host=host, port=port, ssl=ssl)


def cmd_list_collections(client, _args: argparse.Namespace) -> int:
    cols = client.list_collections()
    out = []
    for c in cols:
        cid = getattr(c, "id", None)
        out.append({"name": c.name, "id": str(cid) if cid is not None else None, "metadata": c.metadata})
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_create_collection(client, args: argparse.Namespace) -> int:
    meta: Dict[str, Any] = {"hnsw:space": str(args.space)}
    client.create_collection(name=args.collection, metadata=meta)
    print(json.dumps({"ok": True, "collection": args.collection, "metadata": meta}, ensure_ascii=False))
    return 0


def cmd_delete_collection(client, args: argparse.Namespace) -> int:
    client.delete_collection(name=args.collection)
    print(json.dumps({"ok": True, "deleted": args.collection}, ensure_ascii=False))
    return 0


def cmd_get_collection(client, args: argparse.Namespace) -> int:
    coll = client.get_collection(name=args.collection)
    print(json.dumps({"name": coll.name, "metadata": coll.metadata}, ensure_ascii=False, indent=2))
    return 0


def _load_batch_payload(args: argparse.Namespace) -> Dict[str, Any]:
    if args.payload:
        payload = _load_json_file(Path(args.payload))
    else:
        payload = _parse_json_inline(sys.stdin.read())
    if not isinstance(payload, dict):
        raise ValueError("负载必须是 JSON 对象")
    return payload


def cmd_add(client, args: argparse.Namespace) -> int:
    coll = client.get_or_create_collection(
        name=args.collection,
        metadata={"hnsw:space": str(args.space)},
    )
    payload = _load_batch_payload(args)
    ids = payload.get("ids")
    if not ids or not isinstance(ids, list):
        raise ValueError("负载必须包含非空 ids 数组")
    kwargs: Dict[str, Any] = {"ids": [str(x) for x in ids]}
    if "embeddings" in payload and payload["embeddings"] is not None:
        kwargs["embeddings"] = payload["embeddings"]
    if "documents" in payload and payload["documents"] is not None:
        kwargs["documents"] = payload["documents"]
    if "metadatas" in payload and payload["metadatas"] is not None:
        kwargs["metadatas"] = payload["metadatas"]
    coll.add(**kwargs)
    print(json.dumps({"ok": True, "op": "add", "count": len(kwargs["ids"])}, ensure_ascii=False))
    return 0


def cmd_upsert(client, args: argparse.Namespace) -> int:
    coll = client.get_or_create_collection(
        name=args.collection,
        metadata={"hnsw:space": str(args.space)},
    )
    payload = _load_batch_payload(args)
    ids = payload.get("ids")
    if not ids or not isinstance(ids, list):
        raise ValueError("负载必须包含非空 ids 数组")
    kwargs: Dict[str, Any] = {"ids": [str(x) for x in ids]}
    if "embeddings" in payload and payload["embeddings"] is not None:
        kwargs["embeddings"] = payload["embeddings"]
    if "documents" in payload and payload["documents"] is not None:
        kwargs["documents"] = payload["documents"]
    if "metadatas" in payload and payload["metadatas"] is not None:
        kwargs["metadatas"] = payload["metadatas"]
    coll.upsert(**kwargs)
    print(json.dumps({"ok": True, "op": "upsert", "count": len(kwargs["ids"])}, ensure_ascii=False))
    return 0


def _parse_ids(args: argparse.Namespace) -> List[str]:
    if args.ids_json_file:
        data = _load_json_file(Path(args.ids_json_file))
    else:
        data = _parse_json_inline(args.ids_json)
    if not isinstance(data, list):
        raise ValueError("ids 必须是 JSON 数组")
    return [str(x) for x in data]


def cmd_get(client, args: argparse.Namespace) -> int:
    coll = client.get_collection(name=args.collection)
    ids = _parse_ids(args)
    inc_emb = bool(args.include_embeddings)
    res = coll.get(ids=ids, include=["metadatas", "documents"] + (["embeddings"] if inc_emb else []))
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


def cmd_delete_ids(client, args: argparse.Namespace) -> int:
    coll = client.get_collection(name=args.collection)
    ids = _parse_ids(args)
    coll.delete(ids=ids)
    print(json.dumps({"ok": True, "op": "delete_ids", "count": len(ids)}, ensure_ascii=False))
    return 0


def cmd_query(client, args: argparse.Namespace) -> int:
    coll = client.get_collection(name=args.collection)
    n_results = int(args.n_results)
    where = None
    if args.where_json:
        where = _parse_json_inline(args.where_json)
    qtext = (args.query_text or "").strip()
    qemb_raw = (args.query_embedding_json or "").strip()
    if qtext:
        res = coll.query(query_texts=[qtext], n_results=n_results, where=where)
    elif qemb_raw:
        emb = _parse_json_inline(qemb_raw)
        if not isinstance(emb, list):
            raise ValueError("--query-embedding-json 必须是表示单个向量的 JSON 数组")
        res = coll.query(query_embeddings=[emb], n_results=n_results, where=where)
    else:
        raise ValueError("query 需要 --text 或 --query-embedding-json")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


def cmd_peek(client, args: argparse.Namespace) -> int:
    coll = client.get_collection(name=args.collection)
    res = coll.peek(limit=int(args.limit))
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


def cmd_count(client, args: argparse.Namespace) -> int:
    coll = client.get_collection(name=args.collection)
    c = coll.count()
    print(json.dumps({"collection": args.collection, "count": c}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ChromaDB 本地 CRUD CLI")
    conn = parser.add_mutually_exclusive_group(required=True)
    conn.add_argument("--persist", dest="persist_dir", type=str, help="持久化目录路径（PersistentClient）")
    conn.add_argument("--http", dest="http_tuple", nargs=2, metavar=("HOST", "PORT"), help="Chroma Server 主机与端口")

    parser.add_argument(
        "--ssl",
        dest="http_ssl",
        action="store_true",
        help="HTTP 模式使用 HTTPS（默认关闭）",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-collections", help="列出所有集合")
    p_list.set_defaults(func=cmd_list_collections)

    p_cc = sub.add_parser("create-collection", help="创建集合（若已存在则失败）")
    p_cc.add_argument("--collection", required=True, help="集合名称")
    p_cc.add_argument("--space", default="cosine", choices=["cosine", "l2", "ip"], help="距离度量")
    p_cc.set_defaults(func=cmd_create_collection)

    p_dc = sub.add_parser("delete-collection", help="删除整个集合")
    p_dc.add_argument("--collection", required=True)
    p_dc.set_defaults(func=cmd_delete_collection)

    p_gc = sub.add_parser("get-collection", help="查看集合元信息")
    p_gc.add_argument("--collection", required=True)
    p_gc.set_defaults(func=cmd_get_collection)

    p_add = sub.add_parser("add", help="add：追加记录（id 冲突会报错）")
    p_add.add_argument("--collection", required=True)
    p_add.add_argument("--space", default="cosine", choices=["cosine", "l2", "ip"])
    p_add.add_argument("--payload", type=str, help="负载 JSON 文件路径；缺省从 stdin 读 JSON")
    p_add.set_defaults(func=cmd_add)

    p_up = sub.add_parser("upsert", help="upsert：插入或按 id 覆盖（推荐作为 Update）")
    p_up.add_argument("--collection", required=True)
    p_up.add_argument("--space", default="cosine", choices=["cosine", "l2", "ip"])
    p_up.add_argument("--payload", type=str, help="负载 JSON 文件路径；缺省从 stdin 读 JSON")
    p_up.set_defaults(func=cmd_upsert)

    p_get = sub.add_parser("get", help="按 id 读取记录（Read）")
    p_get.add_argument("--collection", required=True)
    g = p_get.add_mutually_exclusive_group(required=True)
    g.add_argument("--ids-json", dest="ids_json", type=str, help='内联 JSON 数组，例如 \'["id1","id2"]\'')
    g.add_argument("--ids-json-file", type=str, help="包含 id 数组的 JSON 文件路径")
    p_get.add_argument("--include-embeddings", action="store_true", help="返回向量（可能很大）")
    p_get.set_defaults(func=cmd_get)

    p_del = sub.add_parser("delete-ids", help="按 id 删除记录（Delete）")
    p_del.add_argument("--collection", required=True)
    g2 = p_del.add_mutually_exclusive_group(required=True)
    g2.add_argument("--ids-json", dest="ids_json", type=str)
    g2.add_argument("--ids-json-file", type=str)
    p_del.set_defaults(func=cmd_delete_ids)

    p_q = sub.add_parser("query", help="向量/语义查询：--text 使用集合默认 embedding，或传 --query-embedding-json")
    p_q.add_argument("--collection", required=True)
    p_q.add_argument("--text", dest="query_text", type=str, default="", help="查询文本")
    p_q.add_argument(
        "--query-embedding-json",
        type=str,
        default="",
        help="单个查询向量的 JSON 数组字符串",
    )
    p_q.add_argument("--n-results", type=int, default=5)
    p_q.add_argument("--where-json", type=str, default="", help="metadata 过滤条件（JSON），可选")
    p_q.set_defaults(func=cmd_query)

    p_peek = sub.add_parser("peek", help="查看集合中前 N 条（调试）")
    p_peek.add_argument("--collection", required=True)
    p_peek.add_argument("--limit", type=int, default=10)
    p_peek.set_defaults(func=cmd_peek)

    p_cnt = sub.add_parser("count", help="记录条数")
    p_cnt.add_argument("--collection", required=True)
    p_cnt.set_defaults(func=cmd_count)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    _preset_hub_timeouts_before_chroma()
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "http_tuple", None):
        args.http_host = args.http_tuple[0]
        args.http_port = args.http_tuple[1]
    else:
        args.http_host = ""
        args.http_port = 0

    client = build_client(args)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1

    try:
        return int(func(client, args))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
