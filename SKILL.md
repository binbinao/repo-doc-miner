---
name: repo-doc-miner
description: Mine an existing Git repository using a two-stage "topology-first → module-deep-dive" method and generate a coordinated **five-file** Markdown doc set — a repo topology map (Mermaid), developer guide, user guide, from-beginner-to-expert tutorial, and a navigation `README.md` — saved into the repository's `docs/guides/` folder. Use this skill when the user asks to "dig into / mine / analyze this project and produce documentation", "generate a repo topology / architecture map and docs", "write onboarding docs from the codebase", or any similar request where the deliverable is a coordinated doc set derived from reading the current repository.
version: 2.0.0
---

# Repo Doc Miner (v2 — Topology-First)

## Overview

Mine a Git repository and produce a coordinated set of Markdown documents grounded in the actual code, configuration, and examples of the target repo. **v2 restructures the process around a two-stage method:**

1. **Topology generation (Phase 1)** — first build a *structural map* of the repository: enumerate its **entity types** (packages, modules, agents, skills, commands, connectors, configs, scripts…) and extract the **dependency edges** between them (who references whom, what is a single source of truth vs. a synced copy). The topology map (Mermaid diagrams + an entity inventory table) is the **primary deliverable** and the backbone for everything else.
2. **Module deep-dive (Phase 2)** — then read code *along the edges of the topology* rather than flat-file scanning. Modules are visited in priority order (highest complexity / highest value first), so the agent builds a correct mental model before descending into details.

This ordering is what lets the skill scale to very large repositories: a topology collapses O(N) files into an O(entity-type) structural view, and the dependency edges tell you *which* files to read and *in what order* — e.g. you must understand the single source of truth before reading its synced copies, otherwise you mistake a copy for an independent implementation.

The final deliverables are: `topology.md` (the map), `developer_guide.md`, `user_guide.md`, `tutorial.md`, and a `README.md` navigation hub.

## When to Use

Trigger this skill when the user's request matches any of these patterns:

- "挖掘当前项目/仓库，生成拓扑图 + 开发文档、用户文档和教程"
- "Mine this repo, draw an architecture / dependency topology, and produce docs"
- "为这个项目写一套完整的文档（开发者 + 用户 + 入门到精通），先给我结构图"
- "Generate onboarding documentation for this codebase, save into docs/"
- Any request where (a) the primary input is the current repository, and (b) the required output is a multi-audience doc set (with or without an architecture map) written in Markdown.

Do NOT trigger for: single-file API docs, README refresh only, translation tasks, or when the user already has a target doc framework (Sphinx/MkDocs site generation).

## Workflow

Follow these seven phases in order (Phase 0–6). Phases 1–2 are the new topology-first core; Phases 3–6 reuse the grounded-writing machinery from v1.

### Phase 0 · Scope & Output Location

1. Determine the repository root (usually the workspace root).
2. Choose the output directory. Default: `docs/guides/` under the repo root. If `docs/` does not exist, create `docs/guides/` anyway (it is a self-contained sub-folder and will not clash with Sphinx/MkDocs). Prefer an existing docs directory if it is clearly the convention of the repo.
3. Confirm the five target files: `topology.md` (map), `developer_guide.md`, `user_guide.md`, `tutorial.md`, and a `README.md` navigation hub.

### Phase 1 · Topology Generation (core deliverable)

This phase answers *"what is in this repo and how is it wired?"* before any prose is written.

1. **Enumerate entity types.** Detect the repo flavor and list the entities it actually contains. Use `scripts/gen_topology.py` to produce a first draft automatically:

   ```bash
   python scripts/gen_topology.py <repo-root> \
       --out <repo-root>/docs/guides/topology.md \
       [--project-name "<DisplayName>"] \
       [--max-edges 200] [--max-entities 500] [--verbose] [--diff]
   ```

   A relative `--out` is resolved against `<repo-root>`.

   Flags:
   - `--max-edges N` — cap rendered dependency edges; `0` means unlimited (default `200`).
   - `--max-entities N` — cap detected entities; `0` means unlimited (default `500`).
   - `--verbose` — print progress to stderr while scanning.
   - `--diff` — diff the new entity set against an existing `--out` (if any) and emit it to **stdout** without overwriting `--out`. Use this for incremental topology updates.

   The script detects, generically:
   - Top-level directories as **modules** (build/vendor dirs such as `.git`, `node_modules`, `dist`, `.github`, and `*.egg-info` are skipped). Files directly at the repo root are grouped into a `(root)` module.
   - Plugin-style entities: `SKILL.md` (skill), `agents/*.md` (agent), `commands/*.md` (command), `.mcp.json` (MCP connector), `agent.yaml` (managed agent).
   - Language packages: `pyproject.toml` / `setup.py` / `setup.cfg` / `package.json` / `Cargo.toml` / `go.mod`.
   - Tooling: `*.py` / `*.sh` scripts at the repo root and under `scripts/`.

   Mermaid node ids are derived from repo-relative paths, so duplicate basenames in different directories stay distinct, and emission order is sorted — re-running the script produces byte-identical output.

2. **Extract dependency edges.** For each pair of entities, determine whether one references the other. The script captures common edge kinds:
   - Keyword references: `system.file:`, `from_plugin:`, `skills.path:`, `skills:`, `references:`, `src:`, `include:`, `path:` (matched at word boundaries).
   - Path tokens: relative-path includes (`./x`, `../y`) and bare filenames whose extension is in the script's `TEXT_SUFFIXES` set.
   Classify each edge as **source → copy** (a single source of truth synced into copies) or **use/depend** (one entity consumes another). The "source → copy" edges are the most important — they reveal duplication that flat scanning would misinterpret. A reference is classified as source → copy when its own line carries one of the copy keywords (`system.file`, `from_plugin`, `skills.path`, `skills:`, `copied`, `synced`).

3. **Human-refine the draft.** Open the generated `topology.md` and verify the auto-detected edges against the real files (the script is heuristic; confirm the 2–3 most structurally important edges by reading the actual manifests). Edit the Mermaid graphs so they tell the true story of the repo. The refined `topology.md` is the **first deliverable** and the structural backbone for Phase 2.

4. **Produce an entity inventory table** (count + location per entity type). This is the "map" the agent keeps open while deep-diving.

### Phase 2 · Module Deep-Dive (evidence gathering, edge-ordered)

Now read code *along the topology edges*, not at random.

1. **Order by priority.** Sort modules by complexity/value (e.g. largest/most-central skill first; the single source of truth before its copies). Use the inventory table to pick a reading order.
2. **Follow edges.** For each module, read the files the topology points to, then follow outbound edges to the next module. This guarantees the agent understands a capability at its source before meeting its copies/deployments.
3. **Gather the evidence checklist.** Reuse `references/evidence_checklist.md`, but select rows by repo flavor and order them by the topology. Keep a scratch note (internal, not a deliverable) with: project metadata, exported symbols per module, main class signatures, chosen example files, and the confirmed dependency edges.
4. **Mark gaps** with `> TODO(doc-miner): ...` when evidence is missing; never fabricate.

For the concrete per-flavor "what to read" guidance, see `references/evidence_checklist.md` and the two-stage rationale in `references/topology_method.md`.

### Phase 3 · Content Plan (one-screen outline per document)

Before writing prose, draft a one-screen outline for each of the four documents (the fifth file, `README.md`, is the hub that links them). Reuse the canonical outlines in `references/doc_outlines.md` and specialize their section titles with concrete names harvested in Phase 2 (package names, class names, config flags, and — new in v2 — the topology node/edge names). Verify that:

- The **topology** clearly shows the top-level structure, the key dependency edges, and the entity inventory.
- The **developer guide** covers architecture, every top-level module, runtime config, extension/contribution SOPs, and debugging tips.
- The **user guide** walks from installation to the most advanced user-facing feature, using API names that actually exist in the repo.
- The **tutorial** has 8–12 progressive chapters, each anchored in at least one real file from the repo.

### Phase 4 · Writing

Use the templates under `assets/templates/` as the structural scaffold, then fill them with repo-specific content. Run the scaffolder first to lay down skeletons:

```bash
python scripts/scaffold_docs.py <repo-root> --project-name "<DisplayName>" [--out docs/guides] [--force]
```

The scaffolder leaves any template file that already exists in the output directory untouched (it prints `skipped (exists)`) and writes only the missing ones, so the Phase-1 `topology.md` survives. Pass `--force` to overwrite all five files.

Then edit each file in place. Follow these rules:

- **Ground every claim in code**: when mentioning a function, class, or behavior, include the file path (relative to repo root) the first time it is introduced (e.g. `deepxde/model.py::Model.compile`).
- **Prefer real code snippets** taken from `examples/` or tests; condense to ≤ ~30 lines. Preserve the original import style and function signatures; do not invent APIs.
- **Lead with the topology**: `topology.md` is written first and referenced by the other four files; the developer guide can embed or link the Mermaid diagrams rather than re-drawing them.
- **Cross-link all five files**: the tutorial references sections in the user guide; the developer guide references the user guide for API usage; `README.md` links the other four files.
- **Match the repo's host language**: if the existing `docs/` content is primarily Chinese, write in Chinese; primarily English, write in English; bilingual repositories default to the language of the user's current query.
- **Keep each file self-contained**: duplicate a minimum amount of glossary/context so any one file can be opened first.
- **Mark unresolved gaps explicitly** with `> TODO(doc-miner): ...` lines when evidence is insufficient; never fabricate behavior.

### Phase 5 · Validation

Before reporting completion:

1. Spot-check 5 random code snippets against their source files (open the referenced path, compare signatures).
2. Run `rg "TODO\(doc-miner\)"` (requires ripgrep on the PATH) to surface unresolved gaps; either resolve them or list them in the final summary.
3. Ensure every module mentioned in the developer guide actually exists (verify with whatever file-listing tool the agent has available, e.g. `search_file` if the host agent provides one).
4. Confirm the topology's dependency edges are real by opening at least the 2–3 most important manifests.
5. Confirm the five files render correctly as Markdown (headings monotonic, code fences closed, relative links valid, Mermaid blocks well-formed).

### Phase 6 · Handover

Produce a short final summary containing:

- Absolute paths of the five generated files (incl. `topology.md`).
- Line-count per file.
- A coverage bullet list (which modules / examples made it in).
- Any `TODO(doc-miner)` items the user still needs to fill.
- Note: `topology.md` is incrementally updatable — re-running `scripts/gen_topology.py` later diffs structural changes as the repo evolves.

## Resources

### scripts/

- `scripts/gen_topology.py` — **new in v2.** Scans a repo, detects entity types and dependency edges, and writes a Mermaid-backed `topology.md` (structural graph + dependency-edge graph + entity inventory + per-module deep-dive scaffold). Heuristic but safe on arbitrary repos. Run it at the start of Phase 1.
- `scripts/scaffold_docs.py` — creates `<repo>/docs/guides/` and materializes the five document templates from `assets/templates/` with their `{{PROJECT_NAME}}` placeholder substituted (existing files are skipped unless `--force` is passed). Run at the start of Phase 4.

### assets/templates/

Markdown skeletons carrying a fixed section schema. Use them as the literal starting point for each file; do **not** rewrite them from scratch. Replace every `{{PLACEHOLDER}}` with repo-specific content harvested in Phase 2.

- `assets/templates/topology.md` — **new in v2.** The architecture-map scaffold (Mermaid blocks + inventory table + per-module sections).
- `assets/templates/developer_guide.md` — 15-section schema (overview → architecture → module tours → extension SOPs → debugging).
- `assets/templates/user_guide.md` — 20-section schema (install → runtime config → core objects → main loop → advanced features → FAQ → minimal runnable examples).
- `assets/templates/tutorial.md` — 10-chapter "from beginner to expert" schema with slots for real example file paths.
- `assets/templates/README.md` — navigation hub that indexes the other four files.

### references/

Loaded into context on demand.

- `references/topology_method.md` — **new in v2.** The two-stage methodology: why topology-first scales to large repos, how to detect entity types and edges, and a reusable process you can apply to any repository.
- `references/doc_outlines.md` — canonical section-by-section outlines, with guidance on what each section must contain and how to source the evidence.
- `references/evidence_checklist.md` — the minimum set of files and symbols to read during Phase 2, grouped by repo flavor (Python ML library, Python CLI, Node web app, Rust crate, Go service). Updated to be edge-ordered.
- `references/writing_style.md` — writing-style conventions (tone, bilingual rules, code-citation format, TODO markers).

## Failure Modes to Avoid

- Writing generic docs that could apply to any library — **always include at least one concrete class name, file path, or example per section**.
- Copying long code blocks verbatim (> 30 lines). Condense and cite the path instead.
- **Skipping Phase 1 and guessing the architecture.** If you cannot draw the topology, you do not understand the repo — stop and read the manifests the script flagged.
- Mistaking a synced copy for an independent implementation because you read it before its source. Always follow `source → copy` edges.
- Clobbering existing `docs/` content. Always write into a dedicated sub-folder (`docs/guides/` by default).
- Forgetting to produce the navigation `README.md`; without it the other four files feel disconnected.
