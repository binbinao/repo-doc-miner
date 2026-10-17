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

## Phase 4 Batch 1 implementer (MobileChameleon)
- Status: DONE with 3 documented deviations.
- Commits: `2fca72a` (T1 --flavor), `865ca83` (T2 demo block), `71c1248` (T3 --guides-dir).

## Phase 4 Task 4 — Real-world validation (controller)
- Target: `tiangolo/fastapi` (cloned --depth 1)
- `gen_topology.py --summary`: 23 entities (17 scripts, 5 modules, 1 skill), 5 edges
- `scaffold_docs.py --assess --audience contributor`: 6 files materialised; `assess.md` first line `<!-- audience: contributor -->`
- `smoke.py --strict --guides-dir`: exit 0 (R3 closed — `--strict` now meaningful against real output)
- Log written to `.superpowers/sdd/2026-10-11-phase4-wiring-validation/phase4-validation-log.md`.

## Phase 4 Task 5 + 6 (controller)
- README polished: "four questions" (matches assess.md); `docs/guides/` now described as default behind `--out PATH`.
- AGENTS.md Phase 4 paragraph appended to "Fixes already landed".
- Commit: `1a3871d` (README + AGENTS.md + validation log).

## Phase 4 Task 7 (controller)
- All 6 E2E steps pass: --flavor in --help; --guides-dir --strict exits 0 on real scaffold; standard smoke exits 0; README polish verified; no untracked files; git log order matches the plan.

**Phase 4 complete (commits 133822d..1a3871d, 5 commits, 3 files changed in the shipped tree, +134/-11).**

Summary:
- `scripts/scaffold_docs.py`: `--flavor` flag (Task 1) with `_strip_flavors` helper, regex pattern, `keep_flavor` kwarg
- `assets/templates/developer_guide.md`: one demo `<!-- flavor: backend -->` block (Task 2)
- `scripts/smoke.py`: `--guides-dir PATH` flag (Task 3) — closes Phase 2 R3
- `README.md`: 4-questions + configurable --out polish (Task 5)
- `AGENTS.md`: Phase 4 bookkeeping (Task 6)
- `.superpowers/sdd/.../phase4-validation-log.md`: FastAPI validation log (Task 4, force-added to repo for completeness)
- 4 deferred items: `--lang` flag (v4+), `_flavor_strip.md` en-GB/en-US mix, smoke.py `_env.sh`/`_flavor_strip.md` explicit assertions, C5 cap warning-fidelity polish

## Rulings I made (Phase 4)

81. T1: `--flavor` choices = `general|pinn|cli|lib|monorepo` per spec §8.3.
82. T1: regex `<[a-z][a-z0-9_-]*>` for flavor name (alphanumeric + underscore + hyphen).
83. T1: audience blockquote marker preserved (not treated as a flavor marker).
84. T1: mismatched close markers left in place (safety net).
85. T3: `--guides-dir` defaults to None (no audit of real dir unless explicitly passed).
86. T3: `--strict` now meaningful — Phase 2 R3 closure.
87. T4: FastAPI as the validation target (Python library, well-known, ~50 files).
88. T5: README "four questions" matches assess.md's actual content.
89. T5: README `docs/guides/` now described as default behind `--out PATH`.
90. T6: AGENTS.md Phase 4 paragraph appended.

---
