# Phase 4 — Persona Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the two persona-tail gaps from the 2026-11-26 review — novice "first five minutes" material and professional "adoption decision" material — via additive template sections, evidence-checklist rows, and doc-outline updates, with zero script changes and zero breakage of existing section-number references.

**Architecture:** All changes are Markdown, additive-only. `user_guide.md` gains §1 pitch/non-goals blocks, §4 exhaustive rule, §18.1 error triage, and new §19–§21 (glossary, getting help, pitfalls), renumbering old §19/§20 → §22/§23 (verified: no external references). `developer_guide.md` gains §2 vitality rows, §4.1 entry-point map subsection, and new §16–§19 (test map, release policy, dependency risk, quality signals) appended after §15 — no existing section renumbered (Phase -1 references to §4–§5, §15, §1–§14 stay valid). The README hub gains a persona-routing table. `evidence_checklist.md`, `doc_outlines.md`, `SKILL.md`, and `AGENTS.md` are updated in lockstep.

**Tech Stack:** Markdown templates + references (no code; `gen_topology.py` and `scaffold_docs.py` are explicitly untouched).

**Spec:** [`docs/superpowers/specs/2026-10-11-repodocminer-optimization-design.md`](../specs/2026-10-11-repodocminer-optimization-design.md) — section §8 (Phase 4 — Persona Coverage).

---

## Global Constraints

- **No script changes** — `gen_topology.py` and `scaffold_docs.py` untouched (spec §8.5).
- **No new files** — templates stay five, references stay four (spec §8.5).
- **Additive-only** — no existing section heading renumbered except `user_guide.md` old §19/§20 → §22/§23; no PINN-flavored section touched (spec §3, §8.5).
- **Placeholder conventions** — `{{UPPER_SNAKE_CASE}}`; `_OR_TODO` suffix for facts that may legitimately not exist (references/doc_outlines.md conventions).
- **Existing cross-references must survive** — `user_guide §1–§11`, `developer_guide §4–§5`, `§15`, `§1–§14`, `topology §1–§3` (Phase -1 spec/plan) all stay valid.
- **Verification is command-driven** — no test framework exists; use throwaway-repo smoke tests and greps (AGENTS.md "Testing & QA").
- **AGENTS.md bookkeeping** — "Fixes already landed" updated in the final commit of this phase (spec §9.2).
- **Section counts** — user_guide 20 → 23 sections; developer_guide 15 → 19 sections.

---

## Task 1: `assets/templates/user_guide.md` — novice sections

**Files:**
- Modify: `assets/templates/user_guide.md`

**Interfaces:**
- Produces: new placeholders `{{ONE_SENTENCE_PITCH}}`, `{{NON_GOAL_1}}`, `{{NON_GOAL_2}}`, `{{FAQ_SYMPTOM_3}}`/`{{FAQ_PLAIN_3}}`/`{{FAQ_FIX_3}}`, `{{FAQ_SYMPTOM_4}}`/`{{FAQ_PLAIN_4}}`/`{{FAQ_FIX_4}}`, `{{TERM_n}}`/`{{TERM_n_PLAIN}}`/`{{TERM_n_SYMBOL}}` (n=1..3), `{{ISSUE_TRACKER_URL_OR_TODO}}`, `{{COMMUNITY_URL_OR_TODO}}`, `{{PITFALL_n}}`/`{{PITFALL_n_TRUTH}}` (n=1..2). Tasks 4–5 reference the new section numbers.

- [x] **Step 1: Add pitch + non-goals to §1** — after the line `- {{CAPABILITY_3}}`, insert:

```markdown

In one sentence: {{ONE_SENTENCE_PITCH}}.

**What it does NOT do (non-goals):**

- {{NON_GOAL_1}}
- {{NON_GOAL_2}}
```

- [x] **Step 2: Add the exhaustive-knobs rule to §4** — after the line `- \`{{CONFIG_KEY_2}}\` — {{CONFIG_KEY_2_DESC}}`, insert:

```markdown

> List every user-facing knob here — exhaustive, not a sample (harvest from the config module).
```

- [x] **Step 3: Add §18.1 error triage** — after the §18 table row `| \`{{FAQ_SYMPTOM_2}}\` | {{FAQ_FIX_2}} |`, insert:

```markdown

### 18.1 Error triage / 报错急救

Deeper than the quick FAQ above: what the error actually means, in plain language, and the exact fix.

| Error message | What it actually means | Fix |
| --- | --- | --- |
| `{{FAQ_SYMPTOM_3}}` | {{FAQ_PLAIN_3}} | {{FAQ_FIX_3}} |
| `{{FAQ_SYMPTOM_4}}` | {{FAQ_PLAIN_4}} | {{FAQ_FIX_4}} |
```

- [x] **Step 4: Insert new §19–§21** — before the line `## 19. Minimal runnable templates`, insert:

```markdown
## 19. Glossary / 术语表

Domain jargon this project uses, in plain language, mapped to the code that defines it.

| Term | Plain-language meaning | Defined at |
| --- | --- | --- |
| `{{TERM_1}}` | {{TERM_1_PLAIN}} | `{{TERM_1_SYMBOL}}` |
| `{{TERM_2}}` | {{TERM_2_PLAIN}} | `{{TERM_2_SYMBOL}}` |
| `{{TERM_3}}` | {{TERM_3_PLAIN}} | `{{TERM_3_SYMBOL}}` |

## 20. Getting help / 求助渠道

- Issue tracker: {{ISSUE_TRACKER_URL_OR_TODO}} — search open issues before filing a new one.
- Discussions / community: {{COMMUNITY_URL_OR_TODO}}.
- **How to ask a good question:** include the version, a minimal runnable snippet, and the exact error text.

## 21. Common pitfalls & misconceptions / 避坑清单

| Misconception ("don't panic when…") | What is actually going on |
| --- | --- |
| {{PITFALL_1}} | {{PITFALL_1_TRUTH}} |
| {{PITFALL_2}} | {{PITFALL_2_TRUTH}} |

```

- [x] **Step 5: Renumber the tail** — four heading edits:

- `## 19. Minimal runnable templates` → `## 22. Minimal runnable templates`
- `### 19.1 Forward problem` → `### 22.1 Forward problem`
- `### 19.2 Inverse problem` → `### 22.2 Inverse problem`
- `## 20. Further reading` → `## 23. Further reading`

- [x] **Step 6: Add the support pointer to §23** — inside Further reading, after the `- Official docs: {{DOCS_URL_OR_TODO}}` line, add:

```markdown
- Support channels: see §20 (Getting help).
```

- [x] **Step 7: Verify** — Run: `grep -c "^## [0-9]" assets/templates/user_guide.md`
Expected: `23`

- [x] **Step 8: Commit (held until user confirms)** — `feat(templates): user_guide persona sections — pitch, non-goals, error triage, glossary, help, pitfalls`

---

## Task 2: `assets/templates/developer_guide.md` — evaluator sections

**Files:**
- Modify: `assets/templates/developer_guide.md`

**Interfaces:**
- Produces: new placeholders `{{REPO_URL_OR_TODO}}`, `{{LATEST_RELEASE_OR_TODO}}`, `{{LAST_COMMIT_DATE_OR_TODO}}`, `{{ENTRY_CLI_OR_TODO}}`/`{{ENTRY_API_OR_TODO}}`/`{{ENTRY_LIB}}`/`{{ENTRY_HOOK_OR_TODO}}` + `*_DESC`, `{{TEST_DIR_LAYOUT}}`, `{{TEST_RUN_ALL_CMD}}`, `{{TEST_RUN_ONE_CMD}}`, `{{TEST_COVERAGE_CMD_OR_TODO}}`, `{{CI_WORKFLOW_PATH}}`, `{{CI_GATES}}`, `{{VERSION_SCHEME}}`, `{{CHANGELOG_PATH_OR_TODO}}`, `{{BREAKING_POLICY_OR_TODO}}`, `{{SUPPORT_MATRIX_OR_TODO}}`, `{{DEP_RISK_n}}`-family (n=1..2), `{{TODO_HOTSPOTS}}`, `{{DEBT_NOTES_OR_TODO}}`, `{{BUS_FACTOR_OR_TODO}}`. §1–§15 numbering unchanged.

- [x] **Step 1: Add vitality rows to §2** — after the line `- Version source: \`{{VERSION_SOURCE_FILE}}\``, insert:

```markdown

- Repo homepage: `{{REPO_URL_OR_TODO}}`
- Latest release / tag: `{{LATEST_RELEASE_OR_TODO}}`
- Last commit: {{LAST_COMMIT_DATE_OR_TODO}} (vitality signal)
```

- [x] **Step 2: Add §4.1 entry-point map** — after the line `Narrative: {{ARCHITECTURE_NARRATIVE}}`, insert:

```markdown

### 4.1 Entry-point map

Where execution starts, per surface:

| Surface | Entry point | What it does |
| --- | --- | --- |
| CLI | `{{ENTRY_CLI_OR_TODO}}` | {{ENTRY_CLI_DESC}} |
| API / service | `{{ENTRY_API_OR_TODO}}` | {{ENTRY_API_DESC}} |
| Library import | `{{ENTRY_LIB}}` | {{ENTRY_LIB_DESC}} |
| Plugin / hook registration | `{{ENTRY_HOOK_OR_TODO}}` | {{ENTRY_HOOK_DESC}} |
```

- [x] **Step 3: Append §16–§19** — after the §15.3 table (the last table of §15, ending with `| \`{{ERR_2}}\` | {{ERR_2_FIX}} |`), before the `---` + `## References` block, insert:

```markdown

## 16. Test map

- Layout: `{{TEST_DIR_LAYOUT}}` — unit vs. integration vs. e2e split.
- Run everything: `{{TEST_RUN_ALL_CMD}}`.
- Run a single test: `{{TEST_RUN_ONE_CMD}}`.
- Coverage: `{{TEST_COVERAGE_CMD_OR_TODO}}`.
- CI gates: `{{CI_WORKFLOW_PATH}}` runs {{CI_GATES}}.

## 17. Release & compatibility policy

- Versioning scheme: {{VERSION_SCHEME}} (source: `{{VERSION_SOURCE_FILE}}`).
- Changelog: `{{CHANGELOG_PATH_OR_TODO}}`.
- Breaking-change policy: {{BREAKING_POLICY_OR_TODO}}.
- Supported-version matrix: {{SUPPORT_MATRIX_OR_TODO}}.

## 18. Dependency risk surface

| Dependency | Version constraint | License | Risk notes |
| --- | --- | --- | --- |
| `{{DEP_RISK_1}}` | {{DEP_RISK_1_VER}} | {{DEP_RISK_1_LICENSE}} | {{DEP_RISK_1_NOTES}} |
| `{{DEP_RISK_2}}` | {{DEP_RISK_2_VER}} | {{DEP_RISK_2_LICENSE}} | {{DEP_RISK_2_NOTES}} |

> Risk notes cover: unmaintained/deprecated upstream, license incompatibility, pinned ceilings, known CVEs. Write `n/a — clean` when nothing applies.

## 19. Quality & debt signals

- `TODO` / `FIXME` hotspots (top modules by count): {{TODO_HOTSPOTS}}.
- Known dead code or deprecation debt: {{DEBT_NOTES_OR_TODO}}.
- Contributor concentration (bus factor): {{BUS_FACTOR_OR_TODO}} — from `git shortlog -sn`.
```

- [x] **Step 4: Verify** — Run: `grep -c "^## [0-9]" assets/templates/developer_guide.md`
Expected: `19`

- [x] **Step 5: Commit (held)** — `feat(templates): developer_guide evaluator sections — entry points, tests, releases, dependency risk, quality`

---

## Task 3: `assets/templates/README.md` — persona routing

**Files:**
- Modify: `assets/templates/README.md`

**Interfaces:**
- Consumes: section numbers from Tasks 1–2 (`user_guide` §19/§22, `developer_guide` §16–§19).
- Produces: persona routing table; existing "Reading order suggestions" list unchanged.

- [x] **Step 1: Insert the routing table** — before the line `## Reading order suggestions`, insert:

```markdown
## Persona routing / 你是谁,从哪开始

| You are… | Start with |
| --- | --- |
| Completely new to this project | `user_guide.md` §1 (pitch + non-goals) → §2 (install) → §19 (glossary) → §22 (minimal example) |
| Deciding whether to adopt / depend on this repo | `developer_guide.md` §2 (metadata) + §16–§19 (tests, releases, dependencies, quality), then `topology.md` |
| Extending or contributing | `developer_guide.md` end to end, cross-reference `topology.md` |
| Just want the big picture | `topology.md` |

> Not sure which one you are? Read `user_guide.md` §1 — its one-sentence pitch will tell you quickly.

```

- [x] **Step 2: Verify** — Run: `grep -c "Persona routing" assets/templates/README.md`
Expected: `1`

- [x] **Step 3: Commit (held)** — `feat(templates): README hub persona routing table`

---

## Task 4: `references/evidence_checklist.md` — persona-fact rows

**Files:**
- Modify: `references/evidence_checklist.md`

**Interfaces:**
- Produces: Universal-section rows + Phase-2 scratch-note bullets that feed Task 1–2 placeholders. Section numbers referenced: `developer_guide` §2/§4.1/§17/§19, `user_guide` §20.

- [x] **Step 1: Extend the CI row** — replace `| \`.github/workflows/\` (top-level only) | CI install commands, supported platforms. |` with:

```markdown
| `.github/workflows/` (top-level only) | CI install commands, supported platforms, and the test/coverage/lint gates that run per PR. |
```

- [x] **Step 2: Add Universal rows** — after the `| Makefile | Common developer commands. |` row, insert:

```markdown
| `tests/` / `test/` top-level layout | Test map: unit/integration split, run-all + run-one commands. |
| `CHANGELOG.md` / `CHANGES.rst` / GitHub Releases | Release cadence, breaking-change history, versioning scheme. |
| `git log` / `git tag` vitality | Last commit date, tag cadence — trust signals for developer guide §2/§17. |
| `rg -c "TODO\|FIXME"` per module | Quality/debt hotspots for developer guide §19. |
| `SUPPORT.md` / `.github/ISSUE_TEMPLATE/` / `SECURITY.md` | Getting-help channels + security policy for user guide §20. |
| Entry-point files (`__main__.py` / `cli.py` / `app.py` / `cmd/`) | Entry-point map surfaces for developer guide §4.1. |
```

- [x] **Step 3: Extend the Phase-2 output note** — in "Output of Phase 2", after the `- List of chosen example files with a 1-line summary each.` bullet, insert:

```markdown
- Test-map facts: layout, run-all / run-one commands, coverage command, CI gates.
- Release facts: latest tag, last commit date, changelog path, versioning scheme.
- Quality signals: TODO/FIXME counts per module, `git shortlog -sn` top contributors.
- Support channels: issue tracker, discussions/community, security contact.
```

- [x] **Step 4: Verify** — Run: `grep -c "Test-map facts\|Release facts\|Quality signals\|Support channels" references/evidence_checklist.md`
Expected: `4`

- [x] **Step 5: Commit (held)** — `docs(evidence): persona-fact rows — tests, releases, vitality, quality, support, entry points`

---

## Task 5: `references/doc_outlines.md` — outline sync

**Files:**
- Modify: `references/doc_outlines.md`

**Interfaces:**
- Consumes: final section structures from Tasks 1–2.
- Produces: authoritative outlines; numbers must match the templates exactly.

- [x] **Step 1: Update the developer_guide outline** — `## developer_guide.md (15 sections)` → `## developer_guide.md (19 sections)`; item 2 becomes:

```markdown
2. **Metadata snapshot** — license, supported languages/runtimes, dependency list, version source, repo homepage, latest release, last-commit vitality.
```

Item 4 becomes (add a sub-bullet after it):

```markdown
4. **Runtime architecture overview** — ASCII diagram linking the main data/model/runtime classes.
    - 4.1. **Entry-point map** (subsection) — where execution starts per surface: CLI / API / library import / plugin hook.
```

After item 15, append:

```markdown
16. **Test map** — test layout, run-all + run-one commands, coverage, CI gates.
17. **Release & compatibility policy** — versioning scheme, changelog, breaking-change policy, supported-version matrix.
18. **Dependency risk surface** — per-dependency version constraint, license, risk notes (deprecated / pinned / known CVEs).
19. **Quality & debt signals** — TODO/FIXME hotspots, dead code, bus factor (`git shortlog -sn`).
```

And extend the developer-guide grounding rules with:

```markdown
- The test map MUST contain a run-one command that actually exists in the repo (verify before citing).
```

- [x] **Step 2: Update the user_guide outline** — `## user_guide.md (20 sections)` → `## user_guide.md (23 sections)`; items 1, 4, 18 gain notes; old 19/20 renumber to 22/23; new 19–21 inserted:

```markdown
1. What the library can solve / do (user-facing capability list, one-sentence plain-language pitch, non-goals).
```

```markdown
4. Global configuration — precision, seed, autodiff mode, JIT, verbosity. Every user-facing knob, exhaustive.
```

```markdown
18. Troubleshooting — curated FAQ table + §18.1 error triage (error → plain-language meaning → fix).
```

```markdown
19. Glossary — domain jargon in plain language, each term mapped to the defining symbol.
20. Getting help — issue tracker, discussions/community, how to ask a good question.
21. Common pitfalls & misconceptions — "don't panic when…" pairs.
22. Minimal runnable templates — ≥2 end-to-end snippets (forward problem + inverse problem or operator-learning problem).
23. Further reading — pointers to official docs, papers, tutorial, support channels.
```

And extend the user-guide grounding rules with:

```markdown
- Glossary terms MUST cite the defining symbol (`path/to/file.py::Symbol`) in the "Defined at" column.
```

- [x] **Step 3: Verify** — Run: `grep -n "sections)" references/doc_outlines.md`
Expected: `developer_guide.md (19 sections)` and `user_guide.md (23 sections)`

- [x] **Step 4: Commit (held)** — `docs(outlines): sync outlines to persona section structure`

---

## Task 6: `SKILL.md` — workflow + resource descriptions

**Files:**
- Modify: `SKILL.md`

**Interfaces:**
- Consumes: section numbers from Tasks 1–2.
- Produces: updated template descriptions and Phase 3/4 workflow rules.

- [x] **Step 1: Update the Resources descriptions** — replace the two template lines with:

```markdown
- `assets/templates/developer_guide.md` — 19-section schema (overview → architecture → entry-point map → module tours → test map → release policy → dependency risk → quality signals → extension SOPs → debugging).
- `assets/templates/user_guide.md` — 23-section schema (install → runtime config → core objects → main loop → advanced features → FAQ + error triage → glossary → getting help → pitfalls → minimal runnable examples).
```

- [x] **Step 2: Extend the Phase 3 verification bullets** — the developer-guide bullet becomes:

```markdown
- The **developer guide** covers architecture, every top-level module, runtime config, extension/contribution SOPs, and debugging tips, plus the entry-point map (§4.1) and the evaluator sections (test map, release policy, dependency risk, quality signals — §16–§19).
```

The user-guide bullet becomes:

```markdown
- The **user guide** walks from installation to the most advanced user-facing feature, using API names that actually exist in the repo, and includes the novice sections (§1 pitch + non-goals, §18.1 error triage, §19 glossary, §20 getting help, §21 pitfalls).
```

- [x] **Step 3: Add the Phase 4 persona rule** — in "### Phase 4 · Writing", after the "Mark unresolved gaps explicitly" bullet, insert:

```markdown
- **Fill the persona sections**: the novice-facing (pitch + non-goals, error triage, glossary, getting help, pitfalls) and evaluator-facing (entry-point map, test map, release policy, dependency risk, quality signals) sections are mandatory content, not optional flavor. If the repo genuinely lacks a fact, keep the heading and mark it `> TODO(doc-miner): n/a — <reason>`.
```

- [x] **Step 4: Verify** — Run: `grep -c "19-section\|23-section\|Fill the persona sections" SKILL.md`
Expected: `3`

- [x] **Step 5: Commit (held)** — `docs(skill): persona sections in workflow and resource descriptions`

---

## Task 7: `AGENTS.md` — bookkeeping

**Files:**
- Modify: `AGENTS.md`

- [x] **Step 1: Drop the stale line counts** — in the Key Directories table, replace:

```markdown
| `scripts/` | The only executable code. `gen_topology.py` (512 lines, entity/edge miner + Mermaid renderer), `scaffold_docs.py` (132 lines, template materializer). |
```

with:

```markdown
| `scripts/` | The only executable code. `gen_topology.py` (entity/edge miner + Mermaid renderer), `scaffold_docs.py` (template materializer). |
```

- [x] **Step 2: Append to "Fixes already landed"** — extend the final list item with:

```markdown
, the Phase 4 persona-coverage template sections (user_guide §1 pitch/non-goals, §18.1 error triage, §19–§21 glossary/help/pitfalls; developer_guide §2 vitality rows, §4.1 entry-point map, §16–§19 evaluator sections; README persona routing; matching evidence-checklist rows and doc outlines — spec §8)
```

- [x] **Step 3: Verify** — Run: `grep -c "512 lines" AGENTS.md`
Expected: `0`

- [x] **Step 4: Commit (held)** — `docs(agents): Phase 4 landed-facts bookkeeping`

---

## Task 8: Verification — smoke test + template contract

**Files:**
- Test: throwaway repo (never this package)

- [x] **Step 1: Run the smoke test** — Run:

```bash
tmp=$(mktemp -d) && git -C "$tmp" init -q
python3 scripts/gen_topology.py "$tmp" --project-name Demo
python3 scripts/scaffold_docs.py "$tmp" --project-name Demo --force
find "$tmp/docs/guides" -name '*.md' | sort
```

Expected: exit 0; five files listed.

- [x] **Step 2: Assert section counts and new sections** — Run:

```bash
grep -c "^## [0-9]" "$tmp/docs/guides/user_guide.md"        # expect 23
grep -c "^## [0-9]" "$tmp/docs/guides/developer_guide.md"   # expect 19
grep -l "## 19. Glossary" "$tmp/docs/guides/user_guide.md"
grep -l "## 16. Test map" "$tmp/docs/guides/developer_guide.md"
grep -l "### 4.1 Entry-point map" "$tmp/docs/guides/developer_guide.md"
grep -l "Persona routing" "$tmp/docs/guides/README.md"
```

Expected: `23`, `19`, then four file paths printed.

- [x] **Step 3: Assert the placeholder contract** — Run:

```bash
grep -c "{{PROJECT_NAME}}" "$tmp/docs/guides/"*.md | grep -v ":0" ; true
```

Expected: no output (every count is 0).

- [x] **Step 4: Assert cross-file consistency** — Run:

```bash
grep -n "sections)" references/doc_outlines.md
grep -n "19-section schema\|23-section schema" SKILL.md
```

Expected: `developer_guide.md (19 sections)`, `user_guide.md (23 sections)`; both SKILL.md lines present.

- [x] **Step 5: Cleanup** — `rm -rf "$tmp"`

- [x] **Step 6: Report** — surface the four verification outcomes in the handover; list any deviation.
