# Repository Guidelines

## Project Overview

`repo-doc-miner` is a **CodeBuddy / Claude-Code compatible Skill** (v2.0.0) — not a library or application. It is a prompt-and-tooling package that mines a **target** Git repository and generates a coordinated five-file Markdown doc set into that target's `docs/guides/` (an optional sixth file, `assess.md`, is added when Phase -1 is enabled).

`SKILL.md` is the entry point: an agent auto-discovers it via frontmatter (`name`, `description`, `version`) and follows its eight-phase workflow (Phase -1, then Phase 0–6; Phase -1 is opt-in). There is no runtime API, no package manifest, no build, and no test suite. The only executable surface is two stdlib-only Python scripts that **write files into the target repo**.

Two-stage method (the core idea): **topology-first → module-deep-dive**. Draw the entity/dependency map first, then read modules *along the dependency edges* so a capability is understood at its source before its synced copies.

**Critical operational hazard:** both scripts mutate whatever path is passed as `<repo-root>`. Never point them at this package or any repo you do not intend to modify. Use a throwaway directory for smoke tests.

## Architecture & Data Flow

```
SKILL.md (manifest + Phase -1..6 workflow)
   │
   ├─ Phase -1 [opt-in] references/{suitability_signals,audience_profiling,reading_path_suggestions}.md ──> <target>/docs/guides/assess.md  (optional deliverable)
   ├─ Phase 1  scripts/gen_topology.py ──> <target>/docs/guides/topology.md   (deliverable #1, refined by hand)
   ├─ Phase 2  references/evidence_checklist.md + topology_method.md  ──> scratch note (not a deliverable)
   ├─ Phase 3  references/doc_outlines.md ──> per-document content plan
   ├─ Phase 4  scripts/scaffold_docs.py + assets/templates/* ──> 5 files (+ optional assess.md), then filled in place
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
| `SKILL.md` | Skill manifest + canonical Phase -1..6 workflow, trigger conditions, resource list, failure modes. Change workflow semantics here first. |
| `scripts/` | The only executable code. `gen_topology.py` (entity/edge miner + Mermaid renderer, `--dry-run`/`--summary`), `scaffold_docs.py` (template materializer + Phase -1 `--assess`/`--audience`, plus `--flavor`/`--lang`), `smoke.py` (codified safe smoke + Phase-5 checks), `check_resources.py` (Resources-drift validator), `_env.sh` (`REPO_DOC_MINER_HOME`). |
| `references/` | Phase-scoped methodology docs: `topology_method.md` (why + how, and how to extend the miner), `evidence_checklist.md` (Phase-2 minimum reads, per repo flavor), `doc_outlines.md` (Phase-3 fixed section skeletons), `writing_style.md` (Phase-4 cross-cutting prose law), `edge_refinement.md` (verify/refine auto-detected edges), plus the Phase -1 trio `suitability_signals.md` (worth-mining rubric), `audience_profiling.md` (six-bucket reader taxonomy), `reading_path_suggestions.md` (audience × suitability-band entry matrix). |
| `assets/templates/` | Markdown skeletons copied verbatim into the target repo: the core five `topology.md`, `README.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`, plus `assess.md` (materialized only on `--assess`), `_audience_block.md` (prepended only on `--audience`), and `_flavor_strip.md` (marker for `--flavor` block structure). |
| `README.md` | Human-facing companion to `SKILL.md`: install paths, quick start, design principles. |

## Development Commands

No build, lint, format, install, or test commands exist. Only these commands are real:

```bash
# Phase -1 [opt-in] — materialize assess.md and/or prefix the audience block
python3 scripts/scaffold_docs.py <repo-root> \
    --project-name "<DisplayName>" [--out docs/guides] \
    [--assess] [--audience <NAME>]

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

Exit codes: `gen_topology.py` → `0` ok, `1` bad repo root or invalid `--max-edges` / `--max-entities` or unreadable tree, `2` cannot create/write the output file or the `--diff-markdown` target. `scaffold_docs.py` → `0` ok (written and/or skipped), `1` repo root absent, templates directory missing, `_audience_block.md` missing, or the audience block unreadable. A missing `assess.md` template under `--assess` is a soft failure: the error goes to stderr and the script still exits `0` (see "Known inconsistencies to not propagate"). Arguments are always positional `<repo-root>`; cwd is never used — a relative `--out` is resolved against `<repo-root>`, and a relative `--diff-markdown` is resolved against `<out>'s parent`.

`--max-edges` (default 200) caps rendered edges only; it rejects values `< 0` (exit 1). `--max-entities` (default 500) caps detected entities the same way. `--diff` prints a Markdown diff to stdout without overwriting `--out`. `--diff-markdown <PATH>` writes the diff body to `<PATH>` and additionally prints to stdout; exit `2` on write failure. The diff body compares both kind counts and per-location changes; per-location comparison is bounded by the previous topology's three-example cap per kind. `--assess` additionally materializes `assess.md` (opt-in; absent by default). `--audience <NAME>` prepends `assets/templates/_audience_block.md` (with `{{AUDIENCE}}` and `{{PROJECT_NAME}}` substituted) to the four non-hub generated docs and, when `--assess` is also set, to `assess.md`; `README.md` is the hub and is never prefixed.

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

Placeholders: `{{UPPER_SNAKE_CASE}}` everywhere. `scaffold_docs.py` substitutes `{{PROJECT_NAME}}` (and `{{AUDIENCE}}` inside the `_audience_block.md` fragment when `--audience` is passed); every other placeholder is deliberately left for the agent to fill in Phase 4. The naming families and suffix conventions are enumerated in `references/doc_outlines.md` (`## Placeholder conventions`). No YAML front-matter, no templating engine, and **no `<angle-bracket>` slots** in any shipped file — Phase 3 C11 removed the legacy slots in `topology.md`; the 5 core templates now ship slot-free. The single exception to the no-HTML-comments rule is the machine-readable `<!-- audience: {{AUDIENCE}} -->` marker that begins `assets/templates/_audience_block.md`.

## Important Files

| File | Why it matters |
|---|---|
| `SKILL.md` | Trigger conditions, phase sequence, and failure modes. `description` in frontmatter is what makes the skill fire. |
| `scripts/gen_topology.py` | Entity/edge detection (`detect_entities`, `detect_edges`, `_assign_ids`, `_is_ignored`, `_REF_PATTERN`, `COPY_KEYWORDS`, `IGNORE_DIRS`, `TEXT_SUFFIXES`) and Markdown rendering (`build_structural_graph`, `build_edge_graph`, `render_markdown`). |
| `scripts/scaffold_docs.py` | `TEMPLATE_FILES` + `HUB_FILE`, `locate_templates_dir`, `materialize` (returns `(written, skipped)`; Phase -1 params `write_assess` / `audience_prefix`) — the template↔output filename contract. |
| `assets/templates/topology.md` | Shape contract for generated topology output; mirrors `render_markdown`. |
| `references/writing_style.md` | Single source of truth for citation form, snippet caps, TODO markers, link rules. |
| `references/topology_method.md` | Canonical pipeline pseudocode (its `Phase 0..6` block) and the script-extension guide. |
| `LICENSE` | MIT, © 2026 binbinao. Notice must travel with copies in all substantial portions (templates included). |

Name collision to watch: this root `README.md`, `assets/templates/README.md`, and the generated `<target>/docs/guides/README.md` are three different files.

## Runtime/Tooling Preferences

- **Bare `python` / `python3` only.** No virtualenv, no `requirements.txt`, no packaging. `.gitignore` covers `.venv/` (not `venv/`) and `__pycache__/`.
- **Minimum Python version:** `SKILL.md`'s `## Prerequisites` declares `python3 >= 3.8` (added with Phase -1). The scripts target 3.8+-compatible stdlib; local bytecode is `cpython-314`. Do not introduce 3.12+-only syntax without updating `SKILL.md`.
- **`rg` (ripgrep) is required** by the Phase 5 verification step (`rg "TODO\(doc-miner\)"`); `SKILL.md`'s `## Prerequisites` now declares it (added with Phase -1). Treat it as an environment dependency elsewhere.
- **`search_content` / `search_file`** are CodeBuddy agent-provided tools, not part of this package. The docs previously assumed they were always available; Phase 5 now says to fall back to whatever file-listing/read tool the host agent provides.
- **Installation** is directory-copy: `.codebuddy/skills/repo-doc-miner/` (project- or user-scoped under `~/.codebuddy/skills/`). No Claude Code path is documented despite the "Claude-Code compatible" claim.
- **Target-machine assumption:** the scripts run against arbitrary repos, so any new detection logic must skip binaries, cap reads, and never assume a referenced path resolves.

## Testing & QA

There is **no test framework, no CI, and no linter**. Do not add or claim one; verification is manual and command-driven.

Verification gates to run before claiming a change works:

1. **Smoke-test both scripts in a throwaway repo** (command block above). Assert: `gen_topology.py` exits 0 and writes `topology.md` with `## 1..4` headings; a second run is byte-identical (reproducible ordering); `scaffold_docs.py` without `--force` exits 0, prints `skipped (exists)` for `topology.md`, and leaves that file byte-identical; with `--force` it rewrites all five files and no `{{PROJECT_NAME}}` remains. With `--assess` it writes a sixth file, `assess.md`; with `--audience <NAME>` the four non-hub docs gain the `<!-- audience: NAME -->` block while `README.md` stays unprefixed; with neither flag the five core docs are produced with the same byte-identical layout as v2 (Phase 3 C2 added a top-of-file `> TODO(doc-miner): no remaining placeholders` reminder; that reminder is the only intentional change from v2 to v3).
2. **`rg "TODO\(doc-miner\)"` sweep** over generated output — every remaining hit must be either a known gap listed in the handover summary or the **top-of-file** placeholder-sweep reminder that the scaffolder leaves in `developer_guide.md` / `user_guide.md` / `tutorial.md` / `README.md` (Phase 3 C2).
3. **Phase 5 checklist** from `SKILL.md`: spot-check 5 random snippets against real source paths/signatures; confirm every module named in the developer guide exists; verify the 2–3 most important topology edges against real manifests; confirm Markdown renders (monotonic headings, closed fences, valid relative links, well-formed Mermaid).
4. **Template contract:** after editing `assets/templates/`, re-run the scaffolder and confirm `TEMPLATE_FILES` still resolves all five names, `assess.md` / `_audience_block.md` still resolve under `--assess` / `--audience`, and the placeholder set is unchanged in kind.

Keep behavior-proving edits grounded: detection heuristics in `gen_topology.py` are explicitly heuristic and expected to be human-refined, so assert observable script output, not inferred graph quality.

### Known inconsistencies to not propagate

These are real defects in the current tree; fix or avoid echoing them rather than treating them as spec:

- Templates and `references/evidence_checklist.md` are specialized for Python ML/PINN-shaped libraries (DeepXDE-flavored sections: backend abstraction, networks catalog, PDE constraints). Adapting to other repo flavors means adding rows to the checklist and sections to the templates, not rewriting existing ones.
- `rg` (ripgrep) is required by the Phase 5 sweep; it is now declared in `SKILL.md`'s `## Prerequisites` (added with Phase -1), but downstream consumers should still treat it as an environment dependency.
- `scaffold_docs.py` under `--assess` treats a missing `assets/templates/assess.md` as a soft failure: it prints `error: --assess requested but … is missing` to stderr and still exits `0`, unlike the missing-templates-dir and missing-`_audience_block.md` paths which exit `1`. Decide-and-document before relying on that exit code.
- `gen_topology.py`'s entity/edge detection stays heuristic by design (it reads at most `MAX_FILE_READ` per file and never follows real imports). The human-refinement step in Phase 1 is mandatory, not optional.

Fixes already landed (do not re-report these as open defects): phase count (`SKILL.md` states its phase range consistently), the five-file vs "three/four documents" drift across `SKILL.md`/`README.md`/`references/`/templates, the scaffolder's overwrite/exit-code contract (now skip-by-default, exit 0), dead code in both scripts, `IGNORE_DIRS`/`_is_ignored` handling of `*.egg-info` plus `.github` plus `.omp`, the snippet-cap conflict (≤ 30 lines everywhere), the undocumented `--max-edges` flag, the `--diff` early-return bug that dropped location-level changes, the `--diff-markdown <PATH>` flag (file output of the diff body), and the inventory table that used to truncate to the top three per kind (now lists all locations so the diff has a stable prev baseline).

Phase 1 (Pre-Mining Assessment, 2026-10-11): the missing `Phase -1` "is this repo worth mining, who is it for, and where to start reading?" gating stage is now a documented part of the workflow with three references (`suitability_signals.md`, `audience_profiling.md`, `reading_path_suggestions.md`), an `assets/templates/assess.md` deliverable, an `assets/templates/_audience_block.md` fragment, two new optional scaffolder flags (`--assess`, `--audience`), and an explicit `## Prerequisites` section in `SKILL.md` declaring `python3 >= 3.8`, `git`, and `rg` as required tools (B2 from the 2026-10-11 audit is now closed).

Phase 2 (Reliability & Operability, 2026-10-11): reliability hardening for the v2 surface — `references/edge_refinement.md` (deep guide for verifying and refining auto-detected edges after Phase 1), a `#### How to refine edges` subsection in `SKILL.md` `### Phase 1`, a new `## Workflow Variants` section in `SKILL.md` enumerating Full / Lite / Progressive modes (no new code; the existing commands cover them), `## Failure Modes to Avoid` expanded from 6 to 12 entries (covering no-git-history, pure-docs, > 10k-file, monorepo, `git log`-failure miscategorization, and `--audience`-skip cases), and a new `scripts/smoke.py` that codifies the AGENTS.md "safe smoke test" plus Phase-5 checks (Mermaid fence balance; scaffolder-placeholder substitution always enforced; Phase-4 placeholders and `<angle-bracket>` slots enforced under `--strict` for publish-ready files; informational `TODO(doc-miner)` count). All additions are stdlib-only and backwards-compatible; the existing v2 behaviour is unchanged when `--check-only` is not used.

Phase 3 (Generalization & Polish, 2026-10-11): generalization and honesty pass for the v3 surface — `gen_topology.py` gains two opt-in flags (`--dry-run` to print detected counts and the would-be output path without writing, and `--summary` to print a 1-screen human summary of the detected inventory) so the agent can preview a topology before committing; `scripts/_env.sh` is added so agents can `source` it to set `REPO_DOC_MINER_HOME` (no code change today, but a foundation for future workflow scripts); the legacy `<angle-bracket>` slots in `assets/templates/topology.md` (which the script never produced) are removed so the file is slot-free out of the box (C11); `references/evidence_checklist.md` opens with a "tool vs. expectation" callout (C10) and the "Python ML" row is de-PINN-ified + the 4 non-ML flavour sections are expanded to 8–12 rows each (B1); the `> TODO(doc-miner): no remaining {{...}} placeholders` reminder is added to the top of `tutorial.md` and `README.md` (C2; `developer_guide.md` and `user_guide.md` already had it); `assets/templates/_flavor_strip.md` is added as a no-op marker documenting how a future `--flavor FLAVOR_NAME` flag should structure template sections (C1/C7; the scaffolder's `--flavor` arg itself is out of scope for Phase 3 and is a documented future task); the repo `README.md` Contents tree and SKILL.md frontmatter version are bumped to v3 to match the v3 line. All additions are backwards-compatible; the existing v2 behaviour is unchanged when no new flag is passed.

Phase 4 (Wiring Up & Real-World Validation, 2026-10-11): closes the last open Phase 3 spec items in a focused way. `scaffold_docs.py` gains the `--flavor FLAVOR_NAME` flag (default `general`) which strips `<!-- flavor: NAME --> ... <!-- /flavor: NAME -->` blocks from the 5 core templates + `assess.md`, wiring up the `_flavor_strip.md` contract that was a no-op marker through Phase 3 (C1/C7); `assets/templates/developer_guide.md` gains one demonstrative `<!-- flavor: backend -->` block so the stripper has a real block to remove (the other 4 templates remain flavor-free); `scripts/smoke.py` gains `--guides-dir PATH` so `--strict` is now meaningful against a real `docs/guides/` directory (Phase 2 re-reviewer R3 closed: the throwaway-only audit was structurally unreachable, so a failable real-dir audit is added); the README first paragraph is polished — the `four questions` promise now matches `assess.md`'s actual content, and the `docs/guides/` hard-code is now described as the default behind `scaffold_docs.py --out PATH`; a real-world validation pass against `tiangolo/fastapi` confirms the skill works end-to-end on a non-trivial external Python library — `gen_topology.py` detects the expected entities + edges, `scaffold_docs.py --assess --audience` materialises 6 files with the audience blockquote on line 1 of `assess.md`, and `smoke.py --strict --guides-dir` exits 0 against the scaffolded output. The `--lang` flag remains formally deferred to a future release per the spec's §9.3 Open Decisions (the N2 en-GB/en-US mix in `_flavor_strip.md` is closed in Phase 5).

Phase 5 (Production Readiness, 2026-10-11): moves the skill from "works in a worktree" to "works for a downstream user". A `Makefile` provides one-command test entry points (`make test` / `make smoke` / `make smoke-strict` / `make clean` / `make help`); a `CHANGELOG.md` documents the four-phase evolution (1.0.0 → 1.4.0) in Keep-a-Changelog format; a new `scripts/check_resources.py` validator confirms that `SKILL.md`'s `## Resources` section lists every file under `assets/templates/`, `references/`, and `scripts/`, surfacing drift as INFO (exit 0; the check is informational, not a build gate). Four small polish items from earlier phases are also closed: N2 (`assets/templates/_flavor_strip.md` is en-US throughout), N3 (`scripts/smoke.py` now exits 2 if the Phase 3 + Phase 4 auxiliary files, `scripts/_env.sh` and `assets/templates/_flavor_strip.md`, are missing), RES-1 (`references/reading_path_suggestions.md` now uses plain single quotes around 'Phase -1' instead of nested escaped backticks), and C5 (the `gen_topology.py --max-entities` cap warning prints only under `--verbose`, matching the `--max-edges` behaviour and the docstring). The `--lang` flag and the `<br/>`-exemption documentation remain deferred to v4+ per the spec's §9.3 Open Decisions.

Phase 6 (Language & Drift Fixes, 2026-10-11): closes the last 2 deferred items from the spec. `scaffold_docs.py` gains the `--lang {bilingual,en,zh}` flag (default `bilingual`) which picks the H1 heading language for the 5 core templates — `--lang en` rewrites the bilingual H1 to English-only (`# Demo Developer Guide`), `--lang zh` rewrites it to Chinese-only (`# Demo 开发者文档`), `--lang bilingual` (default) is byte-identical to the pre-Phase-6 output. H2 sections are intentionally not rewritten (the templates don't carry parallel Chinese H2s; adding them is a v4+ effort). The SKILL.md `## Resources` section now lists every shipped file (closing the 3 disk-only entries that `scripts/check_resources.py` had been reporting since Phase 5: `assets/templates/_flavor_strip.md`, `references/edge_refinement.md`, and `scripts/check_resources.py` itself); `check_resources.py` now reports zero INFO drift. The `<br/>` exemption documentation in `topology.md` §1 and the `references/audience_profiling.md` `_OR_NONE` suffix-doc update (Phase 1 B2-6 follow-up) remain formally deferred per spec §9.3.

Phase 7 (2nd Real-World Validation & v1.4.0 Release, 2026-10-11): closes the optimization plan with a 2nd real-world validation pass and the v1.4.0 release tag. `pallets/flask` is mined end-to-end with the same flags used in the Phase 4 FastAPI run (`--assess --audience contributor`); `gen_topology.py --summary` detects the Flask `src/` package as a `py-package`; `scaffold_docs.py --assess --audience` materialises 6 files; `smoke.py --strict --guides-dir` exits 0 against the scaffolded output. The Flask end-to-end log lives at `.superpowers/sdd/2026-10-11-phase7-release/phase7-flask-validation-log.md` and confirms that the Phase 1-6 changes generalise to a second non-trivial Python library with a different shape (single package, no Rust extension, no async-first design). A new `make validate` target in the `Makefile` runs the full smoke battery + a `--strict --guides-dir` audit against a throwaway; downstream users can extend it to clone their own target repo. `CHANGELOG.md` gains a `Release notes (2026-10-11)` section listing the headline items. `git tag -a v1.4.0` is created pointing at the current HEAD. The optimization plan is closed; future work (e.g. `--lang` H2 translations, `<br/>` exemption docs, `references/audience_profiling.md` `_OR_NONE` follow-up) is tracked in spec §9.3 Open Decisions for v4+.

Persona Coverage (2026-11-26, landed on main while the SDD line was in flight): the template set gains the persona-tail sections — `user_guide.md` §1 one-sentence pitch + non-goals, §18.1 error triage, §19 Glossary, §20 Getting help, §21 Common pitfalls (old §19/§20 → §22/§23); `developer_guide.md` §2 vitality rows, §4.1 entry-point map, §16 Test map, §17 Release & compatibility, §18 Dependency risk, §19 Quality & debt signals; `README.md` hub persona routing; matching `evidence_checklist.md` rows and `doc_outlines.md` sync; plus the Phase 4 mandatory-persona-sections writing rule (spec §8 of docs/superpowers/specs/2026-10-11-repodocminer-optimization-design.md). The workflow-variant tiers (Full/Lite/Progressive) are recorded above in the Phase 2 paragraph; after the merge, `SKILL.md` carries exactly one `## Workflow Variants` section combining both lines' wording.
