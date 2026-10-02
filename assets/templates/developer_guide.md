# {{PROJECT_NAME}} 开发者文档 / Developer Guide

> Baseline: `{{GIT_BRANCH_OR_COMMIT}}`. For contributors who need to read source, extend the framework, or submit upstream PRs.

---

## 1. Project positioning & scope

{{ONE_PARAGRAPH_POSITIONING}}

Headline capabilities:
- {{HEADLINE_CAPABILITY_1}}
- {{HEADLINE_CAPABILITY_2}}
- {{HEADLINE_CAPABILITY_3}}

## 2. Metadata snapshot

- Package name: `{{PKG_NAME}}`
- License: `{{LICENSE}}`
- Language runtime: `{{LANG_VERSION_CONSTRAINT}}`
- Core dependencies: {{DEPS_LIST}}
- Version source: `{{VERSION_SOURCE_FILE}}`

## 3. Repository layout

```
{{REPO_TREE_ANNOTATED}}
```

## 4. Runtime architecture overview

```
{{ASCII_ARCHITECTURE_DIAGRAM}}
```

Narrative: {{ARCHITECTURE_NARRATIVE}}

## 5. Top-level namespace

| Alias | Real module |
| --- | --- |
| `{{ALIAS_1}}` | `{{REAL_MODULE_1}}` |
| `{{ALIAS_2}}` | `{{REAL_MODULE_2}}` |
| ... | ... |

Source: `{{TOP_INIT_PATH}}`.

## 6. Backend / platform abstraction

> Skip this section if the project has no multi-backend indirection.

- Unified interface file: `{{BACKEND_INTERFACE_PATH}}`.
- Selection priority:
  1. {{BACKEND_PRIORITY_1}}
  2. {{BACKEND_PRIORITY_2}}
  3. {{BACKEND_PRIORITY_3}}
- Enabled-API registry mechanism: {{ENABLED_API_MECHANISM}}.

## 7. Data & domain layer

{{DATA_LAYER_NARRATIVE}}

Full `__all__` of `{{DATA_PKG_PATH}}`:

```text
{{DATA_ALL_LIST}}
```

## 8. Automatic differentiation / computation core

{{AD_NARRATIVE}}

Public API: `{{AD_PUBLIC_API_PATHS}}`.

## 9. Networks / models catalog

| Class | Path | Constructor signature |
| --- | --- | --- |
| `{{NET_1}}` | `{{NET_1_PATH}}` | `{{NET_1_SIG}}` |
| `{{NET_2}}` | `{{NET_2_PATH}}` | `{{NET_2_SIG}}` |
| ... | ... | ... |

## 10. Optimizers & schedulers

- Available optimizer names: {{OPT_NAMES}}.
- LR-decay matrix per backend:

| Backend | Supported decays |
| --- | --- |
| `{{BACKEND_1}}` | {{DECAYS_1}} |
| `{{BACKEND_2}}` | {{DECAYS_2}} |

## 11. Training main loop

Step-by-step narrative of `{{MODEL_PATH}}::{{MODEL_CLASS}}`:

1. `__init__` — {{TRAIN_INIT_NARRATIVE}}
2. `compile` — {{TRAIN_COMPILE_NARRATIVE}}
3. `train` — {{TRAIN_NARRATIVE}}
4. `predict` — {{PREDICT_NARRATIVE}}
5. `save` / `restore` — {{PERSIST_NARRATIVE}}

## 12. Callback / hook system

Base class lifecycle: {{CALLBACK_LIFECYCLE}}.

| Built-in callback | Trigger | Use case |
| --- | --- | --- |
| `{{CB_1}}` | `{{CB_1_TRIGGER}}` | {{CB_1_USE}} |
| `{{CB_2}}` | `{{CB_2_TRIGGER}}` | {{CB_2_USE}} |

## 13. Loss & metric registries

- Loss registry file: `{{LOSS_PATH}}`. Identifiers: {{LOSS_IDS}}.
- Metric registry file: `{{METRICS_PATH}}`. Identifiers: {{METRIC_IDS}}.

## 14. Parallel / distributed training

{{PARALLEL_NARRATIVE}}

## 15. Contribution SOPs & debugging

### 15.1 Dev environment

```bash
{{DEV_SETUP_COMMANDS}}
```

### 15.2 Adding a new {{EXT_UNIT}} (template)

1. {{EXT_STEP_1}}
2. {{EXT_STEP_2}}
3. {{EXT_STEP_3}}

### 15.3 Common error → root cause

| Symptom | Check |
| --- | --- |
| `{{ERR_1}}` | {{ERR_1_FIX}} |
| `{{ERR_2}}` | {{ERR_2_FIX}} |

---

## References

- Main paper / canonical citation: {{CITATION_OR_TODO}}
- Online docs: {{DOCS_URL_OR_TODO}}

> TODO(doc-miner): remove any remaining `{{...}}` placeholders before publishing.
