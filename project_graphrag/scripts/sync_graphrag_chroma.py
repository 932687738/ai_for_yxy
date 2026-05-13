#!/usr/bin/env python3
"""将 project_graphrag 产出的 graph_nodes.jsonl / graph_edges.jsonl 同步到本地持久化 ChromaDB。

Why: JSONL 图谱适合完整导出与脚本处理；Chroma 提供嵌入向量与语义检索，便于「自然语言 → 相关节点/边」。
How: 每行节点/边生成可嵌入文本 + 结构化 metadata，使用 Chroma PersistentClient 落盘。

首次同步会下载 Chroma 默认 ONNX 嵌入模型（约几十 MB）；若遇 httpx ReadTimeout，可增大 HF_HUB_DOWNLOAD_TIMEOUT、
换稳定网络或配置 HuggingFace 镜像；也可使用 --deterministic-embeddings 完全离线同步（检索为近似哈希向量，语义弱于 ONNX）。

依赖: pip install -r project_graphrag/requirements-chroma.txt
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _preset_hub_timeouts_before_chroma() -> None:
    """Chroma 首次写入会下载默认 ONNX 嵌入权重；慢网或企业代理下默认 HTTP 读超时易失败。"""
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "900")
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "120")


def load_jsonl(path: Path) -> List[dict]:
    out: List[dict] = []
    # utf-8-sig：兼容部分编辑器 / PowerShell Set-Content 写入的 UTF-8 BOM
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load_graphrag_config(graph_root: Path) -> dict:
    cfg_path = graph_root / "graphrag_config.json"
    if not cfg_path.exists():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def node_document(n: dict) -> str:
    lines: List[str] = [
        f"节点类型: {n.get('type', '')}",
        f"名称: {n.get('name', '')}",
    ]
    p = n.get("properties") or {}
    qn = p.get("qualified_name")
    if qn:
        lines.append(f"限定名: {qn}")
    rel = p.get("relative_path")
    if rel:
        lines.append(f"相对路径: {rel}")
    fp = p.get("file_path")
    if fp:
        lines.append(f"文件路径: {fp}")
    sig = p.get("signature")
    if sig and isinstance(sig, str):
        snippet = sig.strip().replace("\n", " ")
        if len(snippet) > 1200:
            snippet = snippet[:1200] + "…"
        lines.append(f"签名/片段: {snippet}")
    lang = p.get("language")
    if lang:
        lines.append(f"语言: {lang}")
    line_no = p.get("line")
    if line_no is not None:
        lines.append(f"行号: {line_no}")
    desc = p.get("description")
    if desc and isinstance(desc, str):
        lines.append(f"描述: {desc.strip()[:800]}")
    return "\n".join(lines)


def scalar_metadata_from_node(n: dict) -> dict:
    """Chroma metadata 仅支持标量；复杂字段不入库或转字符串。"""
    p = n.get("properties") or {}
    meta: Dict[str, Any] = {
        "graph_node_id": str(n.get("id", "")),
        "node_type": str(n.get("type", ""))[:256],
        "name": str(n.get("name", ""))[:1024],
    }
    for key in ("relative_path", "qualified_name", "file_path", "language"):
        v = p.get(key)
        if v is not None:
            meta[key] = str(v)[:2048]
    line_no = p.get("line")
    if line_no is not None:
        try:
            meta["line"] = int(line_no)
        except (TypeError, ValueError):
            meta["line"] = 0
    return meta


def edge_stable_id(e: dict) -> str:
    raw = f"{e.get('source_id')}|{e.get('target_id')}|{e.get('type')}|{e.get('properties', {}).get('line', 0)}"
    return f"e_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:32]}"


def edge_document(e: dict, id_to_node: Dict[str, dict]) -> str:
    src = id_to_node.get(e.get("source_id"), {})
    tgt = id_to_node.get(e.get("target_id"), {})
    props = e.get("properties") or {}
    fp = props.get("file_path") or ""
    line = props.get("line", "")
    return (
        f"关系类型: {e.get('type', '')}\n"
        f"源节点: ({src.get('type', '?')}) {src.get('name', e.get('source_id', ''))}\n"
        f"目标节点: ({tgt.get('type', '?')}) {tgt.get('name', e.get('target_id', ''))}\n"
        f"证据文件: {fp}\n"
        f"行号: {line}"
    )


def scalar_metadata_from_edge(e: dict) -> dict:
    p = e.get("properties") or {}
    meta: Dict[str, Any] = {
        "edge_type": str(e.get("type", ""))[:256],
        "source_id": str(e.get("source_id", "")),
        "target_id": str(e.get("target_id", "")),
    }
    fp = p.get("file_path")
    if fp is not None:
        meta["file_path"] = str(fp)[:2048]
    line_no = p.get("line")
    if line_no is not None:
        try:
            meta["line"] = int(line_no)
        except (TypeError, ValueError):
            meta["line"] = 0
    return meta


def batched(seq: List[Any], size: int) -> Iterable[List[Any]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


# 与 Chroma 默认 ONNX MiniLM 维度一致，便于同一集合元数据维度对齐
DETERMINISTIC_EMBEDDING_DIM = 384


def text_embedding_deterministic(text: str, dim: int = DETERMINISTIC_EMBEDDING_DIM) -> List[float]:
    """无需下载模型：由文本派生固定维度单位向量。适合弱网/离线；语义召回质量低于真实嵌入模型。"""
    raw = text.encode("utf-8", errors="ignore")
    vec: List[float] = []
    for i in range(dim):
        h = hashlib.sha256(raw + i.to_bytes(4, "big")).digest()
        x = (int.from_bytes(h[:4], "big") / 2147483648.0) - 1.0
        vec.append(x)
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def sync_collections(
    graph_root: Path,
    persist_dir: Path,
    nodes_collection: str,
    edges_collection: str,
    batch_size: int,
    include_edges: bool,
    reset: bool,
    deterministic_embeddings: bool,
) -> Tuple[int, int]:
    try:
        # noqa: pylint - optional dependency
        import chromadb  # type: ignore
    except ImportError:
        print(
            "未安装 chromadb。请执行: pip install -r project_graphrag/requirements-chroma.txt",
            file=sys.stderr,
        )
        raise SystemExit(2)

    nodes_path = graph_root / "graph_nodes.jsonl"
    edges_path = graph_root / "graph_edges.jsonl"
    if not nodes_path.exists():
        print(f"缺少 {nodes_path}，请先运行 build_graphrag.py 生成图谱。", file=sys.stderr)
        raise SystemExit(1)

    nodes = load_jsonl(nodes_path)
    id_to_node = {n["id"]: n for n in nodes if "id" in n}

    persist_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(presolve := persist_dir.resolve()))
    print(f"Chroma 持久化目录: {presolve}")

    if reset:
        for name in (nodes_collection, edges_collection):
            try:
                client.delete_collection(name)
                print(f"已删除集合: {name}")
            except Exception:
                pass

    coll_nodes = client.get_or_create_collection(
        name=nodes_collection,
        metadata={"hnsw:space": "cosine", "source": "project_graphrag"},
    )

    node_ids: List[str] = []
    node_docs: List[str] = []
    node_metas: List[dict] = []
    for n in nodes:
        nid = str(n.get("id", ""))
        if not nid:
            continue
        node_ids.append(nid)
        node_docs.append(node_document(n))
        node_metas.append(scalar_metadata_from_node(n))

    for chunk_ids, chunk_docs, chunk_metas in zip(
        batched(node_ids, batch_size),
        batched(node_docs, batch_size),
        batched(node_metas, batch_size),
    ):
        if deterministic_embeddings:
            chunk_embs = [text_embedding_deterministic(d) for d in chunk_docs]
            coll_nodes.upsert(
                ids=chunk_ids,
                embeddings=chunk_embs,
                documents=chunk_docs,
                metadatas=chunk_metas,
            )
        else:
            coll_nodes.upsert(ids=chunk_ids, documents=chunk_docs, metadatas=chunk_metas)

    edge_count = 0
    if include_edges and edges_path.exists():
        coll_edges = client.get_or_create_collection(
            name=edges_collection,
            metadata={"hnsw:space": "cosine", "source": "project_graphrag"},
        )
        edges = load_jsonl(edges_path)
        e_ids: List[str] = []
        e_docs: List[str] = []
        e_metas: List[dict] = []
        for e in edges:
            eid = edge_stable_id(e)
            e_ids.append(eid)
            e_docs.append(edge_document(e, id_to_node))
            e_metas.append(scalar_metadata_from_edge(e))
        for chunk_ids, chunk_docs, chunk_metas in zip(
            batched(e_ids, batch_size),
            batched(e_docs, batch_size),
            batched(e_metas, batch_size),
        ):
            if deterministic_embeddings:
                chunk_embs = [text_embedding_deterministic(d) for d in chunk_docs]
                coll_edges.upsert(
                    ids=chunk_ids,
                    embeddings=chunk_embs,
                    documents=chunk_docs,
                    metadatas=chunk_metas,
                )
            else:
                coll_edges.upsert(ids=chunk_ids, documents=chunk_docs, metadatas=chunk_metas)
        edge_count = len(e_ids)
    elif include_edges:
        print(f"未找到 {edges_path}，跳过边集合。", file=sys.stderr)

    return len(node_ids), edge_count


def run_query(
    persist_dir: Path,
    collection_name: str,
    query_text: str,
    top_k: int,
    deterministic_embeddings: bool,
) -> None:
    try:
        import chromadb  # type: ignore
    except ImportError:
        print("未安装 chromadb。", file=sys.stderr)
        raise SystemExit(2)

    client = chromadb.PersistentClient(path=str(persist_dir.resolve()))
    coll = client.get_collection(name=collection_name)
    if deterministic_embeddings:
        qe = text_embedding_deterministic(query_text)
        res = coll.query(query_embeddings=[qe], n_results=top_k)
    else:
        res = coll.query(query_texts=[query_text], n_results=top_k)
    ids_list = res.get("ids") or [[]]
    docs_list = res.get("documents") or [[]]
    meta_list = res.get("metadatas") or [[]]
    dist_list = res.get("distances") or [[]]
    ids = ids_list[0] if ids_list else []
    docs = docs_list[0] if docs_list else []
    metas = meta_list[0] if meta_list else []
    dists = dist_list[0] if dist_list else []
    for i, rid in enumerate(ids):
        dist = dists[i] if i < len(dists) else None
        doc = docs[i] if i < len(docs) else ""
        meta = metas[i] if i < len(metas) else {}
        print(f"--- #{i + 1} id={rid} distance={dist}")
        print(doc)
        if meta:
            print(f"metadata: {json.dumps(meta, ensure_ascii=False)}")


def main() -> int:
    _preset_hub_timeouts_before_chroma()
    parser = argparse.ArgumentParser(description="Sync GraphRAG JSONL artifacts into ChromaDB (local persistent).")
    parser.add_argument("--graph-root", type=Path, required=True, help="图谱根目录（含 graph_nodes.jsonl）")
    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=None,
        help="Chroma 持久化目录，默认 <graph-root>/chroma_data 或 graphrag_config.json 中的 chroma.persist_directory_relative",
    )
    parser.add_argument("--nodes-collection", default=None, help="节点集合名")
    parser.add_argument("--edges-collection", default=None, help="边集合名")
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--skip-edges", action="store_true", help="不同步 graph_edges.jsonl")
    parser.add_argument("--reset", action="store_true", help="删除并重建节点/边集合（清空同名集合）")
    parser.add_argument("--query", default=None, help="同步完成后若指定，则在节点集合上做一次语义查询")
    parser.add_argument("--query-collection", default=None, help="查询使用的集合名，默认与节点集合相同")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument(
        "--deterministic-embeddings",
        action="store_true",
        help="不下载 ONNX 嵌入模型，使用本地 SHA256 派生向量（弱网/离线可用；语义弱于默认模型）。切换模式后请配合 --reset。",
    )
    args = parser.parse_args()

    graph_root = Path(args.graph_root).resolve()
    cfg = load_graphrag_config(graph_root)
    chroma_cfg = cfg.get("chroma") or {}

    persist_dir = args.persist_dir
    if persist_dir is None:
        rel = chroma_cfg.get("persist_directory_relative", "chroma_data")
        persist_dir = graph_root / rel
    else:
        persist_dir = Path(persist_dir).resolve()

    nodes_collection = args.nodes_collection or chroma_cfg.get("nodes_collection", "graphrag_nodes")
    edges_collection = args.edges_collection or chroma_cfg.get("edges_collection", "graphrag_edges")

    if args.deterministic_embeddings:
        print("嵌入模式: 确定性本地向量（无公网模型下载）。")

    node_n, edge_n = sync_collections(
        graph_root=graph_root,
        persist_dir=persist_dir,
        nodes_collection=nodes_collection,
        edges_collection=edges_collection,
        batch_size=max(1, args.batch_size),
        include_edges=not args.skip_edges,
        reset=args.reset,
        deterministic_embeddings=args.deterministic_embeddings,
    )
    print(f"已 upsert 节点: {node_n} 条，边: {edge_n} 条（集合 {nodes_collection} / {edges_collection}）")

    if args.query:
        coll_name = args.query_collection or nodes_collection
        print(f"\n查询集合={coll_name!r} text={args.query!r}\n")
        run_query(
            persist_dir,
            coll_name,
            args.query,
            max(1, args.top_k),
            deterministic_embeddings=args.deterministic_embeddings,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
