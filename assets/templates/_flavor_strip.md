# Flavor-Strip Marker (`_flavor_strip.md`)

> **This file is a no-op marker.** It exists so that:
>
> 1. The scaffolder can recognise it as a flavours-aware template bundle (any `--flavor <X>` flag strips sections of the other 5 templates tagged with `<!-- flavor: <X> -->` markers; this marker file itself is always passed through verbatim).
> 2. Future template maintainers have a documented extension point for adding flavour-specific sections to the 5 core templates.
>
> **Do not** delete this file without first removing the `--flavor` arg from `scripts/scaffold_docs.py` argparse and any references in `SKILL.md` and `references/doc_outlines.md`.

## How to add a new flavour section

In any of the 5 core templates (`topology.md`, `developer_guide.md`, `user_guide.md`, `tutorial.md`, `README.md`), wrap the flavour-specific prose in a `<!-- flavor: <FLAVOR_NAME> -->` ... `<!-- /flavor: <FLAVOR_NAME> -->` pair:

```markdown
<!-- flavor: pinn -->
PINN-specific prose here. Stripped when `--flavor pinn` is NOT set.
<!-- /flavor: pinn -->
```

The scaffolder will:
- **Keep** the block when the user passes `--flavor pinn`.
- **Strip** the block (both the open and close markers, plus the wrapped content) for any other flavour.

The `<!-- /flavor: pinn -->` close marker is required; without it the stripper cannot know where the flavour block ends.

## Reserved flavour names

| Name | Reserved for |
|---|---|
| `general` | Default; no stripping. Equivalent to "all flavours off". |
| `pinn` | Physics-Informed Neural Networks (DeepXDE-shaped libraries). The 5 core templates currently carry no PINN-specific sections, so this is a future placeholder. |
| `cli` | Command-line tools (Click / Typer / argparse-shaped). Future. |
| `lib` | Plain libraries (no CLI, no web service). Future. |
| `monorepo` | Monorepos with multiple language packages. Future. |

## When this file changes

If you add a new flavour to the reserved table above, also:
- Add the new `<!-- flavor: <FLAVOR_NAME> -->` blocks to the relevant templates.
- Add a row to `references/doc_outlines.md` documenting the new flavour.
- Update the scaffolder's argparse `--flavor` choices.
