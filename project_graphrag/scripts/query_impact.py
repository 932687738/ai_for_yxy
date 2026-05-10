#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Dict, List, Set


def load_jsonl(path: Path) -> List[dict]:
    out: List[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def bfs(start_ids: List[str], graph: Dict[str, List[dict]], depth: int, limit: int) -> Set[str]:
    seen: Set[str] = set(start_ids)
    q = deque([(sid, 0) for sid in start_ids])
    while q and len(seen) < limit:
        cur, d = q.popleft()
        if d >= depth:
            continue
        for e in graph.get(cur, []):
            nxt = e["target_id"]
            if nxt in seen:
                continue
            seen.add(nxt)
            q.append((nxt, d + 1))
            if len(seen) >= limit:
                break
    return seen


def main() -> int:
    parser = argparse.ArgumentParser(description="Impact analysis on GraphRAG artifacts.")
    parser.add_argument("--graph-root", required=True)
    parser.add_argument("--entity", required=True, help="Entity name or fuzzy keyword")
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--limit", type=int, default=400)
    args = parser.parse_args()

    root = Path(args.graph_root).resolve()
    nodes = load_jsonl(root / "graph_nodes.jsonl")
    edges = load_jsonl(root / "graph_edges.jsonl")
    lookup = json.loads((root / "entity_lookup.json").read_text(encoding="utf-8"))
    by_id = {n["id"]: n for n in nodes}

    key = args.entity.lower().strip()
    start_ids = set(lookup.get(key, []))
    if not start_ids:
        # fallback contains match
        for k, ids in lookup.items():
            if key in k:
                start_ids.update(ids)
        if len(start_ids) > 80:
            start_ids = set(list(start_ids)[:80])

    if not start_ids:
        print(json.dumps({"entity": args.entity, "matched": 0, "message": "no matched entities"}, ensure_ascii=False, indent=2))
        return 0

    out_graph: Dict[str, List[dict]] = {}
    in_graph: Dict[str, List[dict]] = {}
    for e in edges:
        out_graph.setdefault(e["source_id"], []).append(e)
        in_graph.setdefault(e["target_id"], []).append(
            {
                "source_id": e["target_id"],
                "target_id": e["source_id"],
                "type": e["type"],
                "properties": e.get("properties", {}),
            }
        )

    forward = bfs(list(start_ids), out_graph, args.depth, args.limit)
    reverse = bfs(list(start_ids), in_graph, args.depth, args.limit)

    def pick(ids: Set[str]) -> List[dict]:
        rows = []
        for nid in ids:
            n = by_id.get(nid)
            if not n:
                continue
            rows.append(
                {
                    "id": n["id"],
                    "type": n["type"],
                    "name": n["name"],
                    "file_path": n.get("properties", {}).get("file_path"),
                    "line": n.get("properties", {}).get("line"),
                    "qualified_name": n.get("properties", {}).get("qualified_name"),
                }
            )
        rows.sort(key=lambda x: (x["type"], x["name"]))
        return rows

    result = {
        "entity": args.entity,
        "matched": len(start_ids),
        "matched_nodes": pick(start_ids),
        "forward_impact_count": len(forward),
        "reverse_impact_count": len(reverse),
        "forward_impact": pick(forward),
        "reverse_impact": pick(reverse),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
