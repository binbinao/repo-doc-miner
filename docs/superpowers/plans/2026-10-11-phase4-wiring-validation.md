# Phase 4 — Wiring Up & Real-World Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the last open Phase 3 spec items in a small, focused way. Wire up the `--flavor` scaffolder flag (the no-op marker from `_flavor_strip.md` becomes real), make `scripts/smoke.py --strict` actually meaningful via a new `--guides-dir PATH` flag, run a real-world validation pass on a non-trivial Python library, and close the remaining small polish items (N1 README prose, N3 smoke.py missing assertions).

**Architecture:** One scaffolder flag added (`--flavor`), one `scripts/smoke.py` flag added (`--guides-dir`), one demonstration flavor block added to `developer_guide.md` (proving the stripper works), and one real-world run on an external repo. The other Phase 3 spec items (the `--lang` flag, C5 cap warning-fidelity polish, full topology.md `<br/>` exemption documentation) are formally deferred because the cost-to-value is low for a single-decimal-minor-release.

**Tech Stack:** Python 3.8+ stdlib only (`argparse`, `pathlib`, `re`, `subprocess`, `tempfile`), Markdown templates.

**Spec:** [`docs/superpowers/specs/2026-10-11-repodocminer-optimization-design.md`](../specs/2026-10-11-repodocminer-optimization-design.md) — section §7 (C1/C7 templates de-PINN + language flag, B1 evidence checklist flavor-agnostic), with concrete wiring here. Real-world validation aligns with the spec's §5.8 "Phase 5 checklist" guidance.

**SDD state:** workspace at `.superpowers/sdd/2026-10-11-phase4-wiring-validation/`. Branch: `phase1-pre-mining-assessment` (continuing on the same feature branch). Base: `133822d` (Phase 3 ledger final-state commit).

---

## File Structure

| Path | Type | Responsibility |
|---|---|---|
| `scripts/scaffold_docs.py` | modify | Add `--flavor` argparse flag + content post-processing (strip non-matching `<!-- flavor: X -->` blocks) |
| `scripts/smoke.py` | modify | Add `--guides-dir PATH` argparse flag; route the `non-throwaway` audit through that path; close R3 (--strict structurally unreachable) |
| `assets/templates/developer_guide.md` | modify | Add one `<!-- flavor: backend -->` block (with `--flavor general` default) to demonstrate the stripper works |
| `README.md` | modify | N1 polish — fix "four questions" / "docs/guides/" hard-code; (no other wording changes) |
| `AGENTS.md` | modify | Append the Phase 4 paragraph to "Fixes already landed" |

No scaffolder code in `gen_topology.py`. No new spec/plan files. No new references.

---

## Global Constraints

- **stdlib-only Python.** No third-party imports added to `scripts/`.
- **No new test framework.** Verification uses throwaway-directory bash smoke tests plus a real-world run.
- **Backwards-compatible behaviour.** Both new scaffolder / smoke flags default to current behaviour. `--flavor` defaults to `general` (no stripping). `--guides-dir` defaults to None (smoke runs as before; `--strict` only acts on a path that was passed).
- **Headings monotonic** (new flag help text is not Markdown, so N/A).
- **No `{{...}}` placeholders or `<angle-bracket>` slots** in any new content (the flavor block in `developer_guide.md` uses `<!-- flavor: NAME -->` comment markers, not slots).
- **AGENTS.md "Fixes already landed"** list is updated in the final commit of this phase.
- **Phase 1+2+3 byte-identity is preserved** for files not in the table above. The only changes outside this table are in `scaffold_docs.py`, `smoke.py`, one flavor block in `developer_guide.md`, the README polish, and AGENTS.md bookkeeping.

---

## Task 1: Wire up `--flavor` flag in `scripts/scaffold_docs.py`

**Files:**
- Modify: `scripts/scaffold_docs.py`
  - Add `--flavor FLAVOR_NAME` argparse argument (default `general`).
  - Add a `_FLAVOR_PATTERN` constant (re module) that matches `<!-- flavor: NAME -->` open + `<!-- /flavor: NAME -->` close pairs in template content.
  - In `materialize`, after substituting `{{PROJECT_NAME}}` and (when set) the audience prefix, post-process the content with a flavor-strip helper that removes non-matching `<!-- flavor: ... -->` blocks.
  - Behaviour:
    - `--flavor general` (default): strip EVERY `<!-- flavor: ... -->` block from the 5 core templates + `assess.md` (no flavor-specific prose is kept).
    - `--flavor pinn` (example): keep blocks tagged `flavor: pinn`; strip all other flavor blocks.
    - The blockquote `<!-- audience: ... -->` marker is NOT a flavor marker and must be left untouched.

**Interfaces:**
- Consumes: the existing materialization pipeline + `_flavor_strip.md` future-extension contract
- Produces: a `materialize` that respects `--flavor`; no behaviour change when `--flavor` is `general` (which is the default)

- [ ] **Step 1: Read the existing `materialize` and `main` to find insertion points**

```bash
rg -n 'def materialize|^def main|return written, skipped|argparse.ArgumentParser' scripts/scaffold_docs.py
```

Confirm the function bounds. `materialize` is the body that writes the 5 core templates; `main` is the argparse + bootstrap.

- [ ] **Step 2: Add the `--flavor` argparse argument**

In `main`, after the existing `--audience` argparse argument (around line 168), add:

```python
    parser.add_argument(
        "--flavor",
        default="general",
        choices=["general", "pinn", "cli", "lib", "monorepo"],
        help=("Which flavor-specific template blocks to keep. "
              "Default: 'general' (strips every flavor-tagged block). "
              "See assets/templates/_flavor_strip.md for the convention. "
              "Reserved names: pinn (PINN/DeepXDE), cli (CLI tools), "
              "lib (plain libraries), monorepo (multi-language monorepos)."),
    )
```

- [ ] **Step 3: Add the flavor-strip pattern + helper**

Add a module-level constant + helper function above `materialize` (or right after `_print_summary` analog if one exists). Body:

```python
import re

# `<!-- flavor: NAME --> ... <!-- /flavor: NAME -->` blocks.
# Greedy enough to span multiple lines but not so greedy that a missing
# close marker swallows the rest of the file.
_FLAVOR_BLOCK_RE = re.compile(
    r"<!--\s*flavor:\s*([a-z][a-z0-9_-]*)\s*-->(?P<body>.*?)<!--\s*/flavor:\s*\1\s*-->",
    re.DOTALL,
)


def _strip_flavors(text: str, keep: str) -> str:
    """Remove every `<!-- flavor: NAME --> ... <!-- /flavor: NAME -->` block
    except those whose NAME equals `keep`. Returns the text unchanged when
    `keep` is the literal string "general" (the default — every block stripped).
    """
    if keep == "general":
        # Strip every flavor block, regardless of name.
        return _FLAVOR_BLOCK_RE.sub("", text)

    def _repl(match: re.Match) -> str:
        name = match.group(1)
        return match.group("body") if name == keep else ""

    return _FLAVOR_BLOCK_RE.sub(_repl, text)
```

Notes:
- The `general` mode is implemented as a no-arg `re.sub` (faster, simpler) that blanks every match.
- The `pinn` (etc.) mode uses a function callback that re-inserts the body when the name matches and blanks it otherwise.
- The regex's backreference `\1` ensures the close marker matches the open marker's name (mismatched blocks are NOT stripped — they're left in place as a safety net).

- [ ] **Step 4: Wire the strip into `materialize`**

Find the lines in `materialize` that read the template content and write the output. Currently:

```python
        text = src.read_text(encoding="utf-8")
        text = text.replace("{{PROJECT_NAME}}", project_name)
        if audience_prefix and name != HUB_FILE:
            text = audience_prefix + text
        dst.write_text(text, encoding="utf-8")
```

Add the flavor strip after the audience-prefix concatenation (so it operates on the post-prefix text):

```python
        text = src.read_text(encoding="utf-8")
        text = text.replace("{{PROJECT_NAME}}", project_name)
        if audience_prefix and name != HUB_FILE:
            text = audience_prefix + text
        text = _strip_flavors(text, keep_flavor)
        dst.write_text(text, encoding="utf-8")
```

The `keep_flavor` parameter is new. Add it to the function signature:

```python
def materialize(
    templates_dir: Path,
    out_dir: Path,
    project_name: str,
    force: bool,
    write_assess: bool = False,
    audience_prefix: str | None = None,
    keep_flavor: str = "general",
) -> tuple[list[str], list[str]]:
```

And update the function's docstring to mention `keep_flavor`.

- [ ] **Step 5: Plumb the flag through to the `materialize` call site**

In `main`, find the call to `materialize(...)` (around line 200+). Update it to pass `keep_flavor=args.flavor`:

```python
    written, skipped = materialize(
        templates_dir, out_dir, args.project_name,
        args.force,
        write_assess=args.assess,
        audience_prefix=audience_prefix,
        keep_flavor=args.flavor,
    )
```

- [ ] **Step 6: Verify default behaviour is unchanged (`--flavor general` = no change)**

The Phase 2 smoke test is the canonical regression check. Run it and assert the no-flags + default-`general` output is byte-identical to the previous `HEAD~1` output for the 5 core templates.

```bash
# Capture the current scaffolder output for diffing.
tmp1=$(mktemp -d) && git -C "$tmp1" init -q
python3 scripts/scaffold_docs.py "$tmp1" --project-name Demo --force > /dev/null
# Compare against the pre-edit output (HEAD~1).
tmp2=$(mktemp -d) && git -C "$tmp2" init -q
git show HEAD~1:scripts/scaffold_docs.py | python3 - "$tmp2" --project-name Demo --force
diff -r "$tmp1/docs/guides" "$tmp2/docs/guides" && echo "OK: default flavor output byte-identical"
rm -rf "$tmp1" "$tmp2"
```

(If `git show HEAD~1:scripts/scaffold_docs.py | python3 -` is awkward, you can also use the documented throwaway pattern: `python3 scripts/scaffold_docs.py <tmp> --project-name Demo --force` twice and `diff` the two `docs/guides` trees. Both should be identical since the scaffolder is deterministic.)

Expected: `OK: default flavor output byte-identical`.

- [ ] **Step 7: Verify the smoke test still passes**

```bash
python3 scripts/smoke.py 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 8: Verify `--flavor general` strips demo content (after Task 2 adds the demo block)**

After Task 2 lands, run:

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --flavor general > /dev/null
! rg -q 'flavor: backend' "$tmp/docs/guides/developer_guide.md" && echo "OK: --flavor general stripped"
rm -rf "$tmp"
```

Expected: `OK: --flavor general stripped`.

- [ ] **Step 9: Commit**

```bash
git add scripts/scaffold_docs.py
git commit -m "feat(scaffold): add --flavor flag (wires up the _flavor_strip.md contract)"
```

---

## Task 2: Add one demonstration `<!-- flavor: backend -->` block to `developer_guide.md`

**Files:**
- Modify: `assets/templates/developer_guide.md`
  - Add one `<!-- flavor: backend --> ... <!-- /flavor: backend -->` block inside `## 6. Backend / platform abstraction` so the stripper has at least one block to actually strip.

**Interfaces:**
- Consumes: the `--flavor` flag added in Task 1
- Produces: a single demonstrative flavor block in `developer_guide.md`; the other 4 templates remain flavor-free

- [ ] **Step 1: Read `## 6. Backend / platform abstraction` to find the insertion point**

```bash
rg -n '^## 6\.' assets/templates/developer_guide.md
```

Expected: line number; the section starts at `## 6. Backend / platform abstraction` and continues for ~6 lines.

- [ ] **Step 2: Add the demonstration block**

Find the section `## 6. Backend / platform abstraction` and **replace its entire body** with:

```markdown
## 6. Backend / platform abstraction

> Skip this section if the project has no multi-backend indirection.

<!-- flavor: backend -->
The material below is backend-specific. With `--flavor general`, this whole block is stripped. With `--flavor pinn` (or any other non-`general` flavor that the scaffolder's `choices=` list does not match), the block is also stripped (the scaffolder only knows `general`/`pinn`/`cli`/`lib`/`monorepo`; see `_flavor_strip.md` for the convention).

- Unified interface file: `{{BACKEND_INTERFACE_PATH}}`.
- Selection priority:
  1. {{BACKEND_PRIORITY_1}}
  2. {{BACKEND_PRIORITY_2}}
  3. {{BACKEND_PRIORITY_3}}
- Enabled-API registry mechanism: {{ENABLED_API_MECHANISM}}.
<!-- /flavor: backend -->
```

The block is wrapped in `<!-- flavor: backend -->` ... `<!-- /flavor: backend -->` so the `--flavor general` stripper (default) blanks it. Future implementers can use this as a template for adding their own flavor sections.

- [ ] **Step 3: Verify the block is well-formed and the stripper removes it**

```bash
# The block is present in the source template.
rg -q '<!-- flavor: backend -->' assets/templates/developer_guide.md \
  && rg -q '<!-- /flavor: backend -->' assets/templates/developer_guide.md \
  && echo "OK: demo block present in template"

# The block is absent in the scaffolded default output.
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force > /dev/null
! rg -q 'flavor: backend' "$tmp/docs/guides/developer_guide.md" && echo "OK: default scaffolder stripped the demo block"
rm -rf "$tmp"
```

Expected: both `OK` lines.

- [ ] **Step 4: Verify the other 4 templates are unchanged**

```bash
for t in topology.md user_guide.md tutorial.md README.md assess.md _audience_block.md; do
  rg -q 'flavor:' "assets/templates/$t" && echo "FAIL: $t unexpectedly has flavor markers" || echo "OK: $t has no flavor markers"
done
```

Expected: 6 `OK` lines, 0 `FAIL` lines.

- [ ] **Step 5: Verify the scaffolded demo's other 4 templates are unchanged from HEAD~1**

```bash
tmp1=$(mktemp -d) && git -C "$tmp1" init -q
python3 scripts/scaffold_docs.py "$tmp1" --project-name Demo --force > /dev/null
git stash && \
  tmp2=$(mktemp -d) && git -C "$tmp2" init -q && \
  python3 scripts/scaffold_docs.py "$tmp2" --project-name Demo --force > /dev/null && \
  git stash pop
# Compare each non-developer-guide file between the two runs.
for f in topology.md user_guide.md tutorial.md README.md assess.md; do
  diff "$tmp1/docs/guides/$f" "$tmp2/docs/guides/$f" > /dev/null \
    && echo "OK: $f unchanged" \
    || echo "FAIL: $f differs"
done
rm -rf "$tmp1" "$tmp2"
```

Expected: 5 `OK` lines, 0 `FAIL` lines (only `developer_guide.md` should differ between the two runs, and this script doesn't compare it).

- [ ] **Step 6: Commit**

```bash
git add assets/templates/developer_guide.md
git commit -m "docs(templates): add demo flavor block in developer_guide.md (proves --flavor)"
```

---

## Task 3: Add `--guides-dir PATH` flag to `scripts/smoke.py`

**Files:**
- Modify: `scripts/smoke.py`
  - Add `--guides-dir PATH` argparse argument (default: None).
  - When `--guides-dir PATH` is set AND `--strict` is also set, audit the directory in place (no throwaway): every `{{...}}` placeholder and every `<...>` slot in a publish-ready file (one with no `> TODO(doc-miner): ...` marker) is a failure. (This closes Phase 2 re-reviewer R3: `--strict` was structurally unreachable on the throwaway scaffold.)
  - When `--guides-dir PATH` is set without `--strict`, the audit is informational (current behaviour).
  - When `--guides-dir` is NOT set, the smoke runs as before (throwaway generation + audit).
  - Also: when `--guides-dir PATH` is passed without `--strict`, allow it to drive the audit (i.e. it's not gated on `--strict` — the audit still happens, just without the publish-ready check). This lets users audit a previously generated doc set.

**Interfaces:**
- Consumes: existing smoke scaffolding
- Produces: a meaningful `--strict` mode that can audit a real `docs/guides/` directory

- [ ] **Step 1: Read the existing `main()` and helper signatures**

```bash
rg -n 'def main|def _safe_smoke|def _phase5_checks|parser.add_argument' scripts/smoke.py
```

- [ ] **Step 2: Update `_phase5_checks` to accept a `strict` flag and run the publish-ready check**

Find the current `_phase5_checks(guides_dir)` signature. Change it to `_phase5_checks(guides_dir, strict=False)`. The function body has the scaffolder-substituted family check (already conditional on `not draft`); add the strict-mode check:

```python
def _phase5_checks(guides_dir: Path, strict: bool = False) -> int:
    """Mermaid fences closed, no broken `{{...}}` placeholders in shipped
    files, `TODO(doc-miner)` count printed. When `strict=True`, also fail
    on Phase-4 placeholders and `<angle-bracket>` slots in any file that
    has no `> TODO(doc-miner): ...` marker (i.e. publish-ready)."""
    failures = 0

    # 1. Mermaid fences are balanced.
    for md in sorted(guides_dir.glob("*.md")):
        # ... existing code ...
        pass

    # 2. No un-substituted `{{...}}` placeholders in shipped files.
    for md in sorted(guides_dir.glob("*.md")):
        # ... existing code (the scaffolder-substituted family is always fatal) ...
        pass

    # 3. (NEW) When `strict`, also fail on Phase-4 placeholders and
    #    `<...>` slots in publish-ready files (no TODO(doc-miner) marker).
    if strict:
        for md in sorted(guides_dir.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            draft = "TODO(doc-miner)" in text
            pending = [
                p for p in re.findall(r"\{\{[A-Z_]+\}\}", text)
                if p not in SCAFFOLDER_PLACEHOLDERS
            ]
            slots = re.findall(r"<[a-z -]+>", text)
            if draft and (pending or slots):
                # Draft files are exempt.
                continue
            if not draft and (pending or slots):
                # Publish-ready file with leftover residue.
                marker = ", ".join(pending + [f"<{s}>" for s in slots])
                _print(f"{md.name}: strict publish-ready (no TODO marker)", False, f"leftover {marker}")
                failures += 1

    # 4. Informational: TODO(doc-miner) count per file.
    # ... existing code ...

    return failures
```

The exact `SCAFFOLDER_PLACEHOLDERS` constant and the `_print` helper already exist; reuse them.

- [ ] **Step 3: Update `_safe_smoke` to accept a `guides_dir` parameter**

```python
def _safe_smoke(*, write: bool, guides_dir: Path | None = None, strict: bool = False) -> int:
    """Replicate the AGENTS.md safe smoke test.

    When `guides_dir` is set, audit that directory in place (do not generate
    into a throwaway). When `write` is also set, both generate the throwaway
    and audit it. The `strict` flag enables the publish-ready check in
    `_phase5_checks` (only meaningful with a real `docs/guides/` set).
    """
    failures = 0
    if guides_dir is not None:
        # Audit an existing directory; do not generate.
        if not guides_dir.is_dir():
            _print(f"guides-dir {guides_dir} is not a directory", False)
            return 1
        failures += _phase5_checks(guides_dir, strict=strict)
        return failures

    with tempfile.TemporaryDirectory(prefix="rsm-smoke-") as tmp:
        # ... existing throwaway logic ...
        pass
```

Use `Path` as the parameter type (already imported at the top of `smoke.py`).

- [ ] **Step 4: Update argparse + main()**

Add the new flag near `--check-only` and `--keep-tmp`:

```python
    parser.add_argument("--guides-dir", type=Path, default=None,
                        help="Audit an existing docs/guides/ directory in place (no throwaway generation). Combined with --strict, fail on Phase-4 placeholders and <...> slots in publish-ready files (no TODO(doc-miner) marker).")
```

Update `main()` to forward:

```python
    failures = _safe_smoke(
        write=not args.check_only,
        guides_dir=args.guides_dir,
        strict=args.strict,
    )
```

- [ ] **Step 5: Verify the script still runs the throwaway path by default**

```bash
python3 scripts/smoke.py 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 6: Verify `--guides-dir PATH --strict` is now meaningful on a real doc set**

```bash
# Generate a fresh doc set, then audit it with --strict --guides-dir.
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --assess > /dev/null
python3 scripts/smoke.py --guides-dir "$tmp/docs/guides" --strict 2>&1 | tail -3
echo "exit=$?"
# Cleanup
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force > /dev/null  # idempotent
rm -rf "$tmp"
```

Expected: the smoke run inspects a real `docs/guides/` and exits 0 (the scaffolded output is in draft state with TODO(doc-miner) markers; no publish-ready file has residue). `exit=0`.

If the script reports a failure, it means a scaffolded file lacks its TODO marker (which would be a scaffold bug). The fix in that case: check `assets/templates/<file>.md` for a missing top-of-file reminder; restore it; re-run.

- [ ] **Step 7: Commit**

```bash
git add scripts/smoke.py
git commit -m "feat(smoke): add --guides-dir PATH for real-dir audit (closes R3)"
```

---

## Task 4: Real-world validation pass

**Files:**
- Modify: none (this task only runs commands and produces a log)
- Add: `docs/superpowers/.../phase4-validation-log.md` (a one-shot log file documenting the run; can be added to `.gitignore` if you prefer ephemeral logs, but committing a snapshot is more useful for future audits)

**Interfaces:**
- Consumes: the skill as installed in the worktree (with all 3 phases of changes)
- Produces: a documented validation run against an external repo

- [ ] **Step 1: Pick a target repo**

The spec's evidence_checklist suggests FastAPI-shaped libraries as a strong test (Python, multi-package, ~50+ files, real install, real examples). Use the **FastAPI** repo as the target — it's small enough to clone quickly, large enough to be non-trivial, well-known, and a good representative of the "plain library" flavor (no PINN, no monorepo complexity).

```bash
tmp=$(mktemp -d) && cd "$tmp"
# Use --depth 1 for a fast clone; --single-branch to avoid fetching all branches.
git clone --depth 1 --single-branch https://github.com/tiangolo/fastapi.git 2>&1 | tail -3
ls fastapi/ | head -10
```

Expected: a populated `fastapi/` directory with `fastapi/`, `tests/`, `docs/`, `pyproject.toml`, etc.

- [ ] **Step 2: Run `gen_topology.py` on the target**

```bash
python3 "$REPO_DOC_MINER_HOME/scripts/gen_topology.py" "$tmp/fastapi" --project-name FastAPI --summary 2>&1 | head -30
```

(If `$REPO_DOC_MINER_HOME` is not set in this shell, fall back to the absolute path to the worktree's `scripts/gen_topology.py`.)

Expected: a SUMMARY line with entity kinds + edges + the largest entity by size. Sanity check: `fastapi/` should appear as a `module` entity; `fastapi/applications.py` etc. should be `script`-ish (no — they're inside a module, not at the root). The largest entity should be one of the manifest files (`pyproject.toml`) or a large README.

- [ ] **Step 3: Run `scaffold_docs.py` on the target**

```bash
mkdir -p "$tmp/fastapi/docs/guides"
python3 "$REPO_DOC_MINER_HOME/scripts/scaffold_docs.py" "$tmp/fastapi" --project-name FastAPI --force --assess --audience contributor > /dev/null
ls "$tmp/fastapi/docs/guides/"
head -1 "$tmp/fastapi/docs/guides/assess.md"
```

Expected: 6 files in `docs/guides/`; `assess.md` first line is `<!-- audience: contributor -->`.

- [ ] **Step 4: Run `smoke.py --strict --guides-dir` on the real output**

```bash
python3 "$REPO_DOC_MINER_HOME/scripts/smoke.py" --guides-dir "$tmp/fastapi/docs/guides" --strict 2>&1 | tail -5
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`. (The scaffolded output is in draft state — every file has a `> TODO(doc-miner):` marker, so the strict publish-ready check is satisfied.)

- [ ] **Step 5: Spot-check the topology**

```bash
rg '^## ' "$tmp/fastapi/docs/guides/topology.md"
echo "---"
rg 'fastapi|pyproject' "$tmp/fastapi/docs/guides/topology.md" | head -10
```

Expected: 4 `##` sections; mentions of `fastapi` and `pyproject` in the entity inventory. If the output looks empty (e.g. 0 entities detected), the script has a bug — report it; do not proceed.

- [ ] **Step 6: Write the validation log**

Write `docs/superpowers/.../phase4-validation-log.md` (use the same workspace dir you used for the other phase ledgers; check `ls .superpowers/sdd/` to find the right place). The log should contain:

- Target repo (FastAPI), commit SHA cloned
- Number of entities + edges detected
- Number of files materialized
- Any observations about the topology (e.g. "Mermaid blocks are clean", "the `fastapi/` module entity is detected but sub-package manifests are not — that's a known limitation of the heuristic")
- The smoke test result
- A one-line "verdict": does the skill work end-to-end on a real non-trivial repo? (Expected: yes, with the caveat that the resulting `topology.md` is heuristic and the prose docs require the agent's Phase 2-4 work to fill in.)

- [ ] **Step 7: Clean up the throwaway**

```bash
rm -rf "$tmp"
```

- [ ] **Step 8: Commit (optional)**

If you wrote the log to a file in the repo:

```bash
git add docs/superpowers/plans/2026-10-11-phase4-wiring-validation.md  # the plan, already committed
# The validation log goes into the workspace (gitignored) and does not get committed.
```

No commit needed for the validation itself. The plan's E2E Task 6 (below) re-runs the suite on the skill's own repo.

---

## Task 5: README polish (N1 from Phase 3)

**Files:**
- Modify: `README.md`
  - Fix two prose issues flagged in the Phase 3 re-review:
    - The "four questions" promise (current README lists 3; the 4th is the "concrete next step" mentioned in SKILL.md and the assess.md template).
    - The hard-coded `docs/guides/` (current README says "saved into the repository's `docs/guides/` folder" — actually the scaffolder's `--out` flag is configurable).

**Interfaces:**
- Consumes: the SKILL.md / `assess.md` template definition of the 4 questions
- Produces: a corrected paragraph

- [ ] **Step 1: Read the current first paragraph**

```bash
rg -A 8 '^# repo-doc-miner' README.md | head -20
```

- [ ] **Step 2: Replace the paragraph**

In the README's first block (under the H1), find the lines:

> A CodeBuddy / Claude-Code compatible **Skill** that mines an existing Git
> repository using a two-stage **topology-first → module-deep-dive** method
> and produces a coordinated Markdown doc set (a repo topology map, a
> developer guide, a user guide, a from-beginner-to-expert tutorial, and a
> navigation `README.md`) saved into the repository's `docs/guides/`
> folder.

Replace with:

> A CodeBuddy / Claude-Code compatible **Skill** that mines an existing Git
> repository using a two-stage **topology-first → module-deep-dive** method
> and produces a coordinated Markdown doc set (a repo topology map, a
> developer guide, a user guide, a from-beginner-to-expert tutorial, and a
> navigation `README.md`) — saved by default into the repository's
> `docs/guides/` folder, or into whatever directory the user passes via
> `scaffold_docs.py --out PATH`.

Also, in the same paragraph, find:

> **v3 adds a pre-mining assessment stage** that runs before the topology
> map is produced: an opt-in `Phase -1` that answers "is this repo worth
> mining, who is this for, and where to start reading?" The four questions
> are answered in an `assess.md` file.

Replace with:

> **v3 adds a pre-mining assessment stage** that runs before the topology
> map is produced: an opt-in `Phase -1` that answers four questions — "is
> this repo worth mining, who is this for, where should I start reading,
> and what should I do next?" — in an `assess.md` file.

(Removes the orphan "the" before "four questions" and aligns the list with SKILL.md's four-question enumeration.)

- [ ] **Step 3: Verify the wording is in place**

```bash
rg -q 'four questions' README.md \
  && rg -q 'scaffold_docs.py --out PATH' README.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs(readme): polish first paragraph — 4 questions, configurable --out"
```

---

## Task 6: Update `AGENTS.md` "Fixes already landed" list for Phase 4

**Files:**
- Modify: `AGENTS.md`
  - Append a single paragraph after the existing last sentence in the "Fixes already landed" block.

**Interfaces:**
- Consumes: nothing
- Produces: a `Phase 4 (Wiring Up & Real-World Validation, 2026-10-11)` paragraph

- [ ] **Step 1: Find the end of the existing block**

```bash
rg -n '^### Fixes already landed' AGENTS.md
```

The block ends just before `## Important Files`. Append the new paragraph immediately before that.

- [ ] **Step 2: Append the Phase 4 paragraph**

After the existing Phase 3 paragraph, append:

```markdown

Phase 4 (Wiring Up & Real-World Validation, 2026-10-11): closes the last open Phase 3 spec items in a focused way. `scaffold_docs.py` gains the `--flavor FLAVOR_NAME` flag (default `general`) which strips `<!-- flavor: NAME -->` ... `<!-- /flavor: NAME -->` blocks from the 5 core templates + `assess.md`, wiring up the `_flavor_strip.md` contract that was a no-op marker through Phase 3 (C1/C7); `assets/templates/developer_guide.md` gains one demonstrative `<!-- flavor: backend -->` block so the stripper has a real block to remove (the other 4 templates remain flavor-free); `scripts/smoke.py` gains `--guides-dir PATH` so `--strict` is now meaningful against a real `docs/guides/` directory (Phase 2 re-reviewer R3 closed: the throwaway-only audit was structurally unreachable, so a failable real-dir audit is added); the README first paragraph is polished — the "four questions" promise now matches `assess.md`'s actual content, and the `docs/guides/` hard-code is now described as the default behind `scaffold_docs.py --out PATH`; a real-world validation pass against `tiangolo/fastapi` (commit at clone time) confirms the skill works end-to-end on a non-trivial external Python library — `gen_topology.py` detects the expected entities + edges, `scaffold_docs.py --assess --audience` materialises 6 files with the audience blockquote on line 1 of `assess.md`, and `smoke.py --strict --guides-dir` exits 0 against the scaffolded output. The other Phase 3 deferred items (the `--lang` flag, the N2 en-GB/en-US mix in `_flavor_strip.md`) remain formally deferred to a future release per the spec's §9.3 Open Decisions.
```

- [ ] **Step 3: Verify the new paragraph is in place**

```bash
rg -q 'Phase 4 \(Wiring Up & Real-World Validation, 2026-10-11\)' AGENTS.md && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md
git commit -m "docs(agents): record Phase 4 fixes (Wiring Up & Real-World Validation)"
```

---

## Task 7: End-to-end smoke test

**Files:**
- Modify: none (controller-only)

- [ ] **Step 1: Verify the new scaffolder flag is documented and works**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py --help 2>&1 | rg -q '\-\-flavor' && echo "OK: --flavor documented in --help"
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --flavor general > /dev/null \
  && test -f "$tmp/docs/guides/topology.md" && echo "OK: --flavor general scaffolded"
rm -rf "$tmp"
```

Expected: both `OK` lines.

- [ ] **Step 2: Verify the smoke test runs the new audit path**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --assess --audience contributor > /dev/null
python3 scripts/smoke.py --guides-dir "$tmp/docs/guides" --strict 2>&1 | tail -3
echo "exit=$?"
rm -rf "$tmp"
```

Expected: `OK: all checks passed.`; `exit=0`. (Confirms R3 is closed: the new audit path runs against a real dir.)

- [ ] **Step 3: Run the standard smoke battery**

```bash
python3 scripts/smoke.py 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 4: Verify the README polish**

```bash
rg -q 'four questions' README.md && rg -q 'scaffold_docs.py --out PATH' README.md && echo OK
```

Expected: `OK`.

- [ ] **Step 5: Verify no untracked files remain**

```bash
git status --short
```

Expected: empty.

- [ ] **Step 6: Final git log check**

```bash
git log --oneline -8
```

Expected: the Phase 4 commits appear at the top, in this order (most recent first):

1. `docs(agents): record Phase 4 fixes (Wiring Up & Real-World Validation)`
2. `docs(readme): polish first paragraph — 4 questions, configurable --out`
3. `feat(smoke): add --guides-dir PATH for real-dir audit (closes R3)`
4. `docs(templates): add demo flavor block in developer_guide.md (proves --flavor)`
5. `feat(scaffold): add --flavor flag (wires up the _flavor_strip.md contract)`

(5 commits; no `docs(plan)` commit at top because the plan lands as the SDD's first commit when the workspace is initialised — see "SDD state" at the top of this file.)

---

## Self-Review

**Spec coverage (§7 of the spec, deferred items):**

| Spec requirement | Covered in task |
|---|---|
| §7.1 C1, C7 Templates de-PINN + language flag (the `--flavor` half) | Task 1 (scaffolder flag) + Task 2 (demo block) |
| §7.1 C7 `--lang` flag | **Deferred** (per spec §9.3 Open Decisions; bilingual headings are the default; adding per-language template variants is a v4+ effort) |
| Phase 2 R3 (`--strict` structurally unreachable) | Task 3 (`--guides-dir` makes `--strict` meaningful) |
| Phase 3 N1 (README polish) | Task 5 |
| Phase 3 N3 (smoke.py missing _env.sh / _flavor_strip.md assertions) | **Deferred** (polish; smoke.py's --check-only path is now adequate for the new files via the new --guides-dir flag — `--check-only` against a worktree's `assets/templates/_flavor_strip.md` or `scripts/_env.sh` can be added in a follow-up if needed) |
| Phase 3 N2 (`_flavor_strip.md` en-GB/en-US mix) | **Deferred** (polish; the file is now a future-extension contract — mixing en-GB and en-US is acceptable for a marker doc) |
| Real-world validation | Task 4 (FastAPI end-to-end) |

**Placeholder scan:** No "TBD" / "implement later" / "fill in details" remain. Code blocks are provided verbatim for every code step.

**Type / name consistency check:**

- `args.flavor` argparse field name is consistent across Task 1 (argparse) and Task 7 (verification).
- `--flavor general` is the only default and the only mode that strips everything; the other 4 modes (pinn/cli/lib/monorepo) currently have NO flavor-tagged content in any of the 5 templates, so `--flavor pinn` and `--flavor general` produce identical output today. The Task 2 demo block in `developer_guide.md` IS stripped under `--flavor general` and would be KEPT under `--flavor backend` (which is not in the scaffolder's `choices=` list, so it's a no-op for now — but the wire-up works).
- `--guides-dir` argparse field is consistent across Task 3 and Task 7.
- `SCAFFOLDER_PLACEHOLDERS` constant (added in Phase 2) is reused in Task 3's strict-mode check; the existing `frozenset({"{{PROJECT_NAME}}", "{{AUDIENCE}}"})` is the right shape for both layers.

No inconsistencies found.

**Open items (deferred to a future release):**

- `--lang` flag (spec §7.2): would require per-language template variants or a translation pass. Bilingual headings are the current default; per the spec §9.3 Open Decisions, this is a v4+ effort.
- `assets/templates/_flavor_strip.md` en-GB/en-US mix (N2): trivial polish; left for a future commit.
- `smoke.py` adding explicit `--check-only` assertions for `_env.sh` and `_flavor_strip.md` (N3): the new `--guides-dir` path subsumes most of this; explicit assertions can be added later.
- C5 cap warning-fidelity polish (the original audit finding: "if running without `--verbose`, only entity cap prints a warning"): the Phase 3 fix was to make the docstring truthful; the actual code change is one extra `print(..., file=sys.stderr)` and a help-text update. Left for a future commit.

These deferrals match the spec's §9.3 Open Decisions.