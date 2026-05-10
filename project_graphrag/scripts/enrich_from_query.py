#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


SOURCE_EXTENSIONS = {".java", ".xml", ".properties", ".sql", ".kt", ".py", ".go", ".ts", ".js", ".cs"}
EXCLUDED_DIRS = {".git", ".idea", ".vscode", "node_modules", ".venv", "venv", "target", "build", "dist", "out", "vendor"}


def sha1_text(text: str) -> str:
    import hashlib

    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def atomic_write_json(path: Path, data: object) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    last_error = None
    for _ in range(8):
        try:
            os.replace(tmp, path)
            return
        except PermissionError as ex:
            last_error = ex
            time.sleep(0.3)
    if last_error:
        raise last_error


def atomic_write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    last_error = None
    for _ in range(8):
        try:
            os.replace(tmp, path)
            return
        except PermissionError as ex:
            last_error = ex
            time.sleep(0.3)
    if last_error:
        raise last_error


def load_jsonl(path: Path) -> List[dict]:
    out: List[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def node_id(node_type: str, name: str, path: str = "") -> str:
    return f"n_{sha1_text(f'{node_type}|{name}|{path}')[:24]}"


def edge_key(e: dict) -> str:
    return f"{e['source_id']}|{e['target_id']}|{e['type']}|{e.get('properties', {}).get('line', 0)}"


def build_lookup(nodes: List[dict]) -> dict:
    import re

    lookup: Dict[str, List[str]] = {}
    for n in nodes:
        keys = {n["name"].lower()}
        qn = n.get("properties", {}).get("qualified_name")
        if qn:
            keys.add(qn.lower())
        for part in re.split(r"[._:/\\-]", n["name"]):
            part = part.strip().lower()
            if part:
                keys.add(part)
        for k in keys:
            lookup.setdefault(k, []).append(n["id"])
    return lookup


def find_file_node(nodes: List[dict], path: str) -> Optional[dict]:
    for n in nodes:
        if n["type"] == "FILE" and n.get("properties", {}).get("file_path") == path:
            return n
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill graph evidence nodes from a query keyword.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--graph-root", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--max-matches", type=int, default=600)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    graph_root = Path(args.graph_root).resolve()
    q = args.query.strip().lower()
    if not q:
        return 0

    nodes_path = graph_root / "graph_nodes.jsonl"
    edges_path = graph_root / "graph_edges.jsonl"
    lookup_path = graph_root / "entity_lookup.json"
    if not nodes_path.exists() or not edges_path.exists():
        raise FileNotFoundError("Graph files not found. Build graph first.")

    nodes = load_jsonl(nodes_path)
    edges = load_jsonl(edges_path)
    node_map = {n["id"]: n for n in nodes}
    edge_dedup: Set[str] = {edge_key(e) for e in edges}

    entities_by_file: Dict[str, List[Tuple[int, str, str]]] = {}
    for n in nodes:
        if n["type"] not in {"METHOD", "CLASS"}:
            continue
        fp = n.get("properties", {}).get("file_path")
        line = n.get("properties", {}).get("line")
        if fp and line is not None:
            entities_by_file.setdefault(fp, []).append((int(line), n["id"], n["type"]))
    for fp in entities_by_file:
        entities_by_file[fp].sort(key=lambda x: x[0])

    def closest_owner(file_path: str, line_no: int) -> Optional[str]:
        owner = None
        for ln, nid, nt in entities_by_file.get(file_path, []):
            if ln <= line_no and nt == "METHOD":
                owner = nid
        if owner:
            return owner
        for ln, nid, nt in entities_by_file.get(file_path, []):
            if ln <= line_no and nt == "CLASS":
                owner = nid
        return owner

    match_count = 0
    file_count = 0
    touched_files: Set[str] = set()
    for root, dirs, names in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for name in names:
            p = Path(root) / name
            if p.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            path = str(p.resolve())
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = p.read_text(encoding="latin-1", errors="ignore")
            file_node = find_file_node(nodes, path)
            if not file_node:
                rel = str(p.relative_to(project_root)).replace("\\", "/")
                file_node = {
                    "id": node_id("FILE", rel, path),
                    "type": "FILE",
                    "name": rel,
                    "properties": {"file_path": path, "relative_path": rel},
                }
                node_map[file_node["id"]] = file_node
                nodes.append(file_node)
            lines = text.splitlines()
            for i, line in enumerate(lines, start=1):
                if q not in line.lower():
                    continue
                ev_id = node_id("CODE_EVIDENCE", f"{path}:{i}:{q}")
                ev_node = {
                    "id": ev_id,
                    "type": "CODE_EVIDENCE",
                    "name": q,
                    "properties": {
                        "keyword": q,
                        "file_path": path,
                        "line": i,
                        "snippet": line.strip()[:300],
                    },
                }
                node_map[ev_id] = ev_node
                e1 = {
                    "source_id": file_node["id"],
                    "target_id": ev_id,
                    "type": "REFERENCES",
                    "properties": {"line": i, "file_path": path, "origin": "query_backfill"},
                }
                k1 = edge_key(e1)
                if k1 not in edge_dedup:
                    edge_dedup.add(k1)
                    edges.append(e1)
                owner = closest_owner(path, i)
                if owner:
                    e2 = {
                        "source_id": owner,
                        "target_id": ev_id,
                        "type": "REFERENCES",
                        "properties": {"line": i, "file_path": path, "origin": "query_backfill"},
                    }
                    k2 = edge_key(e2)
                    if k2 not in edge_dedup:
                        edge_dedup.add(k2)
                        edges.append(e2)
                match_count += 1
                touched_files.add(path)
                if match_count >= args.max_matches:
                    break
            if match_count >= args.max_matches:
                break
        if match_count >= args.max_matches:
            break

    file_count = len(touched_files)
    nodes = list(node_map.values())
    lookup = build_lookup(nodes)
    atomic_write_jsonl(nodes_path, nodes)
    atomic_write_jsonl(edges_path, edges)
    atomic_write_json(lookup_path, lookup)

    print(json.dumps({"query": args.query, "matches": match_count, "files": file_count, "nodes": len(nodes), "edges": len(edges)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
