# Edge Refinement (Phase 1)

> **What this is.** A practitioner's guide to verifying and refining the dependency edges emitted by `gen_topology.py`. Auto-detection is heuristic; this file is the manual that converts "looks right" into "verified right".
> **When to use it.** After Phase 1 produces a draft `topology.md` and before you start Phase 2. Skim once; deep-dive when an edge looks wrong.

## Why refinement is non-optional

`gen_topology.py` reads at most `MAX_FILE_READ = 200_000` bytes per file and never follows real imports. It captures two edge kinds:

- **`source → copy`** — a single source of truth synced into copies. Drawn dotted when the reference's own line carries one of `system.file`, `from_plugin`, `skills.path`, `skills:`, `copied`, `synced`.
- **`uses`** — one entity consumes another. Drawn solid otherwise.

Both are heuristic. Phase 1 ships the draft; you ship the truth. The rest of this doc tells you which edges matter, how to verify them, and what to ignore.

## Which edges to verify first

Not all edges are equal. Spend your refinement budget on these, in order:

1. **Edges that affect the `source → copy` count.** A misclassified `source → copy` will make Phase 2 read the same content multiple times and miss the single source. If the count looks too high, the most common cause is a false positive: a file that mentions `system.file:` in a comment but is not actually a synced copy.
2. **Edges that change the inventory count.** If a file the script counts as a single entity is actually two (a Python module + its test under the same `__init__.py`-style aggregation), split it; if two are actually one (a documented interface + its auto-generated stub), merge it.
3. **Edges from manifests to the entity they declare.** `pyproject.toml` → `mypkg`, `package.json` → `app`, etc. — verify the manifest actually lists the package and the path is reachable. The script's `by_path` lookup is exact; any mismatch means the script can't see the relationship even if it exists.

## How to verify an edge

For each edge, do this:

1. Open the source file (the file the script emitted the edge from). Find the line containing the keyword (`system.file:`, `from_plugin`, `skills.path`, `skills:`, etc.) or the path token.
2. Confirm the line is *meant* to declare a dependency, not a string literal in a code example. A common false positive is a documentation example that uses `system.file: foo.md` to teach the syntax.
3. If the dependency is real, confirm the target path resolves. `git log -- path/to/target` confirms the file exists and was committed.
4. Re-emit the edge in your refined `topology.md` (edit the Mermaid block) so a re-run of `gen_topology.py` will diff against your hand-curated map.

## Common false positives

- **Comments / docs mentioning the keyword.** A README that says "use the `system.file:` directive" will be picked up as a `source → copy`. Check whether the line is in a code fence or a prose paragraph.
- **Test fixtures.** A test under `tests/fixtures/sample-system-file.md` may legitimately be a copy; decide whether to keep it.
- **Vendored content.** Anything under a directory in the script's `IGNORE_DIRS` set (e.g. `node_modules/`, `dist/`, `build/`, `target/`) or inside a `*.egg-info/` directory is ignored; if you see a vendored entity in the inventory, `IGNORE_DIRS` may be too permissive for your repo.

## Common false negatives

- **Imports the script doesn't know about.** Python `from . import sibling` (relative imports with no leading module) is hard to resolve from a single file. Phase 2 humans must add these manually.
- **Generated artifacts.** If `dist/foo.js` is built from `src/foo.ts`, the script sees `dist/foo.js` as a top-level entity but won't draw an edge from `src/foo.ts`. Add the edge by hand.
- **Edges to files the script skipped.** Files filtered out by the script's hardcoded `IGNORE_DIRS` list (plus any `*.egg-info/` directory) never enter the inventory; their upstream source may still be. The script does not read `.gitignore` and never shells out to git, so a file ignored only by `.gitignore` and sitting outside those directories *is* inventoried. Add the upstream-to-skipped edge manually.

## What this guide deliberately does not do

- It does not propose a different edge taxonomy. The script emits two kinds; that's deliberate, and the taxonomy is documented in `references/topology_method.md`.
- It does not automate verification. The script's heuristic is fast; a human-in-the-loop check is slower but catches what regex can't.
- It does not propose a fix for `gen_topology.py`. Phase 3 (Generalization & Polish) is where script-level improvements land; this file is the bridge between "script says X" and "user believes X".
