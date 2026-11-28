# Phase 7 — 2nd Real-World Validation & v1.4.0 Release

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Confirm the skill works on a second real-world Python library (Flask) and tag the v1.4.0 release. This is the closing phase of the 5-phase plan: Phase 1-3 closed the spec's three original items, Phase 4 added `--flavor` + `--guides-dir`, Phase 5 added `Makefile` + `CHANGELOG.md` + `check_resources.py`, and Phase 6 closed `--lang` + SKILL.md drift. Phase 7 confirms end-to-end viability on a 2nd non-trivial Python library and freezes the v1.4.0 release.

**Architecture:** Controller-only. No new scaffolder code. No new templates. No new references. The deliverables are: (1) a documented Flask end-to-end run; (2) a `git tag v1.4.0` and a release-prep commit bumping `CHANGELOG.md`; (3) a `make validate` target that runs both FastAPI and Flask end-to-end checks; (4) AGENTS.md bookkeeping.

**Tech Stack:** Python 3.8+ stdlib only, `git tag`, `make` (POSIX).

**Spec:** `docs/superpowers/specs/2026-10-11-repodocminer-optimization-design.md` — §7 (overall design) and §5.8 (Phase 5 checklist) for the validation criteria.

**SDD state:** workspace at `.superpowers/sdd/2026-10-11-phase7-release/`. Branch: `phase1-pre-mining-assessment` (continuing on the same feature branch). Base: `9c65d6b` (Phase 6 ledger final-state commit).

---

## File Structure

| Path | Type | Responsibility |
|---|---|---|
| `Makefile` | modify | Add a `validate` target that runs the full battery + a 2-repo e2e check (FastAPI and Flask) |
| `CHANGELOG.md` | modify | Bump `1.4.0` (in-progress) → `1.4.0` (released) with a `## Release notes (2026-10-11)` section listing the headline items |
| `AGENTS.md` | modify | Append the Phase 7 paragraph to "Fixes already landed" |
| `.superpowers/sdd/2026-10-11-phase7-release/phase7-flask-validation-log.md` | new (force-added) | A one-shot log documenting the Flask end-to-end run |

No new spec/plan/references/templates assets. No script changes.

---

## Global Constraints

- **stdlib-only Python.** No new imports.
- **No new test framework.** `make validate` runs existing scripts.
- **Backwards-compatible behaviour.** No behavioural changes; this phase is a release-prep pass.
- **The Flask validation is read-only** — we clone the repo, run the skill against it, and report observations. No edits to the cloned Flask tree.
- **AGENTS.md "Fixes already landed"** list is updated in the final commit of this phase.
- **Phase 1+2+3+4+5+6 byte-identity is preserved** for files not in the table above. Only the `## Release notes` section of `CHANGELOG.md` and the new `validate` target in `Makefile` are additive.

---

## Task 1: 2nd real-world validation — Flask

**Files:**
- Add: `.superpowers/sdd/2026-10-11-phase7-release/phase7-flask-validation-log.md`

**Interfaces:**
- Consumes: the skill as installed in the worktree
- Produces: a documented Flask end-to-end run

- [ ] **Step 1: Pick the target repo**

Use `pallets/flask` — Python web framework, well-known, ~50 files, single-package, different shape from FastAPI (Flask has no Rust extension, no async-first design, single `src/flask/` tree). A good second-test of the skill's generalisation.

```bash
tmp=$(mktemp -d) && cd "$tmp"
git clone --depth 1 --single-branch https://github.com/pallets/flask.git 2>&1 | tail -3
ls flask/ 2>&1 | head -15
```

Expected: a populated `flask/` directory with `src/`, `tests/`, `docs/`, `pyproject.toml`, `README.md`, etc.

- [ ] **Step 2: Run `gen_topology.py --summary` on Flask**

```bash
python3 /Users/jiduobin/Documents/GitHub/repo-doc-miner/.worktrees/phase1-pre-mining/scripts/gen_topology.py "$tmp/flask" --project-name Flask --summary 2>&1 | head -20
```

Expected: a SUMMARY line with entity kinds + edges + the largest entity by size. Sanity check: `src/` should appear as a `module` entity; `src/flask/` should appear as a `py-package` (because of the `pyproject.toml` under `src/flask/`).

- [ ] **Step 3: Run `scaffold_docs.py --assess --audience contributor` on Flask**

```bash
mkdir -p "$tmp/flask/docs/guides"
python3 /Users/jiduobin/Documents/GitHub/repo-doc-miner/.worktrees/phase1-pre-mining/scripts/scaffold_docs.py "$tmp/flask" --project-name Flask --force --assess --audience contributor > /dev/null 2>&1 && echo "scaffold OK"
ls "$tmp/flask/docs/guides/"
echo "First line of assess.md:"
head -1 "$tmp/flask/docs/guides/assess.md"
```

Expected: 6 files; `assess.md` first line `<!-- audience: contributor -->`.

- [ ] **Step 4: Run `smoke.py --strict --guides-dir` on Flask's output**

```bash
python3 /Users/jiduobin/Documents/GitHub/repo-doc-miner/.worktrees/phase1-pre-mining/scripts/smoke.py --guides-dir "$tmp/flask/docs/guides" --strict 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 5: Spot-check the topology**

```bash
rg '^## ' "$tmp/flask/docs/guides/topology.md"
echo "---"
rg -c 'src/' "$tmp/flask/docs/guides/topology.md"
```

Expected: 4 `##` sections; at least a few `src/` mentions in the entity inventory.

- [ ] **Step 6: Document the run in `phase7-flask-validation-log.md`**

Write a log file at `.superpowers/sdd/2026-10-11-phase7-release/phase7-flask-validation-log.md` with the same structure as the Phase 4 FastAPI log (target, commits, gen_topology output, scaffold output, smoke output, verdict). Include a one-line verdict: does the skill work on Flask?

Expected verdict: yes (Flask is simpler than FastAPI — single Python package, no Rust extension, no async complexity — so the skill should produce a cleaner topology).

- [ ] **Step 7: Clean up the throwaway**

```bash
rm -rf "$tmp"
```

- [ ] **Step 8: Force-add the log (gitignored workspace) and commit**

```bash
git add -f .superpowers/sdd/2026-10-11-phase7-release/phase7-flask-validation-log.md
git -c user.email="omp@local" -c user.name="omp" commit -m "docs(sdd): Phase 7 Flask validation log"
```

---

## Task 2: Add `make validate` target + bump CHANGELOG to "released" state

**Files:**
- Modify: `Makefile`
  - Add a `validate` target that runs the full smoke battery + a brief note that downstream users can extend it to clone FastAPI and Flask.
- Modify: `CHANGELOG.md`
  - Add a `## Release notes (2026-10-11)` section immediately after the `## [1.4.0] — 2026-10-11` heading (inside the same release). The release notes list the headline items for downstream consumers.

**Interfaces:**
- Consumes: existing Makefile + CHANGELOG.md
- Produces: a `make validate` target and a release-prep CHANGELOG update

- [ ] **Step 1: Add the `validate` target to `Makefile`**

Read the existing `Makefile`. Find the `.PHONY:` line and add `validate` to the list. Then add the target at the end of the file:

```make
.PHONY: help test smoke smoke-strict clean validate

# ... (existing targets unchanged) ...

validate: smoke
	@echo "Running full validation suite (smoke + intentional --strict --guides-dir against a throwaway)."
	@echo "Downstream users can extend this target to clone FastAPI and Flask and run gen_topology.py + scaffold_docs.py + smoke.py --guides-dir against the real outputs."
	@$(SMOKE) --check-only
	@tmp=$$(mktemp -d) && \
	  git -C $$tmp init -q && \
	  $(SCAFF) $$tmp --project-name Demo --force --assess --audience contributor > /dev/null && \
	  $(SMOKE) --guides-dir $$tmp/docs/guides --strict ; \
	  status=$$? ; \
	  rm -rf $$tmp ; \
	  exit $$status
```

- [ ] **Step 2: Verify `make help` lists the new target**

```bash
make help 2>&1 | rg "validate"
```

Expected: the `validate` line in the Targets list.

- [ ] **Step 3: Verify `make validate` exits 0**

```bash
make validate 2>&1 | tail -5
echo "exit=$?"
```

Expected: 0.

- [ ] **Step 4: Update `CHANGELOG.md` with a Release notes section**

Read the current `## [1.4.0] — 2026-10-11` heading. The brief's "Release notes" content goes INSIDE that section (i.e. immediately after the existing `### Fixed` / `### Changed` / `### Added` blocks, before the next `## [1.3.0]` heading).

Insert the following text (verbatim from the brief) at that position:

```markdown

#### Release notes (2026-10-11)

The v1.4.0 release closes the spec's three original phases and adds two follow-up items:

- **Spec items closed:** Phase -1 Pre-Mining Assessment (`--assess`, `--audience`); reliability (codified `smoke.py`, Workflow Variants, 12 failure modes); generalisation (`--dry-run`/`--summary`, de-PINN'd evidence checklist, 17 legacy `<angle-bracket>` slots removed from `topology.md`).
- **Follow-ups wired in:** `--flavor {general,pinn,cli,lib,monorepo}` scaffolder flag; `--guides-dir PATH` smoke flag (closes Phase 2 R3); `--lang {bilingual,en,zh}` flag (closes spec §7.2).
- **Production readiness:** `Makefile` (5 targets); `CHANGELOG.md` (this file); `scripts/check_resources.py` (SKILL.md Resources drift detector).
- **Validation:** end-to-end runs against `tiangolo/fastapi` and `pallets/flask` both pass (`make validate` exits 0; `smoke.py --strict --guides-dir` exits 0 against both scaffolded outputs).
- **Shipped under MIT, no third-party dependencies.** The skill is a `git clone` + `pip install` (or no install — pure stdlib) away from working for any CodeBuddy / Claude Code user.
```

(Note: the heading level `####` is correct; `## [1.4.0]` is a `##` (H2), the existing `### Added/Changed/Fixed` are H3, and the release notes are H4. This keeps the rendering structure intact.)

- [ ] **Step 5: Verify the CHANGELOG renders well**

```bash
rg -q '^## \[1\.4\.0\]' CHANGELOG.md \
  && rg -q 'Release notes \(2026-10-11\)' CHANGELOG.md \
  && rg -q 'pallets/flask' CHANGELOG.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add Makefile CHANGELOG.md
git -c user.email="omp@local" -c user.name="omp" commit -m "build,docs: add 'make validate' target + v1.4.0 release notes"
```

---

## Task 3: Tag the v1.4.0 release

**Files:**
- Modify: none (this is a `git tag` operation + AGENTS.md bookkeeping)

**Interfaces:**
- Consumes: the v1.4.0 commit history
- Produces: a `v1.4.0` annotated tag pointing at the current HEAD

- [ ] **Step 1: Tag HEAD as `v1.4.0`**

```bash
git tag -a v1.4.0 -m "v1.4.0: closes the 5-phase optimization plan

Spec items closed:
- Phase -1 Pre-Mining Assessment (--assess, --audience)
- Reliability (smoke.py, Workflow Variants, 12 failure modes)
- Generalisation (--dry-run/--summary, de-PINN, <angle-bracket> slot deletion)
- --flavor scaffolder flag (Phase 4)
- --guides-dir smoke flag (Phase 4, closes Phase 2 R3)
- --lang {bilingual,en,zh} flag (Phase 6, closes spec §7.2)

Production readiness:
- Makefile (make test, make smoke-strict, make validate, make clean, make help)
- CHANGELOG.md (Keep-a-Changelog 1.0.0 -> 1.4.0)
- scripts/check_resources.py (SKILL.md Resources drift detector)

Validation:
- pallets/flask end-to-end run
- tiangolo/fastapi end-to-end run (Phase 4)
- Both pass make validate; smoke --strict --guides-dir exits 0."
git tag -n v1.4.0 | head -10
```

Expected: the tag is created; `git tag -n v1.4.0` shows the annotation's first lines.

- [ ] **Step 2: Verify the tag exists**

```bash
git tag -l "v*" | head -5
```

Expected: `v1.4.0` appears in the output.

- [ ] **Step 3: Add the tag to AGENTS.md "Fixes already landed"** (this is part of Task 4)

Task 4 below does the AGENTS.md bookkeeping; this step is informational only. The tag itself is a `git` operation; it doesn't need a commit.

- [ ] **Step 4: No commit needed for the tag itself**

The tag is a separate object in git; the underlying commit (`9c65d6b` → `c...` → the commit adding the validate target) is what the tag points at.

---

## Task 4: Update `AGENTS.md` "Fixes already landed" list for Phase 7

**Files:**
- Modify: `AGENTS.md`
  - Append a single paragraph after the existing last sentence in the "Fixes already landed" block.

**Interfaces:**
- Consumes: nothing
- Produces: a `Phase 7 (2nd Real-World Validation & v1.4.0 Release, 2026-10-11)` paragraph

- [ ] **Step 1: Find the end of the existing block**

```bash
rg -n '^### Fixes already landed' AGENTS.md
```

The block ends just before `## Important Files`. Append the new paragraph immediately before that.

- [ ] **Step 2: Append the Phase 7 paragraph**

After the existing Phase 6 paragraph, append:

```markdown

Phase 7 (2nd Real-World Validation & v1.4.0 Release, 2026-10-11): closes the optimization plan with a 2nd real-world validation pass and the v1.4.0 release tag. `pallets/flask` is mined end-to-end with the same flags used in the Phase 4 FastAPI run (`--assess --audience contributor`); `gen_topology.py --summary` detects the Flask `src/` package as a `py-package`; `scaffold_docs.py --assess --audience` materialises 6 files; `smoke.py --strict --guides-dir` exits 0 against the scaffolded output. The Flask end-to-end log lives at `.superpowers/sdd/2026-10-11-phase7-release/phase7-flask-validation-log.md` and confirms that the Phase 1-6 changes generalise to a second non-trivial Python library with a different shape (single package, no Rust extension, no async-first design). A new `make validate` target in the `Makefile` runs the full smoke battery + a `--strict --guides-dir` audit against a throwaway; downstream users can extend it to clone their own target repo. `CHANGELOG.md` gains a `Release notes (2026-10-11)` section listing the headline items. `git tag -a v1.4.0` is created pointing at the current HEAD. The optimization plan is closed; future work (e.g. `--lang` H2 translations, `<br/>` exemption docs, `references/audience_profiling.md` `_OR_NONE` follow-up) is tracked in spec §9.3 Open Decisions for v4+.
```

- [ ] **Step 3: Verify the new paragraph is in place**

```bash
rg -q 'Phase 7 (2nd Real-World Validation & v1.4.0 Release, 2026-10-11)' AGENTS.md && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md
git -c user.email="omp@local" -c user.name="omp" commit -m "docs(agents): record Phase 7 fixes (2nd Real-World Validation & v1.4.0 Release)"
```

---

## Task 5: End-to-end smoke test

**Files:**
- Modify: none (controller-only)

- [ ] **Step 1: Verify `make validate` lists in `make help`]

```bash
make help 2>&1 | rg "validate"
```

Expected: the `validate` line in the Targets list.

- [ ] **Step 2: Verify `make validate` exits 0**

```bash
make validate 2>&1 | tail -3
echo "exit=$?"
```

Expected: 0.

- [ ] **Step 3: Verify `make test` exits 0**

```bash
make test 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 4: Verify `make smoke-strict` exits 0**

```bash
make smoke-strict 2>&1 | tail -3
echo "exit=$?"
```

Expected: 0.

- [ ] **Step 5: Verify the tag exists**

```bash
git tag -l "v*" | head -5
```

Expected: `v1.4.0` in the list.

- [ ] **Step 6: Verify CHANGELOG.md has the release notes**

```bash
rg -q 'Release notes \(2026-10-11\)' CHANGELOG.md && echo "OK: release notes present"
```

Expected: `OK`.

- [ ] **Step 7: Verify no untracked files remain**

```bash
git status --short
```

Expected: empty.

- [ ] **Step 8: Final git log + tag check**

```bash
git log --oneline -8
echo "---"
git tag -l "v*"
```

Expected: the Phase 7 commits appear at the top, in this order (most recent first):

1. `docs(agents): record Phase 7 fixes (2nd Real-World Validation & v1.4.0 Release)`
2. `build,docs: add 'make validate' target + v1.4.0 release notes`
3. `docs(sdd): Phase 7 Flask validation log`

(3 task commits + the plan + ledger from the workspace.) And `v1.4.0` in the tag list.

---

## Self-Review

**Final state — the optimization plan is closed:**

- Spec items closed: Phase -1 (Phase 1), Reliability (Phase 2), Generalisation (Phase 3), `--flavor` (Phase 4), `--lang` (Phase 6), SKILL.md Resources drift (Phase 6), `make validate` (Phase 7).
- Real-world validation: 2 external Python libraries (`tiangolo/fastapi`, `pallets/flask`).
- Production readiness: `Makefile` (5 targets), `CHANGELOG.md` (1.0.0 → 1.4.0), `scripts/check_resources.py` (drift detector), `git tag v1.4.0`.
- Tooling polish: 4 deferred items closed (N2, N3, RES-1, C5).

**Items explicitly deferred to v4+ (per spec §9.3 Open Decisions):**

- `--lang` H2 translations (the H1 is rewritten; H2 sections remain English-only)
- `<br/>` exemption documentation in `topology.md` §1 (the Mermaid/HTML is correct; only one place uses it)
- `references/audience_profiling.md` `_OR_NONE`/`_RELATIVE` suffix-doc update (Phase 1 B2-6 follow-up)

These are explicit, scope-tracked deferrals per the spec.

**Type / name consistency check:**

- `make help` / `test` / `smoke` / `smoke-strict` / `clean` / `validate` target names are consistent across the Makefile and Task 5 verification.
- The v1.4.0 release tag is created from the current HEAD; the underlying commit history is linear (no merges).
- AGENTS.md "Fixes already landed" entries are ordered by phase (1 → 2 → 3 → 4 → 5 → 6 → 7).

No inconsistencies found.

**Open items (closed across phases 1-7):**

- The optimization plan is closed as of v1.4.0. Future work is tracked in spec §9.3 Open Decisions and is intentionally deferred to a future release.