# repo-doc-miner (v3 — Topology-First + Pre-Mining Assessment)

A CodeBuddy / Claude-Code compatible **Skill** that mines an existing Git
repository using a two-stage **topology-first → module-deep-dive** method
and produces a coordinated Markdown doc set (a repo topology map, a
developer guide, a user guide, a from-beginner-to-expert tutorial, and a
navigation `README.md`) saved into the repository's `docs/guides/`
folder. Use this skill when the user asks to "dig into / mine / analyze
this project and produce documentation", "generate a repo topology /
architecture map and docs", "write onboarding docs from the codebase", or
any similar request where the deliverable is a coordinated doc set
derived from reading the current repository.

**v3 adds a pre-mining assessment stage** that runs before the topology
map is produced: an opt-in `Phase -1` that answers "is this repo worth
mining, who is this for, and where to start reading?" The four questions
are answered in an `assess.md` file. When the user does not opt in, v3
behaves exactly as v2. See [`references/suitability_signals.md`](./references/suitability_signals.md)
for the rubric.

## What changed in v2

v1 scanned files flatly and produced three documents. v2 **leads with a topology
map**: it enumerates the repository's *entity types* (modules, skills, agents,
commands, connectors, packages, scripts…) and extracts the *dependency edges*
between them — especially `source → copy` edges where one file is a synced copy
of a single source of truth. The topology map is the first deliverable and the
backbone for the other documents. This ordering is what lets the skill scale to
very large repositories: it collapses O(N) files into an O(entity-type)
structure and tells the agent *which* files to read *in what order*.

The key new piece is `scripts/gen_topology.py`, which auto-generates the map; a
human then refines the detected edges by reading the most important manifests.

## Contents

```
.
├── SKILL.md                       # Skill manifest + Phase -1..6 workflow (entry point)
├── assets/
│   └── templates/                 # Markdown skeletons used as the literal starting point
│       ├── topology.md            # architecture-map scaffold (v2; slots removed v3)
│       ├── developer_guide.md     # 15-section schema
│       ├── user_guide.md          # 20-section schema
│       ├── tutorial.md            # 10-chapter schema
│       ├── README.md              # navigation hub
│       ├── assess.md              # NEW v3 (Phase -1): pre-mining assessment deliverable
│       ├── _audience_block.md     # NEW v3 (Phase -1): audience-prefix fragment
│       └── _flavor_strip.md       # NEW v3 (Phase 3): no-op marker for future --flavor
├── references/                    # Loaded on demand during writing
│   ├── topology_method.md         # the two-stage methodology + how to extend
│   ├── doc_outlines.md            # canonical section-by-section outlines
│   ├── evidence_checklist.md      # minimum files/symbols to read; opens with tool-vs-expectation callout (v3)
│   ├── writing_style.md           # prose conventions
│   ├── suitability_signals.md     # NEW v3 (Phase -1): worth-mining rubric
│   ├── audience_profiling.md      # NEW v3 (Phase -1): six-bucket reader taxonomy
│   ├── reading_path_suggestions.md# NEW v3 (Phase -1): (audience × suitability-band) matrix
│   └── edge_refinement.md         # NEW v3 (Phase 2): how to verify and refine auto-detected edges
├── scripts/
│   ├── gen_topology.py            # scan a repo → Mermaid topology + inventory; --dry-run, --summary
│   ├── scaffold_docs.py           # create docs/guides/ and materialize templates; --assess, --audience
│   ├── smoke.py                   # NEW v3 (Phase 2): codified safe smoke + Phase-5 checks
│   └── _env.sh                    # NEW v3 (Phase 3): sourceable REPO_DOC_MINER_HOME exporter
└── LICENSE
```

## Installation

Drop the whole folder into your agent's skill directory:

- **CodeBuddy (project-scoped)**: `<repo>/.codebuddy/skills/repo-doc-miner/`
- **CodeBuddy (user-scoped)**: `~/.codebuddy/skills/repo-doc-miner/`

The agent auto-discovers the skill via `SKILL.md`.

## Quick Start

Once installed, trigger the skill with a request like:

- "挖掘当前项目，先给我拓扑图，再生成开发者文档、用户文档和从入门到精通教程"
- "Mine this repo, draw an architecture topology, and produce docs under `docs/guides/`"

The skill will:

1. **Generate the topology** with `scripts/gen_topology.py` (Phase 1), then refine the detected edges.
2. **Deep-dive modules along the edges** to gather grounded evidence (Phase 2).
3. **Draft and write** the four documents plus the `README.md` hub via the templates (Phases 3–4).
4. **Validate** snippet fidelity, edge reality, and Markdown rendering (Phase 5), then hand over (Phase 6).

You can also run the generators manually:

```bash
# Phase 1: draw the topology map (--out is resolved against <repo-root>)
python scripts/gen_topology.py <repo-root> \
    --project-name "<DisplayName>" \
    --out <repo-root>/docs/guides/topology.md \
    [--max-edges 200]

# Phase 4: scaffold the five doc skeletons (fills {{PROJECT_NAME}};
# existing files are skipped unless --force is given)
python scripts/scaffold_docs.py <repo-root> \
    --project-name "<DisplayName>" [--out docs/guides] [--force]
```

## Design Principles

- **Topology-first** — map the structure and dependencies before reading details; the map is the first deliverable.
- **Edge-ordered reading** — understand a single source of truth before its synced copies.
- **Ground every claim in code** — file paths and symbol names accompany every feature description.
- **Prefer real snippets** from `examples/` or tests, capped at ~30 lines.
- **Cross-link** the five files so any one of them is a valid entry point.
- **Mark unresolved gaps** with `TODO(doc-miner)` instead of fabricating behavior.

See `SKILL.md` for the full eight-phase workflow (Phase -1, then Phase 0–6; Phase -1 is opt-in) and
`references/topology_method.md` for the methodology and how to extend the
topology detector to new repo families.

## License

[MIT](./LICENSE)
