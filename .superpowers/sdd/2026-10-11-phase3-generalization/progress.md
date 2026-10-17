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
