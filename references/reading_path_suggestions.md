# Reading-Path Suggestions (Phase -1)

> **What this is.** The deterministic (audience × suitability-band) → entry-point mapping the agent uses to populate `assess.md` §3 ("Where to start reading") and §4 ("Reading suggestions").
> **Inputs:** primary audience (from [`audience_profiling.md`](./audience_profiling.md)), suitability score (from [`suitability_signals.md`](./suitability_signals.md), banded High/Mid/Low).
> **Outputs:** entry file, jump list (one or more `file#anchor` references), 1–3 concrete next-step actions.

## Suitability bands (re-stated for self-containment)

| Band | Score |
|---|---|
| **High** | 4.0 – 5.0 |
| **Mid** | 2.0 – 3.9 |
| **Low** | 0.0 – 1.9 |

When a hard veto from `suitability_signals.md` fires, the agent skips the matrix entirely and goes to the "Skip — and why" branch.

## The matrix

| Audience \\ Band | High | Mid | Low |
|---|---|---|---|
| `first-time-end-user` | `user_guide.md` §1–§11 + `tutorial.md` Ch. 1–4 | `user_guide.md` §1–§11 only | Skip |
| `applied-engineer` | `tutorial.md` (chapter matching the task) | Same, narrower: just the matching chapter + its exercises | Skip |
| `contributor` | `developer_guide.md` end-to-end + `topology.md` §1–§3 | `developer_guide.md` §1–§14 + `topology.md` §1–§3 | Skip |
| `auditor` | `topology.md` + `developer_guide.md` §15 | `topology.md` only | Skip |
| `learner` | `tutorial.md` Ch. 1 → 10 (sequential) | `tutorial.md` Ch. 1–4, then re-assess | Skip |
| `integrator` | `topology.md` + `developer_guide.md` §4–§5 | `topology.md` only | Skip |

The matrix is a plain Markdown table — there is no programmatic logic. The agent reads the row that matches (audience, band) and uses its entry.

## "Skip" branch

When the band is Low (no veto) the agent writes one short paragraph naming the weakest signal and pointing the user at one remediation (e.g. "open an issue requesting a `LICENSE`" or "consider running on a more active fork"). Do **not** recommend `--force`; if the user wants to mine anyway, they can run the scaffolder without `--audience` and ignore the assess.md.

## Next-step actions (§4 of `assess.md`)

After picking the entry file, the agent writes 1–3 imperative actions. Templates:

- For High: `Open \`<entry file>\`. If the suggested section lands a working example within 30 minutes, treat the doc set as a fit; otherwise re-run \`Phase -1\` with a different audience.`
- For Mid: `Skim \`<entry file>\`'s first 100 lines. If the first concrete API or class matches what you need, proceed; otherwise stop.`
- For Skip: `<remediation sentence>; re-run \`Phase -1\` afterwards.`

These are starting points, not fixed wording — adjust per audience when needed (e.g., add `git clone` for an integrator audience).
