# repo-doc-miner — Optimization Plan Design

**Date:** 2026-10-11
**Status:** Brainstormed → User-approved → Drafting
**Audience:** Maintainers of `repo-doc-miner` v2.0.0
**Author:** Brainstorming session (user + assistant)

---

## 1. Goal & Motivation

`repo-doc-miner` v2 already does two things well:

1. **Topology-first mining** — `gen_topology.py` collapses O(N) files into an O(entity-type) structural map.
2. **Edge-ordered deep-dive** — the skill reads along dependency edges, not flat.

But the user (and any future user) still has three unanswered questions before the first `python scripts/gen_topology.py` run:

- **Is this repo even worth mining?** — A repo of 3 stub files, an archived fork, or a vendor-only monorepo should be filtered out before we burn tokens.
- **Who is this doc set for?** — The five files currently go to "everyone" with only a 4-line audience table in `assets/templates/README.md`.
- **Where do I start reading?** — The same file has 3 lines of "reading order suggestions" but no analytical basis for them.

These gaps fall under one heading: **pre-mining strategy**. The skill today jumps from "trigger detected" straight to Phase 0 scope → Phase 1 topology with no gating, no audience analysis, no entry-point reasoning.

**This spec adds an explicit pre-mining assessment stage, a persona-coverage pass, and a handful of supporting improvements across four incremental phases.**

## 3. Non-Goals

This design does **not**:

- Change the deliverable count (still 5 Markdown files in `docs/guides/`).
- Add third-party dependencies to `scripts/` (stdlib-only constraint preserved).
- Restructure the existing Phase 1–6 numbering; new work slots in as **Phase -1** ("Pre-Mining Assessment") which runs *before* Phase 0.
- Introduce a templating engine; placeholders remain `{{UPPER_SNAKE_CASE}}` + `<angle-bracket>` where used.
- Replace any existing template section with a flavor-agnostic rewrite in the same commit; flavor-agnostic variants are *additive* (new sections / new rows in checklist), per AGENTS.md "Known inconsistencies to not propagate".
- Add new scripts, flags, or deliverable files in Phase 4 (persona facts are agent-gathered during Phase 2, not miner-computed).

## 4. Approach Overview

Four incremental phases, each shippable independently. Each phase lands one coherent capability and updates `AGENTS.md`'s "Fixes already landed" list so it is visible in the next audit.

```
Phase 1 · Pre-Mining Assessment (P0)       ← user-facing primary ask
Phase 2 · Reliability & Operability (P1)    ← deps, failure modes, smoke test
Phase 3 · Generalization & Polish (P2+P3)   ← template dedup, lang flag, paths
Phase 4 · Persona Coverage (P4)              ← novice onboarding + evaluator decision sections
```

Each phase is its own brainstorm → spec → plan → implement cycle, but this document pre-records intent.

---

## 5. Phase 1 — Pre-Mining Assessment (P0)

### 5.1 Capability

Add a `Phase -1` step that runs **before** Phase 0 and produces a single document — `assess.md` (placed alongside the five generated files in `docs/guides/`) — answering four questions:

1. **Is this repo worth mining?** — *Suitability* score 0–5 across ~6 signals (size, vitality, license, docs quality, test presence, entry-point clarity). Hard vetoes (no `LICENSE`, archived repo) downgrade to "skip — and why".
2. **Who should read the docs?** — *Audience profile* chosen from a small fixed set (see §5.3).
3. **Where should each audience start?** — *Reading paths* (one suggested entry point + order per audience).
4. **What concrete next step should the user take?** — *Reading suggestions* (1–3 actions).

The Phase -1 output is a standalone `assess.md` file in the same `docs/guides/` directory; the `README.md` (hub) references it from its file table when present (only when `--assess` was used). `topology.md` does **not** carry a `## 0. Pre-Mining Assessment` section — the assessment is a peer file, not front-matter.

### 5.2 New files

| Path | Purpose |
|---|---|
| `references/audience_profiling.md` | Defines the audience taxonomy + how to detect which audience is dominant for a given repo (signals: README positioning, audience phrases, code style, presence of `examples/` vs `tests/` vs `docs/`). |
| `references/suitability_signals.md` | Enumerates the ~6 hard signals, scoring rubric (0–5), hard vetoes, and the "skip — and why" message template. |
| `references/reading_path_suggestions.md` | Maps audience → recommended entry point + order across the 4 non-hub generated docs (`topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`). |
| `assets/templates/assess.md` | The Phase -1 deliverable template; agent fills it during execution. |
| `assets/templates/_audience_block.md` | (Reusable fragment) the `> Audience: …` block embedded at the head of `topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`. |

### 5.3 Audience taxonomy (initial draft, refine in implementation)

Six buckets; chosen because they map cleanly to doc-set sections that already exist:

| Audience | Best entry file | Why |
|---|---|---|
| **First-time end user** | `user_guide.md` §1–§11 + §18–§19 | Capability list + install + minimal runnable + FAQ |
| **Applied engineer (specific task)** | `tutorial.md` matching chapter | Pattern-matching |
| **Contributor / framework developer** | `developer_guide.md` end-to-end | Architecture + extension SOPs |
| **Auditor / reviewer** (security, licensing, code quality) | `topology.md` §1–§3 + `developer_guide.md` §15 | Structure + contribution SOPs |
| **Learner** (any level, no specific use case) | `tutorial.md` Ch. 1 → 10 | Progressive curriculum |
| **Tooling / automation integrator** | `topology.md` + `developer_guide.md` §4–§5 | Module + namespace table |

Detected by `references/audience_profiling.md` signals (README's "Who this is for" line if present; presence of `examples/` / `docs/` / `CONTRIBUTING.md`; first-paragraph positioning of README; package classifiers in `pyproject.toml` / `package.json`; etc.).

### 5.4 Suitability scoring (initial draft)

Six signals, each scored 0–2 (max 12 → rescaled to 0–5):

| Signal | Source | 0 = bad | 1 = ok | 2 = good |
|---|---|---|---|---|
| **Size** | file count in repo (excluding `.git`, vendor) | < 5 | 5–500 | > 500 |
| **Vitality** | last commit date from `git log -1 --format=%ct` | > 2 years | 6 mo–2 yrs | < 6 mo |
| **License** | presence + SPDX-recognised | absent | permissive copyleft only | clear permissive (MIT/Apache/BSD) |
| **Entry-point clarity** | existence of `README.md` first paragraph + a recognizable manifest | neither | one | both |
| **Documentation quality** | existing `docs/` size + completeness | none | partial | substantial |
| **Test/example presence** | `tests/` or `examples/` directory | neither | one | both |

**Hard vetoes** (force score → 0 + emit skip reason):

- Repo is **archived** — best-effort detection: presence of `ARCHIVED.md`, or a README banner stating the project is archived/no longer maintained (e.g. `[![No Maintenance Intended](...)](...)`, the strings `no longer maintained`, `archived`, or `sunset`).
- Repo has **no LICENSE** AND README has **no usage hint** (defined as: any of the strings `Install`, `Usage`, `Quickstart`, `pip install`, `npm install`, `cargo install`, `go install`, `go get`, or a fenced `bash` block within the first 200 lines).
- Repo is a **vendor fork** (no top-level source dir; only `node_modules/`, `dist/`, etc.).
- Repo has **< 3 readable source files** after `.gitignore` style filtering.

**Not-a-git fallback.** If `git log -1 --format=%ct` fails (target is not a Git repo, or has no commits), score Vitality = 0 and record the reason in `assess.md` §1. The other five signals are computed from the on-disk tree and remain valid.

The agent computes signals manually in Phase -1 (it has `git` available via shell, file listing via tools). No new script in Phase 1 — keeping scope minimal.

### 5.5 Reading paths

`references/reading_path_suggestions.md` defines a deterministic mapping from (audience, suitability-band) to (entry file, jump list). Initial matrix:

| Audience \ Suitability | High (4–5) | Mid (2–3) | Low (0–1) |
|---|---|---|---|
| First-time end user | `user_guide.md` §1–§11 + §18–§19 + `tutorial.md` Ch. 1–4 | `user_guide.md` §1–§11 + §19 only | Skip — explain in assess.md |
| Applied engineer | `tutorial.md` Ch. matching task | Same, narrower (just relevant chapter) | Skip |
| Contributor | `developer_guide.md` + `topology.md` | Same | Skip |
| Auditor | `topology.md` + `developer_guide.md` §15 | `topology.md` only | Skip |
| Learner | `tutorial.md` Ch. 1–10 | `tutorial.md` Ch. 1–4 then decide | Skip |
| Integrator | `topology.md` + `developer_guide.md` §4–§5 | `topology.md` only | Skip |

The mapping is a plain table — no logic, agent reads the row.

### 5.6 Script changes

| File | Change |
|---|---|
| `scripts/gen_topology.py` | **No change in Phase 1.** The script's job is topology, not assessment. (C5 is in Phase 3.) |
| `scripts/scaffold_docs.py` | New flags: `--assess` (**default off**; when set, writes `assess.md` from new template) and `--audience <name>` (**default off**; when set, prefixes the 4 non-hub docs — `topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md` — with `_audience_block.md`. `README.md` is the hub and is **not** prefixed; the block's own text references it. When `--assess` is also passed, `assess.md` is also prefixed with the audience block; this is consistent with `assess.md` being the first deliverable of the Phase -1 flow.) Both flags off by default so existing smoke tests stay green. When `--assess` is used without `--audience`, only `assess.md` is added; the 5 templates are not modified. When `--audience` is used without `--assess`, the 4 non-hub docs are prefixed and `assess.md` is not written. |
| `assets/templates/_audience_block.md` | New fragment: `<!-- audience: {{AUDIENCE}} -->` followed by a 2-line audience blockquote (`> **Audience:** {{AUDIENCE}} — …`). Embedded verbatim at the top of each generated doc when `--audience` is set. |

The audience block is rendered as an HTML comment + a visible blockquote so both machine readers (to skip it) and humans (to read it) work. The placeholder convention stays `{{...}}` and the agent fills it during Phase 4.

### 5.7 SKILL.md diff summary

- **Phase numbering decision (lock this in):** keep the additive `Phase -1` prefix to avoid breaking all internal references in templates / references / README. Existing `Phase 0–6` numbers stay untouched. The new section in `SKILL.md` is titled `Phase -1 · Pre-Mining Assessment` and listed before `Phase 0`.
- New `Do NOT trigger for:` entries (under `## When to Use`) informed by the suitability vetoes.
- New `## Prerequisites` section (B2 from audit, **also lands in Phase 1** because the assessment itself uses `git log`).

### 5.8 Test plan

1. Smoke-test the scaffolder with `--assess --audience contributor` on a throwaway repo: assert `assess.md` and audience-block-comments are written; assert the 5 files do not have any `<angle-bracket>` markers that aren't in `assess.md`.
2. Verify the `Phase -1` text in `SKILL.md` reads cleanly when rendered.
3. Manual review: pick one of the existing throwaway smoke tests, generate `assess.md` by hand, and check the rubric agrees with a human reader.

---

## 6. Phase 2 — Reliability & Operability (P1)

### 6.1 Capability

Three reliability improvements that ship together:

- **B2: Prerequisites declared.** `SKILL.md` gains an explicit "Prerequisites" section listing `python3 >= 3.8`, `git`, and **`rg` (ripgrep)** with rationale ("Phase 5 sweep").
- **B3: Edge-refinement guide.** Phase 1 in `SKILL.md` is extended with a "How to refine edges" subsection: which 2–3 edges matter, how to verify by reading the manifest, common false positives, common false negatives. A new `references/edge_refinement.md` captures the deep guide.
- **C3: Failure modes expand.** "Failure Modes to Avoid" grows from 6 to ~12 entries (see audit B+C lists).
- **C12: Lite mode & progressive mode documented in SKILL.md as workflow branches**, no new code. New section `## Workflow Variants` enumerates "Full mode", "Lite mode (topology only)", "Progressive mode (topology → decide → continue)". **— landed 2026-11-26, pulled forward ahead of Phase 2 (see §0 revision history).**
- **C4: `scripts/smoke.py`** — A new stdlib-only script that runs:
  - Safe smoke test (the bash block from AGENTS.md, codified).
  - Topology-only smoke (verify `gen_topology.py` produces a non-empty `topology.md`).
  - Scaffolder smoke (verify all 5 templates materialize with `{{PROJECT_NAME}}` substituted).
  - Phase-5 checks on a generated output: Mermaid fences closed, no broken `{{...}}` placeholders, no broken relative links (best-effort), `TODO(doc-miner)` count printed.
  - Returns 0 on full pass, non-zero on any check failure.

### 6.2 New files

| Path | Purpose |
|---|---|
| `references/edge_refinement.md` | How to verify & refine auto-detected edges after `Phase 1`. |
| `scripts/smoke.py` | The codified smoke test + Phase-5 validator. |

### 6.3 SKILL.md diff summary

- Add `## Prerequisites` after the frontmatter table.
- Add `## Workflow Variants` after `## When to Use`. *(landed 2026-11-26, pulled forward ahead of Phase 2)*
- Expand `## Failure Modes to Avoid` from 6 to ~12 items.
- Extend `### Phase 1 · Topology Generation` with a "How to refine edges" subsection referencing `references/edge_refinement.md`.

### 6.4 Test plan

- `python scripts/smoke.py` exits 0 on the skill's own repo (after running `gen_topology.py` once to populate `docs/guides/topology.md`).
- `python scripts/smoke.py --check-only` exits 0 without writing anything.
- Documentation: rendered `SKILL.md` shows the new sections without breaking the existing TOC.

---

## 7. Phase 3 — Generalization & Polish (P2 + P3)

### 7.1 Capability

- **B1: Evidence checklist flavor-agnostic.** `references/evidence_checklist.md` adds four flavor sections (Python CLI, Node lib, Rust crate, Go module) with **balanced length** (8–12 rows each, currently 4–6). The "Python ML" row becomes flavor-agnostic by replacing PINN-specific lines (e.g. `<pkg>/icbc/` → generic constraint subdir).
- **C1, C7: Templates de-PINN + language flag.** Each of the 5 templates gains (a) optional PINN sections marked `<!-- flavor: pinn -->` that the scaffolder strips when a non-PINN flag is passed; (b) a top-level language selector (`--lang en|zh|bilingual`) that picks the heading string. New `assets/templates/_flavor_strip.md` is a no-op marker file the scaffolder recognizes.
- **C2: Placeholder-sweep reminder** added to the top of every template (`> TODO(doc-miner): no remaining {{...}} placeholders before publishing.`). Currently only in `developer_guide.md` / `user_guide.md`.
- **C5: `--dry-run` / `--summary` on `gen_topology.py`.** Two new flags: `--dry-run` prints detected entity/edge counts and would-be output path, no file write; `--summary` writes a 1-screen human summary to stdout (entity kinds, edge count, largest entity by size, top-3 outbound edges).
- **C8: Skill home variable.** `SKILL.md` & templates reference `${REPO_DOC_MINER_HOME}` (with a fallback note) instead of bare `scripts/...` paths; a `scripts/_env.sh` exports it.
- **C10: Tool-vs-expectation honesty.** `references/evidence_checklist.md` opens with a "What this checklist expects vs. what `gen_topology.py` can deliver" callout.
- **C11: `<angle-bracket>` slot fate.** Decide between (a) deleting them from `topology.md` template (since the script never produces them), or (b) keeping them and explicitly documenting "manual-write only" in the template. **Default choice (to confirm in Phase 3 brainstorm): delete**, since the script-driven flow is the only documented one.
- **C13: README.md refresh.** First paragraph of the repo `README.md` mentions the new "pre-mining assessment" capability and links to `references/suitability_signals.md`.

### 7.2 New flags summary

| Flag | Default | Effect |
|---|---|---|
| `scaffold_docs.py --lang {en,zh,bilingual}` | `bilingual` | Pick template language |
| `scaffold_docs.py --flavor {pinn,general,cli,lib,monorepo}` | `general` | Strip flavor-specific sections |
| `gen_topology.py --dry-run` | off | Print, no write |
| `gen_topology.py --summary` | off | Stdout 1-screen summary |

### 7.3 Test plan

- Re-run `smoke.py` after each flavor & language combination.
- Re-run the AGENTS.md "safe smoke test" verbatim and confirm the output is byte-identical.
- One end-to-end run on the `repo-doc-miner` repo itself using `--audience contributor --lang en` and visually confirm the audience block.

---

## 8. Phase 4 — Persona Coverage (P4)

### 8.1 Origin: persona gap analysis (2026-11-26)

A persona review of the v2 deliverables found the five-file set serves the "middle" (applied engineers + potential contributors) well, while both tails are thin: the novice's **first five minutes** and the professional's **adoption decision**. Phase 4 closes those gaps with additive template sections + evidence rows. Gap tables (need → coverage before Phase 4 → where Phase 4 addresses it):

**Novice (first-time visitor)**

| Need | Before Phase 4 | Addressed in |
| --- | --- | --- |
| Plain-language elevator pitch ("what is this, one sentence") | missing — §1 has capability bullets only | `user_guide.md` §1 pitch block |
| "Is this for me?" fit check | missing — Phase -1 answers "who reads the docs", not "does this fit my problem" | README hub persona routing + Phase 1 amendment (§8.6) |
| Can/cannot-do list incl. non-goals | capability bullets only, no Non-goals anywhere | `user_guide.md` §1 non-goals block |
| Error triage (error → plain meaning → fix) | 2-row symptom→suggestion table | `user_guide.md` §18.1 |
| Glossary (jargon → plain language → code symbol) | missing | `user_guide.md` §19 |
| Getting help (channels + how to ask a good question) | `{{DOCS_URL_OR_TODO}}` placeholder only | `user_guide.md` §20 |
| Trust signals (vitality, release cadence) | license only in §2 | `developer_guide.md` §2 new rows |
| Pitfalls & misconceptions ("don't panic when you see X") | missing | `user_guide.md` §21 |

**Professional (evaluator / integrator / contributor)**

| Need | Before Phase 4 | Addressed in |
| --- | --- | --- |
| Entry-point map (where execution starts, per surface) | implied in architecture narrative only | `developer_guide.md` §4.1 |
| Test map (layout, run-one-test command, CI gates) | missing | `developer_guide.md` §16 |
| Release & compatibility policy | version source file only | `developer_guide.md` §17 |
| Dependency risk surface (version, license, deprecation) | plain dependency list | `developer_guide.md` §18 |
| Quality & debt signals (TODO/FIXME hotspots, bus factor) | missing | `developer_guide.md` §19 |
| Exhaustive config matrix | 2-knob sample | `user_guide.md` §4 exhaustive rule |

Out of scope for Phase 4 (owned elsewhere or future work): runtime sequence diagrams and git-history change-coupling (future candidates); de-PINN flavor stripping (Phase 3); suitability scoring (Phase -1).

### 8.2 Template changes (additive only)

**`assets/templates/user_guide.md`** — 20 → 23 sections; §1–§18 numbering untouched (Phase -1 references to `user_guide.md` §1–§11 stay valid):

- §1: add a one-sentence plain-language pitch line + a non-goals block after the capability bullets.
- §4: add the exhaustive-knobs rule (enumerate every user-facing knob, not a sample).
- §18: add subsection §18.1 "Error triage" — 3-column table: error → what it actually means → fix.
- NEW §19 Glossary — table: term → plain-language meaning → defining code symbol.
- NEW §20 Getting help — issue tracker, discussions/community, how-to-ask guidance.
- NEW §21 Common pitfalls & misconceptions — table: misconception → what is actually going on.
- Old §19 → §22 (Minimal runnable templates; subsections renumber 19.x → 22.x), old §20 → §23 (Further reading; gains a pointer to §20).

**`assets/templates/developer_guide.md`** — 15 → 19 sections; §1–§15 numbering untouched (Phase -1 references to §4–§5, §15, §1–§14 stay valid):

- §2: add rows — repo homepage, latest release/tag, last-commit date (vitality signal).
- §4: add subsection §4.1 "Entry-point map" — table: surface (CLI / API / library import / plugin hook) → entry point (`path::Symbol`) → what it does.
- NEW §16 Test map — layout, run-all + run-one commands, coverage, CI gates.
- NEW §17 Release & compatibility policy — versioning scheme, changelog path, breaking-change policy, supported-version matrix.
- NEW §18 Dependency risk surface — per-dependency table: version constraint, license, risk notes.
- NEW §19 Quality & debt signals — TODO/FIXME hotspots, dead code/deprecations, bus factor (`git shortlog -sn`).

**`assets/templates/README.md`** — add a persona-routing table ("You are… → start with…") before the existing reading-order list; the existing list stays.

### 8.3 references changes

- `references/evidence_checklist.md` — Universal section adds rows: tests-layout, CI gates detail (extend the existing workflow row), changelog/releases, git vitality (last commit, tag cadence), TODO/FIXME density scan (`rg -c`), support channels (`SUPPORT.md` / issue templates / `SECURITY.md`), entry-point scan (`__main__.py` / `cli.py` / `app.py` / `cmd/`). "Output of Phase 2" scratch note gains: test-map facts, release facts, quality signals, support channels.
- `references/doc_outlines.md` — update `developer_guide.md` (15 → 19 sections) and `user_guide.md` (20 → 23 sections) outlines with the new entries; add grounding rules: glossary terms cite their defining symbol; the test map must contain a run-one command that actually exists in the repo.

### 8.4 SKILL.md changes

- Resources: template descriptions updated to the new section counts, mentioning the persona sections.
- Phase 3 verification bullets: user guide must cover pitch/non-goals, glossary, error triage, getting help, pitfalls; developer guide must cover the entry-point map and the evaluator sections (test map, release policy, dependency risk, quality signals).
- Phase 4 writing rules: add a rule that persona sections are mandatory content, not optional flavor — if the repo genuinely lacks a fact, keep the heading and mark it `> TODO(doc-miner): n/a — <reason>`.

### 8.5 Constraints

- No script changes: `gen_topology.py` and `scaffold_docs.py` untouched. Persona facts are agent-gathered (rg/git) during Phase 2, not miner-computed.
- No new files: templates stay five, references stay four; only existing files gain sections/rows.
- No existing section heading may be renumbered except `user_guide.md` old §19/§20 (verified by grep 2026-11-26: no external references to those numbers).
- New placeholders follow existing conventions: `{{UPPER_SNAKE_CASE}}`, with `_OR_TODO` suffix for facts that may legitimately not exist.
- All existing PINN-flavored sections stay untouched (Phase 3 owns de-flavoring).

### 8.6 Phase 1 amendment (fold into the Phase 1 plan before executing it)

`assess.md` §4 reading suggestions gain a fit-check line: for the dominant audience, one "fits / does not fit" sentence ("fits if you need X; look elsewhere for Y"). This is the user-side complement to the audience profile. The README persona routing (§8.2) is the interim mechanism until Phase 1 lands.

### 8.7 Test plan

1. Throwaway-repo scaffolder smoke: all five files materialize; new sections present (grep for `## 19. Glossary`, `## 16. Test map`, `### 4.1 Entry-point map`); no `{{PROJECT_NAME}}` remains after substitution.
2. AGENTS.md gate 4 (template contract): `TEMPLATE_FILES` still resolves five names; placeholder set unchanged in kind.
3. Cross-file consistency: `doc_outlines.md` numbers match templates; `SKILL.md` section counts updated.
4. `AGENTS.md` "Fixes already landed" entry appended in the same commit.

---

## 9. Cross-Phase Concerns

### 9.1 Backwards Compatibility

- All new `scaffold_docs.py` and `gen_topology.py` flags default to current behavior. Existing smoke tests stay green.
- Existing template `{{PROJECT_NAME}}` substitution unchanged.
- The Phase -1 output is a standalone `assess.md` (a new template), **not** a `## 0.` section prepended to `topology.md`. The hub README carries the conditional reference; `topology.md` is unchanged.

### 9.2 Documentation Discipline

- Every new template file lands with the same `> TODO(doc-miner): remove any remaining {{...}} placeholders before publishing.` reminder (C2).
- Every new references file lands with at least one concrete example (writing_style.md rule).
- `AGENTS.md` "Fixes already landed" list updated in the same commit as each phase lands.

### 9.3 Open Decisions

| Decision | Owner | Where to decide |
|---|---|---|
| `<angle-bracket>` slot fate (delete vs. keep) | user | Phase 3 brainstorm |
| Default audience when none detectable | user | Phase 1 implementation |
| Hard veto "archived repo" detection mechanism | user | Phase 1 implementation (manual vs. web fetch) |
| Should `Phase -1` be a real Phase or sub-step of Phase 0? | user | Phase 1 implementation |

---

## 10. Implementation Plan

This spec hands off to the **writing-plans** skill (next step) which will produce a per-phase implementation plan. Rough sequencing:

1. Phase 1 — Brainstorm spec detail → plan → implement (~6 commits)
2. Phase 2 — Plan → implement (~3 commits)
3. Phase 3 — Plan → implement (~8 commits)
4. Phase 4 — Plan → implement (~2 commits)

Each phase ends with a smoke test, a docs update (CHANGELOG-style entry in AGENTS.md "Fixes already landed"), and a handover line in the spec's `## 0. Revision history`.

---

## 0. Revision history

| Date | Author | Change |
|---|---|---|
| 2026-10-11 | brainstorm session | Initial draft, 3-phase plan, user approved |
| 2026-11-26 | persona review session | Added Phase 4 — Persona Coverage (§8); old §8/§9 renumbered to §9/§10; user approved |
| 2026-11-26 | persona review session | Workflow Variants (Full/Lite/Progressive, §6.1 C12) pulled forward and landed ahead of Phase 2 |
| 2026-11-28 | post-merge cleanup | SDD line merged into main (PR #3). §9 subsections renumbered 8.1/8.2/8.3 → 9.1/9.2/9.3 (collateral of the §8 Persona Coverage insertion); 27 stale `§8.3 Open Decisions` references updated to `§9.3`; `CHANGELOG.md` gains a `[3.0.0]` entry aligning it with the `SKILL.md` frontmatter version |