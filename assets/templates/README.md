# {{PROJECT_NAME}} 指南中心 / Guide Hub

> TODO(doc-miner): no remaining `{{...}}` placeholders before publishing. The `{{PROJECT_NAME}}` slot is filled by the scaffolder; every other `{{...}}` slot below is for the writing agent to fill from the Phase 2 evidence scratch note.

This folder contains **up to six** coordinated files derived from mining the {{PROJECT_NAME}} source tree using the topology-first workflow (five documents plus this hub). When the scaffolder was invoked with `--assess`, an additional `assess.md` is present — the Phase -1 pre-mining assessment (suitability score, audience, reading path, verdict) produced **before** any of the documents below. Start with `assess.md` if it is present; otherwise jump straight to the file that matches your role in the table below.

| File | Audience | Contents |
| --- | --- | --- |
| [`assess.md`](./assess.md) *(only when `--assess` was used)* | Everyone (read first if present) | Phase -1 pre-mining assessment: suitability score + evidence, audience profile, reading path, verdict. |
| [`topology.md`](./topology.md) | Everyone (start here) | Structural map (Mermaid) + entity inventory + dependency edges. The backbone for the other docs. |
| [`developer_guide.md`](./developer_guide.md) | Framework developers / contributors | Architecture, module tours, extension SOPs, debugging tips. |
| [`user_guide.md`](./user_guide.md) | End users / applied engineers | Installation, core API, typical workflows, FAQ. |
| [`tutorial.md`](./tutorial.md) | Learners at any level | 10-chapter "from beginner to expert" walkthrough grounded in `examples/`. |

> Upstream project: {{PROJECT_HOMEPAGE_OR_TODO}}
> Official docs: {{DOCS_URL_OR_TODO}}

## How these documents were produced

- Based on direct reading of `{{SOURCE_PACKAGE_PATH}}/`, `examples/`, and existing `docs/` material.
- Every claim is grounded in a concrete source path; unresolved facts are marked with `> TODO(doc-miner): ...`.

## Persona routing / 你是谁,从哪开始

| You are… | Start with |
| --- | --- |
| Completely new to this project | `user_guide.md` §1 (pitch + non-goals) → §2 (install) → §19 (glossary) → §22 (minimal example) |
| Deciding whether to adopt / depend on this repo | `developer_guide.md` §2 (metadata) + §16–§19 (tests, releases, dependencies, quality), then `topology.md` |
| Extending or contributing | `developer_guide.md` end to end, cross-reference `topology.md` |
| Just want the big picture | `topology.md` |

> Not sure which one you are? Read `user_guide.md` §1 — its one-sentence pitch will tell you quickly.

## Reading order suggestions

Read `assess.md` first, then pick the audience bucket that matches you (entry files follow the Phase -1 reading-path matrix, High band):

first-time-end-user: `user_guide.md` §1–§11 + §18–§19, then `tutorial.md` Ch. 1–4.

applied-engineer: `tutorial.md` — the chapter matching your task.

contributor: `developer_guide.md` end to end + `topology.md` §1–§3; cross-reference `user_guide.md` when a user-facing API is discussed.

auditor: `topology.md` + `developer_guide.md` §15.

learner: `tutorial.md` Ch. 1 → 10, in order.

integrator: `topology.md` + `developer_guide.md` §4–§5.
