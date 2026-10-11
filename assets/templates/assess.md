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

> Detection rubric: `references/audience_profiling.md`.

## 3. Where to start reading

**Entry file:** `{{ENTRY_FILE_RELATIVE}}`
**Jump list:** {{ENTRY_JUMP_LIST}}

> Matrix source: `references/reading_path_suggestions.md`.

## 4. Reading suggestions

1. {{READING_SUGGESTION_1}}
2. {{READING_SUGGESTION_2}}
3. {{READING_SUGGESTION_3}}

## 5. Verdict

{{VERDICT_PARAGRAPH}}

---

> TODO(doc-miner): remove any remaining `{{...}}` placeholders before publishing. The `{{PROJECT_NAME}}` slot is filled by the scaffolder; every other `{{...}}` slot above is for the Phase -1 agent to fill from this run's findings.
