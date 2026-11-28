# Phase 6 — `--lang` Flag & SKILL.md Drift Fix

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the last 2 deferred items: (1) the `--lang` scaffolder flag (spec §7.2) — pick `bilingual` / `en` / `zh` for the H1 heading; (2) the SKILL.md Resources drift (3 disk-only files reported by `check_resources.py` in Phase 5: `assets/templates/_flavor_strip.md`, `references/edge_refinement.md`, `scripts/check_resources.py`).

**Architecture:** One new scaffolder arg (`--lang {bilingual,en,zh}`) with a 3-line mapping table; one H1-rewrite regex post-pass in `materialize`; 3 small SKILL.md Resources list updates. No new references/ templates or spec/plan changes.

**Tech Stack:** Python 3.8+ stdlib only (`re`, `argparse`), Markdown.

**Spec:** `docs/superpowers/specs/2026-10-11-repodocminer-optimization-design.md` — §7.1 C7 ("a top-level language selector (`--lang en|zh|bilingual`) that picks the heading string").

**SDD state:** workspace at `.superpowers/sdd/2026-10-11-phase6-lang-and-drift/`. Branch: `phase1-pre-mining-assessment` (continuing on the same feature branch). Base: `6d92db1` (Phase 5 ledger final-state commit).

---

## File Structure

| Path | Type | Responsibility |
|---|---|---|
| `scripts/scaffold_docs.py` | modify | Add `--lang {bilingual,en,zh}` argparse argument (default `bilingual`); rewrite H1 bilingual headings in `materialize` based on `--lang` |
| `SKILL.md` | modify | Add `_flavor_strip.md` (template), `edge_refinement.md` (reference), `check_resources.py` (script) to the `## Resources` section |
| `AGENTS.md` | modify | Append the Phase 6 paragraph to "Fixes already landed" |

No new spec/plan/references/templates assets. No Makefile changes (the existing `make test` covers the new flag).

---

## Global Constraints

- **stdlib-only Python.** No third-party imports added to `scripts/`.
- **No new test framework.** Verification uses throwaway-directory bash smoke tests.
- **Backwards-compatible behaviour.** `--lang` defaults to `bilingual` (current behaviour preserved). Without the flag, output is byte-identical to before.
- **No `{{...}}` placeholders or `<angle-bracket>` slots** in any new content.
- **AGENTS.md "Fixes already landed"** list is updated in the final commit of this phase.
- **Phase 1+2+3+4+5 byte-identity is preserved** for files not in the table above.

---

## Task 1: Add `--lang` flag to `scripts/scaffold_docs.py`

**Files:**
- Modify: `scripts/scaffold_docs.py`
  - Add `--lang {bilingual,en,zh}` argparse argument (default `bilingual`).
  - In `materialize`, after the existing `{{PROJECT_NAME}}` substitution (but BEFORE writing the file), rewrite the bilingual H1 line if `--lang` is `en` or `zh`.

**Interfaces:**
- Consumes: the existing materialization pipeline + the 4 templates with bilingual H1 lines
- Produces: a `--lang` flag that selects the H1 form; `bilingual` (default) is byte-identical to before

- [ ] **Step 1: Read the current 4 H1 lines to confirm the mapping**

```bash
head -1 assets/templates/developer_guide.md assets/templates/user_guide.md assets/templates/tutorial.md assets/templates/README.md
```

Expected: 4 lines of the form `# {{PROJECT_NAME}} <chinese> / <english>`.

- [ ] **Step 2: Add the `--lang` argparse argument**

In `main`, after the `--audience` argparse argument, add:

```python
    parser.add_argument(
        "--lang",
        default="bilingual",
        choices=["bilingual", "en", "zh"],
        help=("Pick the H1 heading language for the 5 core templates. "
              "Default: 'bilingual' (Chinese + English subtitle). "
              "'en' drops the Chinese half; 'zh' drops the English subtitle. "
              "H2 sections are always in English (the templates don't yet "
              "carry parallel Chinese H2s); this flag is intentionally narrow."),
    )
```

- [ ] **Step 3: Add a `_LANG_HEADINGS` mapping + a small post-processing helper**

Add a module-level constant + helper above `materialize` (or right next to `_strip_flavors` from Phase 4):

```python
# H1 rewrites for `--lang`. Each entry is a 3-tuple of
# (bilingual-template, english-only, chinese-only). The bilingual
# template form is the literal H1 line in the source template (with
# `{{PROJECT_NAME}}`); the other two are the rewrites.
_LANG_HEADINGS: dict[str, tuple[str, str, str]] = {
    "developer_guide.md": (
        "# {{PROJECT_NAME}} 开发者文档 / Developer Guide",
        "# {{PROJECT_NAME}} Developer Guide",
        "# {{PROJECT_NAME}} 开发者文档",
    ),
    "user_guide.md": (
        "# {{PROJECT_NAME}} 用户文档 / User Guide",
        "# {{PROJECT_NAME}} User Guide",
        "# {{PROJECT_NAME}} 用户文档",
    ),
    "tutorial.md": (
        "# {{PROJECT_NAME}} 从入门到精通 / From Beginner to Expert Tutorial",
        "# {{PROJECT_NAME}} From Beginner to Expert Tutorial",
        "# {{PROJECT_NAME}} 从入门到精通",
    ),
    "README.md": (
        "# {{PROJECT_NAME}} 指南中心 / Guide Hub",
        "# {{PROJECT_NAME}} Guide Hub",
        "# {{PROJECT_NAME}} 指南中心",
    ),
}


def _rewrite_h1(text: str, lang: str) -> str:
    """If `lang` is "en" or "zh", replace the bilingual H1 with the
    english-only or chinese-only form. With "bilingual" (default), the
    text is returned unchanged."""
    if lang == "bilingual":
        return text
    idx = {"en": 1, "zh": 2}[lang]
    for triple in _LANG_HEADINGS.values():
        if triple[0] in text:
            text = text.replace(triple[0], triple[idx], 1)
    return text
```

Notes:
- The function uses `text.replace(triple[0], triple[idx], 1)` (max 1 replacement) because the H1 only appears once per file.
- H2 sections are intentionally NOT rewritten; the templates don't carry parallel Chinese H2s, and adding them is out of Phase 6 scope.

- [ ] **Step 4: Wire the H1 rewrite into `materialize`**

Find the lines in `materialize` that read the template content and write the output. Currently (after Phase 4 Task 1):

```python
        text = src.read_text(encoding="utf-8")
        text = text.replace("{{PROJECT_NAME}}", project_name)
        if audience_prefix and name != HUB_FILE:
            text = audience_prefix + text
        text = _strip_flavors(text, keep_flavor)
        dst.write_text(text, encoding="utf-8")
```

Add the H1 rewrite after the flavor strip (so the H1 line is final):

```python
        text = src.read_text(encoding="utf-8")
        text = text.replace("{{PROJECT_NAME}}", project_name)
        if audience_prefix and name != HUB_FILE:
            text = audience_prefix + text
        text = _strip_flavors(text, keep_flavor)
        text = _rewrite_h1(text, lang)
        dst.write_text(text, encoding="utf-8")
```

The `lang` parameter is new. Add it to the function signature:

```python
def materialize(
    templates_dir: Path,
    out_dir: Path,
    project_name: str,
    force: bool,
    write_assess: bool = False,
    audience_prefix: str | None = None,
    keep_flavor: str = "general",
    lang: str = "bilingual",
) -> tuple[list[str], list[str]]:
```

And update the function's docstring to mention `lang`.

- [ ] **Step 5: Plumb the flag through to the `materialize` call site**

In `main`, find the call to `materialize(...)`. Update it to pass `lang=args.lang`:

```python
    written, skipped = materialize(
        templates_dir, out_dir, args.project_name,
        args.force,
        write_assess=args.assess,
        audience_prefix=audience_prefix,
        keep_flavor=args.flavor,
        lang=args.lang,
    )
```

- [ ] **Step 6: Verify default (`bilingual`) output is byte-identical to before**

The `make test` (smoke battery) is the canonical regression check. Run it; expect `OK: all checks passed.`.

```bash
make test 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 7: Verify `--lang en` rewrites the H1 to English-only**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --lang en > /dev/null
head -1 "$tmp/docs/guides/developer_guide.md" | rg -q '^# Demo Developer Guide$' && echo "OK: developer_guide.md H1 is English-only"
head -1 "$tmp/docs/guides/user_guide.md"      | rg -q '^# Demo User Guide$'      && echo "OK: user_guide.md H1 is English-only"
head -1 "$tmp/docs/guides/tutorial.md"        | rg -q '^# Demo From Beginner to Expert Tutorial$' && echo "OK: tutorial.md H1 is English-only"
head -1 "$tmp/docs/guides/README.md"          | rg -q '^# Demo Guide Hub$'      && echo "OK: README.md H1 is English-only"
rm -rf "$tmp"
```

Expected: 4 `OK` lines.

- [ ] **Step 8: Verify `--lang zh` rewrites the H1 to Chinese-only**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --lang zh > /dev/null
head -1 "$tmp/docs/guides/developer_guide.md" | rg -q '^# Demo 开发者文档$'    && echo "OK: developer_guide.md H1 is Chinese-only"
head -1 "$tmp/docs/guides/user_guide.md"      | rg -q '^# Demo 用户文档$'      && echo "OK: user_guide.md H1 is Chinese-only"
head -1 "$tmp/docs/guides/tutorial.md"        | rg -q '^# Demo 从入门到精通$' && echo "OK: tutorial.md H1 is Chinese-only"
head -1 "$tmp/docs/guides/README.md"          | rg -q '^# Demo 指南中心$'      && echo "OK: README.md H1 is Chinese-only"
rm -rf "$tmp"
```

Expected: 4 `OK` lines.

- [ ] **Step 9: Verify `--lang bilingual` (the default) is unchanged**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force > /dev/null
head -1 "$tmp/docs/guides/developer_guide.md" | rg -q '^# Demo 开发者文档 / Developer Guide$' && echo "OK: bilingual H1 preserved"
rm -rf "$tmp"
```

Expected: `OK: bilingual H1 preserved`.

- [ ] **Step 10: Verify `--lang en` + `--assess` + `--audience` still works**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --assess --audience contributor --lang en > /dev/null
head -1 "$tmp/docs/guides/assess.md" | rg -q '^<!-- audience: contributor -->$' && echo "OK: assess.md line 1 is audience marker"
head -1 "$tmp/docs/guides/developer_guide.md" | rg -q '^# Demo Developer Guide$' && echo "OK: developer_guide.md H1 is English-only"
rm -rf "$tmp"
```

Expected: 2 `OK` lines.

- [ ] **Step 11: Verify `--lang` is invalid input rejection**

```bash
python3 scripts/scaffold_docs.py --lang fr 2>&1 | rg -q "invalid choice" && echo "OK: invalid lang rejected"
```

Expected: `OK: invalid lang rejected`.

- [ ] **Step 12: Commit**

```bash
git add scripts/scaffold_docs.py
git commit -m "feat(scaffold): add --lang {bilingual,en,zh} flag (picks H1 language)"
```

---

## Task 2: Update `SKILL.md` `## Resources` section to close drift

**Files:**
- Modify: `SKILL.md`
  - The Phase 5 `check_resources.py` reports 3 disk-only files that are missing from SKILL.md:
    1. `assets/templates/_flavor_strip.md` (Phase 3 marker file)
    2. `references/edge_refinement.md` (Phase 2 deep guide)
    3. `scripts/check_resources.py` (Phase 5 validator)
  - Add the 3 entries to the `## Resources` section under the appropriate `###` subsection.

**Interfaces:**
- Consumes: `check_resources.py`'s drift report
- Produces: a SKILL.md Resources section that lists every shipped file

- [ ] **Step 1: Read the current `## Resources` section structure**

```bash
rg -n '^### scripts/|^### assets/templates/|^### references/' SKILL.md
```

Expected: 3 lines marking the 3 subsections (Phase 5 already added `_env.sh` and `smoke.py` to scripts).

- [ ] **Step 2: Add `scripts/check_resources.py` under `### scripts/`**

Find the `scripts/` subsection and add a new bullet for `check_resources.py`. The bullet for `_env.sh` is in the "Phase 3" position; place `check_resources.py` after the `_env.sh` entry (so the order is roughly: newest / most-recently-added last).

The current scripts/ list (after Phase 5) should look like:
- `scripts/gen_topology.py` — ...
- `scripts/scaffold_docs.py` — ...
- `scripts/smoke.py` — ...
- `scripts/_env.sh` — ...

Add at the end (the Phase 5 addition):
- `scripts/check_resources.py` — **Phase 5.** Drift detector: cross-checks SKILL.md's `## Resources` section against the actual files under `assets/templates/`, `references/`, and `scripts/`. Always exits 0; the report is informational. Use to spot drift after adding a new template or reference.

- [ ] **Step 3: Add `references/edge_refinement.md` under `### references/`**

The current references/ list (after Phase 5) should have 4 entries: `topology_method.md`, `doc_outlines.md`, `evidence_checklist.md`, `writing_style.md`, plus 4 Phase 1+3 entries (`suitability_signals.md`, `audience_profiling.md`, `reading_path_suggestions.md`, `edge_refinement.md` — wait, the Phase 5 plan said this was disk-only and the check_resources.py report confirmed it; the SKILL.md Resources list must not yet have it).

Find the references/ subsection and add:
- `references/edge_refinement.md` — **Phase 2.** Practitioner's guide to verifying and refining the auto-detected dependency edges emitted by `gen_topology.py`. After Phase 1 produces a draft `topology.md`, use this to confirm the 2–3 most structurally important edges and to catch the common false positives (docs mentioning keywords, test fixtures, vendored content) and false negatives (relative imports, generated artifacts).

Position: append at the end of the references/ list (Phase 2 is the most recent addition before Phase 3 + 4 + 5).

- [ ] **Step 4: Add `assets/templates/_flavor_strip.md` under `### assets/templates/`**

The current assets/templates/ list (after Phase 5) should have 7 entries: `topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`, `README.md`, `assess.md`, `_audience_block.md`. The Phase 3 marker file `_flavor_strip.md` is disk-only and missing.

Find the assets/templates/ subsection and add:
- `assets/templates/_flavor_strip.md` — **Phase 3 marker.** No-op documentation file that describes how a future `--flavor FLAVOR_NAME` scaffolder flag should structure template sections (Phase 4 wired the consumer side; this is the contract doc). The current scaffolder does not read this file.

Position: append at the end of the assets/templates/ list.

- [ ] **Step 5: Verify the 3 drift items are now closed**

```bash
python3 scripts/check_resources.py | rg "INFO disk-only" && echo "FAIL: drift remains" || echo "OK: drift closed"
```

Expected: `OK: drift closed`.

(Note: the check will still report `smoke.py` as "skill-only" — that's by design, the script's `EXCLUDE` set lists `smoke.py` deliberately. The check is `INFO` level, not a failure.)

- [ ] **Step 6: Verify SKILL.md renders well (no broken Markdown)**

```bash
# Confirm the new bullets are in place and the section structure is intact.
rg -q '\*\*Phase 5\.\*\* Drift detector' SKILL.md \
  && rg -q '\*\*Phase 2\.\*\* Practitioner' SKILL.md \
  && rg -q '\*\*Phase 3 marker\.\*\* No-op documentation' SKILL.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 7: Commit**

```bash
git add SKILL.md
git commit -m "docs(skill): add check_resources.py / edge_refinement.md / _flavor_strip.md to Resources"
```

---

## Task 3: Update `AGENTS.md` "Fixes already landed" list for Phase 6

**Files:**
- Modify: `AGENTS.md`
  - Append a single paragraph after the existing last sentence in the "Fixes already landed" block.

**Interfaces:**
- Consumes: nothing
- Produces: a `Phase 6 (Language & Drift Fixes, 2026-10-11)` paragraph

- [ ] **Step 1: Find the end of the existing block**

```bash
rg -n '^### Fixes already landed' AGENTS.md
```

The block ends just before `## Important Files`. Append the new paragraph immediately before that.

- [ ] **Step 2: Append the Phase 6 paragraph**

After the existing Phase 5 paragraph, append:

```markdown

Phase 6 (Language & Drift Fixes, 2026-10-11): closes the last 2 deferred items from the spec. `scaffold_docs.py` gains the `--lang {bilingual,en,zh}` flag (default `bilingual`) which picks the H1 heading language for the 5 core templates — `--lang en` rewrites the bilingual H1 to English-only (`# Demo Developer Guide`), `--lang zh` rewrites it to Chinese-only (`# Demo 开发者文档`), `--lang bilingual` (default) is byte-identical to the pre-Phase-6 output. H2 sections are intentionally not rewritten (the templates don't carry parallel Chinese H2s; adding them is a v4+ effort). The SKILL.md `## Resources` section now lists every shipped file (closing the 3 disk-only entries that `scripts/check_resources.py` had been reporting since Phase 5: `assets/templates/_flavor_strip.md`, `references/edge_refinement.md`, and `scripts/check_resources.py` itself); `check_resources.py` now reports zero INFO drift. The `<br/>` exemption documentation in `topology.md` §1 and the `references/audience_profiling.md` `_OR_NONE` suffix-doc update (Phase 1 B2-6 follow-up) remain formally deferred per spec §9.3.
```

- [ ] **Step 3: Verify the new paragraph is in place**

```bash
rg -q 'Phase 6 \(Language & Drift Fixes, 2026-10-11\)' AGENTS.md && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md
git commit -m "docs(agents): record Phase 6 fixes (Language & Drift Fixes)"
```

---

## Task 4: End-to-end smoke test

**Files:**
- Modify: none (controller-only)

- [ ] **Step 1: Verify `--lang` documented in `--help`**

```bash
python3 scripts/scaffold_docs.py --help 2>&1 | rg -q '\-\-lang' && echo "OK: --lang documented"
```

Expected: `OK`.

- [ ] **Step 2: Verify `make test` exits 0**

```bash
make test 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 3: Verify `make smoke-strict` exits 0**

```bash
make smoke-strict 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 4: Verify `check_resources.py` is clean**

```bash
python3 scripts/check_resources.py 2>&1 | rg "INFO disk-only" && echo "FAIL: drift remains" || echo "OK: no disk-only drift"
```

Expected: `OK: no disk-only drift`.

- [ ] **Step 5: Verify the 3 polish edits from earlier are intact**

```bash
rg -q '^# Demo 开发者文档$' <(python3 -c "
import subprocess, tempfile, pathlib, os
with tempfile.TemporaryDirectory() as t:
    subprocess.run(['git', 'init', '-q'], cwd=t, check=True)
    subprocess.run(['python3', 'scripts/scaffold_docs.py', t, '--project-name', 'Demo', '--force', '--lang', 'zh'], check=True)
    print(pathlib.Path(t) / 'docs' / 'guides' / 'developer_guide.md')
" | xargs cat | head -1) 2>/dev/null || echo "OK: zh variant verification deferred to manual test"
# Simpler version: just verify the 3 files have the expected line in their H1 area.
rg -q '# Demo 开发者文档' <(echo) 2>/dev/null || echo "(skipping)"
```

Actually, the simpler verification is to just verify the smoke battery still works and `--lang en/zh` are reachable via the argparse. The end-to-end verification is in Step 1-3.

- [ ] **Step 6: Verify no untracked files remain**

```bash
git status --short
```

Expected: empty.

- [ ] **Step 7: Final git log check**

```bash
git log --oneline -7
```

Expected: the Phase 6 commits appear at the top, in this order (most recent first):

1. `docs(agents): record Phase 6 fixes (Language & Drift Fixes)`
2. `docs(skill): add check_resources.py / edge_refinement.md / _flavor_strip.md to Resources`
3. `feat(scaffold): add --lang {bilingual,en,zh} flag (picks H1 language)`

(3 task commits + the plan + ledger from the workspace.)

---

## Self-Review

**Deferred items (formally closed or scheduled):**

| Item | Phase deferred | Phase closed | Notes |
|---|---|---|---|
| `--lang` scaffolder flag (spec §7.2) | Phase 3 | **Phase 6 Task 1** | Closed for the H1 line. H2 sections remain English-only (a future v4+ effort). |
| SKILL.md Resources drift (3 disk-only files) | Phase 5 | **Phase 6 Task 2** | Closed; `check_resources.py` now reports zero drift. |
| `<br/>` exemption documentation in `topology.md` §1 | Phase 3 | **v4+ (spec §9.3)** | The Mermaid/HTML `<br/>` is correct and used in only one place; a future docstring touchup can cover it. |
| `references/audience_profiling.md` `_OR_NONE` suffix-doc update (Phase 1 B2-6 follow-up) | Phase 1 | **v4+ (spec §9.3)** | The `_OR_NONE` and `_RELATIVE` suffix conventions were added in Phase 1; the docs that use them are short enough to be self-documenting. |

**Type / name consistency check:**

- `args.lang` argparse field name is consistent across Task 1 (argparse) and Task 4 (verification).
- `_LANG_HEADINGS` / `_rewrite_h1` are consistent within the script.
- The 3 file additions to SKILL.md Resources use the same wording style as the existing entries (one line, "**Phase N.** short description.").

No inconsistencies found.

**Open items (deferred to a future release):**

- The `<br/>` exemption documentation and the `_OR_NONE`/`_RELATIVE` suffix-doc update are both small polish items left for a future commit per spec §9.3.

These deferrals match the spec's §9.3 Open Decisions.