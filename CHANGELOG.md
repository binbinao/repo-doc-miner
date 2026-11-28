# Changelog

All notable changes to `repo-doc-miner` are documented in this file. Versions follow [Semantic Versioning](https://semver.org/).

## [3.0.0] — 2026-11-28

Aligns this changelog with the `SKILL.md` frontmatter version (`3.0.0` since the v3 line of 2026-10-11; the `[1.x]` entries below were the SDD optimization line's internal track, and from here on the two counters are one). This entry records the work that landed on `main` while the SDD line was in flight, plus the merge (PR #3) that brought the two lines together.

### Added

- **Persona coverage** (spec §8, PR #1): novice- and evaluator-facing sections across the template set.
  - `assets/templates/user_guide.md` 20 → 23 sections: §1 one-sentence pitch + non-goals, §18.1 error-triage table, §19 Glossary, §20 Getting help, §21 Common pitfalls (old §19/§20 → §22/§23; cross-references updated).
  - `assets/templates/developer_guide.md` 15 → 19 sections: §2 repo-vitality rows, §4.1 entry-point map, §16 Test map, §17 Release & compatibility, §18 Dependency risk, §19 Quality & debt signals.
  - `assets/templates/README.md` persona routing table ("You are … → Start with …").
  - `references/evidence_checklist.md` matching evidence rows (tests layout, CHANGELOG, git vitality, TODO/FIXME hotspots, SUPPORT/SECURITY, entry-point files) and Phase 2 scratch-note facts.
  - `references/doc_outlines.md` synced to the 23-/19-section schemas.
  - `SKILL.md` Phase 4 "persona sections are mandatory content" rule.
- **Workflow Variants** (PR #2, pulled forward from spec §6.1 C12 ahead of Phase 2): Full (default) / Lite (topology only) / Progressive (topology → decide → continue); Phase 0 states the mode, Phase 6 reports it.
- `CLAUDE.md` — repo instructions for Claude Code instances working on this package.

### Changed

- **Merged the SDD optimization line into main (PR #3):** `SKILL.md` now carries exactly one `## Workflow Variants` section — the SDD line added it in [1.3.0] and main pulled it forward in parallel; the resolved section keeps the SDD line's Full/Lite/Progressive + when-to-skip structure and folds in the pull-forward's substance sizing, scaffolder rules, and Phase 0/6 reporting. `AGENTS.md` Key Directories unioned to list `scripts/smoke.py`, `scripts/check_resources.py`, `scripts/_env.sh`, `references/edge_refinement.md`, and `assets/templates/_flavor_strip.md`; the landed ledger records the SDD Phase 1–7 paragraphs plus a Persona Coverage (2026-11-26) entry.
- Spec §9 subsections renumbered `8.1/8.2/8.3` → `9.1/9.2/9.3` (collateral of the §8 Persona Coverage insertion); 27 stale `§8.3 Open Decisions` references updated to `§9.3` across `AGENTS.md` and the phase 3–7 plans.

### Fixed

- `assets/templates/user_guide.md` §23 (Further reading) now points support questions at §20 (Getting help) instead of duplicating the channel list.

**Validation:** `scripts/smoke.py` exits 0; `gen_topology.py` double-run byte-identical; `scaffold_docs.py` skip-by-default confirmed on a throwaway repo.

## [1.4.0] — 2026-10-11

### Added
- `scaffold_docs.py --flavor FLAVOR_NAME` flag (default `general`) which strips `<!-- flavor: NAME --> ... <!-- /flavor: NAME -->` blocks from the 5 core templates + `assess.md`, wiring up the `_flavor_strip.md` contract that was a no-op marker through v1.3.0. (Spec C1/C7.)
- `assets/templates/developer_guide.md` §6 now contains a demonstrative `<!-- flavor: backend -->` block so the stripper has a real block to remove.
- `scripts/smoke.py --guides-dir PATH` flag — the `--strict` audit is now meaningful against a real `docs/guides/` directory (previously structurally unreachable on the throwaway scaffold). Closes Phase 2 R3.
- `Makefile` — top-level `make test` / `make smoke` / `make smoke-strict` / `make clean` / `make help` targets for downstream users.
- `CHANGELOG.md` — this file.
- `scripts/check_resources.py` — stdlib-only validator confirming the `## Resources` section in `SKILL.md` lists every file under `assets/templates/`, `references/`, and `scripts/`.

### Changed
- `references/suitability_signals.md` removed the legacy `.github/CODEOWNERS`-based archived-detection (the script doesn't read CODEOWNERS).
- `assets/templates/topology.md` removed the 17 legacy `<angle-bracket>` slots that the script never produced (the 5 core templates now ship slot-free).
- `references/evidence_checklist.md` opens with a "Tool vs. expectation" callout (C10) and the "Python ML" row is de-PINN-ified.
- `SKILL.md` and `README.md` frontmatter / title bumped from v2 to v3; `README.md` Contents tree now lists all 7 templates, 8 references, 4 scripts.

### Fixed
- `gen_topology.py`: the `--max-entities` cap warning now prints only under `--verbose` (the `--max-edges` cap was always correct; the two now behave consistently). C5 polish.
- `references/reading_path_suggestions.md`: the `\\`Phase -1\\` escaped-backtick pattern is now plain inline code (CommonMark backslash escapes do not apply inside code spans). RES-1 closure.

#### Release notes (2026-10-11)

The v1.4.0 release closes the spec's three original phases and adds two follow-up items:

- **Spec items closed:** Phase -1 Pre-Mining Assessment (`--assess`, `--audience`); reliability (codified `smoke.py`, Workflow Variants, 12 failure modes); generalisation (`--dry-run`/`--summary`, de-PINN'd evidence checklist, 17 legacy `<angle-bracket>` slots removed from `topology.md`).
- **Follow-ups wired in:** `--flavor {general,pinn,cli,lib,monorepo}` scaffolder flag; `--guides-dir PATH` smoke flag (closes Phase 2 R3); `--lang {bilingual,en,zh}` flag (closes spec §7.2).
- **Production readiness:** `Makefile` (5 targets); `CHANGELOG.md` (this file); `scripts/check_resources.py` (SKILL.md Resources drift detector).
- **Validation:** end-to-end runs against `tiangolo/fastapi` and `pallets/flask` both pass (`make validate` exits 0; `smoke.py --strict --guides-dir` exits 0 against both scaffolded outputs).
- **Shipped under MIT, no third-party dependencies.** The skill is a `git clone` + `pip install` (or no install — pure stdlib) away from working for any CodeBuddy / Claude Code user.

## [1.3.0] — 2026-10-11

### Added
- Phase -1 Pre-Mining Assessment stage: `references/suitability_signals.md`, `references/audience_profiling.md`, `references/reading_path_suggestions.md`, `assets/templates/assess.md`, `assets/templates/_audience_block.md`.
- `scaffold_docs.py --assess` and `--audience NAME` flags.
- `SKILL.md` `### Phase -1` section + `## Prerequisites` table.
- `## Workflow Variants` section in `SKILL.md` (Full / Lite / Progressive modes).
- `references/edge_refinement.md` (Phase 2).
- `scripts/smoke.py` (Phase 2).
- `scripts/_env.sh` (Phase 3).
- `assets/templates/_flavor_strip.md` (Phase 3 marker file).
- `gen_topology.py --dry-run` and `--summary` flags (Phase 3).
- Failure-Modes list grown from 6 to 12 entries (Phase 2).

### Changed
- `SKILL.md` phase numbering: now `Phase -1 → Phase 0–6` (the additive `Phase -1` prefix keeps `Phase 0–6` references stable).

## [1.2.0] — 2026-10-11

### Added
- First release of the v2 topology-first workflow.
- `scripts/gen_topology.py` (entity + edge detection, Mermaid rendering).
- `scripts/scaffold_docs.py` (5-template materializer with `{{PROJECT_NAME}}` substitution).
- 5 core templates (`topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`, `README.md`).
- 4 references (`topology_method.md`, `doc_outlines.md`, `evidence_checklist.md`, `writing_style.md`).
- `SKILL.md` seven-phase workflow (Phase 0–6).
- AGENTS.md "safe smoke test" bash block.

## [1.1.0] — 2026-10-11

### Added
- v1.0 / v1.1 changelog entries were retroactive; the original v1 (DeepXDE-shaped) shipped with one batch of templates and a different workflow.

## [1.0.0] — earlier

Initial release. v1 (pre-topology) was a flat file scanner that produced three documents. v2 (this repo's reason for being) is the topology-first rewrite.
