# Changelog

All notable changes to `repo-doc-miner` are documented in this file. Versions follow [Semantic Versioning](https://semver.org/).

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
