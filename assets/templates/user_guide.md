# {{PROJECT_NAME}} 用户文档 / User Guide

> For end users and applied engineers who want to solve real problems with {{PROJECT_NAME}}.

---

## 1. What {{PROJECT_NAME}} can do

- {{CAPABILITY_1}}
- {{CAPABILITY_2}}
- {{CAPABILITY_3}}

In one sentence: {{ONE_SENTENCE_PITCH}}.

**What it does NOT do (non-goals):**

- {{NON_GOAL_1}}
- {{NON_GOAL_2}}

## 2. Installation

{{INSTALL_MATRIX}}

```bash
{{INSTALL_COMMANDS}}
```

## 3. Choosing a backend / runtime

> Delete this section if the project has no multi-backend support.

{{BACKEND_CHOICE_TABLE}}

## 4. Global configuration

```python
{{CONFIG_SNIPPET}}
```

Key knobs:
- `{{CONFIG_KEY_1}}` — {{CONFIG_KEY_1_DESC}}
- `{{CONFIG_KEY_2}}` — {{CONFIG_KEY_2_DESC}}

> List every user-facing knob here — exhaustive, not a sample (harvest from the config module).

## 5. Core-object map

```
{{CORE_OBJECT_DIAGRAM}}
```

## 6. Geometry / domain definition

{{GEOMETRY_SECTION}}

## 7. Boundary / initial conditions

```python
{{ICBC_SIGNATURES}}
```

## 8. Data objects

| Class | When to use |
| --- | --- |
| `{{DATA_1}}` | {{DATA_1_USE}} |
| `{{DATA_2}}` | {{DATA_2_USE}} |

## 9. PDE residual / constraint authoring

```python
{{AD_SNIPPET}}
```

## 10. Networks

```python
{{NET_SNIPPET}}
```

Built-ins: {{NET_CATALOG}}.

## 11. Training

```python
{{TRAIN_SNIPPET}}
```

Key options: `{{OPT_OPTIONS}}`.

## 12. Inverse problems

{{INVERSE_NARRATIVE}}

```python
{{INVERSE_SNIPPET}}
```

## 13. Operator learning

{{OPERATOR_NARRATIVE}}

## 14. Uncertainty quantification & multifidelity

{{UQ_NARRATIVE}}

## 15. Persistence

```python
{{PERSIST_SNIPPET}}
```

## 16. Visualization & post-processing

```python
{{VIZ_SNIPPET}}
```

## 17. Parallel training

{{PARALLEL_SECTION}}

## 18. Troubleshooting

| Symptom | Suggestion |
| --- | --- |
| `{{FAQ_SYMPTOM_1}}` | {{FAQ_FIX_1}} |
| `{{FAQ_SYMPTOM_2}}` | {{FAQ_FIX_2}} |

### 18.1 Error triage / 报错急救

Deeper than the quick FAQ above: what the error actually means, in plain language, and the exact fix.

| Error message | What it actually means | Fix |
| --- | --- | --- |
| `{{FAQ_SYMPTOM_3}}` | {{FAQ_PLAIN_3}} | {{FAQ_FIX_3}} |
| `{{FAQ_SYMPTOM_4}}` | {{FAQ_PLAIN_4}} | {{FAQ_FIX_4}} |

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

## 22. Minimal runnable templates

### 22.1 Forward problem

```python
{{FORWARD_EXAMPLE}}
```

### 22.2 Inverse problem

```python
{{INVERSE_EXAMPLE}}
```

## 23. Further reading

- Developer guide: [`developer_guide.md`](./developer_guide.md)
- Tutorial: [`tutorial.md`](./tutorial.md)
- Official docs: {{DOCS_URL_OR_TODO}}
- Support channels: see §20 (Getting help).

> TODO(doc-miner): remove any remaining `{{...}}` placeholders before publishing.
