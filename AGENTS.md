# Repository Guidelines

## Project Overview

`repo-doc-miner` is a **CodeBuddy / Claude-Code compatible Skill** (v2.0.0) — not a library or application. It is a prompt-and-tooling package that mines a **target** Git repository and generates a coordinated five-file Markdown doc set into that target's `docs/guides/`.

`SKILL.md` is the entry point: an agent auto-discovers it via frontmatter (`name`, `description`, `version`) and follows its seven-phase workflow (Phase 0–6). There is no runtime API, no package manifest, no build, and no test suite. The only executable surface is two stdlib-only Python scripts that **write files into the target repo**.

Two-stage method (the core idea): **topology-first → module-deep-dive**. Draw the entity/dependency map first, then read modules *along the dependency edges* so a capability is understood at its source before its synced copies.

**Critical operational hazard:** both scripts mutate whatever path is passed as `<repo-root>`. Never point them at this package or any repo you do not intend to modify. Use a throwaway directory for smoke tests.

## Architecture & Data Flow

```
SKILL.md (manifest + Phase 0-6 workflow)
   │
   ├─ Phase 1  scripts/gen_topology.py ──> <target>/docs/guides/topology.md   (deliverable #1, refined by hand)
   ├─ Phase 2  references/evidence_checklist.md + topology_method.md  ──> scratch note (not a deliverable)
   ├─ Phase 3  references/doc_outlines.md ──> per-document content plan
   ├─ Phase 4  scripts/scaffold_docs.py + assets/templates/* ──> 5 files, then filled in place
   ├─ Phase 5  validation gates (see Testing & QA)
   └─ Phase 6  handover summary (paths, line counts, coverage, open TODOs)
```

Phase ownership is the load-bearing structure: `references/` files are *phase-scoped instructions loaded on demand*, and `assets/templates/` are the literal Phase-4 scaffolding. Cross-file coupling is by **path string and filename contract**, never by imports:

- `scaffold_docs.py:TEMPLATE_FILES` must match the actual filenames in `assets/templates/`.
- `gen_topology.py` emits section headings `## 1..4` and `> TODO(doc-miner)` markers that `assets/templates/topology.md` and `references/topology_method.md` both assume.
- All five templates cross-link as relative siblings (`./developer_guide.md`), so filenames are an interface.

**Same-directory ordering:** Phase 1 writes `topology.md` into `docs/guides/`, and Phase 4's scaffolder targets that same directory. `scaffold_docs.py` therefore **skips files that already exist** (printing `skipped (exists): <path>`, exit 0) and writes only the missing ones, so a Phase-1 `topology.md` survives Phase 4 untouched. `--force` overwrites all five files. Detection guards: `Entity.id` is derived from the repo-relative path (`_assign_ids`/`sanitize_id`) so Mermaid node ids are unique, entity and edge emission is sorted for reproducible diffs, and `_is_ignored` skips build/vendor directories (including `*.egg-info` and `.github`).

There are no subagents, services, caches, or persistence — the data flow is files in, files out.

## Key Directories

| Path | Purpose |
|---|---|
| `SKILL.md` | Skill manifest + canonical Phase 0–6 workflow, trigger conditions, resource list, failure modes. Change workflow semantics here first. |
| `scripts/` | The only executable code. `gen_topology.py` (512 lines, entity/edge miner + Mermaid renderer), `scaffold_docs.py` (132 lines, template materializer). |
| `references/` | Phase-scoped methodology docs: `topology_method.md` (why + how, and how to extend the miner), `evidence_checklist.md` (Phase-2 minimum reads, per repo flavor), `doc_outlines.md` (Phase-3 fixed section skeletons), `writing_style.md` (Phase-4 cross-cutting prose law). |
| `assets/templates/` | Five Markdown skeletons copied verbatim into the target repo: `topology.md`, `README.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`. |
| `README.md` | Human-facing companion to `SKILL.md`: install paths, quick start, design principles. |

## Development Commands

No build, lint, format, install, or test commands exist. Only three commands are real:

```bash
# Phase 1 — mine the target repo (writes only if the path is writable)
python3 scripts/gen_topology.py <repo-root> \
    --out <repo-root>/docs/guides/topology.md \
    [--project-name "<DisplayName>"] [--max-edges 200] \
    [--diff] [--diff-markdown <PATH>]

# Phase 4 — scaffold the five doc skeletons (fills {{PROJECT_NAME}} only; existing files
# are skipped, so the Phase-1 topology.md is preserved — pass --force to overwrite all five)
python3 scripts/scaffold_docs.py <repo-root> \
    --project-name "<DisplayName>" [--out docs/guides] [--force]

# Phase 5 — open-gap sweep
rg "TODO\(doc-miner\)" <repo-root>/docs/guides
```

Safe smoke test (never run against this package):

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force
find "$tmp/docs/guides" -name '*.md' | sort
rm -rf "$tmp"
```

Exit codes: `gen_topology.py` → `0` ok, `1` bad repo root or invalid `--max-edges` / `--max-entities` or unreadable tree, `2` cannot create/write the output file or the `--diff-markdown` target. `scaffold_docs.py` → `0` ok (written and/or skipped), `1` bad repo root / templates missing. Arguments are always positional `<repo-root>`; cwd is never used — a relative `--out` is resolved against `<repo-root>`, and a relative `--diff-markdown` is resolved against `<out>'s parent`.

`--max-edges` (default 200) caps rendered edges only; it rejects values `< 0` (exit 1). `--max-entities` (default 500) caps detected entities the same way. `--diff` prints a Markdown diff to stdout without overwriting `--out`. `--diff-markdown <PATH>` writes the diff body to `<PATH>` and additionally prints to stdout; exit `2` on write failure. The diff body compares both kind counts and per-location changes; per-location comparison is bounded by the previous topology's three-example cap per kind.

## Code Conventions & Common Patterns

Both scripts follow one identical template — match it exactly when extending:

- **Stdlib only.** `argparse`, `pathlib`, `json`, `re`, `sys`, `dataclasses`. No third-party imports, ever; there is no dependency manifest to add them to.
- **Header contract:** `#!/usr/bin/env python3`, then `from __future__ import annotations`, then a module docstring containing a `Usage:` block and an `Exit codes:` block.
- **Entry point:** `def main(argv: list[str] | None = None) -> int:` guarded by `if __name__ == "__main__": raise SystemExit(main())`.
- **Typing:** PEP 604 unions (`Path | None`), builtin generics (`list[Entity]`, `dict[str, int]`), annotations on every parameter and return. No `Any` unless unavoidable.
- **Paths:** `pathlib.Path` exclusively; no `os.path`. Encoding is always explicit `encoding="utf-8"`; reads use `errors="ignore"` for hostile repos.
- **Error handling:** helper-level failures raise; `main` converts them to `print(..., file=sys.stderr)` + integer return (detection is wrapped in `except OSError` → exit 1; output creation/write in `except Exception` → exit 2). Uncaught exceptions are bugs. Never `logging`; progress goes to stdout via `print(f"...")`.
- **Private helpers** are `_`-prefixed (`_add`, `_assign_ids`, `_is_ignored`, `_module_of`, `_label`, `_file_size`, `_count_mcp_servers`). Section banner comments (`# ---- Helpers`, `# ---- Entity detection`, `# ---- Rendering`, `# ---- Main`) separate regions in `gen_topology.py`.
- **Data model** is `@dataclass` (`Entity`, `Edge`), not dicts. `Entity.id` is assigned after detection by `_assign_ids` (repo-relative path → `sanitize_id`, `_2`/`_3` suffix on collision); `(kind, rel_path)` is the dedup key. Tolerate malformed input: `safe_read()` swallows all exceptions and returns `""`, reading at most `MAX_FILE_READ = 200_000` bytes.
- **Rendering is contract-bearing.** Mermaid lines (`graph TD` / `graph LR`), `style` directives, `## N.` headings, and `> TODO(doc-miner)` markers are consumed by templates and docs — change them only in lockstep with `assets/templates/topology.md`.

Doc-prose conventions live in `references/writing_style.md` and apply to anything this skill generates (including, recursively, docs written about this repo):

- Cite symbols as `` `path/relative/to/repo.py::Symbol` `` on first mention per document.
- Snippets ≤ 30 lines, correct fence language, original import style preserved; never invent API names.
- ASCII diagrams ≤ 72 chars wide, only the whitelisted box characters.
- Unresolved facts get `` > TODO(doc-miner): <missing fact> ``; never fabricate behavior.
- Match the language of the target repo's existing `docs/`; bilingual → language of the user's latest query. No marketing adjectives.

Placeholders: `{{UPPER_SNAKE_CASE}}` everywhere, plus `<angle-bracket>` slots in `topology.md` only. `scaffold_docs.py` substitutes **only** `{{PROJECT_NAME}}`; every other placeholder is deliberately left for the agent to fill in Phase 4. The naming families and suffix conventions are enumerated in `references/doc_outlines.md` (`## Placeholder conventions`). No YAML front-matter, no HTML comments, no templating engine.

## Important Files

| File | Why it matters |
|---|---|
| `SKILL.md` | Trigger conditions, phase sequence, and failure modes. `description` in frontmatter is what makes the skill fire. |
| `scripts/gen_topology.py` | Entity/edge detection (`detect_entities`, `detect_edges`, `_assign_ids`, `_is_ignored`, `_REF_PATTERN`, `COPY_KEYWORDS`, `IGNORE_DIRS`, `TEXT_SUFFIXES`) and Markdown rendering (`build_structural_graph`, `build_edge_graph`, `render_markdown`). |
| `scripts/scaffold_docs.py` | `TEMPLATE_FILES`, `locate_templates_dir`, `materialize` (returns `(written, skipped)`) — the template↔output filename contract. |
| `assets/templates/topology.md` | Shape contract for generated topology output; mirrors `render_markdown`. |
| `references/writing_style.md` | Single source of truth for citation form, snippet caps, TODO markers, link rules. |
| `references/topology_method.md` | Canonical pipeline pseudocode (its `Phase 0..6` block) and the script-extension guide. |
| `LICENSE` | MIT, © 2026 binbinao. Notice must travel with copies in all substantial portions (templates included). |

Name collision to watch: this root `README.md`, `assets/templates/README.md`, and the generated `<target>/docs/guides/README.md` are three different files.

## Runtime/Tooling Preferences

- **Bare `python` / `python3` only.** No virtualenv, no `requirements.txt`, no packaging. `.gitignore` covers `.venv/` (not `venv/`) and `__pycache__/`.
- **No minimum Python version is declared** anywhere. The scripts target 3.8+-compatible stdlib; local bytecode is `cpython-314`. Do not introduce 3.12+-only syntax without updating `SKILL.md`.
- **`rg` (ripgrep) is required** by the Phase 5 verification step (`rg "TODO\(doc-miner\)"`) but is not listed in any prerequisites section — treat it as an environment dependency when running the workflow.
- **`search_content` / `search_file`** are CodeBuddy agent-provided tools, not part of this package. The docs previously assumed they were always available; Phase 5 now says to fall back to whatever file-listing/read tool the host agent provides.
- **Installation** is directory-copy: `.codebuddy/skills/repo-doc-miner/` (project- or user-scoped under `~/.codebuddy/skills/`). No Claude Code path is documented despite the "Claude-Code compatible" claim.
- **Target-machine assumption:** the scripts run against arbitrary repos, so any new detection logic must skip binaries, cap reads, and never assume a referenced path resolves.

## Testing & QA

There is **no test framework, no CI, and no linter**. Do not add or claim one; verification is manual and command-driven.

Verification gates to run before claiming a change works:

1. **Smoke-test both scripts in a throwaway repo** (command block above). Assert: `gen_topology.py` exits 0 and writes `topology.md` with `## 1..4` headings; a second run is byte-identical (reproducible ordering); `scaffold_docs.py` without `--force` exits 0, prints `skipped (exists)` for `topology.md`, and leaves that file byte-identical; with `--force` it rewrites all five files and no `{{PROJECT_NAME}}` remains.
2. **`rg "TODO\(doc-miner\)"` sweep** over generated output — every remaining hit must be either a known gap listed in the handover summary or the trailing cleanup marker that is meant to be removed.
3. **Phase 5 checklist** from `SKILL.md`: spot-check 5 random snippets against real source paths/signatures; confirm every module named in the developer guide exists; verify the 2–3 most important topology edges against real manifests; confirm Markdown renders (monotonic headings, closed fences, valid relative links, well-formed Mermaid).
4. **Template contract:** after editing `assets/templates/`, re-run the scaffolder and confirm `TEMPLATE_FILES` still resolves all five names and the placeholder set is unchanged in kind.

Keep behavior-proving edits grounded: detection heuristics in `gen_topology.py` are explicitly heuristic and expected to be human-refined, so assert observable script output, not inferred graph quality.

### Known inconsistencies to not propagate

These are real defects in the current tree; fix or avoid echoing them rather than treating them as spec:

- Templates and `references/evidence_checklist.md` are specialized for Python ML/PINN-shaped libraries (DeepXDE-flavored sections: backend abstraction, networks catalog, PDE constraints). Adapting to other repo flavors means adding rows to the checklist and sections to the templates, not rewriting existing ones.
- `rg` (ripgrep) is required by the Phase 5 sweep but is not listed in any prerequisites section beyond `SKILL.md`; treat it as an environment dependency.
- `gen_topology.py`'s entity/edge detection stays heuristic by design (it reads at most `MAX_FILE_READ` per file and never follows real imports). The human-refinement step in Phase 1 is mandatory, not optional.

Fixes already landed (do not re-report these as open defects): phase count (`SKILL.md` says Phase 0–6 consistently), the five-file vs "three/four documents" drift across `SKILL.md`/`README.md`/`references/`/templates, the scaffolder's overwrite/exit-code contract (now skip-by-default, exit 0), dead code in both scripts, `IGNORE_DIRS`/`_is_ignored` handling of `*.egg-info` plus `.github` plus `.omp`, the snippet-cap conflict (≤ 30 lines everywhere), the undocumented `--max-edges` flag, the `--diff` early-return bug that dropped location-level changes, the `--diff-markdown <PATH>` flag (file output of the diff body), and the inventory table that used to truncate to the top three per kind (now lists all locations so the diff has a stable prev baseline).
