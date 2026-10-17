# {{PROJECT_NAME}} 从入门到精通 / From Beginner to Expert Tutorial

> TODO(doc-miner): no remaining `{{...}}` placeholders before publishing. The `{{PROJECT_NAME}}` slot is filled by the scaffolder; every other `{{...}}` slot below is for the writing agent to fill from the Phase 2 evidence scratch note.

> Ten chapters, progressively deeper. Every chapter is anchored in at least one real script under `examples/`.

## Table of contents

- Chapter 1 — Environment setup & Hello example
- Chapter 2 — Domain / input space basics
- Chapter 3 — Constraints: soft vs. hard
- Chapter 4 — Time-dependent problem
- Chapter 5 — Convergence techniques
- Chapter 6 — Inverse problems
- Chapter 7 — Complex geometry / high-dim / multiscale / fractional
- Chapter 8 — Operator learning
- Chapter 9 — Acceleration
- Chapter 10 — Mastery

---

## Chapter 1 · Environment setup & Hello example

Install:

```bash
{{INSTALL_SHORT}}
```

First runnable script (adapted from `{{HELLO_EXAMPLE_PATH}}`):

```python
{{HELLO_EXAMPLE_CODE}}
```

Run:

```bash
{{HELLO_RUN_COMMAND}}
```

Expected result: {{HELLO_EXPECTED}}.

**Exercise** — {{HELLO_EXERCISE}}.

---

## Chapter 2 · Domain / input space basics

{{CH2_NARRATIVE}}

Representative example: `{{CH2_EXAMPLE_PATH}}`.

**Exercise** — {{CH2_EXERCISE}}.

---

## Chapter 3 · Constraints: soft vs. hard

{{CH3_NARRATIVE}}

**Exercise** — {{CH3_EXERCISE}}.

---

## Chapter 4 · Time-dependent problem

Example: `{{CH4_EXAMPLE_PATH}}`.

```python
{{CH4_EXAMPLE_CODE}}
```

Workflow: {{CH4_WORKFLOW}}.

**Exercise** — {{CH4_EXERCISE}}.

---

## Chapter 5 · Convergence techniques

- Adaptive sampling: {{CH5_ADAPTIVE}}
- Two-stage optimizer pipeline (Adam → L-BFGS): {{CH5_PIPELINE}}
- Loss weighting: {{CH5_WEIGHTS}}
- Learning-rate decay: {{CH5_DECAY}}
- Early stopping: {{CH5_EARLY_STOP}}

**Exercise** — {{CH5_EXERCISE}}.

---

## Chapter 6 · Inverse problems

Example: `{{CH6_EXAMPLE_PATH}}`.

```python
{{CH6_EXAMPLE_CODE}}
```

The five ingredients of an inverse problem in {{PROJECT_NAME}}:
1. {{CH6_ITEM_1}}
2. {{CH6_ITEM_2}}
3. {{CH6_ITEM_3}}
4. {{CH6_ITEM_4}}
5. {{CH6_ITEM_5}}

**Exercise** — {{CH6_EXERCISE}}.

---

## Chapter 7 · Complex geometry / high-dim / multiscale / fractional

{{CH7_NARRATIVE}}

Pointers into `examples/`:
- {{CH7_POINTER_1}}
- {{CH7_POINTER_2}}

**Exercise** — {{CH7_EXERCISE}}.

---

## Chapter 8 · Operator learning

### 8.1 Data-driven

Example: `{{CH8_DATA_EXAMPLE_PATH}}`.

```python
{{CH8_DATA_CODE}}
```

### 8.2 Physics-informed

Example: `{{CH8_PI_EXAMPLE_PATH}}`.

```python
{{CH8_PI_CODE}}
```

**Exercise** — {{CH8_EXERCISE}}.

---

## Chapter 9 · Acceleration

- Mixed precision: {{CH9_MIXED}}
- Forward-mode AD: {{CH9_FWD}}
- Caching / shift tricks: {{CH9_ZCS}}
- Multi-GPU: {{CH9_MULTI_GPU}}

**Exercise** — {{CH9_EXERCISE}}.

---

## Chapter 10 · Mastery

Pick any of the following extension points and implement a small patch:

1. Custom callback — {{CH10_CUSTOM_CB}}
2. Custom network — {{CH10_CUSTOM_NET}}
3. Custom BC / constraint — {{CH10_CUSTOM_BC}}
4. Custom loss / metric — {{CH10_CUSTOM_LOSS}}
5. Custom backend (advanced) — {{CH10_CUSTOM_BACKEND}}

**Exercise** — {{CH10_EXERCISE}}.

---

## After this tutorial

- Deep source reading: [`developer_guide.md`](./developer_guide.md).
- API lookup: [`user_guide.md`](./user_guide.md).
- Official docs: {{DOCS_URL_OR_TODO}}.
