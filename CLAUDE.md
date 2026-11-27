# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`repo-doc-miner` is a **Skill package** (v2.0.0) — not a library or application. It mines a *target* Git repository and generates a five-file Markdown doc set into that target's `docs/guides/`: `topology.md` (Mermaid structure map — the primary deliverable), `developer_guide.md`, `user_guide.md`, `tutorial.md`, and a `README.md` navigation hub.

`SKILL.md` is the entry point (Phase 0–6 workflow). There is no runtime, no package manifest, no build, no linter, no test framework. The only executable code is two stdlib-only Python scripts in `scripts/`.

`AGENTS.md` (repo root) is the deeper companion to this file — full code-convention catalog, template contracts, verification gates, and the "Known inconsistencies to not propagate" + "Fixes already landed" ledgers. Consult it before extending either script or the templates.

## Critical hazard

Both scripts **write files into whatever path is passed as `<repo-root>`**. Never point them at this package or any repo you do not intend to modify. Smoke-test only in a throwaway directory.

## Commands

The only real commands (run from this repo root):

```bash
# Phase 1 — mine a target repo (--out defaults to <repo-root>/docs/guides/topology.md)
python3 scripts/gen_topology.py <repo-root> --project-name "<DisplayName>" \
    [--max-edges 200] [--max-entities 500] [--diff] [--diff-markdown <PATH>]

# Phase 4 — scaffold the five doc skeletons (skips existing files; --force overwrites all five)
python3 scripts/scaffold_docs.py <repo-root> --project-name "<DisplayName>" [--out docs/guides] [--force]

# Phase 5 — open-gap sweep (requires rg on PATH)
rg "TODO\(doc-miner\)" <repo-root>/docs/guides
```

Exit codes: `gen_topology.py` → `0` ok / `1` bad repo root, unreadable tree, or invalid cap flag / `2` cannot write the output or `--diff-markdown` target. `scaffold_docs.py` → `0` ok (written and/or skipped) / `1` bad repo root or missing templates.

Safe smoke test (never run against this package):

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force
find "$tmp/docs/guides" -name '*.md' | sort
rm -rf "$tmp"
```

## Architecture

Files in, files out — nothing imports anything across files; **all coupling is by path string and filename contract**:

```
SKILL.md (manifest + Phase 0–6 workflow)
 ├─ Phase 1  scripts/gen_topology.py ──> <target>/docs/guides/topology.md (then refined by hand)
 ├─ Phase 2  references/evidence_checklist.md + topology_method.md ──> scratch note (not a deliverable)
 ├─ Phase 3  references/doc_outlines.md ──> per-document content plan
 ├─ Phase 4  scripts/scaffold_docs.py + assets/templates/* ──> 5 files, filled in place
 ├─ Phase 5  validation gates (see AGENTS.md "Testing & QA")
 └─ Phase 6  handover summary
```

Load-bearing contracts:

- `scaffold_docs.py:TEMPLATE_FILES` must match the actual filenames in `assets/templates/`.
- `gen_topology.py` emits `## 1..4` headings and `> TODO(doc-miner)` markers that `assets/templates/topology.md` and `references/topology_method.md` both assume; Mermaid lines (`graph TD` / `graph LR`) and `style` directives are contract-bearing — change them only in lockstep.
- All five templates cross-link as relative siblings — filenames are an interface.
- **Same-directory ordering:** Phase 4's scaffolder targets the same `docs/guides/` that Phase 1 wrote `topology.md` into, so it skips existing files by default (exit 0). That skip behavior is what preserves the Phase-1 human refinement.
- **Determinism:** entity/edge emission is sorted and Mermaid node ids derive from repo-relative paths, so re-runs are byte-identical. Preserve this — reproducible diffs depend on it.
- `references/` files are phase-scoped instructions loaded on demand; `assets/templates/` are the literal Phase-4 scaffolding. `scaffold_docs.py` substitutes only `{{PROJECT_NAME}}`; every other `{{PLACEHOLDER}}` is deliberately left for the agent to fill in Phase 4.

Code conventions for `scripts/` (match the existing template exactly; full catalog in AGENTS.md): stdlib only; `from __future__ import annotations`; module docstring with `Usage:` and `Exit codes:` blocks; `main(argv: list[str] | None = None) -> int` guarded entry point; `pathlib` everywhere with explicit `encoding="utf-8"`; `@dataclass` models (`Entity`, `Edge`); `_`-prefixed private helpers; helper failures raise, `main` converts them to a stderr line + int; reads capped at `MAX_FILE_READ = 200_000` bytes with `errors="ignore"` (the scripts run against arbitrary, possibly hostile repos).

Doc-prose law (`references/writing_style.md`, applies to everything this skill generates): cite symbols as `` `path/to/file.py::Symbol` `` on first mention per document; snippets ≤ 30 lines, real APIs only; unresolved facts get `> TODO(doc-miner): ...` — never fabricate; match the target repo's docs language; no marketing adjectives.

## Testing & QA

No test framework exists — do not add one. Verification is manual and command-driven:

1. Smoke-test both scripts in a throwaway repo (block above). Assert: a second `gen_topology.py` run is byte-identical; the scaffolder without `--force` prints `skipped (exists)` for `topology.md` and leaves it byte-identical; with `--force` it rewrites all five files and no `{{PROJECT_NAME}}` remains.
2. `rg "TODO\(doc-miner\)"` sweep over generated output — every remaining hit must be a known gap listed in the handover or the trailing cleanup marker.
3. Phase 5 spot-checks: 5 random snippets vs. real source signatures; every module named in the developer guide exists; the 2–3 most important topology edges verified against real manifests; Markdown/Mermaid renders.

## Ongoing work — planned but NOT implemented

The three-phase optimization recorded under `docs/superpowers/` is **spec + plan only** (as of 2026-11-26: 0 of 52 plan checkboxes done):

- Spec: `docs/superpowers/specs/2026-10-11-repodocminer-optimization-design.md` (Phase 1 = Pre-Mining Assessment, Phase 2 = reliability/operability, Phase 3 = generalization/polish)
- Plan: `docs/superpowers/plans/2026-10-11-phase1-pre-mining-assessment.md` — adds a Phase -1 (`assess.md` deliverable, `--assess` / `--audience` scaffolder flags, three new `references/` rubric files, two new templates)

Read the plan before proposing or implementing any of this; it fixes hard constraints (stdlib-only, byte-identical scaffolder output when the new flags are off, no phase renumbering, additive template sections only).

## Repo-state notes

- `docs/guides/topology.md` is this repo's own self-mined topology — gitignored smoke output, not a source of truth.
- `.omp/` and `.worktrees/` are gitignored tooling directories, not part of the skill; `.omp/` is also skipped by the topology miner's ignore list.
- Installation is directory-copy into `.codebuddy/skills/repo-doc-miner/`; no Claude Code install path is documented despite the "Claude-Code compatible" claim.
- License: MIT © 2026 binbinao — the notice must travel with copies (templates included) in all substantial portions.
