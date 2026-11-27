# Phase 2 — Reliability & Operability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three reliability/operability improvements to `repo-doc-miner` v2.0.0: (1) a deep edge-refinement guide + a "How to refine edges" SKILL.md subsection; (2) a "Workflow Variants" section (Full / Lite / Progressive) + expanded "Failure Modes to Avoid" (6 → 12); (3) a codified `scripts/smoke.py` that runs the existing manual bash smoke + Phase-5 checks.

**Architecture:** Two new content files (`references/edge_refinement.md`, `scripts/smoke.py`) and three SKILL.md sections (Phase 1 "How to refine edges" subsection, "Workflow Variants" h2, expanded Failure Modes). No new scaffolder code; the smoke script is stdlib-only and reuses the existing throwaway-directory pattern from AGENTS.md. No third-party dependencies anywhere. No change to `gen_topology.py` or `scaffold_docs.py`.

**Tech Stack:** Python 3.8+ stdlib only (`argparse`, `pathlib`, `re`, `subprocess`), Markdown templates.

**Spec:** [`docs/superpowers/specs/2026-10-11-repodocminer-optimization-design.md`](../specs/2026-10-11-repodocminer-optimization-design.md) — section §6 (Phase 2 — Reliability & Operability, B2/B3/C3/C12/C4).

**SDD state:** workspace at `.superpowers/sdd/2026-10-11-phase2-reliability/`. Branch: `phase1-pre-mining-assessment` (we continue on the Phase 1 branch since Phase 2 work is additive). Base: `860831b` (Phase 1 final-review commit).

---

## File Structure

| Path | Type | Responsibility |
|---|---|---|
| `references/edge_refinement.md` | new | The deep guide for verifying and refining auto-detected edges after `gen_topology.py` runs (B3) |
| `scripts/smoke.py` | new | stdlib-only codification of the AGENTS.md "safe smoke test" + Phase-5 checks (C4) |
| `SKILL.md` | modify | Add `### Phase 1 · Topology Generation` "How to refine edges" subsection; add `## Workflow Variants`; expand `## Failure Modes to Avoid` from 6 to 12 |

`gen_topology.py` and `scaffold_docs.py` are NOT touched in this phase.

---

## Global Constraints

- **stdlib-only Python.** No third-party imports added to `scripts/`.
- **No new test framework.** `scripts/smoke.py` is a stdlib script that exits 0 / non-zero; downstream agents can `pytest` later if desired but no `pytest` dep is added now.
- **Backwards-compatible behaviour.** `scripts/smoke.py` defaults to running the safe smoke test (matching AGENTS.md "Verification gates" verbatim) and exits 0; `--check-only` does no work. SKILL.md additions do not break any existing section.
- **Headings monotonic.** New SKILL.md sections follow `## → ## → ###` strictly.
- **Snippet cap ≤ 30 lines** (per `references/writing_style.md`).
- **No `{{...}}` placeholders / no `<angle-bracket>` slots** in any new content file (per AGENTS.md "Placeholder conventions" + `references/doc_outlines.md`).
- **AGENTS.md "Fixes already landed"** list is updated in the final commit of this phase.
- **Phase 1 byte-identity is preserved.** No edits to the three Phase 1 references/ docs, the three Phase 1 templates (assess.md, _audience_block.md), or to README.md / scaffold_docs.py / gen_topology.py. The only Phase 1 content touched is SKILL.md (additive) and references/doc_outlines.md (only if we add a new section style convention).

---

## Task 1: Create `references/edge_refinement.md`

**Files:**
- Create: `references/edge_refinement.md`

**Interfaces:**
- Consumes: nothing (parallel to Task 1/2/3 of Phase 1)
- Produces: a Markdown doc explaining how to verify and refine the auto-detected edges emitted by `gen_topology.py`

- [ ] **Step 1: Write the file content**

Create `references/edge_refinement.md` with the exact content below. The structure follows the Phase 1 references docs' style: short intro blockquote + 4–5 H2 sections + a "What this guide deliberately does not do" closer.

```markdown
# Edge Refinement (Phase 1)

> **What this is.** A practitioner's guide to verifying and refining the dependency edges emitted by `gen_topology.py`. Auto-detection is heuristic; this file is the manual that converts "looks right" into "verified right".
> **When to use it.** After Phase 1 produces a draft `topology.md` and before you start Phase 2. Skim once; deep-dive when an edge looks wrong.

## Why refinement is non-optional

`gen_topology.py` reads at most `MAX_FILE_READ = 200_000` bytes per file and never follows real imports. It captures three edge kinds:

- **`source → copy`** — a single source of truth synced into copies. Drawn dotted when the reference's own line carries one of `system.file`, `from_plugin`, `skills.path`, `skills:`, `copied`, `synced`.
- **`uses`** — one entity consumes another. Drawn solid otherwise.

Both are heuristic. Phase 1 ships the draft; you ship the truth. The rest of this doc tells you which edges matter, how to verify them, and what to ignore.

## Which edges to verify first

Not all edges are equal. Spend your refinement budget on these, in order:

1. **Edges that affect the `source → copy` count.** A misclassified `source → copy` will make Phase 2 read the same content multiple times and miss the single source. If the count looks too high, the most common cause is a false positive: a file that mentions `system.file:` in a comment but is not actually a synced copy.
2. **Edges that change the inventory count.** If a file the script counts as a single entity is actually two (a Python module + its test under the same `__init__.py`-style aggregation), split it; if two are actually one (a documented interface + its auto-generated stub), merge it.
3. **Edges from manifests to the entity they declare.** `pyproject.toml` → `mypkg`, `package.json` → `app`, etc. — verify the manifest actually lists the package and the path is reachable. The script's `by_path` lookup is exact; any mismatch means the script can't see the relationship even if it exists.

## How to verify an edge

For each edge, do this:

1. Open the source file (the file the script emitted the edge from). Find the line containing the keyword (`system.file:`, `from_plugin`, `skills.path`, `skills:`, etc.) or the path token.
2. Confirm the line is *meant* to declare a dependency, not a string literal in a code example. A common false positive is a documentation example that uses `system.file: foo.md` to teach the syntax.
3. If the dependency is real, confirm the target path resolves. `git log -- path/to/target` confirms the file exists and was committed.
4. Re-emit the edge in your refined `topology.md` (edit the Mermaid block) so a re-run of `gen_topology.py` will diff against your hand-curated map.

## Common false positives

- **Comments / docs mentioning the keyword.** A README that says "use the `system.file:` directive" will be picked up as a `source → copy`. Check whether the line is in a code fence or a prose paragraph.
- **Test fixtures.** A test under `tests/fixtures/sample-system-file.md` may legitimately be a copy; decide whether to keep it.
- **Vendored content.** Anything under `vendor/`, `third_party/`, `node_modules/`, or `dist/` is ignored by the script (see `IGNORE_DIRS`); if you see a vendored entity in the inventory, the script's `IGNORED_DIRS` may be too permissive for your repo.

## Common false negatives

- **Imports the script doesn't know about.** Python `from . import sibling` (relative imports with no leading module) is hard to resolve from a single file. Phase 2 humans must add these manually.
- **Generated artifacts.** If `dist/foo.js` is built from `src/foo.ts`, the script sees `dist/foo.js` as a top-level entity but won't draw an edge from `src/foo.ts`. Add the edge by hand.
- **Edges to files the script skipped.** Files under `.gitignore`-style filters (e.g. large generated files) won't be in the inventory; their upstream source may still be. Add the upstream-to-skipped edge manually.

## What this guide deliberately does not do

- It does not propose a different edge taxonomy. The script emits two kinds; that's deliberate, and the taxonomy is documented in `references/topology_method.md`.
- It does not automate verification. The script's heuristic is fast; a human-in-the-loop check is slower but catches what regex can't.
- It does not propose a fix for `gen_topology.py`. Phase 3 (Generalization & Polish) is where script-level improvements land; this file is the bridge between "script says X" and "user believes X".
```

- [ ] **Step 2: Verify the file exists and has the required sections**

Run:
```bash
test -f references/edge_refinement.md \
  && rg -q '^## Why refinement is non-optional' references/edge_refinement.md \
  && rg -q '^## Which edges to verify first' references/edge_refinement.md \
  && rg -q '^## How to verify an edge' references/edge_refinement.md \
  && rg -q '^## Common false positives' references/edge_refinement.md \
  && rg -q '^## Common false negatives' references/edge_refinement.md \
  && rg -q '^## What this guide deliberately does not do' references/edge_refinement.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Verify the file has no `{{...}}` placeholders and no `<angle-bracket>` slots**

Run:
```bash
! rg -q '\{\{[A-Z_]+\}\}' references/edge_refinement.md \
  && ! rg -q '<[a-z -]+>' references/edge_refinement.md \
  && echo OK
```

Expected: `OK`. Per `references/doc_outlines.md` placeholder convention, content files (not templates) must not carry unsubstituted placeholders. The regex `<[a-z -]+>` matches slots with spaces too (Batch 1 F6 lockstep).

- [ ] **Step 4: Commit**

```bash
git add references/edge_refinement.md
git commit -m "docs(refs): add edge_refinement.md (Phase 1 verification guide)"
```

---

## Task 2: Add "How to refine edges" subsection to `### Phase 1 · Topology Generation` in `SKILL.md`

**Files:**
- Modify: `SKILL.md`
  - Inside `### Phase 1 · Topology Generation` (around line 92), insert a new `#### How to refine edges` subsection between step 3 and the next section.
  - The new subsection must reference the new `references/edge_refinement.md`.

**Interfaces:**
- Consumes: `references/edge_refinement.md` (Task 1)
- Produces: a SKILL.md subsection that points the agent at the deep guide

- [ ] **Step 1: Read the existing `### Phase 1 · Topology Generation` section to find the insertion point**

```bash
rg -n '^### Phase 1' SKILL.md
```

Expected: a line number; the section spans from that heading to the next `###` (Phase 2).

- [ ] **Step 2: Insert the new `#### How to refine edges` subsection**

Find the end of the `### Phase 1 · Topology Generation` step list (the line that says "Edit the Mermaid graphs so they tell the true story..." or similar — the last prose paragraph before `### Phase 2`). Insert the following block immediately **after** that paragraph (before `### Phase 2 · Module Deep-Dive`):

```markdown
#### How to refine edges

`gen_topology.py` reads at most `MAX_FILE_READ = 200_000` bytes per file and never follows real imports. Its three edge kinds (`source → copy`, `uses`) are heuristic, not authoritative. After the script produces a draft `topology.md`:

1. **Verify the 2–3 most structurally important edges by reading the actual manifests** (the spec's Phase 1 step 3). Edit the Mermaid block in `topology.md` if any are wrong.
2. **Spend the rest of the refinement budget on `source → copy` edges.** A misclassified copy makes Phase 2 read the same content multiple times and miss the single source.
3. **For the deep guide** (which edges to verify first, how to verify an edge, common false positives and negatives), see [`references/edge_refinement.md`](./references/edge_refinement.md).

The script's intent is to ship a useful draft quickly, not to be the final answer. Treat the auto-detected `topology.md` as a starting point; refine it as you read the manifests.
```

- [ ] **Step 3: Verify the new subsection is in place**

Run:
```bash
rg -q '^#### How to refine edges$' SKILL.md \
  && rg -q 'references/edge_refinement.md' SKILL.md \
  && rg -n '^### Phase 1' SKILL.md && rg -n '^### Phase 2' SKILL.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Verify heading monotonicity in the new subsection**

Run:
```bash
awk '/^### Phase 1/,/^### Phase 2/' SKILL.md | rg -c '^#### ' && echo "(should be at least 2: the existing sub-step + the new subsection)"
```

Expected: prints a number ≥ 2.

- [ ] **Step 5: Commit**

```bash
git add SKILL.md
git commit -m "docs(skill): add 'How to refine edges' subsection to Phase 1"
```

---

## Task 3: Add `## Workflow Variants` section to `SKILL.md`

**Files:**
- Modify: `SKILL.md`
  - Add a new `## Workflow Variants` h2 section immediately after `## When to Use` (around line 53, before `## Workflow` at line 53).

**Interfaces:**
- Consumes: nothing (new content; describes existing skill capabilities)
- Produces: a SKILL.md section enumerating Full / Lite / Progressive workflow branches

- [ ] **Step 1: Find the insertion point**

```bash
rg -n '^## Workflow$' SKILL.md
```

The new section goes immediately before this line.

- [ ] **Step 2: Insert the new section**

Find the line `## Workflow` in `SKILL.md`. Insert the following block **immediately before** it (and the existing `## Workflow` section stays verbatim):

```markdown
## Workflow Variants

The seven phases (Phase 0–6) above describe the **Full mode** workflow. Two lighter modes are supported without code changes — the skill's existing commands and the agent's discretion cover them. Pick the variant that matches the user's request.

### Full mode

Default. Run all seven phases in order. Use when the user wants a complete, polished doc set derived from a non-trivial repository.

### Lite mode (topology only)

Use when the user wants a quick map of the repo without the prose. The deliverables are:

- `topology.md` only (Phase 1 output).
- Skip Phases 2–6 entirely.

The user gets the structural map and can ask for more later. This is the right answer to "what's in this repo?" or "draw me the architecture".

### Progressive mode (topology → decide → continue)

Use when the user wants to evaluate the topology before committing to the full mining. The deliverables across two turns:

- **Turn 1** (Lite mode): `topology.md`.
- **Turn 2** (if the user says "continue" or similar): run Phases 2–6, producing the four prose documents and the `README.md` hub.

This is the right answer to "is this repo worth a full write-up?" — the user sees the topology first and decides.

### When to skip even Lite mode

Even Lite mode is overkill when:

- The repo is a single file or < 5 source files (the suitability rubric would mark it Low).
- The repo is a vendor fork with no top-level source (no modules to enumerate).
- The repo is archived (the rubric's hard veto).

In all three cases, `Phase -1 · Pre-Mining Assessment` (when enabled) tells the user up front; the agent should report "skip — and why" and stop.
```

- [ ] **Step 3: Verify the new section is in place and ordering is correct**

Run:
```bash
rg -q '^## Workflow Variants$' SKILL.md \
  && rg -q '^### Full mode' SKILL.md \
  && rg -q '^### Lite mode' SKILL.md \
  && rg -q '^### Progressive mode' SKILL.md \
  && rg -q '^### When to skip even Lite mode' SKILL.md \
  && rg -n '^## When to Use$|^## Workflow Variants$|^## Workflow$' SKILL.md \
  && echo OK
```

Expected: `OK`. The rg `-n` should show the three headings in this order: `## When to Use`, `## Workflow Variants`, `## Workflow`.

- [ ] **Step 4: Verify heading monotonicity around the new section**

Run:
```bash
awk '/^## When to Use/,/^## Workflow$/' SKILL.md | ! rg -q '^### ' && echo OK
```

Expected: `OK`. (Confirms no `###` heading sits between `## When to Use` and `## Workflow` — the new section uses `### Full mode` etc. *inside* `## Workflow Variants` and so is the same nesting level as the existing `### Full mode` placeholder doesn't break anything. If you see a false-positive, double-check: the `###` heading in the awk span would mean a misplaced `###` between the two `##` headings.)

Actually the right check: confirm `### Full mode` (the new) appears AFTER `## Workflow Variants`. The above rg ran without a final-anchor issue; just run:

```bash
rg -n '^## Workflow Variants$' SKILL.md && rg -n '^### Full mode' SKILL.md
```

Expected: both lines print, and the `### Full mode` line number is greater than the `## Workflow Variants` line number.

- [ ] **Step 5: Commit**

```bash
git add SKILL.md
git commit -m "docs(skill): add Workflow Variants section (Full / Lite / Progressive)"
```

---

## Task 4: Expand `## Failure Modes to Avoid` from 6 to 12 in `SKILL.md`

**Files:**
- Modify: `SKILL.md`
  - Append 6 new bullet entries to the existing `## Failure Modes to Avoid` list (currently 6 items).

**Interfaces:**
- Consumes: nothing (additive)
- Produces: a more complete failure-modes list

- [ ] **Step 1: Find the current list end**

```bash
rg -n '^## Failure Modes to Avoid$' SKILL.md
rg -n '^- Forgetting to produce' SKILL.md
```

The list currently ends at the `^- Forgetting to produce ... README.md; ...` bullet. Six new bullets go immediately after that one, before the next `## ` heading.

- [ ] **Step 2: Append 6 new bullet entries**

After the `Forgetting to produce the navigation README.md` bullet, add a blank line and the following 6 bullets:

```markdown
- **Mining a repo with no git history.** `gen_topology.py` reads the working tree but the vitality signal uses `git log -1 --format=%ct`; if the repo is not a Git repo or has no commits, that signal scores 0. Do not assume the rest of the file is broken — the on-disk tree is still valid; only Vitality is 0.
- **Mining a pure-docs repo (no code).** The topology will be empty or near-empty; the entity inventory will show 0 modules. The prose docs will be of limited value. If the user asks, recommend `--assess` (the suitability rubric's "Test/example presence" signal will mark it Low and the verdict will say "skip — and why").
- **Mining a > 10k-file repo.** `gen_topology.py`'s `--max-entities` defaults to 500; `--max-edges` defaults to 200. Above these the script silently truncates and prints a warning. Either pass higher caps (`--max-entities 2000 --max-edges 800`) or pre-warn the user that the topology is partial.
- **Treating `git log` failure as a fatal error.** The suitability rubric's not-a-git fallback scores Vitality = 0 and records the reason in `assess.md` §1. The other five signals are computed from the on-disk tree and remain valid. Do not abort the assessment just because the target isn't a Git repo.
- **Mining a monorepo as a single repo.** The script treats the top-level directory as one repo; each sub-package's `pyproject.toml` / `package.json` is a `py-package` / `node-package` entity. The inventory table will show them all but the prose docs will be confused about which "main" package to focus on. Mine each sub-package separately, or accept the lossy top-level view.
- **Skipping `--audience NAME` when the user has stated their role clearly.** If the user said "I'm a contributor" or "I just need a quick overview", do not skip `--assience` — the prefix adds a one-line blockquote that costs < 100 bytes and saves the reader several minutes of orientation.
```

- [ ] **Step 3: Verify the new bullets are in place and ordering is correct**

Run:
```bash
rg -c '^- ' SKILL.md | awk '$1 >= 12 { print "OK: >= 12 bullets, count =", $1; exit } $1 < 12 { print "FAIL: only", $1, "bullets"; exit 1 }'
```

Expected: prints `OK: >= 12 bullets, count = NN` with NN ≥ 12 (the 6 original + 6 new).

- [ ] **Step 4: Verify the 6 new bullets match the brief verbatim**

Run:
```bash
rg -q 'Mining a repo with no git history' SKILL.md \
  && rg -q 'Mining a pure-docs repo' SKILL.md \
  && rg -q 'Mining a > 10k-file repo' SKILL.md \
  && rg -q "Treating .git log. failure as a fatal error" SKILL.md \
  && rg -q 'Mining a monorepo as a single repo' SKILL.md \
  && rg -q 'Skipping .--audience NAME. when the user has stated' SKILL.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add SKILL.md
git commit -m "docs(skill): expand Failure Modes to Avoid (6 -> 12)"
```

---

## Task 5: Create `scripts/smoke.py`

**Files:**
- Create: `scripts/smoke.py`
  - Python 3.8+ stdlib only. 200–300 lines. Shebang `#!/usr/bin/env python3`.
  - Public API: `python scripts/smoke.py [--check-only] [--keep-tmp]`.

**Interfaces:**
- Consumes: `scripts/gen_topology.py`, `scripts/scaffold_docs.py`, AGENTS.md "safe smoke test" pattern, throwaway directories
- Produces: a stdlib runner that codifies the AGENTS.md safe smoke test + Phase-5 checks; exit 0 on full pass, non-zero on any check failure

- [ ] **Step 1: Write the file content**

Create `scripts/smoke.py` with the exact content below. The script is a single-file stdlib CLI; no `__pycache__`; argparse-driven.

```python
#!/usr/bin/env python3
"""Codified smoke test + Phase-5 checks for the repo-doc-miner skill.

This script exists because the AGENTS.md "Verification gates" section
contains a bash block (the "safe smoke test") that is meant to be run
manually after every change to `scripts/`. It is easy to skip; harder to
notice when it has drifted. This file makes it a single command and
adds Phase-5 checks (Mermaid fences, placeholder residue, link
integrity) that the manual block does not cover.

Usage
-----
    python scripts/smoke.py                # run the full battery
    python scripts/smoke.py --check-only    # no writes; just verify
    python scripts/smoke.py --keep-tmp      # leave the throwaway dir behind

Exit codes
----------
    0  every check passed
    1  one or more checks failed (printed to stderr)
    2  invocation error (bad args, scripts not on PATH, etc.)
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parent


def _print(check: str, ok: bool, detail: str = "") -> None:
    marker = "OK  " if ok else "FAIL"
    line = f"[{marker}] {check}"
    if detail:
        line += f"  -- {detail}"
    print(line)


def _safe_smoke(*, write: bool) -> int:
    """Replicate the AGENTS.md safe smoke test.

    Returns 0 on success. When `write` is False, the scaffolder is
    invoked with `--force` semantics skipped (i.e. not invoked at all),
    which makes this safe to call from `--check-only` mode.
    """
    failures = 0
    with tempfile.TemporaryDirectory(prefix="rsm-smoke-") as tmp:
        tmp_path = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)

        gen = subprocess.run(
            [sys.executable, str(HERE / "gen_topology.py"), str(tmp_path), "--project-name", "Demo"],
            capture_output=True, text=True,
        )
        if gen.returncode != 0:
            _print("gen_topology.py on throwaway", False, gen.stderr.strip().splitlines()[-1] if gen.stderr else "exit non-zero")
            failures += 1
        else:
            _print("gen_topology.py on throwaway", True, gen.stdout.strip().splitlines()[-1] if gen.stdout else "")

        if write:
            scaff = subprocess.run(
                [sys.executable, str(HERE / "scaffold_docs.py"), str(tmp_path),
                 "--project-name", "Demo", "--force"],
                capture_output=True, text=True,
            )
            if scaff.returncode != 0:
                _print("scaffold_docs.py on throwaway", False, scaff.stderr.strip().splitlines()[-1] if scaff.stderr else "exit non-zero")
                failures += 1
            else:
                _print("scaffold_docs.py on throwaway", True, scaff.stdout.strip().splitlines()[-1] if scaff.stdout else "")
                # Phase-5 checks on the materialized output
                failures += _phase5_checks(tmp_path / "docs" / "guides")
        else:
            _print("scaffold_docs.py skipped (--check-only)", True)

    return failures


def _phase5_checks(guides_dir: Path) -> int:
    """Mermaid fences closed, no broken `{{...}}` placeholders in shipped
    files, `TODO(doc-miner)` count printed (informational)."""
    failures = 0

    # 1. Mermaid fences are balanced.
    for md in sorted(guides_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        # Each ```mermaid ... ``` block must be closed.
        # We use a fence-aware state machine: count ``` not inside code blocks.
        in_code = False
        in_mermaid = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("```"):
                if not in_code:
                    in_code = True
                    in_mermaid = stripped == "```mermaid"
                else:
                    if in_mermaid:
                        in_mermaid = False
                    in_code = False
        if in_mermaid:
            _print(f"{md.name}: mermaid fence balanced", False, "unclosed ```mermaid block")
            failures += 1
        else:
            _print(f"{md.name}: mermaid fence balanced", True)

    # 2. No un-substituted `{{...}}` placeholders in shipped files (the
    # scaffolder substitutes `{{PROJECT_NAME}}`; nothing else is
    # expected to survive).
    for md in sorted(guides_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        leftover = re.findall(r"\{\{[A-Z_]+\}\}", text)
        if leftover:
            _print(f"{md.name}: no leftover placeholders", False, f"found {sorted(set(leftover))}")
            failures += 1
        else:
            _print(f"{md.name}: no leftover placeholders", True)

    # 3. No <angle-bracket> slots in shipped files (Batch 1 F6 rule).
    for md in sorted(guides_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        slots = re.findall(r"<[a-z -]+>", text)
        if slots:
            _print(f"{md.name}: no <angle-bracket> slots", False, f"found {sorted(set(slots))}")
            failures += 1
        else:
            _print(f"{md.name}: no <angle-bracket> slots", True)

    # 4. Informational: TODO(doc-miner) count per file.
    for md in sorted(guides_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        todo = len(re.findall(r"^> TODO\(doc-miner\)", text, re.M))
        if todo:
            print(f"[INFO] {md.name}: {todo} TODO(doc-miner) marker(s) (expected before Phase 4 fill-in)")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check-only", action="store_true",
                        help="Run only the topology generation step; skip scaffolder writes.")
    parser.add_argument("--keep-tmp", action="store_true",
                        help="(Reserved) leave the throwaway dir behind for inspection.")
    args = parser.parse_args(argv)

    if not (HERE / "gen_topology.py").is_file():
        print(f"error: {HERE / 'gen_topology.py'} not found", file=sys.stderr)
        return 2
    if not (HERE / "scaffold_docs.py").is_file():
        print(f"error: {HERE / 'scaffold_docs.py'} not found", file=sys.stderr)
        return 2

    print(f"repo-doc-miner smoke test (check_only={args.check_only})")
    print(f"  repo: {REPO}")
    print()

    failures = _safe_smoke(write=not args.check_only)
    print()
    if failures:
        print(f"FAILED: {failures} check(s) did not pass.", file=sys.stderr)
        return 1
    print("OK: all checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Verify the script parses and runs the no-write path**

Run:
```bash
test -f scripts/smoke.py \
  && python3 -m py_compile scripts/smoke.py && echo "py_compile OK" \
  && python3 scripts/smoke.py --check-only 2>&1 | tail -20
```

Expected: `py_compile OK` and the script runs the topology generation step, prints `[OK ]` for each sub-check, and ends with `OK: all checks passed.` Exit code 0.

- [ ] **Step 3: Verify the script runs the full battery (default) and exits 0**

Run:
```bash
python3 scripts/smoke.py 2>&1 | tail -20
echo "exit=$?"
```

Expected: prints the full battery (topology + scaffolder + Phase-5 checks) and ends with `OK: all checks passed.`; exit code 0.

- [ ] **Step 4: Verify the script surfaces failures when a check is broken (negative test)**

Make a temporary copy with a deliberate bug, run it, and confirm exit code != 0.

```bash
tmp=$(mktemp -d) && cp scripts/smoke.py "$tmp/smoke.py"
# Inject a check that will always fail.
python3 -c "
import re, pathlib
p = pathlib.Path('$tmp/smoke.py')
text = p.read_text()
text = text.replace('def _phase5_checks(guides_dir: Path) -> int:',
                    'def _phase5_checks(guides_dir: Path) -> int:\n    _print(\"intentional fail\", False, \"negative test\")\n    return 1\n    ', 1)
p.write_text(text)
"
python3 "$tmp/smoke.py" --check-only > /dev/null 2>&1
echo "exit=$?"
```

Expected: `exit=1`. (The patched script's `_phase5_checks` is never reached in `--check-only` mode; so this negative test only fires on the full battery. If the exit is 0 in `--check-only`, the negative test didn't reach the check. Drop the `--check-only` flag for the actual negative test:

```bash
python3 "$tmp/smoke.py" > /dev/null 2>&1
echo "exit=$?"
```

Expected: `exit=1`. (This runs the full battery, which calls `_phase5_checks`, which now returns 1.)

```bash
rm -rf "$tmp"
```

- [ ] **Step 5: Commit**

```bash
git add scripts/smoke.py
chmod +x scripts/smoke.py
git commit -m "feat(smoke): add scripts/smoke.py (codified AGENTS.md safe smoke + Phase-5 checks)"
```

---

## Task 6: Update `AGENTS.md` "Fixes already landed" list for Phase 2

**Files:**
- Modify: `AGENTS.md`
  - Append a single paragraph after the existing last sentence in the "Fixes already landed" block.

**Interfaces:**
- Consumes: nothing
- Produces: a `Phase 2 (Reliability & Operability, 2026-10-11)` paragraph

- [ ] **Step 1: Find the end of the existing "Fixes already landed" block**

```bash
rg -n '^### Fixes already landed' AGENTS.md
rg -n '^## Important Files' AGENTS.md
```

The "Fixes already landed" block ends just before `## Important Files`. Append the new paragraph immediately before that.

- [ ] **Step 2: Append the Phase 2 paragraph**

Find the last existing sentence in the "Fixes already landed" block (currently ending with the Phase 1 sentence) and append the following paragraph after it:

```markdown

Phase 2 (Reliability & Operability, 2026-10-11): reliability hardening for the v2 surface — `references/edge_refinement.md` (deep guide for verifying and refining auto-detected edges after Phase 1), a `#### How to refine edges` subsection in `SKILL.md` `### Phase 1`, a new `## Workflow Variants` section in `SKILL.md` enumerating Full / Lite / Progressive modes (no new code; the existing commands cover them), `## Failure Modes to Avoid` expanded from 6 to 12 entries (covering no-git-history, pure-docs, > 10k-file, monorepo, and `--audience`-skip cases), and a new `scripts/smoke.py` that codifies the AGENTS.md "safe smoke test" plus Phase-5 checks (Mermaid fence balance, no leftover `{{...}}` placeholders, no `<angle-bracket>` slots, informational `TODO(doc-miner)` count). All additions are stdlib-only and backwards-compatible; the existing v2 behaviour is unchanged when `--check-only` is not used.
```

- [ ] **Step 3: Verify the new paragraph is in place**

Run:
```bash
rg -q 'Phase 2 \(Reliability & Operability, 2026-10-11\)' AGENTS.md && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md
git commit -m "docs(agents): record Phase 2 fixes (Reliability & Operability)"
```

---

## Task 7: End-to-end smoke test

**Files:**
- Modify: none (this task only runs verification commands; nothing is committed)

**Interfaces:**
- Consumes: every file created or modified in Tasks 1–6
- Produces: a smoke-test log proving Phase 2 is wired up

- [ ] **Step 1: Verify `references/edge_refinement.md` exists and the new SKILL.md subsections are in place**

Run:
```bash
test -f references/edge_refinement.md \
  && rg -q '^#### How to refine edges' SKILL.md \
  && rg -q '^## Workflow Variants' SKILL.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 2: Run `scripts/smoke.py` and verify it exits 0**

Run:
```bash
python3 scripts/smoke.py 2>&1 | tail -5
echo "exit=$?"
```

Expected: ends with `OK: all checks passed.`; `exit=0`.

- [ ] **Step 3: Verify SKILL.md renders with monotonic headings end-to-end**

Run:
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

Expected: prints `OK: monotonic headings, total = NN` for some `NN` (the total should be at least 19 + the new Phase 2 headings, so ≥ 25).

- [ ] **Step 4: Verify the 12-item Failure Modes list is complete**

Run:
```bash
rg -c '^- ' SKILL.md | awk '$1 >= 12 { print "OK: >= 12 bullets, count =", $1; exit } $1 < 12 { print "FAIL: only", $1, "bullets"; exit 1 }'
```

Expected: prints `OK: >= 12 bullets, count = 12` (exactly 12; no extra bullets).

- [ ] **Step 5: Verify no untracked files remain after all commits**

Run:
```bash
git status --short
```

Expected: empty output.

- [ ] **Step 6: Final verification — no work to commit; close the loop**

Run:
```bash
git log --oneline -8
```

Expected: the Phase 2 commits appear at the top, in this order (most recent first):
1. `docs(agents): record Phase 2 fixes (Reliability & Operability)`
2. `feat(smoke): add scripts/smoke.py (codified AGENTS.md safe smoke + Phase-5 checks)`
3. `docs(skill): expand Failure Modes to Avoid (6 -> 12)`
4. `docs(skill): add Workflow Variants section (Full / Lite / Progressive)`
5. `docs(skill): add 'How to refine edges' subsection to Phase 1`
6. `docs(refs): add edge_refinement.md (Phase 1 verification guide)`

If any commit is missing, return to the corresponding task and amend before declaring Phase 2 done.

---

## Self-Review

**Spec coverage (§6 of the spec):**

| Spec requirement | Covered in task |
|---|---|
| §6.1 B2 Prerequisites declared | Already done in Phase 1 Batch 4 (no Phase 2 work) |
| §6.1 B3 Edge-refinement guide | Task 1 (new `references/edge_refinement.md`) + Task 2 (SKILL.md `#### How to refine edges` subsection) |
| §6.1 C3 Failure modes expand (6 → 12) | Task 4 (6 new bullets added) |
| §6.1 C12 Lite/Progressive documented | Task 3 (`## Workflow Variants` section) |
| §6.1 C4 `scripts/smoke.py` | Task 5 (new script with full battery + `--check-only`) |
| §6.2 New files (2) | Task 1 (`edge_refinement.md`) + Task 5 (`smoke.py`) |
| §6.3 SKILL.md changes (4 sub-edits) | Task 2 (Phase 1 subsection) + Task 3 (Workflow Variants) + Task 4 (Failure Modes expansion) — and Phase 1 Batch 4 already did Prerequisites |
| §6.4 Test plan (3 sub-checks) | Task 7 (Steps 2, 3, 4) |

**Placeholder scan:** No "TBD" / "implement later" / "fill in details" remain. Code blocks are provided verbatim for every code step. Each task's commit message is included.

**Type / name consistency check:**

- `edge_refinement.md` filename is consistent across Task 1 (creation) and Task 2 (SKILL.md reference).
- `scripts/smoke.py` filename is consistent across Task 5 (creation) and Task 7 (invocation).
- `--check-only` flag spelling is consistent across Task 5 (definition) and Task 7 (verification).
- `references/edge_refinement.md` reference path is consistent (no `../../` escapes; SKILL.md lives at the skill root).

No inconsistencies found.
