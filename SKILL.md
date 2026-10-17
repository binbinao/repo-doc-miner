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

## Prerequisites

Tools the skill expects on `PATH` before any of its scripts run:

| Tool | Why | Min version |
|---|---|---|
| `python3` | runs `scripts/gen_topology.py`, `scripts/scaffold_docs.py` | 3.8 (matches the script's `from __future__ import annotations` + PEP-604 typing) |
| `git` | Phase -1 uses `git log -1 --format=%ct` for the vitality signal | any |
| `rg` (ripgrep) | Phase 5 final sweep (`rg "TODO\(doc-miner\)"`) | any |

If `rg` is missing the agent falls back to a host project file-listing tool, but the experience is best with it installed.

## When to Use

Trigger this skill when the user's request matches any of these patterns:

- "挖掘当前项目/仓库，生成拓扑图 + 开发文档、用户文档和教程"
- "Mine this repo, draw an architecture / dependency topology, and produce docs"
- "为这个项目写一套完整的文档（开发者 + 用户 + 入门到精通），先给我结构图"
- "Generate onboarding documentation for this codebase, save into docs/"
- Any request where (a) the primary input is the current repository, and (b) the required output is a multi-audience doc set (with or without an architecture map) written in Markdown.

Do NOT trigger for any of the following:

- Single-file API docs.
- README refresh only.
- Translation tasks.
- The user already has a target doc framework (Sphinx/MkDocs site generation).
- The repo is **archived** or explicitly "no longer maintained" (see `references/suitability_signals.md` hard veto).
- The repo has **no `LICENSE` and no usage hint in its README** (same source).
- The repo is a **vendor fork** with no top-level source directory (only `node_modules/`, `dist/`, etc.).
- The repo has **fewer than 3 readable source files** after build/vendor filtering (same source).

## Workflow Variants

The eight phases (Phase -1, then Phase 0–6) below describe the **Full mode** workflow. Phase -1 is **opt-in** (the agent only runs it when the user explicitly enables `--assess`; see below). Two lighter modes are supported without code changes — the skill's existing commands and the agent's discretion cover them. Pick the variant that matches the user's request.

### Full mode

Default. Run the seven phases (Phase 0–6) in order; add Phase -1 only when the user opts in. Use when the user wants a complete, polished doc set derived from a non-trivial repository.

### Lite mode (topology only)

Use when the user wants a quick map of the repo without the prose. The deliverables are:

- `topology.md` only (Phase 1 output).
- Skip Phases 2–6 entirely.

The user gets the structural map and can ask for more later. This is the right answer to "what's in this repo?" or "draw me the architecture".

### Progressive mode (topology → decide → continue)

Use when the user wants to evaluate the topology before committing to the full mining. The deliverables across two turns:

- **Turn 1** (Lite mode): `topology.md`.
- **Turn 2** (if the user says "continue" or similar): run Phases 2–6, producing the four prose documents and the `README.md` hub.

This is the right answer to "is this repo worth a full write-up?" — the user sees the topology first and decides.

### When to skip even Lite mode

Even Lite mode is overkill when:

- The repo is a single file or < 5 source files (the suitability rubric would mark it Low).
- The repo is a vendor fork with no top-level source (no modules to enumerate).
- The repo is archived (the rubric's hard veto).

In all three cases, `Phase -1 · Pre-Mining Assessment` (when enabled) tells the user up front; the agent should report "skip — and why" and stop.

## Workflow

Follow these eight phases in order (Phase -1, then Phase 0–6). Phase -1 is opt-in (see below); Phases 1–2 are the new topology-first core; Phases 3–6 reuse the grounded-writing machinery from v1.

### Phase -1 · Pre-Mining Assessment

> **Add this only when the user opts in.** Two optional scaffolder flags drive the new behaviour: `--assess` materialises `assets/templates/assess.md`; `--audience NAME` prefixes the four non-hub generated docs (`topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`) with the audience block (`assets/templates/_audience_block.md`) and, when `--assess` is also set, prefixes `assess.md` itself. `README.md` is the hub and is **not** prefixed. Without either flag the skill behaves exactly as v2.

This phase answers four questions **before** any code is read or topology generated:

1. **Is this repo worth mining?** — apply the rubric in `references/suitability_signals.md`. Six signals, 0–2 each (max raw = 12), rescaled to 0–5 via `round(raw * 5 / 12, 1)`. Hard vetoes (archived, no license + no usage hint, vendor fork, < 3 source files) skip without scoring.
2. **Who is this for?** — pick one or two buckets from `references/audience_profiling.md`. Six buckets cover end-users, applied engineers, contributors, auditors, learners, and integrators.
3. **Where to start reading?** — apply the (audience × suitability-band) matrix in `references/reading_path_suggestions.md`.
4. **What concrete next step?** — write 1–3 imperative actions into `assess.md` §4.

#### Procedure

1. **Materialise the template** with the scaffolder (writes `assess.md` only when `--assess` is passed; the four non-hub docs are prefixed only when `--audience` is also passed):

   ```bash
   python scripts/scaffold_docs.py <repo-root> \
       --project-name "<DisplayName>" [--out docs/guides] \
       --assess [--audience <NAME>]
   ```

2. **Apply the rubric.** Compute the six signals using on-disk facts only (file counts, `git log -1 --format=%ct`, `LICENSE` presence, manifest presence, `docs/` directory size, `tests/` / `examples/` presence). The agent has all of these via standard file-listing tools; no API calls. If `git log` fails (target is not a Git repo, or has no commits), score Vitality = 0 and record the reason in `assess.md` §1.
3. **Pick the audience** using the detection signals in `audience_profiling.md` (README first paragraph, presence of `CONTRIBUTING.md` / `examples/` / framework classifiers, etc.). Record a primary + at most one secondary.
4. **Resolve the entry file and jump list** from the matrix in `reading_path_suggestions.md`.
5. **Fill `assess.md`.** Substitute every `{{...}}` placeholder with the run's findings; leave any genuinely unknown fact as `> TODO(doc-miner): <missing fact>`. Write the verdict paragraph in §5.
6. **If a hard veto fires,** replace §1 with a "Skip — and why" paragraph per the template in `suitability_signals.md`, and stop here. Do not start Phase 0.

The `assess.md` file is the **first deliverable** of the new flow and is referenced from `README.md` as the entry point for the doc set.

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
       [--max-edges 200] [--max-entities 500] [--verbose] \
       [--diff] [--diff-markdown <PATH>]
   ```

   A relative `--out` is resolved against `<repo-root>`.

   Flags:
   - `--max-edges N` — cap rendered dependency edges; `0` means unlimited (default `200`).
   - `--max-entities N` — cap detected entities; `0` means unlimited (default `500`).
   - `--verbose` — print progress to stderr while scanning.
   - `--diff` — diff the new entity set against an existing `--out` (if any) and emit a Markdown diff to **stdout** without overwriting `--out`. Compares both kind counts **and** per-location changes (the location comparison reads the previous `## 3.` inventory table — its locations are capped at three examples per kind, so very large previous topologies can under-report removed locations).
   - `--diff-markdown <PATH>` — with `--diff`, also write the Markdown diff to `<PATH>`. Relative paths resolve against `<repo-root>/docs/guides/`. Exit `2` if the file cannot be written.

   The script detects, generically:
   - Top-level directories as **modules** (build/vendor dirs such as `.git`, `node_modules`, `dist`, `.github`, `.omp`, and `*.egg-info` are skipped). Files directly at the repo root are grouped into a `(root)` module.
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

#### How to refine edges

`gen_topology.py` reads at most `MAX_FILE_READ = 200_000` bytes per file and never follows real imports. Its two edge kinds (`source → copy`, `uses`) are heuristic, not authoritative. After the script produces a draft `topology.md`:

1. **Verify the 2–3 most structurally important edges by reading the actual manifests** (the spec's Phase 1 step 3). Edit the Mermaid block in `topology.md` if any are wrong.
2. **Spend the rest of the refinement budget on `source → copy` edges.** A misclassified copy makes Phase 2 read the same content multiple times and miss the single source.
3. **For the deep guide** (which edges to verify first, how to verify an edge, common false positives and negatives), see [`references/edge_refinement.md`](./references/edge_refinement.md).

The script's intent is to ship a useful draft quickly, not to be the final answer. Treat the auto-detected `topology.md` as a starting point; refine it as you read the manifests.

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
- `scripts/scaffold_docs.py` — creates `<repo>/docs/guides/` and materializes the five document templates from `assets/templates/` with their `{{PROJECT_NAME}}` placeholder substituted (existing files are skipped unless `--force` is passed). Run at the start of Phase 4. Accepts two opt-in flags: `--assess` (materialise `assess.md`) and `--audience NAME` (prefix the four non-hub docs with `_audience_block.md`); both are off by default, so a v2 behaviour is preserved when neither is passed.

### assets/templates/

Markdown skeletons carrying a fixed section schema. Use them as the literal starting point for each file; do **not** rewrite them from scratch. Replace every `{{PLACEHOLDER}}` with repo-specific content harvested in Phase 2.

- `assets/templates/topology.md` — **new in v2.** The architecture-map scaffold (Mermaid blocks + inventory table + per-module sections).
- `assets/templates/developer_guide.md` — 15-section schema (overview → architecture → module tours → extension SOPs → debugging).
- `assets/templates/user_guide.md` — 20-section schema (install → runtime config → core objects → main loop → advanced features → FAQ → minimal runnable examples).
- `assets/templates/tutorial.md` — 10-chapter "from beginner to expert" schema with slots for real example file paths.
- `assets/templates/README.md` — navigation hub that indexes the other four files; mentions the optional `assess.md` first deliverable.
- `assets/templates/assess.md` — **Phase -1 deliverable.** Materialised only when the scaffolder is invoked with `--assess`. The agent fills in suitability score, audience, reading path, and verdict before any of the other docs are written.
- `assets/templates/_audience_block.md` — **Phase -1 fragment.** Prepended to the four non-hub generated docs (and to `assess.md` when `--assess` is also set) when the scaffolder is invoked with `--audience NAME`. `README.md` is the hub and is never prefixed.

### references/

Loaded into context on demand.

- `references/topology_method.md` — **new in v2.** The two-stage methodology: why topology-first scales to large repos, how to detect entity types and edges, and a reusable process you can apply to any repository.
- `references/doc_outlines.md` — canonical section-by-section outlines, with guidance on what each section must contain and how to source the evidence.
- `references/evidence_checklist.md` — the minimum set of files and symbols to read during Phase 2, grouped by repo flavor (Python ML library, Python CLI, Node web app, Rust crate, Go service). Updated to be edge-ordered.
- `references/writing_style.md` — writing-style conventions (tone, bilingual rules, code-citation format, TODO markers).
- `references/suitability_signals.md` — **Phase -1.** Worth-mining rubric: six 0–2 signals rescaled to a 0–5 score, four hard vetoes, and a "skip — and why" branch.
- `references/audience_profiling.md` — **Phase -1.** Six-bucket reader taxonomy (first-time-end-user, applied-engineer, contributor, auditor, learner, integrator) and the on-disk signals that suggest each.
- `references/reading_path_suggestions.md` — **Phase -1.** Deterministic (audience × suitability-band) → entry-point matrix.

## Failure Modes to Avoid

- Writing generic docs that could apply to any library — **always include at least one concrete class name, file path, or example per section**.
- Copying long code blocks verbatim (> 30 lines). Condense and cite the path instead.
- **Skipping Phase 1 and guessing the architecture.** If you cannot draw the topology, you do not understand the repo — stop and read the manifests the script flagged.
- Mistaking a synced copy for an independent implementation because you read it before its source. Always follow `source → copy` edges.
- Clobbering existing `docs/` content. Always write into a dedicated sub-folder (`docs/guides/` by default).
- Forgetting to produce the navigation `README.md`; without it the other four files feel disconnected.
- **Mining a repo with no git history.** `gen_topology.py` reads the working tree but the vitality signal uses `git log -1 --format=%ct`; if the repo is not a Git repo or has no commits, that signal scores 0. Do not assume the rest of the file is broken — the on-disk tree is still valid; only Vitality is 0.
- **Mining a pure-docs repo (no code).** The topology will be empty or near-empty; the entity inventory will show 0 modules. The prose docs will be of limited value. If the user asks, recommend `--assess` (the suitability rubric's "Test/example presence" signal will mark it Low and the verdict will say "skip — and why").
- **Mining a > 10k-file repo.** `gen_topology.py`'s `--max-entities` defaults to 500; `--max-edges` defaults to 200. Above these the script truncates (the edge cap always warns on stderr; the entity cap warns only under `--verbose`). Either pass higher caps (`--max-entities 2000 --max-edges 800`) or pre-warn the user that the topology is partial.
- **Treating `git log` failure as a fatal error.** The suitability rubric's not-a-git fallback scores Vitality = 0 and records the reason in `assess.md` §1. The other five signals are computed from the on-disk tree and remain valid. Do not abort the assessment just because the target isn't a Git repo.
- **Mining a monorepo as a single repo.** The script treats the top-level directory as one repo; each sub-package's `pyproject.toml` / `package.json` is a `py-package` / `node-package` entity. The inventory table will show them all but the prose docs will be confused about which "main" package to focus on. Mine each sub-package separately, or accept the lossy top-level view.
- **Skipping `--audience NAME` when the user has stated their role clearly.** If the user said "I'm a contributor" or "I just need a quick overview", do not skip `--audience` — the prefix adds a one-line blockquote that costs < 100 bytes and saves the reader several minutes of orientation.
