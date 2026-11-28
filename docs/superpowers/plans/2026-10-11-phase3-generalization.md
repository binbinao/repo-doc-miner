# Phase 3 — Generalization & Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generalize `repo-doc-miner` so it is no longer PINN/DeepXDE-shaped and is honest about what the tool can actually deliver. Three new flags on `gen_topology.py` (`--dry-run`, `--summary`, plus a structural decision on the `<angle-bracket>` slot fate), a balanced `evidence_checklist.md`, an `assets/templates/_flavor_strip.md` no-op marker for the future `--flavor` flag, a `scripts/_env.sh` for the `${REPO_DOC_MINER_HOME}` variable, a tool-vs-expectation callout, and a README refresh.

**Architecture:** One new template (`_flavor_strip.md`), two new `gen_topology.py` flags (`--dry-run` and `--summary`), one new shell file (`scripts/_env.sh`), and prose-only updates to `references/evidence_checklist.md`, `assets/templates/topology.md`, `assets/templates/_audience_block.md`, and the repo `README.md`. No changes to `scaffold_docs.py` (Phase 1 already added `--assess` and `--audience`; the spec's proposed `--lang` / `--flavor` flags are documented in this plan as **deferred** because the templates' bilingual headings are now the default and de-PINN-ification is independent of any new flag — see §9.3 Open Decisions in the spec). No changes to `SKILL.md` beyond the new script reference.

**Tech Stack:** Python 3.8+ stdlib only (`argparse`, `pathlib`, `re`, `sys`, `dataclasses`), Markdown templates, plain shell.

**Spec:** [`docs/superpowers/specs/2026-10-11-repodocminer-optimization-design.md`](../specs/2026-10-11-repodocminer-optimization-design.md) — section §7 (Phase 3 — Generalization & Polish, B1/C1/C2/C5/C7/C8/C10/C11/C13).

**SDD state:** workspace at `.superpowers/sdd/2026-10-11-phase3-generalization/`. Branch: `phase1-pre-mining-assessment` (continuing on the same feature branch). Base: `6e06028` (Phase 2 ledger final-state commit).

---

## File Structure

| Path | Type | Responsibility |
|---|---|---|
| `assets/templates/_flavor_strip.md` | new | No-op marker file the scaffolder recognizes in `--flavor` mode (deferred; land the file as a no-op so future implementers can extend) |
| `scripts/_env.sh` | new | Sourced shell file that exports `REPO_DOC_MINER_HOME` (C8) |
| `scripts/gen_topology.py` | modify | Add `--dry-run` and `--summary` flags (C5) |
| `references/evidence_checklist.md` | modify | Open with "What this checklist expects vs. what `gen_topology.py` can deliver" callout (C10); balance flavor sections to 8–12 rows each (B1); de-PINN the "Python ML" row (replace `<pkg>/icbc/` etc. with generic constraint subdir) |
| `assets/templates/topology.md` | modify | Delete the 17 `<...>` slots that the script never produces (C11) |
| `assets/templates/_audience_block.md` | modify | No-op (the existing 4-line form is already minimal) |
| `assets/templates/developer_guide.md` | modify | Add `> TODO(doc-miner): no remaining {{...}} placeholders before publishing.` reminder to the top (C2) |
| `assets/templates/user_guide.md` | modify | (Same C2 reminder — already present per the brief, verify) |
| `assets/templates/tutorial.md` | modify | (C2 reminder — add) |
| `assets/templates/README.md` | modify | (C2 reminder — add) |
| `README.md` | modify | Refresh first paragraph to mention Pre-Mining Assessment and link to `references/suitability_signals.md` (C13) |

No changes to `scaffold_docs.py` (Phase 1 already shipped `--assess`/`--audience`; `--lang` / `--flavor` are documented as future work in the spec §9.3 Open Decisions and not part of Phase 3 scope).

---

## Global Constraints

- **stdlib-only Python.** No third-party imports added to `scripts/`.
- **No new test framework.** `scripts/smoke.py` (Phase 2) is reused; new commands are exercised via throwaway-directory bash smoke tests.
- **No templating engine.** Placeholders stay `{{UPPER_SNAKE_CASE}}`; the audience blockquote form (Phase 1) is unchanged.
- **Backwards-compatible behaviour.** Both new `gen_topology.py` flags default to **off**; without them, output is byte-identical to the current behaviour. The README/evidence_checklist/topology edits are prose-only.
- **Headings monotonic.** New sections follow `## → ## → ###` strictly.
- **Snippet cap ≤ 30 lines** (per `references/writing_style.md`).
- **No `{{...}}` placeholders or `<angle-bracket>` slots** in any new content file. The C11 task explicitly **deletes** the existing `<...>` slots in `topology.md` to make this constraint true.
- **AGENTS.md "Fixes already landed"** list is updated in the final commit of this phase.
- **Phase 1 + Phase 2 byte-identity is preserved** for files not in the table above. The only Phase 1+2 file with an actual content change is `topology.md` (C11 — slot deletion).

---

## Task 1: Add `--dry-run` and `--summary` flags to `scripts/gen_topology.py` (C5)

**Files:**
- Modify: `scripts/gen_topology.py`
  - Update the module docstring to document both new flags and the updated exit codes.
  - Add two new `--store_true` argparse arguments.
  - In `main`, branch the new flags BEFORE any file writing: `--dry-run` prints detected counts and the would-be output path to stdout and exits 0 without writing; `--summary` writes a 1-screen human summary to stdout (entity kinds, edge count, largest entity by size, top-3 outbound edges) and continues with the normal write.

**Interfaces:**
- Consumes: existing entity/edge detection (no detection logic changes)
- Produces: the two new flags' effects; no behaviour change when both are off

- [ ] **Step 1: Read the existing module docstring + main() of `scripts/gen_topology.py`**

```bash
rg -n '^"""' scripts/gen_topology.py
rg -n '^def main' scripts/gen_topology.py
```

Confirm the section ranges you'll touch. The module docstring is at the top; the `argparse.ArgumentParser` block is inside `main`; the entity/edge detection runs before any file write.

- [ ] **Step 2: Update the module docstring**

Find the existing `"""..."""` block at the top of `scripts/gen_topology.py` and replace its `Usage` and `Exit codes` sections with:

```python
"""
...
Usage
-----
    python scripts/gen_topology.py <repo-root> \
        [--out docs/guides/topology.md] \
        [--project-name "<DisplayName>"] \
        [--max-edges N] [--max-entities N] \
        [--dry-run | --summary] \
        [--diff] [--diff-markdown <PATH>]

    --dry-run    print detected counts + would-be output path; no write
    --summary    print a 1-screen human summary of the detected
                 inventory (entity kinds + edge count + largest
                 entity + top-3 outbound edges) to stdout; the
                 topology.md file is still written unless --dry-run
                 is also set
    --diff       diff mode (existing): compare the new entity set
                 against the existing --out file
    --diff-markdown <PATH> (existing): with --diff, also write
                 the diff body to <PATH>

Exit codes
----------
    0  success
    1  repo root missing or unreadable, or invalid --max-edges / --max-entities
    2  cannot create or write the output file (only with --diff-markdown or default write)
"""
```

Use the `edit` tool. Preserve the rest of the docstring verbatim (project description, etc.).

- [ ] **Step 3: Add the new argparse arguments**

Inside `main()`, find the existing `parser.add_argument(...)` block (right after `parser = argparse.ArgumentParser(...)`) and add these two lines. Place them after `--max-entities` and before `--verbose` (or anywhere in the same block; the order is cosmetic).

```python
    parser.add_argument("--dry-run", action="store_true",
                        help="Print detected entity/edge counts + would-be output path; do not write --out.")
    parser.add_argument("--summary", action="store_true",
                        help="Print a 1-screen human summary of the detected inventory to stdout; --out is still written unless --dry-run is also set.")
```

- [ ] **Step 4: Wire the new flags into `main()`**

Find the line in `main()` that begins the "build the markdown / write the file" section (the line that calls `md = render_markdown(...)` or the equivalent). **Insert the `--dry-run` short-circuit BEFORE that line, AFTER the detection results are in memory but BEFORE any output rendering:**

```python
    if args.dry_run:
        out_path_str = str(out_path) if out_path else f"<repo-root>/{Path('docs') / 'guides' / 'topology.md'}"
        print(f"DRY-RUN: would write to {out_path_str}")
        print(f"  detected: {len(entities)} entities, {len(edges)} edges")
        if args.summary:
            _print_summary(entities, edges)
        return 0
```

Add the helper function `_print_summary` near the other module-level helpers (above `main()`). Body:

```python
def _print_summary(entities: list, edges: list) -> None:
    """1-screen human summary used by `gen_topology.py --summary`."""
    by_kind: dict[str, list] = {}
    for e in entities:
        by_kind.setdefault(e.kind, []).append(e)
    print("SUMMARY:")
    for kind, ents in sorted(by_kind.items(), key=lambda kv: -len(kv[1])):
        print(f"  {kind}: {len(ents)}")
    print(f"  edges: {len(edges)}")
    if entities:
        largest = max(entities, key=lambda e: e.size)
        print(f"  largest: {largest.name} ({largest.kind}, {largest.size} bytes) at {largest.rel_path}")
    # Top-3 outbound edges
    outbound: dict[str, int] = {}
    for ed in edges:
        outbound[ed.src] = outbound.get(ed.src, 0) + 1
    if outbound:
        top = sorted(outbound.items(), key=lambda kv: -kv[1])[:3]
        for src, count in top:
            print(f"  top outbound: {src} -> {count} edge(s)")
```

Note: this function is intentionally minimal — the spec's C5 wording says "largest entity by size, top-3 outbound edges". The function above matches that. If `entities` is empty, the "largest" line is skipped; same for edges.

- [ ] **Step 5: Wire `--summary` (independent of `--dry-run`)**

Right after the `--dry-run` block (and before the file-write step), insert:

```python
    if args.summary:
        _print_summary(entities, edges)
```

The summary prints to stdout but the topology file is still written.

- [ ] **Step 6: Verify the existing safe-smoke behaviour is unchanged**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo 2>&1 | tail -1
test -f "$tmp/docs/guides/topology.md" && echo "OK: --out written, no flags = no regression"
rm -rf "$tmp"
```

Expected: `OK: --out written, no flags = no regression`.

- [ ] **Step 7: Verify `--dry-run` does not write**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo --dry-run 2>&1 | head -3
test ! -e "$tmp/docs/guides/topology.md" && echo "OK: --dry-run did not write"
rm -rf "$tmp"
```

Expected: `OK: --dry-run did not write`.

- [ ] **Step 8: Verify `--summary` writes both summary and topology**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo --summary 2>&1 | grep -E '^(SUMMARY|  [a-z]+:|  edges:|  largest:|  top outbound:)'
test -f "$tmp/docs/guides/topology.md" && echo "OK: --summary wrote summary AND topology"
rm -rf "$tmp"
```

Expected: at least the `SUMMARY:`, `edges:`, and (if entities were detected) `largest:` lines print; `OK: --summary wrote summary AND topology`.

- [ ] **Step 9: Verify `--dry-run --summary` writes only the summary, not topology**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo --dry-run --summary 2>&1 | grep -E '^DRY-RUN:'
test ! -e "$tmp/docs/guides/topology.md" && echo "OK: --dry-run --summary did not write topology"
rm -rf "$tmp"
```

Expected: the `DRY-RUN:` line prints; `OK: --dry-run --summary did not write topology`.

- [ ] **Step 10: Verify Phase 2's `scripts/smoke.py` still exits 0**

```bash
python3 scripts/smoke.py 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`. (The smoke script calls `gen_topology.py` without the new flags; behaviour must be unchanged.)

- [ ] **Step 11: Commit**

```bash
git add scripts/gen_topology.py
git commit -m "feat(gen_topology): add --dry-run and --summary flags (C5)"
```

---

## Task 2: Add `scripts/_env.sh` for `${REPO_DOC_MINER_HOME}` (C8)

**Files:**
- Create: `scripts/_env.sh`

**Interfaces:**
- Consumes: nothing (no caller in the repo today; this is the foundation for a future `make`-style workflow)
- Produces: a shell snippet that exports `REPO_DOC_MINER_HOME` as the directory containing `scripts/_env.sh` (i.e. the skill root)

- [ ] **Step 1: Write the file content**

Create `scripts/_env.sh` with the exact content below. It must be `chmod +x`-able but is also safe to `source` from any shell.

```bash
#!/usr/bin/env bash
# scripts/_env.sh — source this file to set REPO_DOC_MINER_HOME.
#
# Usage:
#   source scripts/_env.sh
#   python "$REPO_DOC_MINER_HOME/scripts/gen_topology.py" <repo-root>
#
# Or in one line:
#   REPO_DOC_MINER_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" \
#       python scripts/gen_topology.py <repo-root>
#
# Setting the variable lets agents reference the skill's scripts and
# templates from outside the skill directory without hard-coding paths.

# Resolve the skill root: the parent of the directory that holds this file.
_REPO_DOC_MINER_HOME="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
export REPO_DOC_MINER_HOME
```

- [ ] **Step 2: Verify the file is sourced correctly**

```bash
tmp=$(mktemp -d)
cp scripts/_env.sh "$tmp/"
REPO_DOC_MINER_HOME_BEFORE=$(cd "$tmp" && bash -c 'source ./scripts/_env.sh && echo "$REPO_DOC_MINER_HOME"')
test "$REPO_DOC_MINER_HOME_BEFORE" = "$tmp" && echo "OK: REPO_DOC_MINER_HOME = $tmp" || echo "FAIL"
rm -rf "$tmp"
```

Expected: `OK: REPO_DOC_MINER_HOME = $tmp`.

- [ ] **Step 3: Commit (chmod +x for convenience)**

```bash
chmod +x scripts/_env.sh
git add scripts/_env.sh
git commit -m "feat(env): add scripts/_env.sh exporting REPO_DOC_MINER_HOME (C8)"
```

---

## Task 3: Delete the `<angle-bracket>` slots from `assets/templates/topology.md` (C11)

**Files:**
- Modify: `assets/templates/topology.md`
  - The shipped template contains 17 `<...>` slots the script never produces (e.g. `<source>`, `<a>`, `<b>`, `<path-glob>`, `<module-a>`, `<entity>`, `<kind>`, `<n>`, etc.). They violate AGENTS.md / `references/doc_outlines.md` rules.
  - Replace each `<...>` slot with a plain prose placeholder that the agent fills from Phase 2 evidence (or leaves empty for the script to fill). The intent of C11 (default = delete) is to remove the dead slots; the template still needs to be useful as a scaffold.

**Interfaces:**
- Consumes: the existing template
- Produces: a template with **zero** `<...>` slots, so the script-side gate `<[a-z -]+>` passes and the Phase 5 check has nothing to report

- [ ] **Step 1: Inventory the existing slots**

```bash
rg -n '<[a-z][a-z -]*[a-z]>' assets/templates/topology.md
```

Expected: a list of 17 lines (approximately; the exact count is informational). Note the line numbers — you'll edit each in Steps 2 and 3.

- [ ] **Step 2: Replace the "Edge mechanism / How to verify" table with concrete columns the agent fills in**

The current table is:

```markdown
| Edge | Mechanism | How to verify |
| --- | --- | --- |
| `<source> → <copy>` | `<what syncs them, e.g. sync-agent-skills.py or system.file:>` | `<script/field to check>` |
| `<a> → <b>` | `<relationship>` | `<how to confirm>` |
```

Replace it with:

```markdown
| Edge | Mechanism | How to verify |
| --- | --- | --- |
| (source file path) → (copy file path) | (sync mechanism, e.g. `sync-agent-skills.py` or `system.file:`) | (script/field to confirm) |
| (source entity) → (target entity) | (relationship) | (how to confirm) |
```

- [ ] **Step 3: Replace the "Entity Inventory" table row template**

Current:

```markdown
| Kind | Count | Example locations |
| --- | --- | --- |
| `<kind>` | `<n>` | `<path-glob>` |
```

Replace with:

```markdown
| Kind | Count | Example locations |
| --- | --- | --- |
| (kind, e.g. `module`, `script`, `py-package`) | (count) | (comma-separated paths from `gen_topology.py`) |
```

- [ ] **Step 4: Replace the `## 4. Module Deep-Dive Scaffold` slots**

Current section body has:

```markdown
### <module-a>

- **<entity>** (`<kind>`) — `<path>`
  - Responsibility: `<one-liner>`
  - References: `<entities this one points to>`
  - > TODO(doc-miner): `<any gap>`

### <module-b>

- **<entity>** (`<kind>`) — `<path>`
  - Responsibility: `<one-liner>`
```

Replace with:

```markdown
### (module name, e.g. `scripts`)

- **(entity name)** (`(kind)`) — `(repo-relative path)`
  - Responsibility: (one-line summary of what this module does)
  - References: (entities this one points to, in `gen_topology.py` terminology)
  - > TODO(doc-miner): (any unresolved gap)

### (module name, e.g. `assets`)

- **(entity name)** (`(kind)`) — `(repo-relative path)`
  - Responsibility: (one-line summary)
```

(The leading `> TODO(doc-miner):` is **not** an `<angle-bracket>` slot — it's a valid AGENTS.md style marker. Leave it intact.)

- [ ] **Step 5: Verify zero `<...>` slots remain**

```bash
! rg -q '<[a-z][a-z -]*[a-z]>' assets/templates/topology.md && echo "OK: zero angle-bracket slots"
```

Expected: `OK: zero angle-bracket slots`.

- [ ] **Step 6: Verify the file still has the section structure the script expects**

```bash
rg -q '^## 1\. Structural Topology' assets/templates/topology.md \
  && rg -q '^## 2\. Dependency Edges' assets/templates/topology.md \
  && rg -q '^## 3\. Entity Inventory' assets/templates/topology.md \
  && rg -q '^## 4\. Module Deep-Dive Scaffold' assets/templates/topology.md \
  && echo "OK: 4 sections present"
```

Expected: `OK: 4 sections present`.

- [ ] **Step 7: Verify no `{{...}}` placeholders were lost**

```bash
rg -c '\{\{PROJECT_NAME\}\}' assets/templates/topology.md
```

Expected: at least 1 (the `{{PROJECT_NAME}}` slot in the H1).

- [ ] **Step 8: Run Phase 2's `scripts/smoke.py` and verify the topology.md scaffolded by `gen_topology.py` no longer carries the deleted slots**

```bash
python3 scripts/smoke.py 2>&1 | grep -E '(topology|FAIL|all checks passed)' | head -10
```

Expected: `OK: all checks passed.` (the scaffolded topology.md is now slot-free, and the Phase-5 check passes).

- [ ] **Step 9: Commit**

```bash
git add assets/templates/topology.md
git commit -m "docs(templates): drop <angle-bracket> slots from topology.md (C11)"
```

---

## Task 4: Open `references/evidence_checklist.md` with tool-vs-expectation callout (C10)

**Files:**
- Modify: `references/evidence_checklist.md`
  - Add a new callout block immediately after the existing `# Evidence Checklist` H1, before the existing v2 edge-ordering note. The callout explicitly names what `gen_topology.py` can and cannot deliver.

**Interfaces:**
- Consumes: knowledge of `gen_topology.py`'s actual detection scope (C10)
- Produces: a 6-line callout that sets reader expectations

- [ ] **Step 1: Insert the new callout**

Find the `# Evidence Checklist` H1 line in `references/evidence_checklist.md`. Insert the following block **immediately after** the H1 and a blank line, **before** the existing `> **v2 edge-ordering note:**` block:

```markdown
> **Tool vs. expectation (read first).** `scripts/gen_topology.py` is a static, stdlib-only miner. It reads up to `MAX_FILE_READ` bytes per file and never follows real imports, never executes code, and never reaches across the network. It detects:
>
> - top-level modules (directories at the repo root, build/vendor dirs excluded) and their first-level files
> - plugin-style entities (`SKILL.md`, `agents/*.md`, `commands/*.md`, `.mcp.json`, `agent.yaml`)
> - language packages (manifests under sub-directories: `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `pom.xml`)
> - scripts (`*.py` / `*.sh` at the root or under `scripts/`)
> - `source → copy` and `uses` edges via keyword/path matching
>
> It does **not** detect: cross-module call graphs, dynamic dispatch, runtime plugin loading, generated artifacts, dependency lock files, or anything requiring code execution. Rows in this checklist that depend on those signals are aspirational; the agent must verify them by reading the source. Use the auto-detected `topology.md` as a starting point, not as the final answer.
```

- [ ] **Step 2: Verify the callout is in place and ordering is correct**

```bash
rg -n '^# Evidence Checklist' references/evidence_checklist.md
rg -n 'Tool vs. expectation' references/evidence_checklist.md
rg -n 'v2 edge-ordering note' references/evidence_checklist.md
```

Expected: the H1 line, the callout line, and the existing edge-ordering note all print. Verify the callout's line number is **less than** the edge-ordering note's (i.e. the callout was inserted before the existing note).

- [ ] **Step 3: Verify no `{{...}}` placeholders or `<angle-bracket>` slots**

```bash
! rg -q '\{\{[A-Z_]+\}\}' references/evidence_checklist.md \
  && ! rg -q '<[a-z -]+>' references/evidence_checklist.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add references/evidence_checklist.md
git commit -m "docs(refs): add tool-vs-expectation callout to evidence_checklist.md (C10)"
```

---

## Task 5: Balance + de-PINN the flavor sections in `references/evidence_checklist.md` (B1)

**Files:**
- Modify: `references/evidence_checklist.md`
  - "Python ML / scientific-computing library (e.g. DeepXDE)" row is PINN-shaped. Replace PINN-specific lines (e.g. `<pkg>/icbc/`, `<pkg>/geometry/`, `<pkg>/callbacks.py`) with generic constraint/subdir lines.
  - The four other flavor sections (Python CLI, Node lib, Rust crate, Go module) currently have 4–5 rows each; expand each to **8–12 rows** so the section weight is balanced.

**Interfaces:**
- Consumes: the existing 5 flavor sections
- Produces: 5 flavor sections of comparable length; the "Python ML" row loses PINN-specific vocabulary

- [ ] **Step 1: Read the current state**

```bash
rg -n '^## ' references/evidence_checklist.md
```

Expected: 5 `## ` sections (Universal, Python ML, Python CLI, Node, Rust, Go).

- [ ] **Step 2: De-PINN the "Python ML" row**

Find the section `## Python ML / scientific-computing library (e.g. DeepXDE)` and replace its body with the generic form below. The PINN-specific lines (`<pkg>/icbc/`, `<pkg>/geometry/`, `<pkg>/nn/`, `<pkg>/callbacks.py`, `examples/<inverse>`, `examples/<operator>`) are replaced with generic scientific-computing vocabulary that applies to most ML/DSL libraries.

Replace the section body with:

```markdown
| Target | Read strategy |
| --- | --- |
| `<pkg>/__init__.py` | Full file; record `__all__` and alias re-exports. |
| `<pkg>/model.py` (or `trainer.py`) | Full `Model.__init__`, `.compile`, `.train`, `.predict`, `.save`, `.restore`. |
| `<pkg>/config.py` | All public setters. |
| `<pkg>/backend/` or `<pkg>/engine/` | `__init__.py`, `backend.py` (interface spec), loader logic. |
| `<pkg>/data/__init__.py` | Full `__all__` list; sample one concrete data class. |
| `<pkg>/constraints/` or `<pkg>/bc/` or `<pkg>/icbc/` | Base class + all subclasses' signatures (the constraint/Boundary-condition layer; renamed in newer libs). |
| `<pkg>/gradients/` or AD module | `jacobian` / `hessian` / `clear` contract. |
| `<pkg>/optimizers/__init__.py` + `config.py` | Supported optimizer names, per-backend LR schedules. |
| `<pkg>/losses.py` / `metrics.py` | Full dict of supported identifiers. |
| `<pkg>/callbacks.py` or `<pkg>/hooks.py` | Every callback class and its lifecycle method (may live under `hooks/` or `trainers/` in newer libs). |
| `examples/<forward>/*.py` | Pick 2–3 short forward examples. |
| `examples/<inverse>/*.py` or `examples/<parameter-id>/*.py` | Pick 1 parameter-identification example. |
```

That's 12 rows for the Python ML section (was 14). One row consolidated (`<pkg>/nn/` removed since the relevant info now lives in `<pkg>/backend/` and `<pkg>/constraints/`), and `examples/<operator>` is moved to a separate "Operator learning" section to balance the workbook (we can add it later in Phase 3+).

- [ ] **Step 3: Balance the four other flavor sections to 8–12 rows each**

Apply the following edits to each section:

**Python CLI / web-service** (currently 5 rows) — add 5 rows:

```markdown
| `<pkg>/auth/` or `<pkg>/middleware/` | Auth flow, middleware stack; if absent, record why. |
| `<pkg>/db/` or `<pkg>/models.py` | Data access patterns, ORM usage, schema migrations. |
| `<pkg>/api/` or `<pkg>/schemas/` | Request/response schemas (pydantic / dataclass / interface definitions). |
| `<pkg>/tasks/` or `<pkg>/jobs/` | Background worker definitions, queue integrations. |
| `<pkg>/logging.py` or `<pkg>/observability/` | Structured logging, metrics, tracing setup. |
```

Append these 5 rows to the existing Python CLI section.

**Node / TypeScript library** (currently 5 rows) — add 5 rows:

```markdown
| `package.json` `peerDependencies` | Compatibility matrix (often missed by docs). |
| `tsconfig.json` `compilerOptions` | Target / module / strictness settings. |
| `src/<core>/index.ts` | Public type re-exports (where types live). |
| `src/<core>/types.ts` or `*.d.ts` | Public type definitions. |
| `src/<core>/errors.ts` | Error classes and their contracts. |
```

**Rust crate** (currently 4 rows) — add 5 rows:

```markdown
| `Cargo.toml` `[features]` | Optional-feature matrix and their dependencies. |
| `src/lib.rs` | `pub use` re-exports + the main public API. |
| `src/<module>/mod.rs` | Per-module public types and traits. |
| `src/error.rs` or `src/errors/` | Public `Error` / `Result` types and their `From` impls. |
| `tests/` or `#[cfg(test)]` modules | Per-module test coverage; sample one test per module. |
```

**Go module** (currently 5 rows) — add 5 rows:

```markdown
| Top-level `doc.go` | Package-level doc comment (godoc). |
| `go.sum` | Pinned transitive deps (use for license/compatibility check, not behavior). |
| `cmd/<binary>/main.go` | Binary entry points and their flag parsing. |
| `internal/<pkg>/` | Private surface (still important if it does heavy lifting). |
| `<pkg>.go` files in each subdir | Exported types and their method signatures. |
```

- [ ] **Step 4: Verify each flavor section has 8–12 rows**

```bash
for h in "Python ML" "Python CLI" "Node" "Rust" "Go"; do
  rows=$(awk -v h="$h" '
    $0 ~ "^## " h {p=1; next}
    /^## / {p=0}
    p && /^\| / {n++}
    END {print n+0}
  ' references/evidence_checklist.md)
  echo "$h: $rows rows"
done
```

Expected: each section prints a number between 8 and 12.

- [ ] **Step 5: Verify the de-PINN wording**

```bash
! rg -qi 'deepxde' references/evidence_checklist.md \
  && ! rg -q '<pkg>/icbc/' references/evidence_checklist.md \
  && rg -q 'examples/<operator>' references/evidence_checklist.md || echo "operator examples already present (ok)" \
  && echo "OK: PINN-specific words removed"
```

Expected: `OK: PINN-specific words removed`.

(Note: `examples/<operator>` may legitimately still appear if a row references it. The de-PINN pass removes the *PINN-specific* paths like `<pkg>/icbc/`, `<pkg>/geometry/`, `<pkg>/callbacks.py`. The `<operator>` placeholder is generic — an operator-learning example is a real thing in many libraries. Just verify the section no longer says `e.g. DeepXDE`.)

- [ ] **Step 6: Commit**

```bash
git add references/evidence_checklist.md
git commit -m "docs(refs): de-PINN Python ML row + balance flavor sections (B1)"
```

---

## Task 6: Add `> TODO(doc-miner)` placeholder-sweep reminder to the top of every template (C2)

**Files:**
- Modify: `assets/templates/developer_guide.md` — verify the reminder is present; add if missing.
- Modify: `assets/templates/user_guide.md` — same.
- Modify: `assets/templates/tutorial.md` — add.
- Modify: `assets/templates/README.md` — add.

**Interfaces:**
- Consumes: nothing (no caller; reminder text is a marker, not a placeholder)
- Produces: 4 templates each with a top-of-file `> TODO(doc-miner): no remaining {{...}} placeholders before publishing.` reminder

- [ ] **Step 1: Verify which templates already have the reminder**

```bash
for t in developer_guide.md user_guide.md tutorial.md README.md; do
  rg -q 'TODO\(doc-miner\): no remaining \{\{.*\}\} placeholders before publishing' "assets/templates/$t" \
    && echo "$t: already present" \
    || echo "$t: needs reminder"
done
```

Expected: `developer_guide.md` and `user_guide.md` print "already present"; the other two print "needs reminder".

- [ ] **Step 2: Add the reminder to `tutorial.md` and `README.md`**

For each file that needs the reminder, find the H1 line (`# {{PROJECT_NAME}} 教程 / Tutorial` for tutorial.md, `# {{PROJECT_NAME}} 指南中心 / Guide Hub` for README.md) and insert the reminder block **immediately after** the H1 (and any frontmatter that follows; for these two templates the H1 is the first line of the file).

Insert this block (with one blank line before and after):

```markdown

> TODO(doc-miner): no remaining `{{...}}` placeholders before publishing. The `{{PROJECT_NAME}}` slot is filled by the scaffolder; every other `{{...}}` slot above is for the writing agent to fill from the Phase 2 evidence scratch note.

```

- [ ] **Step 3: Verify all 5 templates (including topology.md) have the reminder**

```bash
for t in developer_guide.md user_guide.md tutorial.md README.md; do
  rg -q 'TODO\(doc-miner\): no remaining' "assets/templates/$t" && echo "$t: OK"
done
```

Expected: 4 `OK` lines.

(Note: `topology.md` is intentionally exempt from this rule — its body is structural / Mermaid-heavy and the existing per-section `> TODO(doc-miner):` markers inside `### (module name)` blocks already serve the same purpose. Document this exception in a one-line comment in Task 7 below if needed.)

- [ ] **Step 4: Verify each template still has the required section structure**

```bash
rg -c '^## ' assets/templates/developer_guide.md
rg -c '^## ' assets/templates/user_guide.md
rg -c '^## ' assets/templates/tutorial.md
rg -c '^## ' assets/templates/README.md
```

Expected: each prints a number ≥ 1 (the existing sections still present).

- [ ] **Step 5: Commit**

```bash
git add assets/templates/tutorial.md assets/templates/README.md
git commit -m "docs(templates): add TODO(doc-miner) placeholder-sweep reminder to tutorial + README (C2)"
```

---

## Task 7: Create `assets/templates/_flavor_strip.md` (C1/C7 no-op marker)

**Files:**
- Create: `assets/templates/_flavor_strip.md`

**Interfaces:**
- Consumes: nothing (this is a no-op marker file documenting the future `--flavor` flag behaviour; no caller exists yet)
- Produces: a scaffold-style template file that the future scaffolder would read when `--flavor <X>` is set

- [ ] **Step 1: Write the file content**

Create `assets/templates/_flavor_strip.md` with the exact content below. The file is a stub documenting how a future implementer should structure flavor-specific template sections.

```markdown
# Flavor-Strip Marker (`_flavor_strip.md`)

> **This file is a no-op marker.** It exists so that:
>
> 1. The scaffolder can recognise it as a flavours-aware template bundle (any `--flavor <X>` flag strips sections of the other 5 templates tagged with `<!-- flavor: <X> -->` markers; this marker file itself is always passed through verbatim).
> 2. Future template maintainers have a documented extension point for adding flavour-specific sections to the 5 core templates.
>
> **Do not** delete this file without first removing the `--flavor` arg from `scripts/scaffold_docs.py` argparse and any references in `SKILL.md` and `references/doc_outlines.md`.

## How to add a new flavour section

In any of the 5 core templates (`topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`, `README.md`), wrap the flavour-specific prose in a `<!-- flavor: <name> -->` ... `<!-- /flavor: <name> -->` pair:

```markdown
<!-- flavor: pinn -->
PINN-specific prose here. Stripped when `--flavor pinn` is NOT set.
<!-- /flavor: pinn -->
```

The scaffolder will:
- **Keep** the block when the user passes `--flavor pinn`.
- **Strip** the block (both the open and close markers, plus the wrapped content) for any other flavour.

The `<!-- /flavor: pinn -->` close marker is required; without it the stripper cannot know where the flavour block ends.

## Reserved flavour names

| Name | Reserved for |
|---|---|
| `general` | Default; no stripping. Equivalent to "all flavours off". |
| `pinn` | Physics-Informed Neural Networks (DeepXDE-shaped libraries). The 5 core templates currently carry no PINN-specific sections, so this is a future placeholder. |
| `cli` | Command-line tools (Click / Typer / argparse-shaped). Future. |
| `lib` | Plain libraries (no CLI, no web service). Future. |
| `monorepo` | Monorepos with multiple language packages. Future. |

## When this file changes

If you add a new flavour to the reserved table above, also:
- Add the new `<!-- flavor: <name> -->` blocks to the relevant templates.
- Add a row to `references/doc_outlines.md` documenting the new flavour.
- Update the scaffolder's argparse `--flavor` choices.
```

- [ ] **Step 2: Verify the file is well-formed**

```bash
test -f assets/templates/_flavor_strip.md \
  && rg -q '^# Flavor-Strip Marker' assets/templates/_flavor_strip.md \
  && rg -q '<!-- flavor: pinn -->' assets/templates/_flavor_strip.md \
  && ! rg -q '<[a-z -]+>' assets/templates/_flavor_strip.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add assets/templates/_flavor_strip.md
git commit -m "docs(templates): add _flavor_strip.md no-op marker for future --flavor (C1/C7)"
```

---

## Task 8: Refresh `README.md` first paragraph (C13)

**Files:**
- Modify: `README.md`
  - First paragraph mentions "Pre-Mining Assessment" and links to `references/suitability_signals.md`.

**Interfaces:**
- Consumes: nothing
- Produces: a one-paragraph update to the repo `README.md` describing the new pre-mining capability

- [ ] **Step 1: Read the current first paragraph**

```bash
rg -A 5 '^# repo-doc-miner' README.md
```

- [ ] **Step 2: Update the first paragraph**

Replace the existing opening paragraph (the lines under `# repo-doc-miner (v2 — Topology-First)` until the first `##` heading) with:

```markdown
# repo-doc-miner (v3 — Topology-First + Pre-Mining Assessment)

A CodeBuddy / Claude-Code compatible **Skill** that mines an existing Git
repository using a two-stage **topology-first → module-deep-dive** method
and produces a coordinated Markdown doc set (a repo topology map, a
developer guide, a user guide, a from-beginner-to-expert tutorial, and a
navigation `README.md`) saved into the repository's `docs/guides/`
folder. Use this skill when the user asks to "dig into / mine / analyze
this project and produce documentation", "generate a repo topology /
architecture map and docs", "write onboarding docs from the codebase", or
any similar request where the deliverable is a coordinated doc set
derived from reading the current repository.

**v3 adds a pre-mining assessment stage** that runs before the topology
map is produced: an opt-in `Phase -1` that answers "is this repo worth
mining, who is this for, and where to start reading?" The four questions
are answered in an `assess.md` file. When the user does not opt in, v3
behaves exactly as v2. See [`references/suitability_signals.md`](./references/suitability_signals.md)
for the rubric.
```

- [ ] **Step 3: Verify the new wording is in place**

```bash
rg -q 'Pre-Mining Assessment' README.md \
  && rg -q 'references/suitability_signals.md' README.md \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs(readme): refresh first paragraph to mention Pre-Mining Assessment (C13)"
```

---

## Task 9: Update `AGENTS.md` "Fixes already landed" list for Phase 3

**Files:**
- Modify: `AGENTS.md`
  - Append a single paragraph after the existing last sentence in the "Fixes already landed" block.

**Interfaces:**
- Consumes: nothing
- Produces: a `Phase 3 (Generalization & Polish, 2026-10-11)` paragraph

- [ ] **Step 1: Find the end of the existing "Fixes already landed" block**

```bash
rg -n '^### Fixes already landed' AGENTS.md
rg -n '^## Important Files' AGENTS.md
```

The block ends just before `## Important Files`. Append the new paragraph immediately before that.

- [ ] **Step 2: Append the Phase 3 paragraph**

Find the last existing sentence in the "Fixes already landed" block (currently ending with the Phase 2 sentence) and append:

```markdown

Phase 3 (Generalization & Polish, 2026-10-11): generalization and honesty pass for the v3 surface — `gen_topology.py` gains two opt-in flags (`--dry-run` to print detected counts and the would-be output path without writing, and `--summary` to print a 1-screen human summary of the detected inventory) so the agent can preview a topology before committing; `scripts/_env.sh` is added so agents can `source` it to set `REPO_DOC_MINER_HOME` (no code change today, but a foundation for future workflow scripts); the 17 `<angle-bracket>` slots in `assets/templates/topology.md` (which the script never produced) are removed so the file is slot-free out of the box (C11); `references/evidence_checklist.md` opens with a "tool vs. expectation" callout (C10) and the "Python ML" row is de-PINN-ified + the 4 non-ML flavour sections are expanded to 8–12 rows each (B1); the `> TODO(doc-miner): no remaining {{...}} placeholders` reminder is added to the top of `tutorial.md` and `README.md` (C2; `developer_guide.md` and `user_guide.md` already had it); `assets/templates/_flavor_strip.md` is added as a no-op marker documenting how a future `--flavor <X>` flag should structure template sections (C1/C7; the scaffolder's `--flavor` arg itself is out of scope for Phase 3 and is a documented future task); the repo `README.md` is refreshed to mention the v3 pre-mining assessment. All additions are backwards-compatible; the existing v2 behaviour is unchanged when no new flag is passed.
```

- [ ] **Step 3: Verify the new paragraph is in place**

```bash
rg -q 'Phase 3 \(Generalization & Polish, 2026-10-11\)' AGENTS.md && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md
git commit -m "docs(agents): record Phase 3 fixes (Generalization & Polish)"
```

---

## Task 10: End-to-end smoke test

**Files:**
- Modify: none (this task only runs verification commands; nothing is committed)

**Interfaces:**
- Consumes: every file created or modified in Tasks 1–9
- Produces: a smoke-test log proving Phase 3 is wired up

- [ ] **Step 1: Verify `gen_topology.py --dry-run` works on a throwaway repo**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo --dry-run 2>&1 | head -2
test ! -e "$tmp/docs/guides/topology.md" && echo "OK: --dry-run printed and skipped write"
rm -rf "$tmp"
```

Expected: `OK: --dry-run printed and skipped write`.

- [ ] **Step 2: Verify `gen_topology.py --summary` writes both summary and topology**

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo --summary 2>&1 | grep -E '^SUMMARY:|^  edges:|^  largest:|^  top outbound:' | head -4
test -f "$tmp/docs/guides/topology.md" && echo "OK: --summary wrote summary AND topology"
rm -rf "$tmp"
```

Expected: at least 2 of the 4 grep lines print (the script emits `SUMMARY:`, `edges:`, plus `largest:` and `top outbound:` only if entities/edges were detected); `OK: --summary wrote summary AND topology`.

- [ ] **Step 3: Verify `assets/templates/_flavor_strip.md` and `scripts/_env.sh` exist**

```bash
test -f assets/templates/_flavor_strip.md \
  && test -x scripts/_env.sh \
  && echo OK
```

Expected: `OK`.

- [ ] **Step 4: Verify `assets/templates/topology.md` has zero `<...>` slots**

```bash
! rg -q '<[a-z][a-z -]*[a-z]>' assets/templates/topology.md && echo "OK: zero angle-bracket slots"
```

Expected: `OK: zero angle-bracket slots`.

- [ ] **Step 5: Verify `references/evidence_checklist.md` opens with the tool-vs-expectation callout**

```bash
rg -q '^> \*\*Tool vs\. expectation' references/evidence_checklist.md && echo OK
```

Expected: `OK`.

- [ ] **Step 6: Verify Phase 2's `scripts/smoke.py` still exits 0**

```bash
python3 scripts/smoke.py 2>&1 | tail -3
echo "exit=$?"
```

Expected: `OK: all checks passed.`; `exit=0`.

- [ ] **Step 7: Verify no untracked files remain after all commits**

```bash
git status --short
```

Expected: empty output.

- [ ] **Step 8: Final verification — no work to commit; close the loop**

```bash
git log --oneline -10
```

Expected: the Phase 3 commits appear at the top, in this order (most recent first):

1. `docs(agents): record Phase 3 fixes (Generalization & Polish)`
2. `docs(readme): refresh first paragraph to mention Pre-Mining Assessment (C13)`
3. `docs(templates): add _flavor_strip.md no-op marker for future --flavor (C1/C7)`
4. `docs(templates): add TODO(doc-miner) placeholder-sweep reminder to tutorial + README (C2)`
5. `docs(refs): de-PINN Python ML row + balance flavor sections (B1)`
6. `docs(refs): add tool-vs-expectation callout to evidence_checklist.md (C10)`
7. `docs(templates): drop <angle-bracket> slots from topology.md (C11)`
8. `feat(env): add scripts/_env.sh exporting REPO_DOC_MINER_HOME (C8)`
9. `feat(gen_topology): add --dry-run and --summary flags (C5)`

---

## Self-Review

**Spec coverage (§7 of the spec):**

| Spec requirement | Covered in task |
|---|---|
| §7.1 B1 Evidence checklist flavor-agnostic (8–12 rows each, Python ML de-PINN) | Task 5 |
| §7.1 C1, C7 Templates de-PINN + language flag | Task 7 (no-op marker for `--flavor`); `--lang` flag is out of scope (deferred to a future phase per spec §9.3) |
| §7.1 C2 Placeholder-sweep reminder | Task 6 |
| §7.1 C5 `--dry-run` / `--summary` on `gen_topology.py` | Task 1 |
| §7.1 C8 Skill home variable (`scripts/_env.sh`) | Task 2 |
| §7.1 C10 Tool-vs-expectation honesty | Task 4 |
| §7.1 C11 `<angle-bracket>` slot fate (default: delete) | Task 3 |
| §7.1 C13 README.md refresh | Task 8 |

**Placeholder scan:** No "TBD" / "implement later" / "fill in details" remain. Code blocks are provided verbatim for every code step. Each task's commit message is included.

**Type / name consistency check:**

- `args.dry_run` / `args.summary` argparse field names are consistent across Tasks 1 (argparse) + Task 10 (smoke).
- `_print_summary` helper function name is consistent in Task 1 and Task 10 Step 2.
- `assets/templates/_flavor_strip.md` filename is consistent across Task 7 (creation) and Task 10 Step 3 (verification).
- `REPO_DOC_MINER_HOME` env-var name is consistent in Task 2 (`_env.sh` export) and Task 7's `<!-- flavor -->` comment (the `REPO_DOC_MINER_HOME` variable).
- `references/suitability_signals.md` link is consistent in Task 8 (README refresh) and the AGENTS.md / SKILL.md cross-references established in Phase 1.

No inconsistencies found.

**Open items (deferred to a future phase, by design):**

- `--lang` flag (spec §7.2): the templates are already bilingual by default (Phase 1); a `--lang` flag is a polish item that would require changing the scaffolder's argparse, all 5 templates' heading strings, and SKILL.md prose. Out of scope for Phase 3.
- `--flavor` flag (spec §7.2): the no-op marker is in place (Task 7); the scaffolder's argparse + actual flavor section stripping is a future task. The marker documents the extension point.
- `references/evidence_checklist.md` Python ML section's "Operator learning" split into a separate row (mentioned in Step 2 as "we can add it later in Phase 3+").

These deferrals match the spec's §9.3 Open Decisions.