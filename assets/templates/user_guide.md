# {{PROJECT_NAME}} 用户文档 / User Guide

> TODO(doc-miner): no remaining `{{...}}` placeholders before publishing. The `{{PROJECT_NAME}}` slot is filled by the scaffolder; every other `{{...}}` slot below is for the writing agent to fill from the Phase 2 evidence scratch note.

> For end users and applied engineers who want to solve real problems with {{PROJECT_NAME}}.

---

## 1. What {{PROJECT_NAME}} can do

- {{CAPABILITY_1}}
- {{CAPABILITY_2}}
- {{CAPABILITY_3}}

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

## 19. Minimal runnable templates

### 19.1 Forward problem

```python
{{FORWARD_EXAMPLE}}
```

### 19.2 Inverse problem

```python
{{INVERSE_EXAMPLE}}
```

## 20. Further reading

- Developer guide: [`developer_guide.md`](./developer_guide.md)
- Tutorial: [`tutorial.md`](./tutorial.md)
- Official docs: {{DOCS_URL_OR_TODO}}
