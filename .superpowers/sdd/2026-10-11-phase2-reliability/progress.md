# SDD ledger — plan: docs/superpowers/plans/2026-10-11-phase2-reliability.md

## Worktree
- Path: `.worktrees/phase1-pre-mining/`
- Branch: `phase1-pre-mining-assessment` (Phase 2 is additive on the same branch)
- Base: `860831b` (Phase 1 final-review commit)

## Batching strategy

Phase 2 is small enough to dispatch as a single implementer run with all 6 file-touching tasks (Tasks 1, 2, 3, 4, 5, 6), then a separate reviewer.

- **Batch 1 (implementer)**: Tasks 1-6 — all 6 file changes (1 new ref doc, 1 new script, 4 SKILL.md edits, 1 AGENTS.md edit).
- **Batch 2 (reviewer)**: scoped review of the 6 commits.
- **Task 7**: E2E smoke test (controller-only).

Total dispatches: 1 implementer + 1 reviewer = 2 subagent runs.

## Preflight review summary

| Cross-task interface | Producer | Consumer | Conflict? |
|---|---|---|---|
| T1 → T2 | edge_refinement.md content | SKILL.md subsection "references" link | None |
| T2 → T7 | New SKILL.md headings | heading-monotonicity check | None |
| T3 → T4 | Workflow Variants (Full / Lite / Progressive) | Failure Modes (Lite mode caveats) | None |
| T5 → T7 | scripts/smoke.py | E2E invocation | None |
| T6 → T7 | AGENTS.md bookkeeping | git status clean check | None |

**Self-consistency:**
- All 6 new file changes are additive.
- T1 (edge_refinement.md) is content-only; T5 (smoke.py) is the only code change; T2/T3/T4 are SKILL.md additions; T6 is AGENTS.md bookkeeping.
- No existing file content is altered (Phase 1 byte-identity preserved).

**Rulings: none.** The plan is internally consistent. Pre-flight proceeds clean.

---

## Phase 2 batch 1 implementer (RespectableDingo)
- Status: DONE with 6 documented deviations.
- Commits: `33b20fc` (T1), `dd20acf` (T2), `b8c4d71` (T3), `a302230` (T4), `1473e5f` (T5), `2a157e3` (T6).
- 4 files changed; +302/-0.

## Phase 2 batch 1 reviewer (QuickRoundworm)
- Verdict: **Needs fixes** — 3 Important + 5 Minor.
- I1: `smoke.py` Phase-5 placeholder/slot checks unfailable (gated on `not draft` which is always True on scaffolded output).
- I2: `edge_refinement.md:36` listed `vendor/`+`third_party/` in IGNORE_DIRS (not actually there).
- I3: `edge_refinement.md:42` claimed `.gitignore` filtering (script doesn't read .gitignore).
- M1-M5: minor polish.

## Phase 2 fix round 1 implementer (RespectableDingo, resumed)
- Status: DONE
- Commits: `b97977a` (content polish), `f9ed8b1` (script gate change).
- Closed I1 with new --strict policy + frozenset + exact membership; closed I2/I3 wording; closed M1-M5.
- All 5 verification checks passed.

## Phase 2 fix round 1 re-reviewer (DevotedSilkworm)
- Verdict: All 8 findings CLOSED.
- New findings: R1 (Important), R2 (Minor), R3 (Nit).
- R1: SKILL.md Workflow Variants self-contradiction (says "all 8 phases" but Phase -1 is opt-in).
- R2: README.md drift ("seven-phase" stale).
- R3: `--strict` flag is structurally unreachable on a throwaway scaffold (design trade-off; accepted).

## Rulings (Phase 2 fix round 2 controller)

| Finding | Ruling | Why | Cost if wrong |
|---|---|---|---|
| R1 | Add opt-in caveat to SKILL.md Workflow Variants intro + Full mode prose. | Self-contradiction between Workflow Variants and `### Phase -1` opt-in callout. | Wrong: user-facing default flow mandates an opt-in phase. |
| R2 | README.md "seven-phase" → "eight-phase + opt-in". | Phase-count drift between README and SKILL.md/AGENTS.md. | Wrong: README still describes v2, not v2+Phase-1. |
| R3 | Defer (accepted as the failable-scaffolder-tier design per I1). | Documented as design trade-off; Phase 3 may add `--guides-dir` if needed. | Wrong: minor — the script still has the always-failable `{{PROJECT_NAME}}`/`{{AUDIENCE}}` gate. |

## Phase 2 fix round 2 (controller)
- Commit: `4096edc` (SKILL.md + README.md).

**Phase 2 complete (commits 860831b..4096edc, 11 commits, 4 files changed, +308/-3 since Phase 1 base).**

Summary:
- `references/edge_refinement.md` (new, 48 lines) — B3 deep guide
- `scripts/smoke.py` (new, ~200 lines) — C4 codified safe smoke + Phase-5 checks
- SKILL.md: +55 lines — `#### How to refine edges` + `## Workflow Variants` + Failure Modes 6→12
- AGENTS.md: +2 lines — Phase 2 bookkeeping paragraph
- README.md: 1 line — R2 phase-count fix
- 8 reviewer findings (QuickRoundworm) + 3 re-reviewer findings (DevotedSilkworm) = 11 findings, all RESOLVED
- 1 formally deferred (R3 --strict unreachable on throwaway)

## Rulings I made (Phase 2)

49. D1: "three edge kinds" → "two" (factual correction).
50. D2: `--assience` → `--audience` (typo fix).
51. D3: Failure Modes truncation clause — truthful re `--verbose`.
52. D4: `--keep-tmp` made functional (mkdtemp + try/finally).
53. D5: Phase-5 publish-vs-draft policy via `--strict` flag.
54. D6: AGENTS.md Phase-5 clause aligned with D5.
55. I1: SCAFFOLDER_PLACEHOLDERS = frozenset; assertion unconditional; pending/slots behind `--strict`.
56. I2: `references/edge_refinement.md:36` — drop `vendor/`+`third_party/`; fix `IGNORED_DIRS` typo.
57. I3: `references/edge_refinement.md:42` — replace `.gitignore-style` with actual `IGNORE_DIRS + *.egg-info`.
58. M1: SKILL.md:55 "above" → "below"; "seven" → "eight" (with opt-in caveat per R1).
59. M2: `smoke.py` docstring drops "link integrity"; `--check-only` accurately documented.
60. M3: `smoke.py` fence tracker — replace toggle with run-length tracker.
61. M4: `SCAFFOLDER_PLACEHOLDERS` exact set membership (folded into I1).
62. M5: `AGENTS.md:159` — list all 6 new Failure-Modes entries.
63. R1: SKILL.md Workflow Variants opt-in caveat.
64. R2: README.md phase-count fix.

---
