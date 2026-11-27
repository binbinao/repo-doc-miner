# Suitability Signals (Phase -1)

> **What this is.** A rubric the agent applies during `Phase -1 · Pre-Mining Assessment` to decide whether the target repository is worth generating a five-file doc set for. Score 0–5; hard vetoes force "skip — and why".
> **Where it lives in the workflow.** Loaded during Phase -1, alongside `audience_profiling.md` and `reading_path_suggestions.md`.

## Scoring rubric (six signals, 0–2 each → rescaled to 0–5)

| Signal | Source | 0 | 1 | 2 |
|---|---|---|---|---|
| **Size** | file count in repo (excluding `.git`, vendor) | < 5 | 5–500 | > 500 |
| **Vitality** | `git log -1 --format=%ct` (Unix timestamp) | > 2 years ago | 6 mo – 2 yrs | < 6 mo |
| **License** | presence + SPDX-recognised | absent | permissive copyleft only | clear permissive (MIT/Apache/BSD) |
| **Entry-point clarity** | `README.md` first paragraph + a recognisable manifest (`pyproject.toml` / `package.json` / `Cargo.toml` / `go.mod` / `pom.xml`) | neither | one | both |
| **Documentation quality** | existing `docs/` directory size + completeness | none | partial | substantial (≥ 5 Markdown files) |
| **Test/example presence** | `tests/` or `examples/` directory | neither | one | both |

**Score formula:** raw = sum of the six 0/1/2 columns (range 0–12); rescaled = `round(raw * 5 / 12, 1)` (maps 0–12 → 0–5). Bands: `4.0–5.0` = High (raw ≥ 10), `2.0–3.9` = Mid (raw 5–9), `0.0–1.9` = Low (raw 0–4).

## Hard vetoes (force score → 0 + emit skip reason)

A repo is **skipped without scoring** when any of the following holds:

1. **Archived** — best-effort detection: presence of `ARCHIVED.md`, or a README banner stating the project is archived/no longer maintained (e.g. `[![No Maintenance Intended](...)](...)`, or the strings `no longer maintained`, `archived`, or `sunset`).
2. **No license + no usage hint** — `LICENSE` (or `LICENSE.md`) is absent AND the README's first 200 lines contain none of: `Install`, `Usage`, `Quickstart`, `pip install`, `npm install`, `cargo install`, `go install`, `go get`, or a fenced `bash` block.
3. **Vendor fork** — no top-level source directory exists (only `node_modules/`, `dist/`, `vendor/`, `third_party/`, `*.egg-info/`).
4. **Too small** — fewer than 3 readable source files remain after applying the script's `IGNORE_DIRS` / `.gitignore` filtering.

When a veto fires, write a `> TODO(doc-miner): skip — …` marker naming the veto reason to `assess.md` §1 and stop.

**Not-a-git fallback.** If `git log -1 --format=%ct` fails (target is not a Git repo, or has no commits), score Vitality = 0 and record the reason in `assess.md` §1. The other five signals are computed from the on-disk tree and remain valid.

## "Skip — and why" message template

When the agent decides to skip, emit one short paragraph that names the veto and points the user at a remediation (open an issue, request a license, etc.). Do not just say "skip".

## What this rubric deliberately does not do

- It does **not** score code quality (no Lint/Test-Coverage/Type-Check signal). Those are runtime concerns; the skill's deliverable is documentation, and a low-quality repo still benefits from a clear map.
- It does **not** judge *whether the user can read the language*. That is captured by the audience profile, not the suitability score.
- It does **not** query GitHub / GitLab APIs. Detection is stdlib + `git log` only; out-of-band facts (stars, archived flag) are inferred from on-disk signals when possible and otherwise skipped silently.
