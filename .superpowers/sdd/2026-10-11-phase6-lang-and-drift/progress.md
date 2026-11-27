# SDD ledger — plan: docs/superpowers/plans/2026-10-11-phase6-lang-and-drift.md

## Worktree
- Path: `.worktrees/phase1-pre-mining/`
- Branch: `phase1-pre-mining-assessment`
- Base: `6d92db1` (Phase 5 ledger final-state commit)

## Batching strategy

Phase 6 has 3 file-touching tasks + 1 controller smoke. One implementer run lands all 3 in sequence.

- **Batch 1** (Tasks 1, 2, 3): one implementer run; 3 commits
- **Task 4**: E2E smoke (controller-only)

Total dispatches: 1 implementer + 1 reviewer = 2 subagent runs.

## Preflight review summary

| Cross-task interface | Producer | Consumer | Conflict? |
|---|---|---|---|
| T1 → T4 | `--lang` flag | smoke battery regression | None |
| T2 → T4 | SKILL.md Resources update | check_resources.py | None |
| T3 → T4 | AGENTS.md bookkeeping | git log | None |

**Self-consistency:** All 3 file changes are additive / small. The `--lang` flag is byte-identical to before for `bilingual` (default). The SKILL.md update is the literal text from the plan. The AGENTS.md paragraph is verbatim.

**Rulings: none.** The plan is internally consistent. Pre-flight proceeds clean.

---

## Phase 6 Batch 1 implementer (PracticalCockroach)
- Status: DONE with 1 documented deviation.
- Commits: `9fcf243` (T1 --lang), `489d1a8` (T2 SKILL.md Resources), `c6fcd30` (T3 AGENTS.md).
- 1 deviation: the plan's `_rewrite_h1` helper was specified to match the literal `{{PROJECT_NAME}}` *after* substitution; that order can't work because `{{PROJECT_NAME}}` is substituted before the rewrite runs. Implementer moved the substitution inside the helper so the source/target forms both contain the substituted name.

## Phase 6 Task 4 (controller)
- All 7 E2E steps pass.
- `make test` / `make smoke-strict` exit 0
- `check_resources.py` reports 0 INFO disk-only drift
- `git status` clean; `git log -8` shows 3 Phase 6 commits in order

**Phase 6 complete (commits 6d92db1..c6fcd30, 3 task commits).**

## Rulings I made (Phase 6)

101. T1: `_LANG_HEADINGS` table is verbatim from the brief (bilingual / en / zh triples for 4 templates).
102. T1: H2 sections are intentionally not rewritten; the templates don't carry parallel Chinese H2s.
103. T1: `--lang fr` rejected by argparse `choices=`.
104. T1 deviation: substitute `{{PROJECT_NAME}}` inside the helper (not before).
105. T2: SKILL.md Resources list now lists every shipped file; `check_resources.py` exits 0 with 0 drift.
106. T3: AGENTS.md Phase 6 paragraph appended after Phase 5.

---
