# Two-Stage Topology-First Method (repo-doc-miner v2)

This reference explains *why* and *how* the skill mines a repository in two
stages — **topology generation first, module deep-dive second** — and how to
apply it to any repository, including very large ones.

## Why topology-first scales

Flat file scanning (the v1 approach) reads files one by one until the agent
"has a feel" for the repo. That breaks down on large repos:

- **O(N) file explosion.** A repo with 400 files yields 400 things to read.
  The agent drowns in detail before seeing the shape.
- **Misread duplication.** Many repos sync a single source of truth into
  multiple copies (e.g. a skill defined once, then copied into 10 agent
  bundles). Read a copy first and you mistake it for an independent
  implementation.
- **No reading order.** Without knowing dependencies, the agent reads a
  leaf before its root and keeps backtracking.

Topology-first fixes all three:

1. **Collapse O(N) files into O(entity-type) structure.** Enumerate the
   *kinds* of things in the repo (modules, skills, agents, connectors,
   packages, scripts…) and draw them as nodes. You now have a 1-screen map.
2. **Extract dependency edges**, especially `source → copy` edges. The edges
   *tell you the reading order*: understand the source before its copies.
3. **The topology is itself a deliverable** — the repo doc miner's primary
   artifact — and it is *incrementally updatable*: re-running the generator
   later diffs structural change as the repo evolves.

## Stage 1 — Topology generation (Phase 1)

**Goal:** answer *"what is in this repo and how is it wired?"* before any prose.

1. **Enumerate entity types.** Run `scripts/gen_topology.py`. It detects,
   generically across repo flavors:
   - top-level directories → **modules** (root-level files land in a `(root)` module);
   - `SKILL.md` → **skill**; `agents/*.md` → **agent**; `commands/*.md` →
     **command**; `.mcp.json` → **connectors**; `agent.yaml` → **managed-agent**;
   - `pyproject.toml` / `setup.py` / `setup.cfg` / `package.json` /
     `Cargo.toml` / `go.mod` → **language package**;
   - `*.py` / `*.sh` scripts at the repo root and under `scripts/` → **script**.
2. **Extract dependency edges.** The script scans each entity's primary file
   for references: the keywords `system.file:`, `from_plugin:`, `skills.path:`,
   `skills:`, `references:`, `src:`, `include:`, `path:`; relative-path tokens
   (`./x`, `../y`); and bare filenames whose extension is in `TEXT_SUFFIXES`.
   It classifies each edge as `source → copy` (synced truth) or `uses` —
   a reference counts as `source → copy` when its own line contains one of
   `COPY_KEYWORDS` (`system.file`, `from_plugin`, `skills.path`, `skills:`,
   `copied`, `synced`).
3. **Human-refine.** Open the generated `topology.md`. Confirm the 2–3 most
   structurally important edges by reading the actual manifests. Fix labels
   so the diagrams tell the *true* story. This refined file is deliverable #1.
4. **Produce an entity inventory** (count + location per kind) — the map you
   keep open during Stage 2.

## Stage 2 — Module deep-dive (Phase 2, edge-ordered)

**Goal:** gather grounded evidence, reading *along the edges*, not at random.

1. **Order by priority.** Sort modules by complexity/value (largest/most
   central entity first; the single source of truth before its copies).
2. **Follow edges.** Read a module's files, then follow its outbound edges to
   the next module. This guarantees you meet a capability at its source
   before its copies/deployments.
3. **Gather the evidence checklist** (`references/evidence_checklist.md`),
   selecting rows by repo flavor and ordering them by the topology. Keep a
   scratch note (not a deliverable) with metadata, exported symbols, main
   signatures, chosen examples, and confirmed edges.
4. **Mark gaps** with `> TODO(doc-miner): ...`; never fabricate.

## Reusable process (copy for any repo)

```
Phase 0  scope & output location (default docs/guides/, five target files)
Phase 1  gen_topology.py <repo> --out docs/guides/topology.md
         → refine edges by reading key manifests
Phase 2  for node in topo.nodes (sorted by complexity):
             read node.files
             follow node.outbound_edges → next node
         → evidence scratch note
Phase 3  draft outlines (references/doc_outlines.md)
Phase 4  scaffold_docs.py + fill templates + topology.md
Phase 5  validate snippets, edges, links
Phase 6  handover (5 files, line counts, coverage, TODOs)
```

## Edge-detection heuristics (so you can extend the script)

The bundled `gen_topology.py` is heuristic. To improve it for a repo family:

- **New entity kind:** add a branch in `detect_entities` keyed on a filename
  or manifest (e.g. `Dockerfile`, `Chart.yaml`, `pom.xml`).
- **New edge syntax:** extend `_REF_PATTERN` with the keyword/pattern your
  repo uses to point at other files.
- **New "copy" marker:** add the keyword to `COPY_KEYWORDS` so the edge is
  drawn as `source → copy` (dotted) rather than `uses` (solid).

Keep the script safe on arbitrary repos: skip binaries, cap file reads
(`MAX_FILE_READ`), and never assume a reference resolves.
