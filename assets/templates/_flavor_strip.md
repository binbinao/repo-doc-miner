# Flavor-Strip Marker (`_flavor_strip.md`)

> **This file is a no-op marker.** The current scaffolder does not read it; it exists to document the extension point for a future `--flavor FLAVOR_NAME` flag.
>
> When that flag lands, the scaffolder will:
>
> 1. Keep blocks in the 5 core templates (`topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`, `README.md`) that are tagged with the selected flavor's `<!-- flavor: FLAVOR_NAME -->` marker.
> 2. Strip every other `<!-- flavor: ... -->` block (both the open and close markers, plus the wrapped content).
> 3. With `--flavor general`, strip every flavor-tagged block (no flavor-specific prose is kept).
>
> Until that flag lands, this file is documentation only. The current scaffolder iterates only `TEMPLATE_FILES` and never reads `_flavor_strip.md`.

## Reserved flavor names

| Name | Reserved for |
|---|---|
| `general` | Default. With `--flavor general`, every flavor-tagged block is stripped. |
| `pinn` | Physics-Informed Neural Networks (DeepXDE-shaped libraries). Future. |
| `cli` | Command-line tools (Click / Typer / argparse-shaped). Future. |
| `lib` | Plain libraries (no CLI, no web service). Future. |
| `monorepo` | Monorepos with multiple language packages. Future. |

## How to add a new flavor section (future)

In any of the 5 core templates, wrap the flavor-specific prose in a `<!-- flavor: FLAVOR_NAME -->` ... `<!-- /flavor: FLAVOR_NAME -->` pair:

```markdown
<!-- flavor: pinn -->
PINN-specific prose here. Kept only when `--flavor pinn` is set.
<!-- /flavor: pinn -->
```

The `<!-- /flavor: FLAVOR_NAME -->` close marker is required; without it the stripper cannot determine where the flavor block ends.

## When this file changes

If you add a new flavor to the reserved table above, also:
- Add the new `<!-- flavor: FLAVOR_NAME -->` blocks to the relevant templates.
- Add a row to `references/doc_outlines.md` documenting the new flavor.
- Update `scripts/scaffold_docs.py` argparse to add the new `--flavor` choice.
- Update SKILL.md to mention the new flag (currently no mention; the scaffolder signature is `--assess` / `--audience` only).
