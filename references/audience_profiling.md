# Audience Profiling (Phase -1)

> **What this is.** The taxonomy of reader personas and the on-disk signals the agent uses during `Phase -1 · Pre-Mining Assessment` to decide *who this doc set is for*.
> **Companion docs:** [`suitability_signals.md`](./suitability_signals.md) decides whether to mine; [`reading_path_suggestions.md`](./reading_path_suggestions.md) maps the chosen audience to an entry file.

## The six-bucket taxonomy

| Bucket | One-line definition | Best entry file |
|---|---|---|
| **first-time-end-user** | Has the repo installed (or about to) and wants to do a specific thing | `user_guide.md` §1–§11 + §18–§19 |
| **applied-engineer** | Knows the domain; needs the *recipe* matching their task | `tutorial.md` (matching chapter) |
| **contributor** | Wants to read source, extend the framework, or submit a PR | `developer_guide.md` (end-to-end) |
| **auditor** | Reviewing for security, licensing, code-quality, supply-chain risk | `topology.md` §1–§3 + `developer_guide.md` §15 |
| **learner** | No specific use case yet; wants a guided curriculum | `tutorial.md` Ch. 1 → 10 |
| **integrator** | Plugging the repo into another system (CI, IDE, automation) | `topology.md` + `developer_guide.md` §4–§5 |

The agent picks **at most two** buckets per target repo (a dominant + a secondary). Picking zero is allowed only when no signal matches; in that case the scaffolder must be invoked with no `--audience` flag.

> Detection rubric: see `assets/templates/_audience_block.md` and the `--audience` flag on `scripts/scaffold_docs.py`. When invoked, the audience block is prefixed onto the four non-hub generated docs (`topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`); `README.md` is the hub and is **not** prefixed.

## Detection signals (on-disk, stdlib only)

The agent inspects the target repo and records one or more of:

| Signal | Where to look | Suggests |
|---|---|---|
| `README.md` first paragraph contains "API", "library", "import", "use X to …" | top of `README.md` | `first-time-end-user` |
| `README.md` first paragraph contains "tutorial", "course", "from beginner" | top of `README.md` | `learner` |
| Presence of `CONTRIBUTING.md`, `.github/CODEOWNERS`, `docs/development/`, or `docs/dev/` | repo root + `.github/` | `contributor` |
| `README.md` mentions "security", "audit", "compliance", "vulnerability" OR `SECURITY.md` exists | `README.md` + repo root | `auditor` |
| Presence of `examples/` with **≥ 5 runnable scripts** OR no top-level source code (only configs + examples) | `examples/` | `applied-engineer` |
| `pyproject.toml` `[project.scripts]` entry OR `package.json` `bin` field, OR explicit "CLI" / "command-line" wording | manifests | `integrator` |
| `pyproject.toml` `[project] classifiers` includes "Framework :: Django" / ":: Flask" / similar web framework | manifest | `integrator` (secondary) |

When signals disagree (e.g., `CONTRIBUTING.md` is present but the README also screams "API library"), the agent records both buckets and labels the secondary as "secondary" in the output. Do **not** silently overwrite.

## What this taxonomy deliberately does not include

- **Roles by seniority** (junior / senior / staff). The buckets above are use-case-agnostic so the same doc set serves any career stage.
- **Roles by company type** (startup / enterprise / academic). Use-case captures intent better than org type.
- **A "general" / "all" bucket.** No signal maps to "general"; if no signal matches, the agent picks nothing and the audience block is omitted.

## Output format in `assess.md`

The agent writes a 2-line summary at `assess.md` §2:

```
**Primary audience:** the chosen bucket — one-sentence rationale citing the signal
**Secondary audience (if any):** the chosen bucket — one-sentence rationale
```
