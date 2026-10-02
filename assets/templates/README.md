# {{PROJECT_NAME}} 指南中心 / Guide Hub

This folder contains five coordinated files derived from mining the {{PROJECT_NAME}} source tree using the topology-first workflow (four documents plus this hub):

| File | Audience | Contents |
| --- | --- | --- |
| [`topology.md`](./topology.md) | Everyone (start here) | Structural map (Mermaid) + entity inventory + dependency edges. The backbone for the other docs. |
| [`developer_guide.md`](./developer_guide.md) | Framework developers / contributors | Architecture, module tours, extension SOPs, debugging tips. |
| [`user_guide.md`](./user_guide.md) | End users / applied engineers | Installation, core API, typical workflows, FAQ. |
| [`tutorial.md`](./tutorial.md) | Learners at any level | 10-chapter "from beginner to expert" walkthrough grounded in `examples/`. |

> Upstream project: {{PROJECT_HOMEPAGE_OR_TODO}}
> Official docs: {{DOCS_URL_OR_TODO}}

## How these documents were produced

- Based on direct reading of `{{SOURCE_PACKAGE_PATH}}/`, `examples/`, and existing `docs/` material.
- Every claim is grounded in a concrete source path; unresolved facts are marked with `> TODO(doc-miner): ...`.

## Reading order suggestions

1. **New users** — start with `user_guide.md` §1–§11, then do chapters 1–4 of `tutorial.md`.
2. **Applied engineers** with a specific task — jump to the matching chapter of `tutorial.md`.
3. **Contributors** — read `developer_guide.md` end to end; cross-reference `user_guide.md` when a user-facing API is discussed.
