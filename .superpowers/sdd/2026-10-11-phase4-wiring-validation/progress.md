# SDD ledger — plan: docs/superpowers/plans/2026-10-11-phase4-wiring-validation.md

## Worktree
- Path: `.worktrees/phase1-pre-mining/`
- Branch: `phase1-pre-mining-assessment` (Phase 4 is additive on the same branch)
- Base: `133822d` (Phase 3 ledger final-state commit)

## Batching strategy

Phase 4 has 6 file-touching tasks (Tasks 1, 2, 3, 5, 6) plus 1 controller smoke (Task 7) and 1 real-world validation (Task 4). Tasks 1 + 2 + 3 are the wiring code; Task 5 is README polish; Task 6 is AGENTS.md bookkeeping; Tasks 4 + 7 are controller-only.

- **Batch 1** (Tasks 1 + 2 + 3): the wiring code — scaffolder flag + demo block + smoke flag
- **Task 4**: real-world validation (controller-only, no subagent)
- **Batch 2** (Tasks 5 + 6): README polish + AGENTS.md bookkeeping
- **Task 7**: E2E smoke (controller-only)

Total dispatches: 1 implementer + 1 reviewer = 2 subagent runs + 2 controller-owned steps.

## Preflight review summary

| Cross-task interface | Producer | Consumer | Conflict? |
|---|---|---|---|
| T1 → T2 → T7 | `--flavor` flag + demo block | smoke battery (regression) | None |
| T3 → T7 | `--guides-dir` flag | E2E smoke | None |
| T4 → T5 | FastAPI validation | confirms README + scaffold behave | None |
| T6 → T7 | AGENTS.md bookkeeping | git log check | None |

**Self-consistency:**
- All 4 new file changes are additive; the only file with an actual content change is `assets/templates/developer_guide.md` (one demo block) and `README.md` (polish).
- No new dependencies; no third-party imports.
- The `_flavor_strip.md` marker file is unchanged (it's already a future-extension contract; this phase wires up the consumer side).

**Rulings: none.** The plan is internally consistent. Pre-flight proceeds clean.

---
