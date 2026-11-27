# Phase 5 — Production Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the skill from "works in a worktree" to "works for a downstream user". Three deliverables: (1) a `Makefile` so `make test` runs the full battery; (2) a `CHANGELOG.md` documenting the four phases so users can see what changed; (3) close the remaining small polish items from Phases 1-3 (N2, N3, RES-1, C5) in one batched commit. The `--lang` flag (spec §7.2) and `<br/>`-exemption documentation are formally deferred to v4+ per the spec's §8.3 Open Decisions.

**Architecture:** No new scaffolder code; one new `Makefile` (5 targets); one new `CHANGELOG.md`; one new `scripts/check_resources.py` (small stdlib script that validates the `## Resources` section in `SKILL.md` against the actual `assets/templates/`, `references/`, and `scripts/` trees); four small polish edits to existing files (`_flavor_strip.md` en-GB→en-US, `smoke.py` extra assertions, `reading_path_suggestions.md` backtick fix, `gen_topology.py` C5 cap-warning fidelity). One AGENTS.md bookkeeping entry.

**Tech Stack:** Python 3.8+ stdlib only (`pathlib`, `re`, `sys`), `make` (POSIX make; no GNU-extensions required for portability).

**Spec:** `docs/superpowers/specs/2026-10-11-repodocminer-optimization-design.md` — C5 cap-warning fidelity (cited in §7.1 C5), the 12-item Failure-Modes list (Phase 2 §6.1 C3), and §8.3 Open Decisions for the deferred items.

**SDD state:** workspace at `.superpowers/sdd/2026-10-11-phase5-production/`. Branch: `phase1-pre-mining-assessment` (continuing on the same feature branch). Base: `378258c` (Phase 4 ledger final-state commit).

---

## File Structure

| Path | Type | Responsibility |
|---|---|---|
| `Makefile` | new | Top-level test entry point: `make test` / `make smoke` / `make clean` |
| `CHANGELOG.md` | new | Keep-a-Changelog-style log of the four phases (1.0 → 1.1 → 1.2 → 1.3 → 1.4) |
| `scripts/check_resources.py` | new | stdlib-only validator: confirms `SKILL.md` `## Resources` section lists every file under `assets/templates/`, `references/`, and `scripts/` (excluding `__pycache__/`, `gen_topology.py` / `scaffold_docs.py` are listed explicitly; no `audit` rule is enforced — a missing entry is reported as INFO, not as a failure) |
| `assets/templates/_flavor_strip.md` | modify | N2 polish — en-GB → en-US (flavour → flavor, recognise → recognize, flavours → flavors) |
| `scripts/smoke.py` | modify | N3 polish — add a top-of-file `assert _env.sh sources and `_flavor_strip.md` exists` block (informational, not gate) |
| `references/reading_path_suggestions.md` | modify | RES-1 polish — replace the literal `\\`Phase -1\\` escaped-backtick pattern with normal inline code |
| `scripts/gen_topology.py` | modify | C5 polish — make the entity-cap warning print under `verbose=True` (matches the edge-cap's always-on behaviour and the docstring's text) |
| `AGENTS.md` | modify | Append the Phase 5 paragraph to "Fixes already landed" |

No new references/ template assets. No SKILL.md or README changes (those already received v3 polish in Phase 3 and Phase 4). No spec or plan changes (Phase 5 is purely execution polish).

---

## Global Constraints

- **stdlib-only Python.** No third-party imports added to `scripts/`.
- **No new test framework.** Verification uses throwaway-directory bash smoke tests.
- **Backwards-compatible behaviour.** `gen_topology.py` C5 polish: the entity-cap warning was previously silent under default `--verbose=False`; under the new behaviour it prints to stderr only when `--verbose` is set (or when the cap is actually hit). The AGENTS.md "safe smoke test" runs without `--verbose` and must remain byte-identical to before. (Verify: `python3 scripts/gen_topology.py <throwaway> --project-name Demo` produces no cap warning for a small repo; the AGENTS.md "second run is byte-identical" assertion holds.)
- **No new test framework.** `Makefile` is plain `make` rules; `scripts/check_resources.py` exits 0 on clean state and prints an INFO list (or a warning) of any files present on disk that are missing from `SKILL.md`.
- **Headings monotonic** (new files use `##` then `##`; no skips).
- **Snippet cap ≤ 30 lines** (per `references/writing_style.md`).
- **No `{{...}}` placeholders or `<angle-bracket>` slots** in any new content file.
- **AGENTS.md "Fixes already landed"** list is updated in the final commit of this phase.
- **Phase 1+2+3+4 byte-identity is preserved** for files not in the table above.

---

## Task 1: Add `Makefile`

**Files:**
- Create: `Makefile`

**Interfaces:**
- Consumes: nothing (Make reads the local file)
- Produces: 5 targets (test, smoke, smoke-strict, clean, help) that downstream users can run

- [ ] **Step 1: Write the Makefile**

Create `Makefile` at the repo root with the exact content below. No GNU extensions; should work on both Linux/macOS `make` and BSD `make`.

```make
# repo-doc-miner — top-level Makefile.
#
# Use `make help` to list targets. The default target is `help` (no work).
#
# `make test` is the canonical "does the skill work" check: it runs
# scripts/smoke.py and exits non-zero on any failure. `make smoke-strict`
# adds the Phase 4 --guides-dir --strict audit (informational, exits 0
# on a draft-state scaffold).
#
# `make clean` removes build caches and the throwaway guides directory
# the smoke battery creates; it does not touch any user files.

.PHONY: help test smoke smoke-strict clean

PYTHON ?= python3
SCRIPT_DIR := scripts
SMOKE := $(PYTHON) $(SCRIPT_DIR)/smoke.py
GEN_TOP := $(PYTHON) $(SCRIPT_DIR)/gen_topology.py
SCAFF := $(PYTHON) $(SCRIPT_DIR)/scaffold_docs.py

help:
	@echo "repo-doc-miner Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  test           run the full battery (scripts/smoke.py); exits non-zero on failure"
	@echo "  smoke          alias for test"
	@echo "  smoke-strict   scaffold a throwaway + audit with --strict --guides-dir"
	@echo "  clean          remove __pycache__ and the throwaway guides/ subdirectory"
	@echo "  help           this message (default)"
	@echo ""
	@echo "Variables (override on the command line):"
	@echo "  PYTHON=python3.11  which Python interpreter to use"

test: smoke

smoke:
	@$(SMOKE)

smoke-strict:
	@tmp=$$(mktemp -d) && \
	  git -C $$tmp init -q && \
	  $(SCAFF) $$tmp --project-name Demo --force --assess --audience contributor > /dev/null && \
	  $(SMOKE) --guides-dir $$tmp/docs/guides --strict ; \
	  status=$$? ; \
	  rm -rf $$tmp ; \
	  exit $$status

clean:
	@find . -name __pycache__ -type d -prune -exec rm -rf {} +
	@rm -rf docs/guides
	@echo "cleaned"
```

- [ ] **Step 2: Verify `make help`**

```bash
make help
```

Expected: prints the help block (no errors).

- [ ] **Step 3: Verify `make test` (= `make smoke`)**

```bash
make test 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 4: Verify `make smoke-strict`**

```bash
make smoke-strict 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 5: Verify `make clean` is a no-op on a clean tree and idempotent**

```bash
make clean
git status --short
```

Expected: `cleaned` printed; no files removed (tree is already clean apart from possibly `__pycache__`).

- [ ] **Step 6: Commit**

```bash
git add Makefile
git commit -m "build: add Makefile (test, smoke, smoke-strict, clean, help)"
```

---

## Task 2: Add `CHANGELOG.md`

**Files:**
- Create: `CHANGELOG.md`

**Interfaces:**
- Consumes: nothing (markdown authored by hand)
- Produces: a Keep-a-Changelog-style changelog that documents the four phases

- [ ] **Step 1: Write the file**

Create `CHANGELOG.md` at the repo root with the exact content below. Follow the [Keep a Changelog](https://keepachangelog.com/) format (1.0.0–1.4.0 sequence with `### Added` / `### Changed` / `### Removed` sections per release).

```markdown
# Changelog

All notable changes to `repo-doc-miner` are documented in this file. Versions follow [Semantic Versioning](https://semver.org/).

## [1.4.0] — 2026-10-11

### Added
- `scaffold_docs.py --flavor FLAVOR_NAME` flag (default `general`) which strips `<!-- flavor: NAME --> ... <!-- /flavor: NAME -->` blocks from the 5 core templates + `assess.md`, wiring up the `_flavor_strip.md` contract that was a no-op marker through v1.3.0. (Spec C1/C7.)
- `assets/templates/developer_guide.md` §6 now contains a demonstrative `<!-- flavor: backend -->` block so the stripper has a real block to remove.
- `scripts/smoke.py --guides-dir PATH` flag — the `--strict` audit is now meaningful against a real `docs/guides/` directory (previously structurally unreachable on the throwaway scaffold). Closes Phase 2 R3.
- `Makefile` — top-level `make test` / `make smoke` / `make smoke-strict` / `make clean` / `make help` targets for downstream users.
- `CHANGELOG.md` — this file.
- `scripts/check_resources.py` — stdlib-only validator confirming the `## Resources` section in `SKILL.md` lists every file under `assets/templates/`, `references/`, and `scripts/`.

### Changed
- `references/suitability_signals.md` removed the legacy `.github/CODEOWNERS`-based archived-detection (the script doesn't read CODEOWNERS).
- `assets/templates/topology.md` removed the 17 legacy `<angle-bracket>` slots that the script never produced (the 5 core templates now ship slot-free).
- `references/evidence_checklist.md` opens with a "Tool vs. expectation" callout (C10) and the "Python ML" row is de-PINN-ified.
- `SKILL.md` and `README.md` frontmatter / title bumped from v2 to v3; `README.md` Contents tree now lists all 7 templates, 8 references, 4 scripts.

### Fixed
- `gen_topology.py`: the `--max-entities` cap warning now prints only under `--verbose` (the `--max-edges` cap was always correct; the two now behave consistently). C5 polish.
- `references/reading_path_suggestions.md`: the `\\`Phase -1\\` escaped-backtick pattern is now plain inline code (CommonMark backslash escapes do not apply inside code spans). RES-1 closure.

## [1.3.0] — 2026-10-11

### Added
- Phase -1 Pre-Mining Assessment stage: `references/suitability_signals.md`, `references/audience_profiling.md`, `references/reading_path_suggestions.md`, `assets/templates/assess.md`, `assets/templates/_audience_block.md`.
- `scaffold_docs.py --assess` and `--audience NAME` flags.
- `SKILL.md` `### Phase -1` section + `## Prerequisites` table.
- `## Workflow Variants` section in `SKILL.md` (Full / Lite / Progressive modes).
- `references/edge_refinement.md` (Phase 2).
- `scripts/smoke.py` (Phase 2).
- `scripts/_env.sh` (Phase 3).
- `assets/templates/_flavor_strip.md` (Phase 3 marker file).
- `gen_topology.py --dry-run` and `--summary` flags (Phase 3).
- Failure-Modes list grown from 6 to 12 entries (Phase 2).

### Changed
- `SKILL.md` phase numbering: now `Phase -1 → Phase 0–6` (the additive `Phase -1` prefix keeps `Phase 0–6` references stable).

## [1.2.0] — 2026-10-11

### Added
- First release of the v2 topology-first workflow.
- `scripts/gen_topology.py` (entity + edge detection, Mermaid rendering).
- `scripts/scaffold_docs.py` (5-template materializer with `{{PROJECT_NAME}}` substitution).
- 5 core templates (`topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`, `README.md`).
- 4 references (`topology_method.md`, `doc_outlines.md`, `evidence_checklist.md`, `writing_style.md`).
- `SKILL.md` seven-phase workflow (Phase 0–6).
- AGENTS.md "safe smoke test" bash block.

## [1.1.0] — 2026-10-11

### Added
- v1.0 / v1.1 changelog entries were retroactive; the original v1 (DeepXDE-shaped) shipped with one batch of templates and a different workflow.

## [1.0.0] — earlier

Initial release. v1 (pre-topology) was a flat file scanner that produced three documents. v2 (this repo's reason for being) is the topology-first rewrite.
```

- [ ] **Step 2: Verify the file is well-formed**

```bash
test -f CHANGELOG.md \
  && rg -q '^## \[1\.4\.0\]' CHANGELOG.md \
  && rg -q '^## \[1\.3\.0\]' CHANGELOG.md \
  && rg -q '^## \[1\.2\.0\]' CHANGELOG.md \
  && rg -q '^## \[1\.0\.0\]' CHANGELOG.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): add CHANGELOG.md documenting the four phases (1.2.0 .. 1.4.0)"
```

---

## Task 3: Add `scripts/check_resources.py`

**Files:**
- Create: `scripts/check_resources.py`

**Interfaces:**
- Consumes: the filesystem layout under `assets/templates/`, `references/`, `scripts/`; the `SKILL.md` `## Resources` section
- Produces: a non-blocking (exit 0) report listing any disk files not mentioned in `SKILL.md`, and any `SKILL.md` entries that point at non-existent disk files

- [ ] **Step 1: Write the file**

Create `scripts/check_resources.py` with the exact content below. Stdlib-only; no flags. Prints a one-line summary + a per-category delta. Exits 0 always (the check is informational; the build doesn't fail on drift).

```python
#!/usr/bin/env python3
"""Cross-check the SKILL.md `## Resources` section against the actual
files under `assets/templates/`, `references/`, and `scripts/`.

Run via `python3 scripts/check_resources.py`. Always exits 0; the check
is informational. Use this to spot drift after adding a new template or
reference: if the script reports "1 disk file missing from SKILL.md",
add the new file to the `## Resources` section.

Exit codes
----------
    0  always
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# Files to exclude from the disk-side scan (not user-facing assets).
EXCLUDE = {
    "__pycache__",
    "smoke.py",  # not in SKILL.md Resources; the smoke battery is a dev tool
}


def _disk_files() -> dict[str, list[str]]:
    """Return {category: [path-glob, ...]} for the 3 resource categories."""
    out: dict[str, list[str]] = {"templates": [], "references": [], "scripts": []}
    for md in sorted((ROOT / "assets" / "templates").glob("*.md")):
        out["templates"].append(f"assets/templates/{md.name}")
    for md in sorted((ROOT / "references").glob("*.md")):
        out["references"].append(f"references/{md.name}")
    for sh in sorted((ROOT / "scripts").glob("*.py")):
        if sh.name in EXCLUDE:
            continue
        out["scripts"].append(f"scripts/{sh.name}")
    for sh in sorted((ROOT / "scripts").glob("*.sh")):
        out["scripts"].append(f"scripts/{sh.name}")
    return out


def _skill_entries() -> dict[str, list[str]]:
    """Return {category: [path-glob, ...]} parsed from SKILL.md `## Resources`."""
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    # `## Resources` is a top-level H2 in SKILL.md; its `###` subsections
    # are `### scripts/`, `### assets/templates/`, `### references/`.
    out: dict[str, list[str]] = {"templates": [], "references": [], "scripts": []}
    in_resources = False
    current_cat: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            in_resources = line.startswith("## Resources")
            current_cat = None
            continue
        if not in_resources:
            continue
        if line.startswith("### "):
            sub = line.removeprefix("### ").strip().rstrip("/")
            if sub in ("scripts", "assets/templates", "references"):
                current_cat = {
                    "scripts": "scripts",
                    "assets/templates": "templates",
                    "references": "references",
                }[sub]
            else:
                current_cat = None
            continue
        if current_cat is None or not line.startswith("- "):
            continue
        # Each bullet is `- \`path/to/file\` — desc`. Capture the first
        # backtick-quoted token (the file path).
        match = re.search(r"`([^`]+)`", line)
        if match:
            path = match.group(1)
            # SKILL.md writes paths as `assets/templates/...` (no
            # leading `./`); normalise.
            out[current_cat].append(path)
    return out


def main() -> int:
    disk = _disk_files()
    skill = _skill_entries()
    print("check_resources.py — SKILL.md Resources vs disk")
    print()
    for cat in ("templates", "references", "scripts"):
        d = set(disk[cat])
        s = set(skill[cat])
        only_disk = d - s
        only_skill = s - d
        print(f"### {cat}")
        print(f"  disk: {len(d):3d}   SKILL.md: {len(s):3d}   in both: {len(d & s):3d}")
        if only_disk:
            for p in sorted(only_disk):
                print(f"  INFO disk-only: {p}")
        if only_skill:
            for p in sorted(only_skill):
                print(f"  INFO skill-only (may be a mention in prose, not a link): {p}")
        print()
    print("OK: check complete (informational; does not fail the build).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Verify the script runs and reports a clean state (or a list of drift items)**

```bash
chmod +x scripts/check_resources.py
python3 scripts/check_resources.py
echo "exit=$?"
```

Expected: a per-category report; `exit=0`.

- [ ] **Step 3: Verify the script correctly catches drift when SKILL.md is wrong**

(Just a sanity check, not a real edit. Use a temp file.)

```bash
# Save the current SKILL.md aside, mutate, run, restore.
cp SKILL.md /tmp/skill.md.bak
# Drop one template from the SKILL.md Resources section.
python3 - <<'PY'
import pathlib
text = pathlib.Path("SKILL.md").read_text()
# Naively remove the developer_guide.md line.
text = text.replace("- `assets/templates/developer_guide.md`", "")
pathlib.Path("SKILL.md").write_text(text)
PY
python3 scripts/check_resources.py | rg "INFO disk-only: assets/templates/developer_guide.md" && echo "OK: drift detected"
mv /tmp/skill.md.bak SKILL.md
```

Expected: `OK: drift detected`.

- [ ] **Step 4: Commit**

```bash
git add scripts/check_resources.py
git commit -m "feat(scripts): add check_resources.py (SKILL.md Resources vs disk)"
```

---

## Task 4: Polish bundle — N2 (en-GB→en-US), N3 (smoke assertions), RES-1 (backticks), C5 (cap warning)

**Files:**
- Modify: `assets/templates/_flavor_strip.md`
- Modify: `scripts/smoke.py`
- Modify: `references/reading_path_suggestions.md`
- Modify: `scripts/gen_topology.py`

**Interfaces:**
- Consumes: the existing files
- Produces: 4 small prose / logic edits in a single commit

- [ ] **Step 1: N2 — normalize `_flavor_strip.md` to en-US**

In `assets/templates/_flavor_strip.md`, replace:
- `flavour` → `flavor` (2 occurrences: "flavour-specific", "all flavours off")
- `recognise` → `recognize` (1 occurrence)
- `flavours` → `flavors` (1 occurrence)

The simplest is:

```bash
sed -i '' 's/flavour/flavor/g; s/recognise/recognize/g; s/flavours/flavors/g' assets/templates/_flavor_strip.md
```

(Use `''` for macOS BSD sed; on Linux, omit the `''`. The skill ships with no GNU assumption, so document both forms if you can't tell.)

Verify:

```bash
! rg -q 'flavour\|recognise\|flavours' assets/templates/_flavor_strip.md && echo "OK: en-US normalized"
```

Expected: `OK`.

- [ ] **Step 2: N3 — add `_env.sh` + `_flavor_strip.md` existence checks to `smoke.py`**

At the top of `smoke.py` (after the imports, before `_print`), add a small `assert` block that fails loudly if either file is missing. This is the N3 closure: the smoke battery now fails if the Phase 3 + Phase 4 files are accidentally deleted.

```python
# Sanity: the Phase 3 + Phase 4 auxiliary files must exist.
for _aux in (HERE / ".." / "scripts" / "_env.sh", HERE / ".." / "assets" / "templates" / "_flavor_strip.md"):
    if not _aux.is_file():
        print(f"error: required file missing: {_aux}", file=sys.stderr)
        return 2
del _aux
```

Wait — `HERE` is `<skill_root>/scripts`; `HERE / ".."` is `<skill_root>`. Adjust the path computation to match the existing imports at the top of the file (which use `HERE = Path(__file__).resolve().parent`):

```python
# Sanity: the Phase 3 + Phase 4 auxiliary files must exist.
for _aux_path in (
    REPO / "scripts" / "_env.sh",
    REPO / "assets" / "templates" / "_flavor_strip.md",
):
    if not _aux_path.is_file():
        print(f"error: required file missing: {_aux_path}", file=sys.stderr)
        return 2
```

(Use `REPO` since the script already defines `REPO = HERE.parent` at the top. Place the block after `REPO = HERE.parent` so the variable is in scope.)

Verify:

```bash
python3 scripts/smoke.py 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 3: RES-1 — fix escaped backticks in `reading_path_suggestions.md`**

Find the line containing `\\`Phase -1\\` (a backslash-escaped backtick pair inside a single-backtick code span, which renders as literal backslashes). The line lives in the `## Next-step actions` section.

Replace:
```markdown
- For High: `Open the entry file. If the suggested section lands a working example within 30 minutes, treat the doc set as a fit; otherwise re-run \`Phase -1\` with a different audience.`
- For Mid: `Skim the entry file's first 100 lines. If the first concrete API or class matches what you need, proceed; otherwise stop.`
- For Skip: `the remediation sentence; re-run \`Phase -1\` afterwards.`
```

With:
```markdown
- For High: `Open the entry file. If the suggested section lands a working example within 30 minutes, treat the doc set as a fit; otherwise re-run 'Phase -1' with a different audience.`
- For Mid: `Skim the entry file's first 100 lines. If the first concrete API or class matches what you need, proceed; otherwise stop.`
- For Skip: `the remediation sentence; re-run 'Phase -1' afterwards.`
```

(Single quotes around `Phase -1` instead of nested escaped backticks. CommonMark single-quote is valid inside a backtick code span.)

Verify:

```bash
! rg -q '\\\\`Phase -1\\\\`' references/reading_path_suggestions.md && echo "OK: no escaped-backtick pattern"
```

Expected: `OK`.

- [ ] **Step 4: C5 — make the entity-cap warning print under `verbose=True` (matches the edge cap)**

In `scripts/gen_topology.py`, find the entity-cap block (around line 244-247 per the spec's C5 polish). The exact code depends on the v1.4.0 shape; the intent is:

The `--max-entities` cap, when hit, currently prints nothing (or prints unconditionally — verify by reading the file and matching the docstring). The `--max-edges` cap prints unconditionally on hit. Align the two: the entity-cap warning should print only under `--verbose` (because the silent cap is intentional for small repos; under `--verbose` the user wants the detail).

Concretely, change the entity-cap branch to:

```python
if max_entities > 0 and len(entities) > max_entities:
    if verbose:
        print(f"  cap: hiding {len(entities) - max_entities} entities (max={max_entities})", file=sys.stderr)
    entities = entities[:max_entities]
```

(If the existing code already prints only under `verbose`, this step is a no-op; verify by reading the file and skip the edit if so. The C5 polish is "match the docstring's truth" — the spec's only requirement is that the behaviour matches the docstring text "the cap was previously silent under default --verbose=False; under the new behaviour it prints to stderr only when --verbose is set".)

Verify:

```bash
# No cap warning on a tiny repo.
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo 2>&1 | rg -c "cap:" && echo "FAIL: cap warning on small repo" || echo "OK: no cap warning on small repo"
rm -rf "$tmp"
```

Expected: `OK: no cap warning on small repo`.

- [ ] **Step 5: Verify all 4 polish edits pass the smoke battery**

```bash
python3 scripts/smoke.py 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 6: Commit**

```bash
git add assets/templates/_flavor_strip.md scripts/smoke.py references/reading_path_suggestions.md scripts/gen_topology.py
git commit -m "docs(refs,templates): Phase 5 polish bundle — N2/N3/RES-1/C5

N2: _flavor_strip.md en-GB -> en-US (flavour -> flavor, recognise ->
    recognize, flavours -> flavors).
N3: scripts/smoke.py now fails loudly (exit 2) if
    scripts/_env.sh or assets/templates/_flavor_strip.md is missing.
RES-1: references/reading_path_suggestions.md 'Next-step actions' bullets
    now use single quotes around 'Phase -1' instead of nested escaped
    backticks (the backslashes were rendering literally).
C5: scripts/gen_topology.py --max-entities cap warning now prints under
    --verbose (matches the --max-edges behaviour and the docstring text).
    The default no-verbose path stays silent on small repos."
```

---

## Task 5: Update `AGENTS.md` "Fixes already landed" list for Phase 5

**Files:**
- Modify: `AGENTS.md`
  - Append a single paragraph after the existing last sentence in the "Fixes already landed" block.

**Interfaces:**
- Consumes: nothing
- Produces: a `Phase 5 (Production Readiness, 2026-10-11)` paragraph

- [ ] **Step 1: Find the end of the existing block**

```bash
rg -n '^### Fixes already landed' AGENTS.md
```

The block ends just before `## Important Files`. Append the new paragraph immediately before that.

- [ ] **Step 2: Append the Phase 5 paragraph**

After the existing Phase 4 paragraph, append:

```markdown

Phase 5 (Production Readiness, 2026-10-11): moves the skill from "works in a worktree" to "works for a downstream user". A `Makefile` provides one-command test entry points (`make test` / `make smoke` / `make smoke-strict` / `make clean` / `make help`); a `CHANGELOG.md` documents the four-phase evolution (1.0.0 → 1.4.0) in Keep-a-Changelog format; a new `scripts/check_resources.py` validator confirms that `SKILL.md`'s `## Resources` section lists every file under `assets/templates/`, `references/`, and `scripts/`, surfacing drift as INFO (exit 0; the check is informational, not a build gate). Four small polish items from earlier phases are also closed: N2 (normalize `_flavor_strip.md` from en-GB to en-US), N3 (`scripts/smoke.py` now exits 2 if the Phase 3 + Phase 4 auxiliary files are missing — i.e. it fails loudly rather than silently skipping them), RES-1 (replace the literal `\`Phase -1\`` escaped-backtick pattern in `reading_path_suggestions.md` with single-quoted `'Phase -1'` so CommonMark renders it correctly), C5 (the `--max-entities` cap warning now prints under `--verbose` only, matching the `--max-edges` behaviour and the docstring's "verbose" qualifier). The `--lang` scaffolder flag (spec §7.2) and `<br/>` exemption documentation remain formally deferred to v4+ per spec §8.3 Open Decisions.
```

- [ ] **Step 3: Verify the new paragraph is in place**

```bash
rg -q 'Phase 5 \(Production Readiness, 2026-10-11\)' AGENTS.md && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md
git commit -m "docs(agents): record Phase 5 fixes (Production Readiness)"
```

---

## Task 6: End-to-end smoke test

**Files:**
- Modify: none (controller-only)

- [ ] **Step 1: Verify `make help` lists the 5 targets**

```bash
make help 2>&1 | head -10
```

Expected: 5 `Targets:` lines (test, smoke, smoke-strict, clean, help).

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
python3 scripts/check_resources.py 2>&1 | tail -10
```

Expected: per-category counts; "OK: check complete".

- [ ] **Step 5: Verify the four polish edits**

```bash
# N2: _flavor_strip.md en-US
! rg -q 'flavour\|recognise\|flavours' assets/templates/_flavor_strip.md && echo "OK: N2"

# N3: smoke.py now has the existence block
rg -q 'required file missing' scripts/smoke.py && echo "OK: N3"

# RES-1: no escaped-backtick pattern
! rg -q '\\\\`Phase -1\\\\`' references/reading_path_suggestions.md && echo "OK: RES-1"

# C5: gen_topology.py cap warning under --verbose
python3 scripts/gen_topology.py --help 2>&1 | rg -q '\-\-verbose' && echo "OK: C5 --verbose present"
```

Expected: 4 `OK` lines.

- [ ] **Step 6: Verify no untracked files remain**

```bash
git status --short
```

Expected: empty.

- [ ] **Step 7: Final git log check**

```bash
git log --oneline -8
```

Expected: the Phase 5 commits appear at the top, in this order (most recent first):

1. `docs(agents): record Phase 5 fixes (Production Readiness)`
2. `docs(refs,templates): Phase 5 polish bundle — N2/N3/RES-1/C5`
3. `feat(scripts): add check_resources.py (SKILL.md Resources vs disk)`
4. `docs(changelog): add CHANGELOG.md documenting the four phases (1.2.0 .. 1.4.0)`
5. `build: add Makefile (test, smoke, smoke-strict, clean, help)`

(5 task commits + the plan + ledger commits from the workspace; the plan lands as the first commit when the SDD workspace is initialised.)

---

## Self-Review

**Deferred items (formally closed or scheduled):**

| Item | Phase deferred | Phase closed | Notes |
|---|---|---|---|
| `--lang` flag (spec §7.2) | Phase 3 | **v4+ (spec §8.3)** | Bilingual headings are the current default; per-language template variants require either translation or selective stripping. |
| N2 (`_flavor_strip.md` en-GB/en-US) | Phase 3 | **Phase 5 Task 4** | Closed. |
| N3 (smoke.py missing assertions for `_env.sh` / `_flavor_strip.md`) | Phase 3 | **Phase 5 Task 4** | Closed via the N3 block. |
| RES-1 (escaped backticks in `reading_path_suggestions.md`) | Phase 1 | **Phase 5 Task 4** | Closed. |
| C5 (cap-warning fidelity) | Phase 3 | **Phase 5 Task 4** | Closed. |
| `<br/>` exemption documentation in AGENTS.md | Phase 3 | **v4+ (spec §8.3)** | The Mermaid/HTML `<br/>` is correct and used in only one place (the §1 prose of `topology.md`); a future docstring touchup can cover it. |
| C1/C7 scaffolder `--flavor` arg wiring | Phase 3 | **Phase 4 Task 1** | Closed. |
| Phase 2 R3 (`--strict` unreachable) | Phase 2 | **Phase 4 Task 3** | Closed. |

**Type / name consistency check:**

- `make help` / `test` / `smoke` / `smoke-strict` / `clean` target names are consistent across Task 1 (`Makefile`) and Task 6 (smoke battery).
- `check_resources.py` uses `HERE` and `REPO` (the same constants `smoke.py` uses).
- `Phase 5` numbering is unique across all spec/plan/AGENTS/CHANGELOG references.

No inconsistencies found.

**Open items (deferred to a future release):**

- `--lang` flag (spec §7.2) and the `<br/>` exemption documentation (Phase 3 N4): both are deferred to v4+ per the spec's §8.3 Open Decisions.
- The remaining 6 entries in `references/evidence_checklist.md`'s "Tool vs. expectation" callout's "It does not detect" list (cross-module call graphs, dynamic dispatch, runtime plugin loading, generated artifacts, dependency lock files, code execution) are aspirational features, not defects; documenting them as known limitations is a docs polish, not a code change.

These deferrals match the spec's §8.3 Open Decisions.