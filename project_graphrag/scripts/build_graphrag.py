#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "vendor",
    "target",
    "build",
    "dist",
    "out",
    ".mvn",
    ".gradle",
}

SOURCE_EXTENSIONS = {
    ".java": "java",
    ".py": "python",
    ".go": "go",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".cs": "csharp",
    ".sql": "sql",
    ".xml": "xml",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".properties": "properties",
    ".kt": "kotlin",
}

TABLE_KEYWORDS = {"from", "join", "update", "into", "table"}

# 标注为待补全（动态调用 / 反射等无法静态解析时写入 gaps 与日志）
GAP_REASON_UNRESOLVED = "unresolved_symbol"
GAP_REASON_AMBIGUOUS_CALL = "ambiguous_call_site"
GAP_REASON_PARSE_SKIP = "parse_exception"


def enrich_method_block_signature(mb: dict, language: str) -> None:
    """在 method 块上补充 return_type、parameters_raw 等（Java/Kotlin/C# 优先）。"""
    sig = mb.get("signature") or ""
    first = sig.split("\n", 1)[0].strip()
    if language in {"java", "kotlin"}:
        stripped = re.sub(
            r"^\s*((public|private|protected|static|final|abstract|synchronized|native|strictfp|default)\s+)+",
            "",
            first,
        )
        m = re.search(r"([A-Za-z_][\w<>\[\],\.\?\@]*(?:\s*[\w<>\[\],\.\?\@]+)*)\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", stripped)
        if m:
            mb["return_type"] = m.group(1).strip()
            mb["parameters_raw"] = m.group(3).strip()
            mb["method_name_parsed"] = m.group(2).strip()
    elif language == "csharp":
        m = re.search(r"([\w<>\[\],\.\?]+)\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", first)
        if m:
            mb["return_type"] = m.group(1).strip()
            mb["parameters_raw"] = m.group(3).strip()
            mb["method_name_parsed"] = m.group(2).strip()


CALL_KEYWORDS = {
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "return",
    "new",
    "throw",
    "sizeof",
    "typeof",
    "case",
    "super",
    "this",
}

RULE_SCAN_EXTENSIONS = {".java", ".xml", ".properties", ".sql", ".kt"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha1_text(text: str) -> str:
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


class Logger:
    def __init__(self, logs_dir: Path):
        logs_dir.mkdir(parents=True, exist_ok=True)
        self.path = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

    def log(self, level: str, message: str) -> None:
        line = f"{datetime.now().isoformat()} [{level}] {message}\n"
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line)

    def info(self, message: str) -> None:
        self.log("INFO", message)

    def warn(self, message: str) -> None:
        self.log("WARN", message)

    def error(self, message: str) -> None:
        self.log("ERROR", message)


class TaskTracker:
    def __init__(self, status_path: Path, logger: Logger):
        self.status_path = status_path
        self.logger = logger
        if status_path.exists():
            try:
                self.data = json.loads(status_path.read_text(encoding="utf-8"))
            except Exception:
                self.data = {}
        else:
            self.data = {}
        self.data.setdefault("tasks", {})
        self.data.setdefault("history", [])

    def save(self) -> None:
        atomic_write_json(self.status_path, self.data)

    def get(self, task_type: str) -> Optional[dict]:
        return self.data["tasks"].get(task_type)

    def start(self, task_id: str, task_type: str, processed_targets: Optional[List[str]] = None) -> None:
        item = {
            "task_id": task_id,
            "task_type": task_type,
            "status": "running",
            "start_time": now_iso(),
            "end_time": None,
            "processed_targets": processed_targets or [],
            "summary": "",
        }
        self.data["tasks"][task_type] = item
        self.data["history"].append(item.copy())
        self.save()
        self.logger.info(f"Task started: {task_type}")

    def complete(self, task_type: str, summary: str, processed_targets: Optional[List[str]] = None) -> None:
        item = self.data["tasks"][task_type]
        item["status"] = "completed"
        item["end_time"] = now_iso()
        item["summary"] = summary
        if processed_targets is not None:
            item["processed_targets"] = processed_targets
        self.data["last_updated"] = now_iso()
        self.save()
        self.logger.info(f"Task completed: {task_type} | {summary}")

    def fail(self, task_type: str, summary: str) -> None:
        item = self.data["tasks"].get(task_type)
        if not item:
            item = {
                "task_id": f"{task_type.lower()}-{int(datetime.now().timestamp())}",
                "task_type": task_type,
                "status": "failed",
                "start_time": now_iso(),
                "end_time": now_iso(),
                "processed_targets": [],
                "summary": summary,
            }
            self.data["tasks"][task_type] = item
        else:
            item["status"] = "failed"
            item["end_time"] = now_iso()
            item["summary"] = summary
        self.save()
        self.logger.error(f"Task failed: {task_type} | {summary}")


@dataclass
class ParsedFile:
    path: str
    language: str
    file_node: dict
    nodes: List[dict]
    raw_edges: List[dict]
    table_defs: List[Tuple[str, List[str], int]]


class GraphBuilder:
    def __init__(self, project_root: Path, graph_root: Path, logger: Logger):
        self.project_root = project_root
        self.graph_root = graph_root
        self.logger = logger
        self.parse_failures: List[str] = []
        self.resolution_gaps: List[dict] = []

        self.nodes_path = graph_root / "graph_nodes.jsonl"
        self.edges_path = graph_root / "graph_edges.jsonl"
        self.file_index_path = graph_root / "file_index.json"
        self.lookup_path = graph_root / "entity_lookup.json"
        self.manifest_path = graph_root / "source_manifest.json"
        self.summary_path = graph_root / "summary.md"

    def has_business_rules(self) -> bool:
        if not self.nodes_path.exists():
            return False
        token = b"\"type\":\"BUSINESS_RULE\""
        with self.nodes_path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                if token in chunk:
                    return True
        return False

    def node_id(self, node_type: str, name: str, path: str = "") -> str:
        return f"n_{sha1_text(f'{node_type}|{name}|{path}')[:24]}"

    def scan_files(self) -> List[dict]:
        files: List[dict] = []
        for root, dirs, names in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for name in names:
                p = Path(root) / name
                ext = p.suffix.lower()
                lang = SOURCE_EXTENSIONS.get(ext)
                if not lang:
                    continue
                try:
                    stat = p.stat()
                    rel = str(p.relative_to(self.project_root)).replace("\\", "/")
                    files.append(
                        {
                            "path": str(p.resolve()),
                            "relative_path": rel,
                            "language": lang,
                            "ext": ext,
                            "mtime": stat.st_mtime,
                            "size": stat.st_size,
                        }
                    )
                except Exception as ex:
                    self.logger.warn(f"Stat failed {p}: {ex}")
        return files

    def hash_file(self, path: str) -> str:
        h = hashlib.sha1()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def detect_changes(self, scanned: List[dict]) -> dict:
        old = {}
        if self.manifest_path.exists():
            try:
                old = json.loads(self.manifest_path.read_text(encoding="utf-8")).get("files", {})
            except Exception:
                old = {}
        current = {}
        added: List[str] = []
        modified: List[str] = []
        for item in scanned:
            fp = item["path"]
            sig = f"{item['mtime']}|{item['size']}"
            current[fp] = {
                "relative_path": item["relative_path"],
                "language": item["language"],
                "mtime": item["mtime"],
                "size": item["size"],
                "sig": sig,
            }
            if fp not in old:
                added.append(fp)
            elif old[fp].get("sig") != sig:
                modified.append(fp)
        deleted = [fp for fp in old.keys() if fp not in current]
        return {"added": added, "modified": modified, "deleted": deleted, "current": current, "old": old}

    def parse_file(self, item: dict) -> ParsedFile:
        path = item["path"]
        language = item["language"]
        text = ""
        try:
            text = Path(path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = Path(path).read_text(encoding="latin-1", errors="ignore")

        lines = text.splitlines()
        file_node = {
            "id": self.node_id("FILE", item["relative_path"], item["path"]),
            "type": "FILE",
            "name": item["relative_path"],
            "properties": {
                "file_path": item["path"],
                "relative_path": item["relative_path"],
                "language": language,
            },
        }
        nodes: List[dict] = [file_node]
        raw_edges: List[dict] = []
        table_defs: List[Tuple[str, List[str], int]] = []

        imports = self.extract_imports(lines, language)
        for imp_name, line_no in imports:
            target_name = imp_name.strip()
            target_id = self.node_id("MODULE", target_name)
            nodes.append(
                {
                    "id": target_id,
                    "type": "MODULE",
                    "name": target_name,
                    "properties": {"external": True},
                }
            )
            raw_edges.append(
                {
                    "source_id": file_node["id"],
                    "target_id": target_id,
                    "type": "IMPORTS",
                    "properties": {"line": line_no, "file_path": path},
                }
            )

        package_name = ""
        if language == "java":
            m = re.search(r"^\s*package\s+([\w\.]+)\s*;", text, flags=re.M)
            if m:
                package_name = m.group(1)

        class_nodes, class_edges, method_nodes, method_edges, extra_nodes, extra_edges = self.extract_entities(
            text=text,
            lines=lines,
            path=item["path"],
            rel_path=item["relative_path"],
            language=language,
            package_name=package_name,
        )
        nodes.extend(class_nodes)
        nodes.extend(method_nodes)
        nodes.extend(extra_nodes)
        raw_edges.extend(class_edges)
        raw_edges.extend(method_edges)
        raw_edges.extend(extra_edges)

        if language in {"java", "kotlin"}:
            for tbl, line_no, origin in self.extract_java_sql_annotations(text):
                raw_edges.append(
                    {
                        "source_id": file_node["id"],
                        "target_name": tbl,
                        "type": "ACCESSES_TABLE",
                        "properties": {"line": line_no, "file_path": path, "mode": origin},
                    }
                )
            for tbl, line_no, origin in self.extract_spring_data_table_refs(text):
                raw_edges.append(
                    {
                        "source_id": file_node["id"],
                        "target_name": tbl,
                        "type": "ACCESSES_TABLE",
                        "properties": {"line": line_no, "file_path": path, "mode": origin},
                    }
                )
        if language == "xml":
            for tbl, line_no, origin in self.extract_mybatis_mapper_tables(text):
                raw_edges.append(
                    {
                        "source_id": file_node["id"],
                        "target_name": tbl,
                        "type": "ACCESSES_TABLE",
                        "properties": {"line": line_no, "file_path": path, "mode": origin},
                    }
                )

        if language in {"sql", "xml", "java", "python", "go", "typescript", "javascript", "csharp"}:
            table_defs.extend(self.extract_create_tables(text))

        return ParsedFile(path=path, language=language, file_node=file_node, nodes=nodes, raw_edges=raw_edges, table_defs=table_defs)

    def extract_imports(self, lines: List[str], language: str) -> List[Tuple[str, int]]:
        out: List[Tuple[str, int]] = []
        if language in {"java", "csharp", "kotlin"}:
            for idx, line in enumerate(lines, start=1):
                m = re.match(r"^\s*import\s+([a-zA-Z0-9_\.\*]+)\s*;?", line)
                if m:
                    out.append((m.group(1), idx))
        elif language == "python":
            for idx, line in enumerate(lines, start=1):
                m1 = re.match(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+", line)
                if m1:
                    out.append((m1.group(1), idx))
                m2 = re.match(r"^\s*import\s+([a-zA-Z0-9_\.,\s]+)", line)
                if m2:
                    for part in m2.group(1).split(","):
                        out.append((part.strip().split(" as ")[0], idx))
        elif language in {"typescript", "javascript"}:
            for idx, line in enumerate(lines, start=1):
                m = re.search(r"import\s+.+?\s+from\s+['\"]([^'\"]+)['\"]", line)
                if m:
                    out.append((m.group(1), idx))
                for m2 in re.finditer(r"require\(['\"]([^'\"]+)['\"]\)", line):
                    out.append((m2.group(1), idx))
        elif language == "go":
            for idx, line in enumerate(lines, start=1):
                m = re.search(r"^\s*import\s+\"([^\"]+)\"", line)
                if m:
                    out.append((m.group(1), idx))
                m2 = re.search(r"^\s*\"([^\"]+)\"\s*$", line)
                if m2:
                    out.append((m2.group(1), idx))
        return out

    def extract_entities(
        self,
        text: str,
        lines: List[str],
        path: str,
        rel_path: str,
        language: str,
        package_name: str,
    ) -> Tuple[List[dict], List[dict], List[dict], List[dict], List[dict], List[dict]]:
        class_nodes: List[dict] = []
        class_edges: List[dict] = []
        method_nodes: List[dict] = []
        method_edges: List[dict] = []
        extra_nodes: List[dict] = []
        extra_edges: List[dict] = []

        class_by_name: Dict[str, dict] = {}
        method_by_key: Dict[str, dict] = {}

        class_pattern = re.compile(
            r"\b(class|interface|enum)\s+([A-Za-z_]\w*)(?:\s+extends\s+([A-Za-z0-9_\.]+))?(?:\s+implements\s+([A-Za-z0-9_\.,\s]+))?"
        )
        py_class_pattern = re.compile(r"^\s*class\s+([A-Za-z_]\w*)(?:\(([^)]*)\))?\s*:")
        go_class_pattern = re.compile(r"^\s*type\s+([A-Za-z_]\w*)\s+(struct|interface)\b")

        for line_no, line in enumerate(lines, start=1):
            if language == "python":
                m = py_class_pattern.match(line)
                if not m:
                    continue
                name = m.group(1)
                bases = [b.strip() for b in (m.group(2) or "").split(",") if b.strip()]
                qn = f"{rel_path}:{name}"
                node = self.make_node("CLASS", qn, name, path, line_no, {"language": language, "kind": "class"})
                class_nodes.append(node)
                class_by_name[name] = node
                for b in bases:
                    class_edges.append(self.make_unresolved_edge(node["id"], b, "INHERITS", path, line_no))
            elif language == "go":
                m = go_class_pattern.match(line)
                if not m:
                    continue
                name, kind = m.groups()
                qn = f"{rel_path}:{name}"
                node = self.make_node("INTERFACE" if kind == "interface" else "CLASS", qn, name, path, line_no, {"language": language})
                class_nodes.append(node)
                class_by_name[name] = node
            else:
                m = class_pattern.search(line)
                if not m:
                    continue
                kind, name, parent, impls = m.groups()
                qn = f"{package_name}.{name}" if package_name else f"{rel_path}:{name}"
                ntype = "INTERFACE" if kind == "interface" else "ENUM" if kind == "enum" else "CLASS"
                node = self.make_node(ntype, qn, name, path, line_no, {"language": language})
                class_nodes.append(node)
                class_by_name[name] = node
                if parent:
                    class_edges.append(self.make_unresolved_edge(node["id"], parent.split(".")[-1], "INHERITS", path, line_no))
                if impls:
                    for itf in [x.strip() for x in impls.split(",") if x.strip()]:
                        class_edges.append(self.make_unresolved_edge(node["id"], itf.split(".")[-1], "IMPLEMENTS", path, line_no))

        blocks = self.extract_method_blocks(lines, language)
        for mb in blocks:
            enrich_method_block_signature(mb, language)
            owner = self.infer_owner_class(mb["start_line"], class_nodes, path)
            mname = mb["name"]
            qn = f"{owner['name']}.{mname}" if owner else f"{rel_path}:{mname}"
            if owner and owner["properties"].get("qualified_name"):
                qn = f"{owner['properties']['qualified_name']}.{mname}"
            meth_props = {
                "signature": mb["signature"],
                "owner_class_id": owner["id"] if owner else None,
                "owner_class_name": owner["name"] if owner else None,
                "language": language,
                "qualified_name": qn,
            }
            if mb.get("return_type"):
                meth_props["return_type"] = mb["return_type"]
            if mb.get("parameters_raw") is not None:
                meth_props["parameters"] = mb["parameters_raw"]
            method_node = self.make_node(
                "METHOD",
                qn,
                mname,
                path,
                mb["start_line"],
                meth_props,
            )
            method_nodes.append(method_node)
            method_by_key[qn] = method_node
            if owner:
                method_edges.append(
                    {
                        "source_id": owner["id"],
                        "target_id": method_node["id"],
                        "type": "DECLARES",
                        "properties": {"line": mb["start_line"], "file_path": path},
                    }
                )

            body = mb["body"]
            for cls in re.findall(r"\bnew\s+([A-Za-z_]\w*)", body):
                method_edges.append(self.make_unresolved_edge(method_node["id"], cls, "INSTANTIATES", path, mb["start_line"]))
            for call in re.findall(r"\b([A-Za-z_]\w*)\s*\(", body):
                if call in CALL_KEYWORDS or call[0].isupper():
                    continue
                method_edges.append(self.make_unresolved_edge(method_node["id"], call, "CALLS", path, mb["start_line"]))
            for tbl in self.extract_table_references(body):
                method_edges.append(self.make_unresolved_edge(method_node["id"], tbl, "ACCESSES_TABLE", path, mb["start_line"]))
            for tref in re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s+[a-zA-Z_]\w*\s*(?:=|;)", body):
                method_edges.append(self.make_unresolved_edge(method_node["id"], tref, "REFERENCES", path, mb["start_line"]))

        for line_no, line in enumerate(lines, start=1):
            if language == "python":
                m = re.match(r"^([A-Za-z_]\w*)\s*=\s*.+", line)
                if m:
                    name = m.group(1)
                    node = self.make_node("GLOBAL_OBJECT", f"{rel_path}:{name}", name, path, line_no, {"language": language})
                    extra_nodes.append(node)
            elif language in {"typescript", "javascript"}:
                m = re.match(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_]\w*)\s*=", line)
                if m:
                    name = m.group(1)
                    node = self.make_node("GLOBAL_OBJECT", f"{rel_path}:{name}", name, path, line_no, {"language": language})
                    extra_nodes.append(node)

        for line_no, line in enumerate(lines, start=1):
            m = re.search(r"@Table\s*\(\s*name\s*=\s*[\"']([A-Za-z0-9_\.]+)[\"']", line)
            if m:
                table_name = m.group(1)
                target_id = self.node_id("DB_TABLE", table_name)
                extra_nodes.append(
                    {
                        "id": target_id,
                        "type": "DB_TABLE",
                        "name": table_name,
                        "properties": {"origin": "orm_annotation"},
                    }
                )
                target_cls = self.closest_class_by_line(class_nodes, line_no)
                if target_cls:
                    extra_edges.append(
                        {
                            "source_id": target_cls["id"],
                            "target_id": target_id,
                            "type": "ACCESSES_TABLE",
                            "properties": {"line": line_no, "file_path": path, "mode": "orm_entity"},
                        }
                    )

        return class_nodes, class_edges, method_nodes, method_edges, extra_nodes, extra_edges

    def extract_method_blocks(self, lines: List[str], language: str) -> List[dict]:
        blocks: List[dict] = []
        if language in {"java", "csharp", "go", "typescript", "javascript", "kotlin"}:
            sig_re = re.compile(
                r"^\s*(?:public|private|protected|internal|static|final|abstract|async|synchronized|virtual|override|\s)*"
                r"(?:[A-Za-z_][\w<>\[\],\.\? ]*\s+)?([A-Za-z_]\w*)\s*\(([^)]*)\)\s*(?:throws [^{]+)?\{"
            )
            brace = 0
            in_method = False
            method = None
            buf: List[str] = []
            for i, line in enumerate(lines, start=1):
                if not in_method:
                    m = sig_re.match(line)
                    if m:
                        name = m.group(1)
                        if name in {"if", "for", "while", "switch", "catch", "return", "new"}:
                            continue
                        in_method = True
                        brace = line.count("{") - line.count("}")
                        method = {"name": name, "signature": line.strip(), "start_line": i, "end_line": i}
                        buf = [line]
                        if brace <= 0:
                            method["body"] = line
                            method["end_line"] = i
                            blocks.append(method)
                            in_method = False
                            method = None
                    continue
                buf.append(line)
                brace += line.count("{") - line.count("}")
                if brace <= 0 and method:
                    method["end_line"] = i
                    method["body"] = "\n".join(buf)
                    blocks.append(method)
                    in_method = False
                    method = None
        elif language == "python":
            sig_re = re.compile(r"^(\s*)def\s+([A-Za-z_]\w*)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?:\s*$")
            in_method = False
            method = None
            indent_len = 0
            buf: List[str] = []
            for i, line in enumerate(lines, start=1):
                if not in_method:
                    m = sig_re.match(line)
                    if m:
                        in_method = True
                        indent_len = len(m.group(1))
                        method = {"name": m.group(2), "signature": line.strip(), "start_line": i, "end_line": i}
                        buf = [line]
                    continue
                cur_indent = len(line) - len(line.lstrip(" "))
                if line.strip() and cur_indent <= indent_len:
                    method["end_line"] = i - 1
                    method["body"] = "\n".join(buf)
                    blocks.append(method)
                    in_method = False
                    method = None
                    if sig_re.match(line):
                        m2 = sig_re.match(line)
                        in_method = True
                        indent_len = len(m2.group(1))
                        method = {"name": m2.group(2), "signature": line.strip(), "start_line": i, "end_line": i}
                        buf = [line]
                    continue
                buf.append(line)
            if in_method and method:
                method["end_line"] = len(lines)
                method["body"] = "\n".join(buf)
                blocks.append(method)
        return blocks

    def infer_owner_class(self, start_line: int, class_nodes: List[dict], file_path: str) -> Optional[dict]:
        candidate = None
        for cls in class_nodes:
            if cls["properties"]["file_path"] != file_path:
                continue
            if cls["properties"]["line"] <= start_line:
                if candidate is None or cls["properties"]["line"] > candidate["properties"]["line"]:
                    candidate = cls
        return candidate

    def closest_class_by_line(self, class_nodes: List[dict], line_no: int) -> Optional[dict]:
        candidate = None
        for cls in class_nodes:
            if cls["properties"]["line"] <= line_no:
                if candidate is None or cls["properties"]["line"] > candidate["properties"]["line"]:
                    candidate = cls
        return candidate

    def extract_create_tables(self, text: str) -> List[Tuple[str, List[str], int]]:
        out: List[Tuple[str, List[str], int]] = []
        create_pat = re.compile(r"create\s+table\s+([`\"\[]?)([A-Za-z0-9_\.]+)\1\s*\((.*?)\)\s*;", re.I | re.S)
        for m in create_pat.finditer(text):
            name = m.group(2)
            body = m.group(3)
            line_no = text[: m.start()].count("\n") + 1
            cols: List[str] = []
            for raw in body.splitlines():
                line = raw.strip().rstrip(",")
                if not line:
                    continue
                head = re.split(r"\s+", line, maxsplit=1)[0].strip("`[]\"")
                if head.lower() in {"primary", "foreign", "constraint", "key", "unique", "index"}:
                    continue
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", head):
                    cols.append(head)
            out.append((name, cols, line_no))
        return out

    def extract_table_references(self, body: str) -> List[str]:
        tables: Set[str] = set()
        for m in re.finditer(r"\b(from|join|update|into|table)\s+[`\"\[]?([A-Za-z0-9_\.]+)", body, re.I):
            tname = m.group(2).strip("`[]\"")
            if tname:
                tables.add(tname)
        for m in re.finditer(r"\bmerge\s+into\s+[`\"\[]?([A-Za-z0-9_\.]+)", body, re.I):
            tname = m.group(1).strip("`[]\"")
            if tname:
                tables.add(tname)
        return sorted(tables)

    def extract_mybatis_mapper_tables(self, text: str) -> List[Tuple[str, int, str]]:
        """从 MyBatis Mapper XML 中提取表引用（行号近似为标签起始行）。"""
        out: List[Tuple[str, int, str]] = []
        low = text.lower()
        if "mapper" not in low and "<select" not in low and "<insert" not in low:
            return out
        # 大段 SQL：select/insert/update/delete/sql 块内全文抓取
        block_pat = re.compile(
            r"<\s*(select|insert|update|delete|sql)\b[^>]*>(.*?)</\s*\1\s*>",
            re.I | re.S,
        )
        for m in block_pat.finditer(text):
            tag = m.group(1).lower()
            chunk = m.group(2)
            line_no = text[: m.start()].count("\n") + 1
            # 去 CDATA
            chunk = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", chunk, flags=re.S)
            for tbl in self.extract_table_references(chunk):
                out.append((tbl, line_no, f"mybatis_{tag}"))
        # 逐行 from / join（补漏）
        for i, line in enumerate(text.splitlines(), start=1):
            for tbl in self.extract_table_references(line):
                out.append((tbl, i, "mybatis_line"))
        return out

    def extract_java_sql_annotations(self, text: str) -> List[Tuple[str, int, str]]:
        """@Select @Insert @Update @Delete … 中字符串 SQL 的表引用。"""
        out: List[Tuple[str, int, str]] = []
        anno_pat = re.compile(
            r"@(Select|Insert|Update|Delete)\s*\(\s*(?:\"([^\"]+)\"|'([^']+)')",
            re.S,
        )
        for m in anno_pat.finditer(text):
            kind = m.group(1).lower()
            sql = (m.group(2) or m.group(3) or "").replace("\\n", "\n")
            line_no = text[: m.start()].count("\n") + 1
            for tbl in self.extract_table_references(sql):
                out.append((tbl, line_no, f"jpa_mybatis_annotation_{kind}"))
        return out

    def extract_spring_data_table_refs(self, text: str) -> List[Tuple[str, int, str]]:
        """Spring Data / JPA 常见 value= 原生查询中的表（保守正则）。"""
        out: List[Tuple[str, int, str]] = []
        for m in re.finditer(r"(?:query|nativeQuery)\s*=\s*(?:\"([^\"]{10,2000})\"|'([^']{10,2000})')", text, re.S):
            sql = (m.group(1) or m.group(2) or "").replace("\\n", "\n")
            line_no = text[: m.start()].count("\n") + 1
            for tbl in self.extract_table_references(sql):
                out.append((tbl, line_no, "spring_data_query"))
        return out

    def make_node(self, node_type: str, qualified_name: str, name: str, path: str, line: int, extra: dict) -> dict:
        node = {
            "id": self.node_id(node_type, qualified_name, path),
            "type": node_type,
            "name": name,
            "properties": {
                "qualified_name": qualified_name,
                "file_path": path,
                "line": line,
            },
        }
        node["properties"].update(extra)
        return node

    def make_unresolved_edge(self, source_id: str, target_name: str, edge_type: str, path: str, line: int) -> dict:
        return {
            "source_id": source_id,
            "target_name": target_name,
            "type": edge_type,
            "properties": {"line": line, "file_path": path},
        }

    def load_jsonl(self, path: Path) -> List[dict]:
        out: List[dict] = []
        if not path.exists():
            return out
        with path.open("r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError as ex:
                    self.logger.warn(f"Skipping malformed JSONL row {lineno} in {path.name}: {ex}")
        return out

    def build_or_update(self, scanned: List[dict], changes: dict, force_full: bool = False) -> Tuple[List[dict], List[dict], dict]:
        self.parse_failures.clear()
        self.resolution_gaps.clear()
        full_build = force_full or not self.nodes_path.exists() or not self.edges_path.exists() or not self.file_index_path.exists()
        changed_files = set(changes["added"] + changes["modified"])
        deleted_files = set(changes["deleted"])
        if full_build:
            self.logger.info("Graph mode: full build (no prior graph data).")
        else:
            self.logger.info(
                f"Graph mode: incremental update (added={len(changes['added'])}, modified={len(changes['modified'])}, deleted={len(changes['deleted'])})."
            )

        if full_build:
            base_nodes: List[dict] = []
            base_edges: List[dict] = []
            file_index: Dict[str, dict] = {}
            targets = scanned
        else:
            base_nodes = self.load_jsonl(self.nodes_path)
            base_edges = self.load_jsonl(self.edges_path)
            file_index = json.loads(self.file_index_path.read_text(encoding="utf-8"))
            remove_paths = changed_files | deleted_files
            remove_node_ids: Set[str] = set()
            for fp in remove_paths:
                info = file_index.get(fp, {})
                for nid in info.get("node_ids", []):
                    remove_node_ids.add(nid)
                file_index.pop(fp, None)
            base_nodes = [n for n in base_nodes if n["id"] not in remove_node_ids]
            base_edges = [e for e in base_edges if e["source_id"] not in remove_node_ids and e["target_id"] not in remove_node_ids]
            targets = [x for x in scanned if x["path"] in changed_files]

        all_nodes = list(base_nodes)
        all_edges = list(base_edges)

        node_map = {n["id"]: n for n in all_nodes}
        edges_dedup = {self.edge_key(e) for e in all_edges}

        for item in targets:
            try:
                parsed = self.parse_file(item)
            except Exception as ex:
                self.logger.warn(f"Parse failed, skipped: {item['path']} | {ex}")
                self.logger.warn(traceback.format_exc())
                self.parse_failures.append(f"{item['relative_path']} | {ex}")
                continue

            local_node_ids: List[str] = []
            for node in parsed.nodes:
                node_map[node["id"]] = node
                local_node_ids.append(node["id"])

            file_index[item["path"]] = {
                "relative_path": item["relative_path"],
                "language": item["language"],
                "mtime": item["mtime"],
                "size": item["size"],
                "hash": self.hash_file(item["path"]),
                "node_ids": local_node_ids,
            }

            for tname, cols, line_no in parsed.table_defs:
                table_id = self.node_id("DB_TABLE", tname)
                node_map[table_id] = {
                    "id": table_id,
                    "type": "DB_TABLE",
                    "name": tname,
                    "properties": {"file_path": item["path"], "line": line_no, "origin": "sql_create"},
                }
                for col in cols:
                    col_qn = f"{tname}.{col}"
                    col_id = self.node_id("DB_COLUMN", col_qn)
                    node_map[col_id] = {
                        "id": col_id,
                        "type": "DB_COLUMN",
                        "name": col,
                        "properties": {"qualified_name": col_qn, "file_path": item["path"], "line": line_no},
                    }
                    self.add_edge(
                        all_edges,
                        edges_dedup,
                        {
                            "source_id": col_id,
                            "target_id": table_id,
                            "type": "COLUMN_OF",
                            "properties": {"file_path": item["path"], "line": line_no},
                        },
                    )

            for edge in parsed.raw_edges:
                self.add_edge(all_edges, edges_dedup, edge)

        all_nodes = list(node_map.values())
        resolved_edges = self.resolve_edges(all_nodes, all_edges)
        all_edges = resolved_edges

        return all_nodes, all_edges, file_index

    def edge_key(self, e: dict) -> str:
        return f"{e['source_id']}|{e['target_id']}|{e['type']}|{e.get('properties', {}).get('line', 0)}"

    def add_edge(self, edges: List[dict], dedup: Set[str], edge: dict) -> None:
        if "target_name" in edge:
            edges.append(edge)
            return
        key = self.edge_key(edge)
        if key in dedup:
            return
        dedup.add(key)
        edges.append(edge)

    def resolve_edges(self, nodes: List[dict], edges: List[dict]) -> List[dict]:
        name_to_nodes: Dict[str, List[dict]] = {}
        method_by_name: Dict[str, List[dict]] = {}
        for n in nodes:
            name_to_nodes.setdefault(n["name"], []).append(n)
            if n["type"] == "METHOD":
                method_by_name.setdefault(n["name"], []).append(n)

        resolved: List[dict] = []
        dedup: Set[str] = set()

        def record_gap(edge: dict, reason: str, detail: str) -> None:
            self.resolution_gaps.append(
                {
                    "reason": reason,
                    "edge_type": edge.get("type"),
                    "target_name": edge.get("target_name"),
                    "source_id": edge.get("source_id"),
                    "file_path": edge.get("properties", {}).get("file_path"),
                    "line": edge.get("properties", {}).get("line"),
                    "detail": detail,
                    "status": "可补全点",
                }
            )

        for e in edges:
            if "target_name" not in e:
                key = self.edge_key(e)
                if key not in dedup:
                    dedup.add(key)
                    resolved.append(e)
                continue

            target_name = e["target_name"]
            candidates: List[dict] = []
            if e["type"] == "CALLS":
                candidates = method_by_name.get(target_name, [])
            elif e["type"] in {"INHERITS", "IMPLEMENTS", "INSTANTIATES", "REFERENCES"}:
                candidates = [n for n in name_to_nodes.get(target_name, []) if n["type"] in {"CLASS", "INTERFACE", "ENUM"}]
            elif e["type"] == "ACCESSES_TABLE":
                candidates = [n for n in name_to_nodes.get(target_name, []) if n["type"] == "DB_TABLE"]
                if not candidates:
                    tid = self.node_id("DB_TABLE", target_name)
                    table_node = {"id": tid, "type": "DB_TABLE", "name": target_name, "properties": {"origin": "inferred_access"}}
                    nodes.append(table_node)
                    name_to_nodes.setdefault(target_name, []).append(table_node)
                    candidates = [table_node]

            if not candidates:
                record_gap(e, GAP_REASON_UNRESOLVED, "no matching symbol in graph")
                continue
            if e["type"] == "CALLS" and len(candidates) > 8:
                record_gap(e, GAP_REASON_AMBIGUOUS_CALL, f"{len(candidates)} method overload candidates")
                continue
            for c in candidates:
                edge = {
                    "source_id": e["source_id"],
                    "target_id": c["id"],
                    "type": e["type"],
                    "properties": e.get("properties", {}),
                }
                key = self.edge_key(edge)
                if key in dedup:
                    continue
                dedup.add(key)
                resolved.append(edge)

        return resolved

    def build_lookup(self, nodes: List[dict]) -> dict:
        lookup: Dict[str, List[str]] = {}
        for n in nodes:
            keys = {n["name"].lower()}
            qn = n["properties"].get("qualified_name")
            if qn:
                keys.add(qn.lower())
            for part in re.split(r"[._:/]", n["name"]):
                part = part.strip().lower()
                if part:
                    keys.add(part)
            for k in keys:
                lookup.setdefault(k, []).append(n["id"])
        return lookup

    def write_outputs(self, nodes: List[dict], edges: List[dict], file_index: dict, manifest: dict) -> None:
        nodes = sorted(nodes, key=lambda x: (x["type"], x["name"], x["id"]))
        edges = sorted(edges, key=lambda x: (x["type"], x["source_id"], x["target_id"]))
        lookup = self.build_lookup(nodes)

        atomic_write_jsonl(self.nodes_path, nodes)
        atomic_write_jsonl(self.edges_path, edges)
        atomic_write_json(self.file_index_path, file_index)
        atomic_write_json(self.lookup_path, lookup)
        atomic_write_json(self.manifest_path, manifest)

    def enrich_business_rules(self, nodes: List[dict], edges: List[dict], scanned: List[dict]) -> Tuple[List[dict], List[dict], dict]:
        node_map = {n["id"]: n for n in nodes}
        edge_dedup = {self.edge_key(e) for e in edges}

        def add_node(node: dict) -> None:
            node_map[node["id"]] = node

        def add_edge(edge: dict) -> None:
            if "target_name" in edge:
                return
            key = self.edge_key(edge)
            if key in edge_dedup:
                return
            edge_dedup.add(key)
            edges.append(edge)

        loc_quarantine = {
            "id": self.node_id("LOC_TYPE", "QUARANTINE"),
            "type": "LOC_TYPE",
            "name": "QUARANTINE",
            "properties": {"code": "CIC_LOC_TYPE_QUARANTINE", "description": "Quarantine location type"},
        }
        loc_exception = {
            "id": self.node_id("LOC_TYPE", "EXCEPTION"),
            "type": "LOC_TYPE",
            "name": "EXCEPTION",
            "properties": {"code": "CIC_LOC_TYPE_EXCEPTION", "description": "Exception location type"},
        }
        stock_table = {
            "id": self.node_id("DB_TABLE", "stock"),
            "type": "DB_TABLE",
            "name": "stock",
            "properties": {"origin": "business_rule_enrichment"},
        }
        add_node(loc_quarantine)
        add_node(loc_exception)
        add_node(stock_table)

        quantity_cols = ["qty", "available_qty", "allocated_qty", "picked_qty", "on_hold_qty", "lend_qty"]
        col_nodes: Dict[str, dict] = {}
        for col in quantity_cols:
            qn = f"stock.{col}"
            col_node = {
                "id": self.node_id("DB_COLUMN", qn),
                "type": "DB_COLUMN",
                "name": col,
                "properties": {"qualified_name": qn, "origin": "business_rule_enrichment"},
            }
            add_node(col_node)
            col_nodes[col] = col_node
            add_edge(
                {
                    "source_id": col_node["id"],
                    "target_id": stock_table["id"],
                    "type": "COLUMN_OF",
                    "properties": {"origin": "business_rule_enrichment", "line": 0},
                }
            )

        file_entities: Dict[str, List[Tuple[int, str, str]]] = {}
        for n in node_map.values():
            if n["type"] not in {"METHOD", "CLASS"}:
                continue
            fp = n.get("properties", {}).get("file_path")
            line = n.get("properties", {}).get("line")
            if not fp or line is None:
                continue
            file_entities.setdefault(fp, []).append((int(line), n["id"], n["type"]))
        for fp in file_entities:
            file_entities[fp].sort(key=lambda x: x[0])

        def closest_owner(file_path: str, line: int) -> Optional[str]:
            owner = None
            for ln, nid, nt in file_entities.get(file_path, []):
                if ln <= line and nt == "METHOD":
                    owner = nid
            if owner:
                return owner
            for ln, nid, nt in file_entities.get(file_path, []):
                if ln <= line and nt == "CLASS":
                    owner = nid
            return owner

        patterns = [
            ("QUARANTINE_LOC_VALIDATION", re.compile(r"quarantine|err_quarantine|cic_loc_type_quarantine", re.I)),
            ("EXCEPTION_LOC_VALIDATION", re.compile(r"exception.*loc|err_exception_loc|cic_loc_type_exception", re.I)),
            ("LEND_QTY_CHANGE", re.compile(r"lend_qty|lendqty|deltalendqty", re.I)),
            (
                "STOCK_QTY_FORMULA",
                re.compile(r"qty.*available[_ ]qty.*allocated[_ ]qty.*picked[_ ]qty.*on[_ ]hold[_ ]qty.*lend[_ ]qty", re.I),
            ),
            ("LEND_QTY_NON_NEGATIVE", re.compile(r"lend_qty\s*\+\s*#\{[^}]+\}\s*>=\s*0", re.I)),
        ]

        rule_count = 0
        rule_files = 0
        touched: Set[str] = set()

        for item in scanned:
            ext = item["ext"].lower()
            if ext not in RULE_SCAN_EXTENSIONS:
                continue
            path = item["path"]
            try:
                text = Path(path).read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = Path(path).read_text(encoding="latin-1", errors="ignore")
            lines = text.splitlines()
            file_node_id = self.node_id("FILE", item["relative_path"], item["path"])
            for idx, line in enumerate(lines, start=1):
                if len(line) > 350:
                    sample = line[:350]
                else:
                    sample = line
                lower_line = line.lower()
                for category, regex in patterns:
                    if not regex.search(lower_line):
                        continue
                    rid = self.node_id("BUSINESS_RULE", f"{path}:{idx}:{category}")
                    rule_node = {
                        "id": rid,
                        "type": "BUSINESS_RULE",
                        "name": category,
                        "properties": {
                            "file_path": path,
                            "line": idx,
                            "snippet": sample.strip(),
                            "category": category,
                        },
                    }
                    add_node(rule_node)
                    owner_id = closest_owner(path, idx) or file_node_id
                    add_edge(
                        {
                            "source_id": owner_id,
                            "target_id": rid,
                            "type": "REFERENCES",
                            "properties": {"line": idx, "file_path": path, "reason": "business_rule"},
                        }
                    )
                    if "QUARANTINE" in category:
                        add_edge(
                            {
                                "source_id": rid,
                                "target_id": loc_quarantine["id"],
                                "type": "REFERENCES",
                                "properties": {"line": idx, "file_path": path},
                            }
                        )
                    if "EXCEPTION" in category:
                        add_edge(
                            {
                                "source_id": rid,
                                "target_id": loc_exception["id"],
                                "type": "REFERENCES",
                                "properties": {"line": idx, "file_path": path},
                            }
                        )
                    if "LEND_QTY" in category or "FORMULA" in category:
                        add_edge(
                            {
                                "source_id": rid,
                                "target_id": stock_table["id"],
                                "type": "REFERENCES",
                                "properties": {"line": idx, "file_path": path},
                            }
                        )
                        add_edge(
                            {
                                "source_id": rid,
                                "target_id": col_nodes["lend_qty"]["id"],
                                "type": "REFERENCES",
                                "properties": {"line": idx, "file_path": path},
                            }
                        )
                    if category == "STOCK_QTY_FORMULA":
                        for col in quantity_cols:
                            add_edge(
                                {
                                    "source_id": rid,
                                    "target_id": col_nodes[col]["id"],
                                    "type": "REFERENCES",
                                    "properties": {"line": idx, "file_path": path},
                                }
                            )
                    touched.add(path)
                    rule_count += 1

        rule_files = len(touched)
        return list(node_map.values()), edges, {"rule_count": rule_count, "rule_files": rule_files}

    def test_queries(self, nodes: List[dict], edges: List[dict]) -> List[dict]:
        by_id = {n["id"]: n for n in nodes}
        out_edges: Dict[str, List[dict]] = {}
        in_edges: Dict[str, List[dict]] = {}
        for e in edges:
            out_edges.setdefault(e["source_id"], []).append(e)
            in_edges.setdefault(e["target_id"], []).append(e)
        method_nodes = [n for n in nodes if n["type"] == "METHOD"]
        tests: List[dict] = []
        for n in method_nodes[:3]:
            fwd = self.bfs(n["id"], out_edges, limit=80)
            rev = self.bfs(n["id"], in_edges, limit=80)
            tables = [by_id[x]["name"] for x in fwd if by_id.get(x, {}).get("type") == "DB_TABLE"]
            tests.append(
                {
                    "entity": n["properties"].get("qualified_name", n["name"]),
                    "forward_reach": len(fwd),
                    "reverse_reach": len(rev),
                    "tables": tables[:10],
                }
            )
        return tests

    def bfs(self, start: str, graph: Dict[str, List[dict]], limit: int = 100) -> List[str]:
        seen: Set[str] = {start}
        q = [start]
        while q and len(seen) < limit:
            cur = q.pop(0)
            for e in graph.get(cur, []):
                nxt = e["target_id"]
                if nxt in seen:
                    continue
                seen.add(nxt)
                q.append(nxt)
                if len(seen) >= limit:
                    break
        return list(seen)

    def write_summary(
        self,
        nodes: List[dict],
        edges: List[dict],
        tests: List[dict],
        changes: dict,
        scanned_file_count: int = 0,
        indexed_file_count: int = 0,
        force_full: bool = False,
    ) -> None:
        type_count: Dict[str, int] = {}
        edge_count: Dict[str, int] = {}
        for n in nodes:
            type_count[n["type"]] = type_count.get(n["type"], 0) + 1
        for e in edges:
            edge_count[e["type"]] = edge_count.get(e["type"], 0) + 1
        table_count = type_count.get("DB_TABLE", 0)
        lines = [
            "# GraphRAG Summary",
            "",
            f"- Generated At (UTC): {now_iso()}",
            f"- Project Root: {self.project_root}",
            f"- Graph Storage: {self.graph_root}",
            f"- Build Mode: {'full (forced)' if force_full else 'incremental / auto'}",
            f"- Total Nodes (entities): {len(nodes)}",
            f"- Total Edges: {len(edges)}",
            f"- DB_TABLE Count: {table_count}",
            f"- Source Files Scanned (eligible extensions): {scanned_file_count}",
            f"- Files Indexed in Graph (parsed into file_index): {indexed_file_count}",
            f"- File Coverage: {100.0 * indexed_file_count / scanned_file_count:.2f}%" if scanned_file_count else "- File Coverage: n/a",
            f"- Parse Failures (count): {len(self.parse_failures)}",
            f"- 可补全点 / Resolution Gaps (count): {len(self.resolution_gaps)}",
            f"- Changed Files (manifest delta): added={len(changes['added'])}, modified={len(changes['modified'])}, deleted={len(changes['deleted'])}",
            "",
            "## Node Counts",
        ]
        for k in sorted(type_count):
            lines.append(f"- {k}: {type_count[k]}")
        lines.extend(["", "## Edge Counts"])
        for k in sorted(edge_count):
            lines.append(f"- {k}: {edge_count[k]}")
        lines.extend(["", "## Query Smoke Tests"])
        if not tests:
            lines.append("- No method nodes found for smoke test.")
        for t in tests:
            lines.append(
                f"- {t['entity']}: forward={t['forward_reach']}, reverse={t['reverse_reach']}, tables={', '.join(t['tables']) if t['tables'] else 'none'}"
            )
        lines.extend(["", "## Parse Failures / 无法解析清单", ""])
        if not self.parse_failures:
            lines.append("- (none — 全部成功解析或已跳过记录为空)")
        else:
            cap = 800
            for i, row in enumerate(self.parse_failures[:cap], start=1):
                lines.append(f"{i}. {row}")
            if len(self.parse_failures) > cap:
                lines.append(f"- … 共 {len(self.parse_failures)} 条，此处截断展示前 {cap} 条；完整列表见 `parse_failures.jsonl`。")

        lines.extend(["", "## 可补全点 (静态无法落地边的调用/符号)", ""])
        if not self.resolution_gaps:
            lines.append("- (none)")
        else:
            gcap = 400
            for i, g in enumerate(self.resolution_gaps[:gcap], start=1):
                lines.append(
                    f"{i}. [{g.get('reason')}] {g.get('edge_type')} → `{g.get('target_name')}` @ {g.get('file_path')}:{g.get('line')} — {g.get('detail')}"
                )
            if len(self.resolution_gaps) > gcap:
                lines.append(f"- … 共 {len(self.resolution_gaps)} 条，此处截断；完整数据见 `resolution_gaps.jsonl`。")

        tmp = self.summary_path.with_suffix(".md.tmp")
        tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.replace(tmp, self.summary_path)

        gaps_path = self.graph_root / "resolution_gaps.jsonl"
        with gaps_path.open("w", encoding="utf-8", newline="\n") as gf:
            for g in self.resolution_gaps:
                gf.write(json.dumps(g, ensure_ascii=False) + "\n")
        fail_path = self.graph_root / "parse_failures.jsonl"
        with fail_path.open("w", encoding="utf-8", newline="\n") as ff:
            for row in self.parse_failures:
                ff.write(json.dumps({"path": row}, ensure_ascii=False) + "\n")


def should_skip_completed(task: Optional[dict], required_paths: List[Path]) -> bool:
    if not task or task.get("status") != "completed":
        return False
    return all(p.exists() for p in required_paths)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and maintain project GraphRAG artifacts.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--graph-root", required=True)
    parser.add_argument(
        "--force-full",
        action="store_true",
        help="Ignore incremental 'no changes' short-circuit; rebuild graph from all scanned sources into graph-root.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    graph_root = Path(args.graph_root).resolve()
    graph_root.mkdir(parents=True, exist_ok=True)
    logs_dir = graph_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = Logger(logs_dir)
    status_path = graph_root / "task_status.json"
    tracker = TaskTracker(status_path, logger)
    builder = GraphBuilder(project_root, graph_root, logger)

    logger.info(f"Build started: project_root={project_root}, graph_root={graph_root}")

    try:
        task = tracker.get("SCAN_DIR_STRUCTURE")
        scanned: List[dict]
        if should_skip_completed(task, [builder.file_index_path, builder.manifest_path]):
            logger.info("Task SCAN_DIR_STRUCTURE skipped by checkpoint.")
            scanned = builder.scan_files()
        else:
            tracker.start(f"scan-{int(datetime.now().timestamp())}", "SCAN_DIR_STRUCTURE")
            scanned = builder.scan_files()
            changes = builder.detect_changes(scanned)
            tracker.complete(
                "SCAN_DIR_STRUCTURE",
                f"Scanned source files: {len(scanned)} | added={len(changes['added'])}, modified={len(changes['modified'])}, deleted={len(changes['deleted'])}",
                processed_targets=[x["relative_path"] for x in scanned[:3000]],
            )

        changes = builder.detect_changes(scanned)
        need_work = bool(
            args.force_full
            or not builder.nodes_path.exists()
            or not builder.edges_path.exists()
            or len(changes["added"]) > 0
            or len(changes["modified"]) > 0
            or len(changes["deleted"]) > 0
            or not builder.has_business_rules()
        )
        if args.force_full:
            logger.info("force-full: full graph rebuild from all scanned files (no incremental skip).")

        if not need_work:
            logger.info("No file change detected; skip parse/build/index tasks.")
            for task_type in [
                "PARSE_CLASSES",
                "PARSE_METHODS",
                "PARSE_DB_TABLES",
                "PARSE_BUSINESS_RULES",
                "BUILD_GRAPH_NODES",
                "BUILD_GRAPH_EDGES",
                "INDEX_GRAPH",
            ]:
                if not tracker.get(task_type) or tracker.get(task_type).get("status") != "completed":
                    tracker.start(f"{task_type.lower()}-{int(datetime.now().timestamp())}", task_type)
                    tracker.complete(task_type, "Skipped due to no source changes.")
            tracker.start(f"auto-update-{int(datetime.now().timestamp())}", "AUTO_UPDATE", processed_targets=[])
            tracker.complete("AUTO_UPDATE", "No changes. Graph unchanged.")
            return 0

        tracker.start(f"parse-classes-{int(datetime.now().timestamp())}", "PARSE_CLASSES")
        tracker.complete(
            "PARSE_CLASSES",
            f"Prepared parse workload: {len(scanned)} files, changed_set={len(changes['added']) + len(changes['modified'])}",
            processed_targets=[Path(p).name for p in (changes["added"] + changes["modified"])[:3000]],
        )

        tracker.start(f"parse-methods-{int(datetime.now().timestamp())}", "PARSE_METHODS")
        tracker.complete("PARSE_METHODS", "Method parsing delegated to graph build pipeline.")

        tracker.start(f"parse-db-{int(datetime.now().timestamp())}", "PARSE_DB_TABLES")
        tracker.complete("PARSE_DB_TABLES", "DB table identification delegated to graph build pipeline.")

        tracker.start(f"parse-rules-{int(datetime.now().timestamp())}", "PARSE_BUSINESS_RULES")
        tracker.complete("PARSE_BUSINESS_RULES", "Business rule parsing scheduled in graph build pipeline.")

        tracker.start(f"build-nodes-{int(datetime.now().timestamp())}", "BUILD_GRAPH_NODES")
        nodes, edges, file_index = builder.build_or_update(scanned, changes, force_full=args.force_full)
        tracker.complete("BUILD_GRAPH_NODES", f"Built nodes: {len(nodes)}")

        tracker.start(f"build-edges-{int(datetime.now().timestamp())}", "BUILD_GRAPH_EDGES")
        nodes, edges, rule_stats = builder.enrich_business_rules(nodes, edges, scanned)
        tracker.complete("BUILD_GRAPH_EDGES", f"Built edges: {len(edges)}")

        tracker.start(f"index-{int(datetime.now().timestamp())}", "INDEX_GRAPH")
        # manifest 与 file_index 对齐：以当前扫描集为准写入文件清单（签名用于下次增量）
        manifest = {"project_root": str(project_root), "generated_at": now_iso(), "files": changes["current"]}
        builder.write_outputs(nodes, edges, file_index, manifest)
        tracker.complete("INDEX_GRAPH", "Graph files and indexes persisted.")

        tracker.start(f"test-{int(datetime.now().timestamp())}", "QUERY_TEST")
        tests = builder.test_queries(nodes, edges)
        builder.write_summary(
            nodes,
            edges,
            tests,
            changes,
            scanned_file_count=len(scanned),
            indexed_file_count=len(file_index),
            force_full=args.force_full,
        )
        tracker.complete("QUERY_TEST", f"Smoke tests executed: {len(tests)}")

        tracker.start(f"auto-update-{int(datetime.now().timestamp())}", "AUTO_UPDATE")
        tracker.complete(
            "AUTO_UPDATE",
            f"Incremental policy active. added={len(changes['added'])}, modified={len(changes['modified'])}, deleted={len(changes['deleted'])}",
            processed_targets=[Path(p).name for p in (changes["added"] + changes["modified"] + changes["deleted"])[:3000]],
        )

        logger.info("Build finished successfully.")
        return 0
    except Exception as ex:
        logger.error(f"Unhandled failure: {ex}")
        logger.error(traceback.format_exc())
        tracker.fail("AUTO_UPDATE", f"Unhandled failure: {ex}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
