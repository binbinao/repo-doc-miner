#!/usr/bin/env python3
"""Generate a repository topology map (Mermaid) + entity inventory.

Part of the repo-doc-miner skill (v2, topology-first). Given a repository
root, this script:

  1. Detects entity types present in the repo (modules, skills, agents,
     commands, MCP connectors, managed agents, language packages, scripts…).
  2. Extracts dependency edges between entities by scanning each entity's
     primary file for keyword references (``system.file:``, ``from_plugin:``,
     ``skills.path:``, ``skills:``, ``references:``, ``src:``, ``include:``,
     ``path:``), relative-path tokens (``./x``, ``../y``), and bare filenames
     whose extension is in ``TEXT_SUFFIXES``.
  3. Writes a Markdown file with two Mermaid diagrams (structural graph +
     dependency-edge graph), an entity inventory table, and a per-module
     deep-dive scaffold.

The output is the *first deliverable* of the skill; a human should refine
the auto-detected edges by reading the most important manifests.

Usage
-----
    python scripts/gen_topology.py <repo-root> \
        [--out docs/guides/topology.md] \
        [--project-name "MyProject"] \
        [--max-edges 200]

A relative ``--out`` is resolved against <repo-root>; the default is
``<repo-root>/docs/guides/topology.md``.

Exit codes
----------
    0  success
    1  repo root missing or unreadable, or an invalid --max-edges
    2  cannot create or write the output file
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", "target", ".idea", ".vscode", ".mypy_cache",
    ".pytest_cache", "site-packages", ".github",
}

TEXT_SUFFIXES = {
    ".md", ".markdown", ".txt", ".py", ".pyi", ".js", ".jsx", ".ts",
    ".tsx", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".sh",
    ".bash", ".rs", ".go", ".java", ".rb", ".lua", ".cpp", ".c", ".h",
}

# Keywords whose presence marks a "source -> copy" (single-source-of-truth)
# relationship rather than an ordinary "uses" relationship.
COPY_KEYWORDS = ("system.file", "from_plugin", "skills.path", "skills:", "copied", "synced")

MAX_FILE_READ = 200_000  # bytes


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class Entity:
    name: str
    kind: str
    rel_path: str          # repo-relative path of the primary file/dir
    module: str            # top-level module (first path segment)
    size: int = 0
    extra: dict[str, object] = field(default_factory=dict)
    id: str = ""           # unique Mermaid node id (filled by _assign_ids)


@dataclass
class Edge:
    src: str               # entity id
    dst: str               # entity id
    kind: str              # "source->copy" | "uses"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def sanitize_id(text: str) -> str:
    """Make a Mermaid-safe node id (letter-first, no spaces / punctuation)."""
    s = re.sub(r"[^0-9A-Za-z_]+", "_", text).strip("_") or "node"
    return s if s[0].isalpha() else f"n_{s}"


def _label(text: str) -> str:
    """Escape a string for use inside a Mermaid node label."""
    return text.replace('"', "&quot;")


def _is_ignored(parts: tuple[str, ...]) -> bool:
    """True when any path segment is a build/vendor dir (or a *.egg-info dir)."""
    return any(part in IGNORE_DIRS or part.endswith(".egg-info") for part in parts)


def _module_of(rel: Path) -> str:
    """Top-level module a repo-relative path belongs to ("(root)" for root files)."""
    return rel.parts[0] if len(rel.parts) > 1 else "(root)"


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def safe_read(path: Path,
                skip_log: list[tuple[str, str]] | None = None) -> str:
    """Read up to MAX_FILE_READ bytes as UTF-8 text, swallowing errors.

    On failure (and when ``skip_log`` is provided), append ``(path, reason)``
    so the caller can report what was dropped. ``reason`` is one of:
    ``"permission-denied"``, ``"not-a-file"``, ``"read-error"``.
    """
    if not path.is_file():
        if skip_log is not None:
            skip_log.append((str(path), "not-a-file"))
        return ""
    try:
        with path.open("rb") as fh:
            data = fh.read(MAX_FILE_READ)
    except PermissionError:
        if skip_log is not None:
            skip_log.append((str(path), "permission-denied"))
        return ""
    except OSError:
        if skip_log is not None:
            skip_log.append((str(path), "read-error"))
        return ""
    except Exception:
        if skip_log is not None:
            skip_log.append((str(path), "read-error"))
        return ""
    return data.decode("utf-8", errors="ignore")


def _assign_ids(entities: list[Entity]) -> None:
    """Give every entity a stable, unique Mermaid node id."""
    used: set[str] = set()
    for e in sorted(entities, key=lambda entity: entity.rel_path):
        base = sanitize_id(e.rel_path)
        nid, n = base, 2
        while nid in used:
            nid = f"{base}_{n}"
            n += 1
        used.add(nid)
        e.id = nid


# --------------------------------------------------------------------------
# Entity detection
# --------------------------------------------------------------------------

def detect_entities(root: Path, *, max_entities: int = 0,
                         verbose: bool = False,
                         skip_log: list[tuple[str, str]] | None = None) -> list[Entity]:
    entities: list[Entity] = []
    seen: set[tuple[str, str]] = set()
    top_modules = sorted(
        (p for p in root.iterdir() if p.is_dir() and not _is_ignored((p.name,))),
        key=lambda p: p.name,
    )

    # 1) Top-level directories are modules.
    for mod in top_modules:
        entities.append(Entity(mod.name, "module", mod.name, mod.name))

    # 2) Walk for typed entities (sorted: the output order must be stable).
    for p in sorted(root.rglob("*"), key=lambda q: q.relative_to(root).as_posix()):
        rel = p.relative_to(root)
        if _is_ignored(rel.parts):
            continue
        name = p.name

        if name == "SKILL.md":
            is_root = len(rel.parts) == 1
            kind, ent = "skill", root.name if is_root else p.parent.name
            _add(entities, seen, Entity(ent, kind, str(rel), _module_of(rel),
                                        size=_file_size(p)))
        elif name == "agent.yaml" or name == "agent.yml":
            kind, ent = "managed-agent", p.parent.name
            _add(entities, seen, Entity(ent, kind, str(rel), _module_of(rel)))
        elif name == ".mcp.json":
            servers = _count_mcp_servers(p, skip_log)
            ent = root.name if p.parent == root else p.parent.name
            _add(entities, seen, Entity(f"{ent} (mcp)", "connectors", str(rel),
                                        _module_of(rel), extra={"servers": servers}))
        elif name == "pyproject.toml" or name == "setup.py" or name == "setup.cfg":
            if p.parent != root:  # package, not repo root metadata
                ent = p.parent.name
                _add(entities, seen, Entity(ent, "py-package", str(rel), _module_of(rel)))
        elif name == "package.json":
            if p.parent != root:
                ent = p.parent.name
                _add(entities, seen, Entity(ent, "node-package", str(rel), _module_of(rel)))
        elif name == "Cargo.toml" and p.parent != root:
            ent = p.parent.name
            _add(entities, seen, Entity(ent, "rust-crate", str(rel), _module_of(rel)))
        elif name == "go.mod" and p.parent != root:
            ent = p.parent.name
            _add(entities, seen, Entity(ent, "go-module", str(rel), _module_of(rel)))

    # 3) agents/*.md and commands/*.md (CodeBuddy/Claude plugin convention).
    for pattern, kind in (("agents/*.md", "agent"), ("commands/*.md", "command")):
        for p in sorted(root.glob(pattern), key=lambda q: q.as_posix()):
            rel = p.relative_to(root)
            if _is_ignored(rel.parts):
                continue
            ent = p.stem
            _add(entities, seen, Entity(ent, kind, str(rel), _module_of(rel),
                                        size=_file_size(p)))

    # 4) Standalone scripts at repo root or under scripts/.
    script_hits = (list(root.glob("*.py")) + list(root.glob("*.sh")) +
                   list(root.glob("scripts/*.py")) + list(root.glob("scripts/*.sh")))
    for p in sorted(script_hits, key=lambda q: q.as_posix()):
        rel = p.relative_to(root)
        if _is_ignored(rel.parts):
            continue
        ent = p.stem
        _add(entities, seen, Entity(ent, "script", str(rel), _module_of(rel),
                                    size=_file_size(p)))

    _assign_ids(entities)
    entities.sort(key=lambda e: (e.module, e.rel_path))
    if max_entities > 0 and len(entities) > max_entities:
        hidden = len(entities) - max_entities
        if verbose:
            print(f"  cap: hiding {hidden} entities (max={max_entities})", file=sys.stderr)
        return entities[:max_entities]
    return entities


def _add(entities: list[Entity], seen: set[tuple[str, str]], e: Entity) -> None:
    key = (e.kind, e.rel_path)
    if key in seen:
        return
    seen.add(key)
    entities.append(e)


def _count_mcp_servers(path: Path,
                         skip_log: list[tuple[str, str]] | None = None) -> int | None:
    """Number of declared MCP servers, or None when the file cannot be parsed."""
    try:
        data = json.loads(safe_read(path, skip_log))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    # Accept both {"mcpServers": {...}} and {"servers": {...}}.
    servers = data.get("mcpServers") or data.get("servers") or {}
    return len(servers) if isinstance(servers, dict) else None


# --------------------------------------------------------------------------
# Edge detection
# --------------------------------------------------------------------------

# Extension alternation derived from TEXT_SUFFIXES; longest first so that
# ".markdown" wins over ".md".
_SUFFIX_ALT = "|".join(sorted((s.lstrip(".") for s in TEXT_SUFFIXES),
                              key=len, reverse=True))

# Whitelisted verbs that introduce a file reference. Bare file tokens NOT
# preceded by one of these (or by a markdown list-item marker) are ignored
# — otherwise the heuristic grabs every random "see x.md" in changelogs.
_IMPORT_VERB = (
    r"(?:see|see\s+also|load|loads|loaded|include|includes|included|"
    r"import|imports|from|via|use|uses|reference|references|referenced|"
    r"copied|synced|mirror|mirrors|read|reads|require|requires)"
)

# Capture a path-like token after a keyword, as a relative path, as a
# verb-led bare file reference, or as a markdown list-item bare file
# reference. Three capture groups (in order): keyword-value, relative
# path, file reference. Bare filename matching is intentionally narrow.
_REF_PATTERN = re.compile(
    r"\b(?:system\.file|from_plugin|skills\.path|skills|references|src|include|path)\b"
    r"\s*[:=]\s*['\"]?([^'\"\n\s,;)\]]+)['\"]?"
    r"|(\.{1,2}/[\w./\-]+)"                          # relative path token
    rf"|(?:(?:{_IMPORT_VERB})\s+|(?:^|\n)\s*(?:[\*\-]\s+|\d+\.\s+))"  # verb or list
    r"([\w./\-]+\.(?:" + _SUFFIX_ALT + r"))"          # file reference token
)


def detect_edges(root: Path, entities: list[Entity], *,
                    verbose: bool = False,
                    skip_log: list[tuple[str, str]] | None = None) -> list[Edge]:
    # Map: normalized repo-relative path / lowercased name -> entity id.
    by_path: dict[str, str] = {}
    by_name: dict[str, str] = {}
    for e in entities:
        by_path[e.rel_path.replace("\\", "/")] = e.id
        by_name.setdefault(e.name.lower(), e.id)

    edges: list[Edge] = []
    seen_pairs: set[tuple[str, str]] = set()

    # Build a quick resolver: given a referenced raw path + the file it came
    # from, resolve to a repo-relative path and match an entity.
    def resolve(raw: str, base_file: Path) -> str | None:
        raw = raw.strip().strip("'\"`").strip()
        if not raw:
            return None
        candidate = (base_file.parent / raw).resolve()
        try:
            rel = candidate.relative_to(root.resolve())
            return rel.as_posix()
        except Exception:
            return None

    total = len(entities)
    for idx, e in enumerate(entities, 1):
        fpath = root / e.rel_path
        if not fpath.is_file():           # directory entities (modules) have no content
            continue
        content = safe_read(fpath, skip_log)
        if not content:
            continue
        lines = content.splitlines()
        if verbose and (idx % 50 == 0 or idx == total):
            print(f"  edge scan {idx}/{total} ({e.rel_path})", file=sys.stderr)

        for m in _REF_PATTERN.finditer(content):
            token = m.group(1) or m.group(2) or m.group(3)
            if not token:
                continue
            # Copy detection reads the whole enclosing line, so "# copied
            # from X" / "synced from Y" classify as source->copy even when
            # the match was anchored on a bare filename.
            line_no = content.count("\n", 0, m.start())
            line = lines[line_no] if line_no < len(lines) else ""
            is_copy = any(kw in line for kw in COPY_KEYWORDS)

            resolved = resolve(token, fpath)
            target_id = None
            if resolved and resolved in by_path:
                target_id = by_path[resolved]
            else:
                # fallback: exact name match, or a path-like token whose text
                # contains a known entity name (sorted, so the first match
                # never depends on dict insertion order).
                low = token.lower()
                for nm, eid in sorted(by_name.items()):
                    if low == nm or (("/" in low or "." in low) and nm in low):
                        target_id = eid
                        break

            if not target_id or target_id == e.id:
                continue
            pair = (e.id, target_id)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            kind = "source->copy" if is_copy else "uses"
            edges.append(Edge(e.id, target_id, kind))

    edges.sort(key=lambda ed: (ed.src, ed.dst, ed.kind))
    return edges


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

KIND_COLOR = {
    "module": "fill:#e1f0ff,stroke:#3b82f6",
    "skill": "fill:#e8f5e9,stroke:#2e7d32",
    "agent": "fill:#fff3e0,stroke:#ef6c00",
    "command": "fill:#f3e5f5,stroke:#8e24aa",
    "managed-agent": "fill:#ffebee,stroke:#c62828",
    "connectors": "fill:#e0f7fa,stroke:#00838f",
    "py-package": "fill:#ede7f6,stroke:#5e35b1",
    "node-package": "fill:#fce4ec,stroke:#d81b60",
    "rust-crate": "fill:#fff8e1,stroke:#ff8f00",
    "go-module": "fill:#e8eaf6,stroke:#3949ab",
    "script": "fill:#f1f8e9,stroke:#7cb342",
}


def build_structural_graph(entities: list[Entity]) -> str:
    lines = ["graph TD"]
    modules: dict[str, list[Entity]] = {}
    for e in entities:
        modules.setdefault(e.module, []).append(e)

    taken = {e.id for e in entities}
    for mod, ents in modules.items():
        base = sanitize_id(f"sg_{mod}")
        sg_id, n = base, 2
        while sg_id in taken:
            sg_id = f"{base}_{n}"
            n += 1
        taken.add(sg_id)
        lines.append(f"    subgraph {sg_id}[\"{_label(mod)}\"]")
        for e in ents:
            nid = e.id
            style = KIND_COLOR.get(e.kind, "")
            extra = ""
            if e.kind == "connectors":
                servers = e.extra.get("servers")
                extra = f" ({servers if servers is not None else '?'} servers)"
            lines.append(f"        {nid}[\"{_label(e.name)}{extra}<br/>{e.kind}\"]")
            if style:
                lines.append(f"        style {nid} {style}")
        lines.append("    end")
    return "\n".join(lines)


def build_edge_graph(entities: list[Entity], edges: list[Edge], max_edges: int) -> str:
    """Render the dependency-edge subgraph. ``max_edges == 0`` means unlimited."""
    lines = ["graph LR"]
    name_of = {e.id: e.name for e in entities}
    shown: set[str] = set()
    capped = edges if max_edges <= 0 else edges[:max_edges]
    if max_edges > 0 and len(edges) > max_edges:
        print(f"  warning: rendering {max_edges} of {len(edges)} edges "
              f"(use --max-edges=0 for unlimited)", file=sys.stderr)
    for ed in capped:
        s, d = ed.src, ed.dst
        shown.add(s)
        shown.add(d)
        arrow = "-.->" if ed.kind == "source->copy" else "-->"
        label = " synced" if ed.kind == "source->copy" else ""
        lines.append(f"    {s} {arrow} {d}[\"{_label(name_of.get(d, d))}\"]{label}")
    if not shown:
        lines.append("    %% no dependency edges detected")
    return "\n".join(lines)


def render_markdown(entities: list[Entity], edges: list[Edge],
                    project_name: str, max_edges: int) -> str:
    modules: dict[str, list[Entity]] = {}
    for e in entities:
        modules.setdefault(e.module, []).append(e)

    inv = []
    inv.append(f"# {project_name} — Repository Topology Map")
    inv.append("")
    inv.append("> Auto-generated by `repo-doc-miner/scripts/gen_topology.py` (v2, "
               "topology-first). This is the **first deliverable** of the mining "
               "process: a structural map of the repository. Refine the detected "
               "edges by reading the most important manifests, then deep-dive each "
               "module along these edges.")
    inv.append("")
    inv.append("---")
    inv.append("")
    inv.append("## 1. Structural Topology")
    inv.append("")
    inv.append("```mermaid")
    inv.append(build_structural_graph(entities))
    inv.append("```")
    inv.append("")
    inv.append("## 2. Dependency Edges")
    inv.append("")
    inv.append("Solid arrows = `uses`; dotted arrows = `source → copy` "
               "(single source of truth synced into copies).")
    inv.append("")
    inv.append("```mermaid")
    inv.append(build_edge_graph(entities, edges, max_edges))
    inv.append("```")
    inv.append("")
    inv.append("## 3. Entity Inventory")
    inv.append("")
    inv.append("| Kind | Count | Example locations |")
    inv.append("| --- | --- | --- |")
    by_kind: dict[str, list[Entity]] = {}
    for e in entities:
        by_kind.setdefault(e.kind, []).append(e)
    for kind, ents in sorted(by_kind.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        locs = ", ".join(sorted({e.rel_path for e in ents})[:3])
        inv.append(f"| {kind} | {len(ents)} | `{locs}` |")
    inv.append("")
    inv.append("## 4. Module Deep-Dive Scaffold")
    inv.append("")
    inv.append("> Walk these modules **along the dependency edges above**, highest "
               "complexity first. Replace each `> TODO(doc-miner)` with findings.")
    inv.append("")
    for mod, ents in modules.items():
        inv.append(f"### {mod}")
        inv.append("")
        for e in ents:
            size = f" (~{e.size // 1024} KB)" if e.size and e.kind in ("skill", "script") else ""
            inv.append(f"- **{e.name}** ({e.kind}) — `{e.rel_path}`{size}")
            inv.append(f"  - > TODO(doc-miner): what does {e.name} do and which entities does it reference?")
        inv.append("")
    inv.append("---")
    inv.append("")
    inv.append("> Refine this map, then use it as the backbone for "
               "`developer_guide.md`, `user_guide.md`, and `tutorial.md`.")
    return "\n".join(inv)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def _parse_inventory(md_text: str) -> dict[str, dict]:
    """Parse the entity-inventory table (section ``## 3.``) out of a topology.md.

    Returns ``{kind: {"count": int, "locations": set[str]}} ``. Returns an empty
    dict when the section or table is absent.
    """
    out: dict[str, dict] = {}
    in_section = False
    for line in md_text.splitlines():
        if line.startswith("## 3."):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("|"):
            continue
        if "---" in line or "Kind" in line:
            continue
        parts = [c.strip() for c in line.split("|")[1:-1]]
        if len(parts) < 3:
            continue
        try:
            count = int(parts[1])
        except ValueError:
            continue
        locs = {tok.strip().strip("`") for tok in parts[2].split(",") if tok.strip()}
        out[parts[0]] = {"count": count, "locations": locs}
    return out


def _emit_diff(out_path: Path, entities: list[Entity], project_name: str) -> int:
    """Diff mode: compare the new entity set against an existing topology.md
    at ``out_path`` (if present) and print a Markdown diff section to stdout.
    Does NOT overwrite ``out_path``."""
    if not out_path.exists():
        print(f"warning: --diff: no previous topology.md at {out_path}",
              file=sys.stderr)
        return 0
    prev = _parse_inventory(out_path.read_text(encoding="utf-8"))
    by_loc: dict[str, str] = {e.rel_path: e.kind for e in entities}
    curr_locs: dict[str, set[str]] = {}
    for e in entities:
        curr_locs.setdefault(e.kind, set()).add(e.rel_path)
    curr_counts: dict[str, int] = {k: len(v) for k, v in curr_locs.items()}

    prev_kinds = set(prev)
    curr_kinds = set(curr_counts)
    added_kinds = sorted(curr_kinds - prev_kinds)
    removed_kinds = sorted(prev_kinds - curr_kinds)
    common = sorted(curr_kinds & prev_kinds)

    added_locs = sorted({(l, k) for k in curr_kinds
                          for l in curr_locs[k] - prev.get(k, {}).get("locations", set())})
    removed_locs = sorted({(l, k) for k in prev_kinds
                           for l in prev.get(k, {}).get("locations", set()) - curr_locs.get(k, set())})

    out = [f"# {project_name} — Topology Diff"]
    out.append("")
    out.append(f"> Generated by `gen_topology.py --diff` against `{out_path}`.")
    out.append("")
    if not added_kinds and not removed_kinds and not any(
        curr_counts.get(k, 0) != prev[k]["count"] for k in common):
        out.append("No changes detected since the previous topology.md.")
        out.append("")
        print("\n".join(out))
        return 0

    out.append("## Kinds")
    out.append("")
    out.append("| Kind | Previous | Current | Δ |")
    out.append("| --- | --- | --- | --- |")
    for k in sorted(set(prev_kinds) | curr_kinds):
        p = prev.get(k, {}).get("count", 0)
        c = curr_counts.get(k, 0)
        out.append(f"| {k} | {p} | {c} | {c - p:+d} |")
    out.append("")
    if added_locs:
        out.append("## Locations added")
        out.append("")
        for loc, k in added_locs:
            out.append(f"- `{loc}` ({k})")
        out.append("")
    if removed_locs:
        out.append("## Locations removed")
        out.append("")
        for loc, k in removed_locs:
            out.append(f"- `{loc}` ({k})")
        out.append("")
    if not added_locs and not removed_locs:
        out.append("No location-level changes.")
        out.append("")
    print("\n".join(out))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a repo topology map (Mermaid) + entity inventory."
    )
    parser.add_argument("repo_root", type=Path, help="Path to the target repository root.")
    parser.add_argument("--out", default=None, help="Output Markdown path (default: <repo_root>/docs/guides/topology.md).")
    parser.add_argument("--project-name", default=None, help="Display name (default: repo folder name).")
    parser.add_argument("--max-edges", type=int, default=200,
                        help="Cap on rendered dependency edges (default 200). 0 = unlimited.")
    parser.add_argument("--max-entities", type=int, default=500,
                        help="Cap on detected entities (default 500). 0 = unlimited.")
    parser.add_argument("--verbose", action="store_true",
                        help="Print progress to stderr while scanning.")
    parser.add_argument("--diff", action="store_true",
                        help="Diff mode: compare with existing --out (if any) and print a Markdown diff section to stdout; do not overwrite --out.")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    if not repo_root.is_dir():
        print(f"error: repo root does not exist: {repo_root}", file=sys.stderr)
        return 1
    if args.max_edges < 0:
        print("error: --max-edges must be >= 0 (0 = unlimited)", file=sys.stderr)
        return 1
    if args.max_entities < 0:
        print("error: --max-entities must be >= 0 (0 = unlimited)", file=sys.stderr)
        return 1

    project_name = args.project_name or repo_root.name
    out_path = Path(args.out) if args.out else (repo_root / "docs" / "guides" / "topology.md")
    if not out_path.is_absolute():
        out_path = repo_root / out_path

    print(f"Mining topology for: {repo_root}")
    skip_log: list[tuple[str, str]] = []
    try:
        entities = detect_entities(repo_root,
                                    max_entities=args.max_entities,
                                    verbose=args.verbose,
                                    skip_log=skip_log)
        print(f"  detected {len(entities)} entities")
    except OSError as exc:
        print(f"error: cannot read {repo_root}: {exc}", file=sys.stderr)
        return 1
    try:
        edges = detect_edges(repo_root, entities,
                            verbose=args.verbose, skip_log=skip_log)
        print(f"  detected {len(edges)} dependency edges")
    except OSError as exc:
        print(f"error: cannot read {repo_root}: {exc}", file=sys.stderr)
        return 1

    if skip_log:
        counts: dict[str, int] = {}
        for _path, reason in skip_log:
            counts[reason] = counts.get(reason, 0) + 1
        parts = ", ".join(f"{c} {r}" for r, c in
                          sorted(counts.items(), key=lambda kv: -kv[1]))
        print(f"  skipped {len(skip_log)} file(s) during edge detection: {parts}",
              file=sys.stderr)

    if args.diff:
        return _emit_diff(out_path, entities, project_name)

    md = render_markdown(entities, edges, project_name, args.max_edges)
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
    except Exception as exc:
        print(f"error: cannot write {out_path}: {exc}", file=sys.stderr)
        return 2

    print(f"  wrote {out_path}")
    print("Done. Next: refine the edges, then run Phase 2 (module deep-dive).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
