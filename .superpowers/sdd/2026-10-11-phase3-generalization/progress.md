# SDD ledger — plan: docs/superpowers/plans/2026-10-11-phase3-generalization.md

## Worktree
- Path: `.worktrees/phase1-pre-mining/`
- Branch: `phase1-pre-mining-assessment` (Phase 3 is additive on the same branch)
- Base: `6e06028` (Phase 2 ledger final-state commit)

## Batching strategy

Phase 3 has 9 file-touching tasks (Tasks 1-9) plus a controller smoke (Task 10). Tasks 6 (templates) is small enough to fold into Task 1's batch; tasks 4 + 5 both touch `evidence_checklist.md` and can be folded.

- **Batch 1** (Tasks 1, 4, 5): code change + 2 evidence_checklist.md prose changes
- **Batch 2** (Tasks 2, 3, 6, 7, 8): 4 new template/script files + 1 README refresh + 1 topology.md slot deletion
- **Batch 3** (Task 9): AGENTS.md bookkeeping
- **Task 10**: E2E smoke (controller-only)

Total dispatches: 2 implementers + 2 reviewers + 1 controller = 5 subagent runs.

## Preflight review summary

| Cross-task interface | Producer | Consumer | Conflict? |
|---|---|---|---|
| T1 → T10 | gen_topology.py --dry-run / --summary flags | smoke battery + manual | None |
| T2 → T10 | scripts/_env.sh | smoke (chmod check) | None |
| T3 → T4 (assess) | topology.md slot deletion | C2 reminder + Phase 2 smoke | None (topology is exempt from C2) |
| T4 → T5 | tool-vs-expectation callout | B1 flavor balancing | None (additive in same file) |
| T5 → T6 | evidence_checklist.md de-PINN | T6 C2 reminder (different file) | None |
| T6 → T10 | 4 templates with sweep reminder | smoke + rendering | None |
| T7 → T10 | _flavor_strip.md | smoke (existence) | None |
| T8 → T10 | README.md refresh | smoke (no regression) | None |
| T9 → T10 | AGENTS.md bookkeeping | git status clean | None |

**Self-consistency:**
- 9 file changes (2 new files, 7 modifications); 0 deletions except topology.md slot removal.
- No new dependencies; no third-party imports.
- All new SKILL.md-affecting changes are prose-only; SKILL.md itself is not touched in Phase 3.

**Rulings: none.** The plan is internally consistent. Pre-flight proceeds clean.

---

## Phase 3 Batch 1 implementer (MarvellousViper)
- Status: DONE with 4 documented deviations.
- Commits: `5f1bea2` (T1 --dry-run/--summary), `bffb341` (T4 C10 callout), `ec34a1a` (T5 B1 de-PINN).

## Phase 3 Batch 1 reviewer (HissingAmphibian)
- Verdict: **Needs fixes** — 1 Important + 2 Minor + 2 Nits.
- I1: callout claims `pom.xml` detected; actually only the 5 listed manifests.
- M1: "and their first-level files" overstates inventory.
- M2: docstring `--dry-run | --summary` implies mutual exclusion.
- N1/N2: minor doc quality.

## Phase 3 Batch 1 fix round (controller)
- Commit: `d136eac` (I1 + M1 + M2 closed; N1 + N2 deferred).

## Phase 3 Batch 2 implementer (BroadBison)
- Status: DONE with 4 plan-defect fixes.
- Commits: `0bba6c7` (T2 _env.sh), `e7b7580` (T3 topology slots), `91b7a96` (T6 C2 reminder), `eed195f` (T7 _flavor_strip.md), `722da98` (T8 README refresh).

## Phase 3 Batch 2 reviewer (NeatEagle)
- Verdict: **Needs fixes** — 2 Important + 3 Minor + 3 Nice-to-haves.
- I1: SKILL.md doesn't reference _env.sh.
- I2: _flavor_strip.md contradicts itself + uses uppercase slots.
- M1: AGENTS.md + doc_outlines.md still claim angle-bracket slots allowed in topology.md.
- M2: README.md Contents tree stale.
- M3: Version labels disagree (v2 vs v3).

## Phase 3 Batch 2 fix round (controller)
- Commit: `6e2bf74` (I1 + I2 + M1 + M2 + M3 closed; N1-N3 deferred).

## Phase 3 Task 9 (AGENTS.md bookkeeping) (controller)
- Commit: `c0be543` (Phase 3 paragraph appended to "Fixes already landed").

## Phase 3 Task 10 (E2E smoke)
- Status: ✅ all checks passed; smoke.py exit 0.

**Phase 3 complete (commits 6e06028..c0be543, 10 commits, 8 files changed, +138/-32).**

Summary:
- `scripts/gen_topology.py`: `--dry-run` + `--summary` flags (C5)
- `scripts/_env.sh`: REPO_DOC_MINER_HOME exporter (C8)
- `assets/templates/topology.md`: 17 `<angle-bracket>` slots removed (C11)
- `references/evidence_checklist.md`: tool-vs-expectation callout (C10); de-PINNed Python ML row + balanced 5 flavor sections (B1)
- 4 templates (developer_guide / user_guide / tutorial / README): top-of-file TODO(doc-miner) reminder (C2)
- `assets/templates/_flavor_strip.md`: no-op marker for future --flavor (C1/C7)
- `README.md`: refreshed to v3 with full Contents tree
- `SKILL.md`: version 2.0.0 → 3.0.0; H1 "v2 — Topology-First" → "v3 — Topology-First + Pre-Mining Assessment"; scripts section now references _env.sh + smoke.py
- `AGENTS.md`: 3 placeholders/testing claims updated (M1); Phase 3 paragraph appended
- 3 reviewer findings (HissingAmphibian) + 5 reviewer findings (NeatEagle) = 8 findings, all RESOLVED
- 3 deferred (N1 README prose; N2 en-GB/en-US mix; N3 smoke.py missing _env.sh/_flavor_strip.md assertions) — minor polish

## Rulings I made (Phase 3)

65. D1: drop `or <pkg>/icbc/` alt in de-PINN row (folded into Task 5).
66. D2: rewrite Rust/Go duplicates to avoid empty rows (folded into Task 5).
67. D3: retain pre-existing `{{PLACEHOLDER}}` reference in closing prose.
68. D4: drop empty commit accidentally created mid-task.
69. D1 (env.sh): export `REPO_DOC_MINER_HOME="$_REPO_DOC_MINER_HOME"` (plan bug).
70. D2 (topology slots): 2 additional slots on line 9 (Mermaid `<br/>` intentional).
71. D3 (C2 reminder): added to all 4 templates, not just 2 (plan precondition false).
72. D4 (_flavor_strip.md): use `<FLAVOR_NAME>` (uppercase) to pass gate.
73. I1 (callout): drop `pom.xml`; add `setup.py`/`setup.cfg`; name Maven in "does not detect".
74. M1 (callout): reword "and their first-level files" → "top-level directories as module entities, plus typed files detected inside them".
75. M2 (docstring): `--dry-run | --summary` → `--dry-run] [--summary]`.
76. I1 (SKILL.md): add _env.sh + smoke.py to scripts section with usage.
77. I2 (_flavor_strip.md): rewrite in future tense; correct direction; drop "remove the arg"; add scaffolder-ignores-this note.
78. M1 (AGENTS.md): drop angle-bracket-allowed claim; drop "trailing" marker claim; drop "byte-identical to pre-Phase -1".
79. M2 (README): Contents tree now lists all 7 templates, 8 references, 4 scripts.
80. M3 (SKILL.md/AGENTS.md): version 2.0.0 → 3.0.0; H1 → v3.

---
