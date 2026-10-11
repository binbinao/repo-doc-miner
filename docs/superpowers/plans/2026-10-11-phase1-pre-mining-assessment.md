# Phase 1 — Pre-Mining Assessment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Phase -1 "Pre-Mining Assessment" capability to `repo-doc-miner` that, before any topology generation runs, produces an `assess.md` answering "is this repo worth mining, who should read it, and where to start?" with two new optional flags on `scripts/scaffold_docs.py`.

**Architecture:** Three new `references/` files define the rubric (suitability signals, audience taxonomy, reading-path matrix). One new template (`assess.md`) and one reusable fragment (`_audience_block.md`) get materialized only when the user passes `--assess` / `--audience` to the scaffolder. `SKILL.md` gains a `Phase -1` section + a `Prerequisites` block + 4 new "When NOT to Use" entries; `AGENTS.md` bookkeeping is updated in the same commit. No third-party dependencies. Both new flags default to **off**, so the existing smoke test from `AGENTS.md` stays byte-identical.

**Tech Stack:** Python 3.8+ stdlib only (`argparse`, `pathlib`, `dataclasses`), Markdown templates.

**Spec:** [`docs/superpowers/specs/2026-10-11-repodocminer-optimization-design.md`](../specs/2026-10-11-repodocminer-optimization-design.md) — sections §5.1–§5.8.

---

## File Structure

| Path | Type | Responsibility |
|---|---|---|
| `references/suitability_signals.md` | new | Rubric for the "is it worth mining?" question |
| `references/audience_profiling.md` | new | Audience taxonomy + how to detect it |
| `references/reading_path_suggestions.md` | new | Audience × suitability → entry-point mapping |
| `assets/templates/assess.md` | new | Template the agent fills during Phase -1 |
| `assets/templates/_audience_block.md` | new | Reusable fragment prefixed to each doc when `--audience` is set |
| `scripts/scaffold_docs.py` | modify | Add `--assess` and `--audience` flags; conditional materialization |
| `SKILL.md` | modify | New `Phase -1` section + `Prerequisites` + expanded `When NOT to Use` |
| `AGENTS.md` | modify | Append to "Fixes already landed" list |

The scaffolder is the only code file touched in this phase; `gen_topology.py` is **not** changed (Phase 3 work).

---

## Global Constraints

- **stdlib-only Python.** No third-party imports added to `scripts/`.
- **No new test framework.** Verification uses throwaway-directory bash smoke tests, consistent with `AGENTS.md` "Testing & QA".
- **No templating engine.** Placeholders stay `{{UPPER_SNAKE_CASE}}`; the new fragment uses `<!-- audience: {{AUDIENCE}} -->` + a 2-line table.
- **Backwards-compatible flags.** Both new scaffolder flags default to **off**; without them, output is byte-identical to the current scaffolder.
- **Phase numbering preserved.** Existing phases remain `Phase 0–6`; new work lives at `Phase -1` (additive prefix only).
- **Headings monotonic.** Every new doc file starts at `#` (h1) and never skips a level.
- **Snippet cap ≤ 30 lines** (per `references/writing_style.md`).
- **AGENTS.md "Fixes already landed"** list is updated in the final commit of this phase.

---

## Task 1: Create `references/suitability_signals.md`

**Files:**
- Create: `references/suitability_signals.md`

**Interfaces:**
- Consumes: nothing (first file in the plan)
- Produces: a single Markdown doc that defines the suitability rubric; no code is produced by this task

- [ ] **Step 1: Write the file content**

Create `references/suitability_signals.md` with the exact content below.

```markdown
# Suitability Signals (Phase -1)

> **What this is.** A rubric the agent applies during `Phase -1 · Pre-Mining Assessment` to decide whether the target repository is worth generating a five-file doc set for. Score 0–5; hard vetoes force "skip — and why".
> **Where it lives in the workflow.** Loaded during Phase -1, alongside `audience_profiling.md` and `reading_path_suggestions.md`.

## Scoring rubric (six signals, 0–2 each → rescaled to 0–5)

| Signal | Source | 0 | 1 | 2 |
|---|---|---|---|---|
| **Size** | file count in repo (excluding `.git`, vendor) | < 5 | 5–500 | > 500 |
| **Vitality** | `git log -1 --format=%ct` (Unix timestamp) | > 2 years ago | 6 mo – 2 yrs | < 6 mo |
| **License** | presence + SPDX-recognised | absent | permissive copyleft only | clear permissive (MIT/Apache/BSD) |
| **Entry-point clarity** | `README.md` first paragraph + a recognisable manifest (`pyproject.toml` / `package.json` / `Cargo.toml` / `go.mod` / `pom.xml`) | neither | one | both |
| **Documentation quality** | existing `docs/` directory size + completeness | none | partial | substantial (≥ 5 Markdown files) |
| **Test/example presence** | `tests/` or `examples/` directory | neither | one | both |

**Score formula:** raw = sum of the six 0/1/2 columns (range 0–12); rescaled = `round(raw * 5 / 12, 1)` (maps 0–12 → 0–5). Bands: `4.0–5.0` = High (raw ≥ 10), `2.0–3.9` = Mid (raw 5–9), `0.0–1.9` = Low (raw 0–4).

## Hard vetoes (force score → 0 + emit skip reason)

A repo is **skipped without scoring** when any of the following holds:

1. **Archived** — best-effort detection: presence of `ARCHIVED.md`, or a README banner stating the project is archived/no longer maintained (e.g. `[![No Maintenance Intended](...)](...)`, or the strings `no longer maintained`, `archived`, or `sunset`).
2. **No license + no usage hint** — `LICENSE` (or `LICENSE.md`) is absent AND the README's first 200 lines contain none of: `Install`, `Usage`, `Quickstart`, `pip install`, `npm install`, `cargo install`, `go install`, `go get`, or a fenced `bash` block.
3. **Vendor fork** — no top-level source directory exists (only `node_modules/`, `dist/`, `vendor/`, `third_party/`, `*.egg-info/`).
4. **Too small** — fewer than 3 readable source files remain after applying the script's `IGNORE_DIRS` / `.gitignore` filtering.

When a veto fires, write `> TODO(doc-miner): skip — <veto reason>` to `assess.md` §1 and stop.

**Not-a-git fallback.** If `git log -1 --format=%ct` fails (target is not a Git repo, or has no commits), score Vitality = 0 and record the reason in `assess.md` §1. The other five signals are computed from the on-disk tree and remain valid.

## "Skip — and why" message template

When the agent decides to skip, emit one short paragraph that names the veto and points the user at a remediation (open an issue, request a license, etc.). Do not just say "skip".

## What this rubric deliberately does not do

- It does **not** score code quality (no Lint/Test-Coverage/Type-Check signal). Those are runtime concerns; the skill's deliverable is documentation, and a low-quality repo still benefits from a clear map.
- It does **not** judge *whether the user can read the language*. That is captured by the audience profile, not the suitability score.
- It does **not** query GitHub / GitLab APIs. Detection is stdlib + `git log` only; out-of-band facts (stars, archived flag) are inferred from on-disk signals when possible and otherwise skipped silently.
```

- [ ] **Step 2: Verify the file exists and contains the required headings**

Run:
```bash
test -f references/suitability_signals.md \
  && rg -q '^## Scoring rubric' references/suitability_signals.md \
  && rg -q '^## Hard vetoes' references/suitability_signals.md \
  && rg -q '^## "Skip — and why" message template' references/suitability_signals.md \
  && rg -q '^## What this rubric deliberately does not do' references/suitability_signals.md \
  && echo OK
```

Expected: `OK`. Any non-zero exit or missing echo is a failure.

- [ ] **Step 3: Verify the file has no `{{...}}` placeholders and no `<angle-bracket>` slots**

Run:
```bash
! rg -q '\{\{[A-Z_]+\}\}' references/suitability_signals.md \
  && ! rg -q '<[a-z -]+>' references/suitability_signals.md \
  && echo OK
```

Expected: `OK`. Per `references/doc_outlines.md` placeholder convention, content files (not templates) must not carry unsubstituted placeholders. The tightened regex `<[a-z -]+>` matches slots containing spaces (e.g. `<entry file>`), unlike the previous `<[a-z-]+>` which only matched single-word slots.

- [ ] **Step 4: Commit**

```bash
git add references/suitability_signals.md
git commit -m "docs(refs): add suitability_signals.md (Phase -1 rubric)"
```

---

## Task 2: Create `references/audience_profiling.md`

**Files:**
- Create: `references/audience_profiling.md`

**Interfaces:**
- Consumes: nothing (parallel to Task 1; both are content-only)
- Produces: a Markdown doc that defines the six-bucket audience taxonomy and how to detect the dominant audience for a target repo

- [ ] **Step 1: Write the file content**

Create `references/audience_profiling.md` with the exact content below.

```markdown
# Audience Profiling (Phase -1)

> **What this is.** The taxonomy of reader personas and the on-disk signals the agent uses during `Phase -1 · Pre-Mining Assessment` to decide *who this doc set is for*.
> **Companion docs:** [`suitability_signals.md`](./suitability_signals.md) decides whether to mine; [`reading_path_suggestions.md`](./reading_path_suggestions.md) maps the chosen audience to an entry file.

## The six-bucket taxonomy

| Bucket | One-line definition | Best entry file |
|---|---|---|
| **first-time-end-user** | Has the repo installed (or about to) and wants to do a specific thing | `user_guide.md` §1–§11 + §18–§19 |
| **applied-engineer** | Knows the domain; needs the *recipe* matching their task | `tutorial.md` (matching chapter) |
| **contributor** | Wants to read source, extend the framework, or submit a PR | `developer_guide.md` (end-to-end) |
| **auditor** | Reviewing for security, licensing, code-quality, supply-chain risk | `topology.md` §1–§3 + `developer_guide.md` §15 |
| **learner** | No specific use case yet; wants a guided curriculum | `tutorial.md` Ch. 1 → 10 |
| **integrator** | Plugging the repo into another system (CI, IDE, automation) | `topology.md` + `developer_guide.md` §4–§5 |

The agent picks **at most two** buckets per target repo (a dominant + a secondary). Picking zero is allowed only when no signal matches; in that case the scaffolder must be invoked with no `--audience` flag (the audience block is omitted from all five files).

## Detection signals (on-disk, stdlib only)

The agent inspects the target repo and records one or more of:

| Signal | Where to look | Suggests |
|---|---|---|
| `README.md` first paragraph contains "API", "library", "import", "use X to …" | top of `README.md` | `first-time-end-user` |
| `README.md` first paragraph contains "tutorial", "course", "from beginner" | top of `README.md` | `learner` |
| Presence of `CONTRIBUTING.md`, `.github/CODEOWNERS`, `docs/development/`, or `docs/dev/` | repo root + `.github/` | `contributor` |
| `README.md` mentions "security", "audit", "compliance", "vulnerability" OR `SECURITY.md` exists | `README.md` + repo root | `auditor` |
| Presence of `examples/` with **≥ 5 runnable scripts** OR no top-level source code (only configs + examples) | `examples/` | `applied-engineer` |
| `pyproject.toml` `[project.scripts]` entry OR `package.json` `bin` field, OR explicit "CLI" / "command-line" wording | manifests | `integrator` |
| `pyproject.toml` `[project] classifiers` includes "Framework :: Django" / ":: Flask" / similar web framework | manifest | `integrator` (secondary) |

When signals disagree (e.g., `CONTRIBUTING.md` is present but the README also screams "API library"), the agent records both buckets and labels the secondary as "secondary" in the output. Do **not** silently overwrite.

## What this taxonomy deliberately does not include

- **Roles by seniority** (junior / senior / staff). The buckets above are use-case-agnostic so the same doc set serves any career stage.
- **Roles by company type** (startup / enterprise / academic). Use-case captures intent better than org type.
- **A "general" / "all" bucket.** No signal maps to "general"; if no signal matches, the agent picks nothing and the audience block is omitted.

## Output format in `assess.md`

The agent writes a 2-line summary at `assess.md` §2:

```
**Primary audience:** the chosen bucket — one-sentence rationale citing the signal
**Secondary audience (if any):** the chosen bucket — one-sentence rationale
```
```

- [ ] **Step 2: Verify the file exists and has the required sections**

Run:
```bash
test -f references/audience_profiling.md \
  && rg -q '^## The six-bucket taxonomy' references/audience_profiling.md \
  && rg -q '^## Detection signals' references/audience_profiling.md \
  && rg -q '^## What this taxonomy deliberately does not include' references/audience_profiling.md \
  && rg -q '^## Output format' references/audience_profiling.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Verify no unsubstituted placeholders**

Run:
```bash
! rg -q '\{\{[A-Z_]+\}\}' references/audience_profiling.md \
  && ! rg -q '<[a-z -]+>' references/audience_profiling.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add references/audience_profiling.md
git commit -m "docs(refs): add audience_profiling.md (Phase -1 taxonomy)"
```

---

## Task 3: Create `references/reading_path_suggestions.md`

**Files:**
- Create: `references/reading_path_suggestions.md`

**Interfaces:**
- Consumes: audience from `audience_profiling.md`, suitability score from `suitability_signals.md`
- Produces: a static matrix the agent reads during Phase -1 to fill `assess.md` §3

- [ ] **Step 1: Write the file content**

Create `references/reading_path_suggestions.md` with the exact content below.

```markdown
# Reading-Path Suggestions (Phase -1)

> **What this is.** The deterministic (audience × suitability-band) → entry-point mapping the agent uses to populate `assess.md` §3 ("Where to start reading") and §4 ("Reading suggestions").
> **Inputs:** primary audience (from [`audience_profiling.md`](./audience_profiling.md)), suitability score (from [`suitability_signals.md`](./suitability_signals.md), banded High/Mid/Low).
> **Outputs:** entry file, jump list (one or more `file#anchor` references), 1–3 concrete next-step actions.

## Suitability bands (re-stated for self-containment)

| Band | Score |
|---|---|
| **High** | 4.0 – 5.0 |
| **Mid** | 2.0 – 3.9 |
| **Low** | 0.0 – 1.9 |

When a hard veto from `suitability_signals.md` fires, the agent skips the matrix entirely and goes to the "Skip — and why" branch.

## The matrix

| Audience \\ Band | High | Mid | Low |
|---|---|---|---|
| `first-time-end-user` | `user_guide.md` §1–§11 + §18–§19 + `tutorial.md` Ch. 1–4 | `user_guide.md` §1–§11 + §19 only | Skip |
| `applied-engineer` | `tutorial.md` (chapter matching the task) | Same, narrower: just the matching chapter + its exercises | Skip |
| `contributor` | `developer_guide.md` end-to-end + `topology.md` §1–§3 | Same as High (full `developer_guide.md` + `topology.md` §1–§3) | Skip |
| `auditor` | `topology.md` + `developer_guide.md` §15 | `topology.md` only | Skip |
| `learner` | `tutorial.md` Ch. 1 → 10 (sequential) | `tutorial.md` Ch. 1–4, then re-assess | Skip |
| `integrator` | `topology.md` + `developer_guide.md` §4–§5 | `topology.md` only | Skip |

The matrix is a plain Markdown table — there is no programmatic logic. The agent reads the row that matches (audience, band) and uses its entry.

## "Skip" branch

When the band is Low (no veto) the agent writes one short paragraph naming the weakest signal and pointing the user at one remediation (e.g. "open an issue requesting a `LICENSE`" or "consider running on a more active fork"). Do **not** recommend `--force`; if the user wants to mine anyway, they can run the scaffolder without `--audience` and ignore the assess.md.

## Next-step actions (§4 of `assess.md`)

After picking the entry file, the agent writes 1–3 imperative actions. Templates:

- For High: `Open \`<entry file>\`. If the suggested section lands a working example within 30 minutes, treat the doc set as a fit; otherwise re-run \`Phase -1\` with a different audience.`
- For Mid: `Skim \`<entry file>\`'s first 100 lines. If the first concrete API or class matches what you need, proceed; otherwise stop.`
- For Skip: `<remediation sentence>; re-run \`Phase -1\` afterwards.`

These are starting points, not fixed wording — adjust per audience when needed (e.g., add `git clone` for an integrator audience).
```

- [ ] **Step 2: Verify the file exists and has the matrix**

Run:
```bash
test -f references/reading_path_suggestions.md \
  && rg -q '^## Suitability bands' references/reading_path_suggestions.md \
  && rg -q '^## The matrix' references/reading_path_suggestions.md \
  && rg -q '^## "Skip" branch' references/reading_path_suggestions.md \
  && rg -q '^## Next-step actions' references/reading_path_suggestions.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Verify no unsubstituted placeholders**

Run:
```bash
! rg -q '\{\{[A-Z_]+\}\}' references/reading_path_suggestions.md \
  && ! rg -q '<[a-z -]+>' references/reading_path_suggestions.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add references/reading_path_suggestions.md
git commit -m "docs(refs): add reading_path_suggestions.md (Phase -1 matrix)"
```

---

## Task 4: Create `assets/templates/assess.md`

**Files:**
- Create: `assets/templates/assess.md`

**Interfaces:**
- Consumes: `{{PROJECT_NAME}}` (single substitution target, like the other 5 templates)
- Produces: a fill-in template the agent materialises during Phase -1; scaffold_docs.py will read this in Task 6

- [ ] **Step 1: Write the file content**

Create `assets/templates/assess.md` with the exact content below. Note: the only `{{...}}` placeholder that the scaffolder substitutes is `{{PROJECT_NAME}}`. Everything else is the agent's job in Phase 4.

```markdown
# {{PROJECT_NAME}} — Pre-Mining Assessment

> Produced by `repo-doc-miner` **Phase -1 · Pre-Mining Assessment**. Generated **before** any topology or document is written. Read this first; if the verdict is "skip", stop here.
> Generated: {{ASSESS_DATE_OR_TODO}} · Target: `{{REPO_PATH}}`

## 1. Suitability

**Score:** {{SUITABILITY_SCORE}} ({{SUITABILITY_BAND}})

**Signal breakdown:**

| Signal | Score (0–2) | Evidence |
|---|---|---|
| Size | {{SIZE_SCORE}} | {{SIZE_EVIDENCE}} |
| Vitality | {{VITALITY_SCORE}} | {{VITALITY_EVIDENCE}} |
| License | {{LICENSE_SCORE}} | {{LICENSE_EVIDENCE}} |
| Entry-point clarity | {{ENTRY_SCORE}} | {{ENTRY_EVIDENCE}} |
| Documentation quality | {{DOCS_SCORE}} | {{DOCS_EVIDENCE}} |
| Test/example presence | {{TEST_EXAMPLE_SCORE}} | {{TEST_EXAMPLE_EVIDENCE}} |

> TODO(doc-miner): if any hard veto from `references/suitability_signals.md` fires, replace this whole section with a "Skip — and why" paragraph per that file's template, and mark the verdict in §5.

## 2. Audience

**Primary audience:** {{PRIMARY_AUDIENCE}} — {{PRIMARY_AUDIENCE_RATIONALE}}
**Secondary audience (if any):** {{SECONDARY_AUDIENCE_OR_NONE}} — {{SECONDARY_AUDIENCE_RATIONALE_OR_NONE}}

> Detection rubric: [`references/audience_profiling.md`](../../references/audience_profiling.md).

## 3. Where to start reading

**Entry file:** `{{ENTRY_FILE_RELATIVE}}`
**Jump list:** {{ENTRY_JUMP_LIST}}

> Matrix source: [`references/reading_path_suggestions.md`](../../references/reading_path_suggestions.md).

## 4. Reading suggestions

1. {{READING_SUGGESTION_1}}
2. {{READING_SUGGESTION_2}}
3. {{READING_SUGGESTION_3}}

## 5. Verdict

{{VERDICT_PARAGRAPH}}

---

> TODO(doc-miner): remove any remaining `{{...}}` placeholders before publishing. The `{{PROJECT_NAME}}` slot is filled by the scaffolder; every other `{{...}}` slot above is for the Phase -1 agent to fill from this run's findings.
```

- [ ] **Step 2: Verify the file exists, has the required headings, and contains only `{{PROJECT_NAME}}` as a non-comment marker**

Run:
```bash
test -f assets/templates/assess.md \
  && rg -q '^## 1\. Suitability' assets/templates/assess.md \
  && rg -q '^## 2\. Audience' assets/templates/assess.md \
  && rg -q '^## 3\. Where to start reading' assets/templates/assess.md \
  && rg -q '^## 4\. Reading suggestions' assets/templates/assess.md \
  && rg -q '^## 5\. Verdict' assets/templates/assess.md \
  && rg -q '\{\{PROJECT_NAME\}\}' assets/templates/assess.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Verify the file contains `> TODO(doc-miner)` markers consistent with the other templates**

Run:
```bash
rg -c '^> TODO\(doc-miner\)' assets/templates/assess.md
```

Expected: at least `2` matches (the two `> TODO(doc-miner): ...` blockquotes).

- [ ] **Step 4: Commit**

```bash
git add assets/templates/assess.md
git commit -m "feat(templates): add assess.md template (Phase -1 deliverable)"
```

---

## Task 5: Create `assets/templates/_audience_block.md`

**Files:**
- Create: `assets/templates/_audience_block.md`

**Interfaces:**
- Consumes: `{{AUDIENCE}}` placeholder substituted by scaffold_docs.py in Task 7
- Produces: a fragment that is prepended to each of the 5 generated docs when `--audience` is passed

- [ ] **Step 1: Write the file content**

Create `assets/templates/_audience_block.md` with the exact content below. The file is prefixed to every generated doc; the leading `<!-- audience: ... -->` is an HTML comment so renderers do not display it but machine tools can still parse it.

```markdown
<!-- audience: {{AUDIENCE}} -->

> **Audience:** {{AUDIENCE_LABEL}} — generated by `repo-doc-miner` `Phase -1 · Pre-Mining Assessment`. Other readers may find [`{{PROJECT_NAME}}` guide hub](./README.md) useful; their recommended entry file is on the hub's first page.

```

> **Note for the engineer:** the file ends with a literal blank line so concatenation produces a paragraph break before the original template's `#` heading. Do not strip the trailing blank line.

- [ ] **Step 2: Verify the file exists and contains the comment + table markers**

Run:
```bash
test -f assets/templates/_audience_block.md \
  && rg -q '^<!-- audience: \{\{AUDIENCE\}\} -->$' assets/templates/_audience_block.md \
  && rg -q '^\*\*Audience:\*\* \{\{AUDIENCE_LABEL\}\}' assets/templates/_audience_block.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Verify the file ends with a trailing newline so concatenation is clean**

Run:
```bash
tail -c 1 assets/templates/_audience_block.md | od -c | rg -q '\\n' && echo OK
```

Expected: `OK`. (This confirms the file ends in `\n` rather than trailing without one.)

- [ ] **Step 4: Commit**

```bash
git add assets/templates/_audience_block.md
git commit -m "feat(templates): add _audience_block.md fragment (Phase -1)"
```

---

## Task 6: Add `--assess` flag to `scripts/scaffold_docs.py`

**Files:**
- Modify: `scripts/scaffold_docs.py`
  - Lines 92–120 (the `main` function) — extend `argparse` to accept `--assess`.
  - Lines 51–78 (the `materialize` function) — extend signature to accept `write_assess: bool`; when true, write `assess.md` from `assess.md` template (it is **not** part of `TEMPLATE_FILES`).
  - Lines 1–15 (the module docstring) — extend the `Usage:` and `Exit codes:` blocks.
- Create: `scripts/scaffold_docs_test/` (used as scratch — see Step 6). The directory is **not** committed; it is only created during the smoke test and removed in Step 7.

**Interfaces:**
- Consumes: `assess.md` template (created in Task 4), `assess.md` flag value
- Produces: `assess.md` written to the output directory when `--assess` is set; no other behaviour change

- [ ] **Step 1: Update the module docstring (header) of `scripts/scaffold_docs.py`**

Find the existing `Usage` and `Exit codes` blocks. Replace them so the docstring reads:

```python
"""Scaffold the five-file doc set for the repo-doc-miner skill.

Creates <repo-root>/<out>/ and materializes the five Markdown templates
(topology, README, developer_guide, user_guide, tutorial) from the
skill's assets/templates/ directory, with a single {{PROJECT_NAME}}
placeholder substituted. All other {{...}} placeholders are intentionally
left in place so the CodeBuddy agent can fill them during Phase 4 of the
workflow described in SKILL.md.

When --assess is passed, additionally materializes the Phase -1
``assess.md`` template into the output directory. ``assess.md`` is the
pre-mining assessment deliverable (see references/suitability_signals.md,
references/audience_profiling.md, references/reading_path_suggestions.md).

Existing template files in the output directory are left untouched unless
--force is supplied, so a Phase-1 topology.md is never clobbered.

Usage
-----
    python scripts/scaffold_docs.py <repo-root> \
        --project-name "MyProject" \
        [--out docs/guides] \
        [--force] \
        [--assess]

Exit codes
----------
    0  success (files written and/or skipped)
    1  repo root does not exist, or the templates directory is missing
"""
```

Apply this by using the `edit` tool with the existing docstring as `old_string` and the new docstring as `new_string`. Verify the edit landed by running:

```bash
rg -q 'When --assess is passed' scripts/scaffold_docs.py && echo OK
```

Expected: `OK`.

- [ ] **Step 2: Extend `materialize` to optionally write `assess.md`**

Locate the existing `materialize` function. Replace its signature and the loop body so that:

1. The function accepts a new parameter `write_assess: bool` (after `force: bool`).
2. After the existing `for name in TEMPLATE_FILES:` loop, an additional block writes `assess.md` **only if** `write_assess` is `True` and `dst` does not yet exist (or `--force` is set).

The new function body is exactly:

```python
def materialize(
    templates_dir: Path,
    out_dir: Path,
    project_name: str,
    force: bool,
    write_assess: bool = False,
) -> tuple[list[str], list[str]]:
    """Write the missing templates; return (written, skipped) file names.

    When ``write_assess`` is True, also materialize ``assess.md`` (the
    Phase -1 deliverable). ``assess.md`` is independent of the
    ``TEMPLATE_FILES`` list — it only appears when the user opts in via
    ``--assess``, keeping the default behaviour unchanged.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    skipped: list[str] = []
    for name in TEMPLATE_FILES:
        src = templates_dir / name
        dst = out_dir / name
        if dst.exists() and not force:
            skipped.append(name)
            print(f"  skipped (exists): {dst}")
            continue
        text = src.read_text(encoding="utf-8")
        # Substitute only the project-name placeholder; all other
        # {{...}} placeholders are intentionally preserved so the
        # agent can fill them with evidence from Phase 2 of the
        # skill workflow.
        text = text.replace("{{PROJECT_NAME}}", project_name)
        dst.write_text(text, encoding="utf-8")
        written.append(name)
        print(f"  wrote {dst}")

    if write_assess:
        assess_src = templates_dir / "assess.md"
        assess_dst = out_dir / "assess.md"
        if not assess_src.is_file():
            print(f"  error: --assess requested but {assess_src} is missing",
                  file=sys.stderr)
            return written, skipped
        if assess_dst.exists() and not force:
            skipped.append("assess.md")
            print(f"  skipped (exists): {assess_dst}")
        else:
            text = assess_src.read_text(encoding="utf-8").replace(
                "{{PROJECT_NAME}}", project_name
            )
            assess_dst.write_text(text, encoding="utf-8")
            written.append("assess.md")
            print(f"  wrote {assess_dst}")

    return written, skipped
```

Apply the edit using `edit` (with the entire current `materialize` function as `old_string`). Verify:

```bash
rg -q 'def materialize\(' scripts/scaffold_docs.py \
  && rg -q 'write_assess: bool = False' scripts/scaffold_docs.py \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Add `--assess` to `argparse` and pass it through to `materialize`**

Inside `main`, find the `parser.add_argument` calls. After the existing `--force` argument, add:

```python
    parser.add_argument(
        "--assess",
        action="store_true",
        help="Additionally materialize the Phase -1 assess.md template. Default: off.",
    )
```

Then find the call `written, skipped = materialize(...)` and replace it with:

```python
    written, skipped = materialize(templates_dir, out_dir, args.project_name,
                                    args.force, write_assess=args.assess)
```

Verify:

```bash
rg -q '"--assess"' scripts/scaffold_docs.py \
  && rg -q 'write_assess=args.assess' scripts/scaffold_docs.py \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Update the final `print` line that reports counts (so users see `assess.md` in the summary)**

Find the line `print(f"Done. {len(written)} written, {len(skipped)} skipped.")` and replace it with:

```python
    print(f"Done. {len(written)} written, {len(skipped)} skipped.")
    if args.assess:
        assess_status = ("written" if "assess.md" in written
                         else "skipped" if "assess.md" in skipped
                         else "missing template")
        print(f"  assess.md: {assess_status}.")
```

Verify:

```bash
rg -q 'assess.md: {assess_status}' scripts/scaffold_docs.py && echo OK
```

Expected: `OK`.

- [ ] **Step 5: Sanity check the script's existing smoke test still passes (no flag, no regress)**

Run the existing AGENTS.md safe-smoke command in a throwaway directory:

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force 2>&1
test -f "$tmp/docs/guides/topology.md" \
  && test -f "$tmp/docs/guides/README.md" \
  && test ! -e "$tmp/docs/guides/assess.md" \
  && echo "OK: 5 files, no assess.md"
rm -rf "$tmp"
```

Expected: stdout ends with `Done. 5 written, 0 skipped.` (no `assess.md:` line). The throwaway contains exactly 5 files; `assess.md` is absent.

- [ ] **Step 6: Smoke test the new flag in a throwaway directory**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --assess 2>&1
test -f "$tmp/docs/guides/assess.md" \
  && rg -q '\{\{PROJECT_NAME\}\}' "$tmp/docs/guides/assess.md" \
  && ! rg -q '\{\{PROJECT_NAME\}\}' "$tmp/docs/guides/topology.md" \
  && echo "OK: assess.md written, PROJECT_NAME substituted"
rm -rf "$tmp"
```

Expected: stdout ends with `Done. 6 written, 0 skipped.` followed by `  assess.md: written.`. `assess.md` exists in the output directory and contains a substituted `{{PROJECT_NAME}}`; the other 5 templates do **not** mention `{{PROJECT_NAME}}` after substitution.

- [ ] **Step 7: Verify --assess is idempotent (second run skips, does not overwrite)**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --assess > /dev/null
md5sum "$tmp/docs/guides/assess.md" > /tmp/assess.md5
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --assess 2>&1 | rg -c 'skipped \(exists\): .*assess.md'
md5sum -c /tmp/assess.md5
rm -rf "$tmp" /tmp/assess.md5
```

Expected: stdout of the second run reports `1` skipped line for `assess.md`; `md5sum -c` reports `OK`.

- [ ] **Step 8: Commit**

```bash
git add scripts/scaffold_docs.py
git commit -m "feat(scaffold): add --assess flag (Phase -1)"
```

---

## Task 7: Add `--audience` flag to `scripts/scaffold_docs.py`

**Files:**
- Modify: `scripts/scaffold_docs.py`
  - `main` — add `--audience` to argparse; pass it to `materialize`.
  - `materialize` — accept `audience: str | None`; when set, prepend `_audience_block.md` to each of the 5 written/skipped template files (so re-runs see the same prefix).
- Test: scratch directory created and removed in Steps 6–7.

**Interfaces:**
- Consumes: `_audience_block.md` (created in Task 5), `{{AUDIENCE}}` substituted at write time
- Produces: each of the 5 generated docs prefixed with the audience block when `--audience` is set; `{{AUDIENCE}}` substituted to the value passed on the CLI

- [ ] **Step 1: Add `_audience_block.md` to the template directory check (so missing templates surface as errors)**

Find the call to `locate_templates_dir()` inside `main`. After it, add a check that the audience block fragment exists, returning exit 1 if not:

```python
    audience_block = templates_dir / "_audience_block.md"
    if not audience_block.is_file():
        print(f"error: audience block missing at {audience_block}; "
              "the skill package appears to be corrupt.", file=sys.stderr)
        return 1
```

Verify:

```bash
rg -q 'audience_block = templates_dir / "_audience_block.md"' scripts/scaffold_docs.py \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 2: Extend `materialize` signature with `audience: str | None`**

Update the `materialize` signature to:

```python
def materialize(
    templates_dir: Path,
    out_dir: Path,
    project_name: str,
    force: bool,
    write_assess: bool = False,
    audience: str | None = None,
) -> tuple[list[str], list[str]]:
```

Verify:

```bash
rg -q 'audience: str \| None = None' scripts/scaffold_docs.py && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Read and substitute the audience block once, then apply it to each template**

Replace the existing `materialize` body so that, after the `out_dir.mkdir(parents=True, exist_ok=True)` line and **before** the `for name in TEMPLATE_FILES:` loop, it reads and substitutes the fragment:

```python
    audience_prefix: str | None = None
    if audience:
        try:
            block = audience_block.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read audience block: {exc}", file=sys.stderr)
            return [], []
        audience_prefix = (block
            .replace("{{PROJECT_NAME}}", project_name)
            .replace("{{AUDIENCE}}", audience)
            .replace("{{AUDIENCE_LABEL}}", audience))
```

Wait — `audience_block` was defined in `main`, not `materialize`. To keep the function self-contained, pass the **path** of the audience block into `materialize`, or pass the **resolved prefix string** in. Choose the latter (no I/O inside the loop):

Replace `audience_prefix` derivation so it accepts the already-substituted prefix as a parameter. Add a new keyword arg `audience_prefix: str | None = None` and update the body to use it directly without re-reading the file.

Final signature:

```python
def materialize(
    templates_dir: Path,
    out_dir: Path,
    project_name: str,
    force: bool,
    write_assess: bool = False,
    audience_prefix: str | None = None,
) -> tuple[list[str], list[str]]:
```

Final body (the relevant block):

```python
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    skipped: list[str] = []
    for name in TEMPLATE_FILES:
        src = templates_dir / name
        dst = out_dir / name
        if dst.exists() and not force:
            skipped.append(name)
            print(f"  skipped (exists): {dst}")
            continue
        text = src.read_text(encoding="utf-8")
        # Substitute only the project-name placeholder; all other
        # {{...}} placeholders are intentionally preserved so the
        # agent can fill them with evidence from Phase 2 of the
        # skill workflow.
        text = text.replace("{{PROJECT_NAME}}", project_name)
        if audience_prefix:
            text = audience_prefix + text
        dst.write_text(text, encoding="utf-8")
        written.append(name)
        print(f"  wrote {dst}")
```

And for the assess.md branch:

```python
    if write_assess:
        assess_src = templates_dir / "assess.md"
        assess_dst = out_dir / "assess.md"
        if not assess_src.is_file():
            print(f"  error: --assess requested but {assess_src} is missing",
                  file=sys.stderr)
            return written, skipped
        if assess_dst.exists() and not force:
            skipped.append("assess.md")
            print(f"  skipped (exists): {assess_dst}")
        else:
            text = assess_src.read_text(encoding="utf-8").replace(
                "{{PROJECT_NAME}}", project_name
            )
            if audience_prefix:
                text = audience_prefix + text
            assess_dst.write_text(text, encoding="utf-8")
            written.append("assess.md")
            print(f"  wrote {assess_dst}")

    return written, skipped
```

Apply the edit (replace the previous `materialize` body). Verify:

```bash
rg -q 'audience_prefix: str \| None = None' scripts/scaffold_docs.py \
  && rg -q 'text = audience_prefix \+ text' scripts/scaffold_docs.py \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Add `--audience` argparse arg and resolve the prefix in `main`**

In `main`, after the `--assess` argument, add:

```python
    parser.add_argument(
        "--audience",
        default=None,
        metavar="NAME",
        help=("Prefix each generated doc with the audience block "
              "(_audience_block.md), substituting {{AUDIENCE}}. NAME is "
              "free-form (e.g. 'contributor', 'first-time-end-user'). "
              "Default: no audience block."),
    )
```

Then, after the audience-block existence check (Step 1) and before `materialize(...)`, compute `audience_prefix` once:

```python
    audience_prefix: str | None = None
    if args.audience:
        try:
            block = audience_block.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read audience block: {exc}", file=sys.stderr)
            return 1
        audience_prefix = (block
            .replace("{{PROJECT_NAME}}", args.project_name)
            .replace("{{AUDIENCE}}", args.audience)
            .replace("{{AUDIENCE_LABEL}}", args.audience))
```

Update the call to `materialize` so it passes the prefix:

```python
    written, skipped = materialize(templates_dir, out_dir, args.project_name,
                                    args.force, write_assess=args.assess,
                                    audience_prefix=audience_prefix)
```

Verify:

```bash
rg -q '"--audience"' scripts/scaffold_docs.py \
  && rg -q 'audience_prefix=audience_prefix' scripts/scaffold_docs.py \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 5: Re-run the no-flag smoke test from Task 6 Step 5 (no regress)**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force 2>&1 | tail -2
test ! -e "$tmp/docs/guides/assess.md" \
  && ! rg -q '<!-- audience:' "$tmp/docs/guides/topology.md" \
  && echo "OK: no flag = no assess.md, no audience block"
rm -rf "$tmp"
```

Expected: stdout ends with `Done. 5 written, 0 skipped.` (no `assess.md:` line). `assess.md` absent; `topology.md` has no `<!-- audience:` comment.

- [ ] **Step 6: Smoke test the `--audience` flag alone**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --audience contributor 2>&1 | tail -2
rg -q '^<!-- audience: contributor -->$' "$tmp/docs/guides/topology.md" \
  && ! rg -q '^<!-- audience: contributor -->$' "$tmp/docs/guides/README.md" \
  && rg -q '^\*\*Audience:\*\* contributor' "$tmp/docs/guides/user_guide.md" \
  && test ! -e "$tmp/docs/guides/assess.md" \
  && echo "OK: audience block in 4 non-hub files, README unchanged"
rm -rf "$tmp"
```

Expected: stdout ends with `Done. 5 written, 0 skipped.`. The 4 non-hub files (`topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`) start with `<!-- audience: contributor -->` followed by `**Audience:** contributor`. `README.md` is **not** prefixed. `assess.md` is absent.

- [ ] **Step 7: Smoke test `--assess --audience` together**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --assess --audience contributor 2>&1 | tail -2
rg -q '^<!-- audience: contributor -->$' "$tmp/docs/guides/assess.md" \
  && rg -q 'Demo' "$tmp/docs/guides/assess.md" \
  && echo "OK: assess.md has audience block + PROJECT_NAME substituted"
rm -rf "$tmp"
```

Expected: stdout ends with `Done. 6 written, 0 skipped.` followed by `  assess.md: written.`. `assess.md` starts with the audience comment and contains the substituted project name.

- [ ] **Step 8: Commit**

```bash
git add scripts/scaffold_docs.py
git commit -m "feat(scaffold): add --audience flag (Phase -1)"
```

---

## Task 8: Add `Phase -1 · Pre-Mining Assessment` section to `SKILL.md`

**Files:**
- Modify: `SKILL.md`
  - Insert a new section **before** the existing `### Phase 0 · Scope & Output Location` heading.
  - Numbering: the new section is `### Phase -1 · Pre-Mining Assessment`; existing `Phase 0–6` numbering is unchanged (additive prefix per spec §5.7).
- Test: grep + click-through read.

**Interfaces:**
- Consumes: `references/suitability_signals.md`, `references/audience_profiling.md`, `references/reading_path_suggestions.md` (all created in Tasks 1–3); `assets/templates/assess.md` (Task 4); `--assess` / `--audience` flags on `scaffold_docs.py` (Tasks 6–7)
- Produces: the new section text appended to `SKILL.md`

- [ ] **Step 1: Insert the new section before `### Phase 0`**

Find the line `### Phase 0 · Scope & Output Location` in `SKILL.md`. Insert the following block **immediately before** that line. (Use the `edit` tool with `### Phase 0` as the search anchor and the new block + `### Phase 0` line as the replacement, so the existing line is preserved.)

```markdown
### Phase -1 · Pre-Mining Assessment

> **Add this only when the user opts in.** Two optional scaffolder flags drive the new behaviour: `--assess` materialises `assets/templates/assess.md`; `--audience NAME` prefixes the four non-hub generated docs (`topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`) with the audience block (`assets/templates/_audience_block.md`). `README.md` is the hub and is **not** prefixed. Without either flag the skill behaves exactly as v2.

This phase answers four questions **before** any code is read or topology generated:

1. **Is this repo worth mining?** — apply the rubric in `references/suitability_signals.md`. Six signals, 0–2 each (max raw = 12), rescaled to 0–5 via `round(raw * 5 / 12, 1)`. Hard vetoes (archived, no license + no usage hint, vendor fork, < 3 source files) skip without scoring.
2. **Who is this for?** — pick one or two buckets from `references/audience_profiling.md`. Six buckets cover end-users, applied engineers, contributors, auditors, learners, and integrators.
3. **Where to start reading?** — apply the (audience × suitability-band) matrix in `references/reading_path_suggestions.md`.
4. **What concrete next step?** — write 1–3 imperative actions into `assess.md` §4.

#### Procedure

1. **Materialise the template** with the scaffolder (writes `assess.md` only when `--assess` is passed; the four non-hub docs are prefixed only when `--audience` is also passed):

   ```bash
   python scripts/scaffold_docs.py <repo-root> \
       --project-name "<DisplayName>" [--out docs/guides] \
       --assess [--audience <NAME>]
   ```

2. **Apply the rubric.** Compute the six signals using on-disk facts only (file counts, `git log -1 --format=%ct`, `LICENSE` presence, manifest presence, `docs/` directory size, `tests/` / `examples/` presence). The agent has all of these via standard file-listing tools; no API calls. If `git log` fails (target is not a Git repo, or has no commits), score Vitality = 0 and record the reason in `assess.md` §1.
3. **Pick the audience** using the detection signals in `audience_profiling.md` (README first paragraph, presence of `CONTRIBUTING.md` / `examples/` / framework classifiers, etc.). Record a primary + at most one secondary.
4. **Resolve the entry file and jump list** from the matrix in `reading_path_suggestions.md`.
5. **Fill `assess.md`.** Substitute every `{{...}}` placeholder with the run's findings; leave any genuinely unknown fact as `> TODO(doc-miner): <missing fact>`. Write the verdict paragraph in §5.
6. **If a hard veto fires,** replace §1 with a "Skip — and why" paragraph per the template in `suitability_signals.md`, and stop here. Do not start Phase 0.

The `assess.md` file is the **first deliverable** of the new flow and is referenced from `README.md` as the entry point for the doc set.

### Phase 0 · Scope & Output Location
```

(The last line is the existing `### Phase 0` heading — kept verbatim so the rest of `SKILL.md` is unchanged.)

Apply the edit. Verify:

```bash
rg -q '^### Phase -1 · Pre-Mining Assessment$' SKILL.md \
  && rg -q '^### Phase 0 · Scope & Output Location$' SKILL.md \
  && rg -q 'references/suitability_signals.md' SKILL.md \
  && rg -q 'references/audience_profiling.md' SKILL.md \
  && rg -q 'references/reading_path_suggestions.md' SKILL.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 2: Verify heading monotonicity (no level skips) in the inserted section**

Run:

```bash
awk '/^### Phase -1/,/^### Phase 0/' SKILL.md | rg -q '^#### Procedure$' && echo OK
```

Expected: `OK`. (Confirms `####` is used under `### Phase -1` only and no other levels appear in that span.)

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "docs(skill): add Phase -1 Pre-Mining Assessment section"
```

---

## Task 9: Add `Prerequisites` section + 4 new `When NOT to Use` entries to `SKILL.md`

**Files:**
- Modify: `SKILL.md`
  - Add a `## Prerequisites` section **after** the frontmatter table (which lives under the `## Overview` heading in the current file).
  - Expand the existing `## When to Use` / `Do NOT trigger for` bullet list with 4 new entries.

**Interfaces:**
- Consumes: nothing (documentation-only)
- Produces: prerequisites + extended trigger rules

- [ ] **Step 1: Verify the current location of the "Do NOT trigger" list in `SKILL.md`**

```bash
rg -n '^Do NOT trigger for' SKILL.md
```

Expected: prints a line number. Note it; insert below.

- [ ] **Step 2: Insert the `## Prerequisites` block after the `## Overview` paragraph**

Find the line `# Repo Doc Miner (v2 — Topology-First)` (the first `#`-level heading under the frontmatter) and the next paragraph ending. Insert a new `## Prerequisites` section immediately **after** the first `## Overview` heading block.

Find the existing `## Overview` heading in `SKILL.md` and after its closing paragraph (the line starting `v2 restructures the process …`) and before the next `## When to Use` heading, insert:

```markdown
## Prerequisites

Tools the skill expects to be on `PATH` before Phase -1 (Pre-Mining Assessment) runs:

| Tool | Why | Min version |
|---|---|---|
| `python3` | runs `scripts/gen_topology.py`, `scripts/scaffold_docs.py` | 3.8 (matches the script's `from __future__ import annotations` + PEP-604 typing) |
| `git` | Phase -1 uses `git log -1 --format=%ct` for the vitality signal | any |
| `rg` (ripgrep) | Phase 5 final sweep (`rg "TODO\(doc-miner\)"`) | any |

If `rg` is missing the agent falls back to a host project file-listing tool, but the experience is best with it installed.
```

Apply the edit (anchor: the existing `## When to Use` line is the search target; replacement includes the new block + the existing line). Verify:

```bash
rg -q '^## Prerequisites$' SKILL.md \
  && rg -q '| `rg` \(ripgrep\) |' SKILL.md \
  && rg -q '## When to Use' SKILL.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Add 4 new entries to the `Do NOT trigger for:` list**

Find the existing 4-item bulleted list under `Do NOT trigger for:`. Append 4 new items **after** the last existing bullet (but before the next `## Workflow` heading). The exact new bullets are:

```markdown
- The repo is **archived** or explicitly "no longer maintained" (see `references/suitability_signals.md` hard veto).
- The repo has **no `LICENSE` and no usage hint in its README** (same source).
- The repo is a **vendor fork** with no top-level source directory (only `node_modules/`, `dist/`, etc.).
- The repo has **fewer than 3 readable source files** after build/vendor filtering (same source).
```

Verify:

```bash
rg -q 'The repo is \*\*archived\*\* or explicitly' SKILL.md \
  && rg -q 'The repo is a \*\*vendor fork\*\*' SKILL.md \
  && rg -q 'fewer than 3 readable source files' SKILL.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Verify the heading sequence is still monotonic (no level skips around the new sections)**

```bash
awk '/^## Prerequisites/,/^## Workflow/' SKILL.md | ! rg -q '^### ' && echo OK
```

Expected: `OK`. (Confirms no `###` heading sits between `## Prerequisites` and `## Workflow`.)

- [ ] **Step 5: Commit**

```bash
git add SKILL.md
git commit -m "docs(skill): add Prerequisites section + 4 When NOT to Use entries"
```

---

## Task 10: Update `AGENTS.md` "Fixes already landed" list

**Files:**
- Modify: `AGENTS.md`
  - Append a single paragraph to the existing `### Fixes already landed (do not re-report these as open defects):` block describing Phase 1's fixes.

**Interfaces:**
- Consumes: nothing
- Produces: one new paragraph added to `AGENTS.md`

- [ ] **Step 1: Locate the existing list**

```bash
rg -n '^Fixes already landed' AGENTS.md
```

Expected: prints a line number; note it.

- [ ] **Step 2: Append a new paragraph to the end of the "Fixes already landed" list**

Find the last existing sentence in the `Fixes already landed` block (currently ending with "…stable prev baseline.") and append immediately after it:

```markdown

Phase 1 (Pre-Mining Assessment, 2026-10-11): the missing `Phase -1` "is this repo worth mining, who is it for, and where to start reading?" gating stage is now a documented part of the workflow with three references (`suitability_signals.md`, `audience_profiling.md`, `reading_path_suggestions.md`), an `assets/templates/assess.md` deliverable, an `assets/templates/_audience_block.md` fragment, two new optional scaffolder flags (`--assess`, `--audience`), and an explicit `## Prerequisites` section in `SKILL.md` declaring `python3 >= 3.8`, `git`, and `rg` as required tools (B2 from the 2026-10-11 audit is now closed).
```

Apply the edit (anchor: the existing last sentence). Verify:

```bash
rg -q 'Phase 1 \(Pre-Mining Assessment, 2026-10-11\)' AGENTS.md && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs(agents): record Phase 1 fixes (Pre-Mining Assessment)"
```

---

## Task 11: End-to-end smoke test

**Files:**
- Modify: none (this task only runs verification commands; nothing is committed)

**Interfaces:**
- Consumes: every file created or modified in Tasks 1–10
- Produces: a smoke-test log proving the full Phase -1 flow works on a throwaway repo

- [ ] **Step 1: Re-run the existing AGENTS.md safe smoke test, verifying byte-identical behaviour**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo 2>&1 | tail -1
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force 2>&1 | tail -1
find "$tmp" -name '*.md' | sort
rm -rf "$tmp"
```

Expected output:
- `Done. Next: refine the edges, then run Phase 2 (module deep-dive).`
- `Done. 5 written, 0 skipped.`
- 5 `.md` files: `developer_guide.md`, `README.md`, `topology.md`, `tutorial.md`, `user_guide.md`.

(No `assess.md`; no audience block. Confirms backwards compatibility.)

- [ ] **Step 2: Run the new `--assess --audience` end-to-end flow**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
mkdir -p "$tmp/docs" "$tmp/examples"
echo "MIT License — do X with this library" > "$tmp/README.md"
echo "fn main() {}" > "$tmp/main.rs"
echo "fn add(a, b) { a + b }" > "$tmp/examples/add.js"
python3 scripts/gen_topology.py "$tmp" --project-name Demo 2>&1 | tail -1
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force --assess --audience contributor 2>&1 | tail -3
ls "$tmp/docs/guides/"
head -1 "$tmp/docs/guides/assess.md"
rm -rf "$tmp"
```

Expected output:
- `Done. Next: refine the edges, then run Phase 2 (module deep-dive).`
- `Done. 6 written, 0 skipped.`
- `  assess.md: written.`
- 6 files in `$tmp/docs/guides/` (the existing 5 + `assess.md`).
- First line of `assess.md` is `<!-- audience: contributor -->`.

- [ ] **Step 3: Verify SKILL.md renders with monotonic headings end-to-end**

```bash
python3 - <<'PY'
import re, pathlib
text = pathlib.Path("SKILL.md").read_text(encoding="utf-8")
levels = [len(m.group(1)) for m in re.finditer(r'^(#{1,6}) ', text, re.M)]
prev = 0
for lvl in levels:
    assert lvl <= prev + 1, f"heading jump: {prev} -> {lvl}"
    prev = lvl
print("OK: monotonic headings, total =", len(levels))
PY
```

Expected: prints `OK: monotonic headings, total = NN` for some `NN`.

- [ ] **Step 4: Verify no untracked files remain after all commits**

```bash
git status --short
```

Expected: empty output (no untracked files, no staged changes).

- [ ] **Step 5: Final verification — no work to commit; close the loop**

```bash
git log --oneline -12
```

Expected: 11 new commits since the spec commit `0d77051`, in this order (most recent first):

1. `docs(agents): record Phase 1 fixes (Pre-Mining Assessment)`
2. `docs(skill): add Prerequisites section + 4 When NOT to Use entries`
3. `docs(skill): add Phase -1 Pre-Mining Assessment section`
4. `feat(scaffold): add --audience flag (Phase -1)`
5. `feat(scaffold): add --assess flag (Phase -1)`
6. `feat(templates): add _audience_block.md fragment (Phase -1)`
7. `feat(templates): add assess.md template (Phase -1 deliverable)`
8. `docs(refs): add reading_path_suggestions.md (Phase -1 matrix)`
9. `docs(refs): add audience_profiling.md (Phase -1 taxonomy)`
10. `docs(refs): add suitability_signals.md (Phase -1 rubric)`

If any commit is missing or in the wrong order, return to the corresponding task and amend before declaring Phase 1 done.

---

## Self-Review

**Spec coverage (§5 of the spec):**

| Spec requirement | Covered in task |
|---|---|
| §5.1 capability (4 questions answered by `assess.md`) | Task 4 (template) + Tasks 8–9 (SKILL.md text) |
| §5.2 new files: `audience_profiling.md`, `suitability_signals.md`, `reading_path_suggestions.md`, `assess.md`, `_audience_block.md` | Tasks 1–5 |
| §5.3 audience taxonomy (6 buckets) | Task 2 (full table) |
| §5.4 suitability scoring (0–2 per signal → 0–5; 4 hard vetoes; usage-hint definition) | Task 1 (full rubric + usage-hint definition) |
| §5.5 reading paths (audience × band matrix) | Task 3 |
| §5.6 script changes: scaffold_docs.py adds `--assess` (default off), `--audience` (default off); gen_topology.py unchanged | Tasks 6 + 7; Tasks 6 Steps 5, 7 + 7 Steps 5–7 verify defaults |
| §5.7 SKILL.md: Phase -1 + When NOT to Use + Prerequisites | Tasks 8 + 9 |
| §5.8 test plan | Tasks 6 Step 5, 6 Step 6, 6 Step 7, 7 Steps 5–7, Task 11 |
| Open Decisions: `<angle-bracket>` slot fate — **deferred to Phase 3** (spec §8) ✓ | not in this plan |
| Open Decisions: Default audience when none — **defined as "no audience block"** in §5.1 spec ✓ | Task 7 Step 5 verifies absence when no flag |
| Open Decisions: Archived-repo veto mechanism — **on-disk signals only**, no API calls | Task 1 hard vetoes |
| Open Decisions: Phase -1 as real phase — **yes, additive prefix** | Task 8 |

**Placeholder scan:** No "TBD" / "implement later" / "fill in details" remain. Code blocks are provided verbatim for every code step. Each task's commit message is included.

**Type / name consistency check:**

- `assess.md` filename is used consistently across Tasks 4, 6, 7, 8, 9, 11.
- `assess_src`, `assess_dst` variable names match across Tasks 6 and 7.
- `_audience_block.md` filename is consistent across Tasks 5, 6 Step 1, 7 Step 1, 7 Step 2.
- `--assess` / `--audience` flag spellings are consistent across Tasks 6 and 7.
- `audience_prefix` variable name is consistent across Tasks 7 Step 2, Step 3, Step 4.
- `references/suitability_signals.md`, `references/audience_profiling.md`, `references/reading_path_suggestions.md` paths are consistent.

No inconsistencies found.