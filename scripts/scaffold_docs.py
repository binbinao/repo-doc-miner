#!/usr/bin/env python3
"""Scaffold the five-file doc set for the repo-doc-miner skill.

Creates <repo-root>/<out>/ and materializes the five Markdown templates
(topology, README, developer_guide, user_guide, tutorial) from the
skill's assets/templates/ directory, with a single {{PROJECT_NAME}}
placeholder substituted. All other {{...}} placeholders are intentionally
left in place so the CodeBuddy agent can fill them during Phase 4 of the
workflow described in SKILL.md.

When --assess is passed, additionally materializes the Phase -1
``assess.md`` template into the output directory. ``assess.md`` is the
pre-mining assessment deliverable (see references/suitability_signals.md,
references/audience_profiling.md, references/reading_path_suggestions.md).

When --audience is passed, prepends the ``_audience_block.md`` fragment
(with ``{{AUDIENCE}}`` and ``{{PROJECT_NAME}}`` substituted) to the four
non-hub generated docs (topology, developer_guide, user_guide, tutorial)
and, when --assess is also set, to ``assess.md``. ``README.md`` is the hub
and is never prefixed.

Existing template files in the output directory are left untouched unless
--force is supplied, so a Phase-1 topology.md is never clobbered.

Usage
-----
    python scripts/scaffold_docs.py <repo-root> \
        --project-name "MyProject" \
        [--out docs/guides] \
        [--force] \
        [--assess] \
        [--audience NAME] \
        [--flavor FLAVOR_NAME]

Exit codes
----------
    0  success (files written and/or skipped)
    1  repo root does not exist, or the templates directory is missing
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEMPLATE_FILES = (
    "topology.md",
    "README.md",
    "developer_guide.md",
    "user_guide.md",
    "tutorial.md",
)

# The doc set is one hub (README.md, which already carries the audience
# table) plus four spokes. The Phase -1 audience block is prepended to the
# spokes only; the hub stays unprefixed so a re-run sees the same block.
HUB_FILE = "README.md"

# `<!-- flavor: NAME --> ... <!-- /flavor: NAME -->` blocks. The
# backreference ensures a close marker must repeat its open marker's name,
# so a mismatched pair is left in place rather than swallowing content.
_FLAVOR_BLOCK_RE = re.compile(
    r"<!--\s*flavor:\s*([a-z][a-z0-9_-]*)\s*-->(?P<body>.*?)"
    r"<!--\s*/flavor:\s*\1\s*-->",
    re.DOTALL,
)


def _strip_flavors(text: str, keep: str) -> str:
    """Remove flavor-tagged blocks from ``text``.

    Every ``<!-- flavor: NAME --> ... <!-- /flavor: NAME -->`` block is
    removed except those whose NAME equals ``keep``. The default flavor
    ``general`` is special: it keeps no flavor-specific prose, so every
    block is stripped.
    """
    if keep == "general":
        return _FLAVOR_BLOCK_RE.sub("", text)

    def _repl(match: re.Match) -> str:
        name = match.group(1)
        return match.group("body") if name == keep else ""

    return _FLAVOR_BLOCK_RE.sub(_repl, text)


def locate_templates_dir() -> Path:
    """Resolve the templates directory relative to this script's location."""
    here = Path(__file__).resolve().parent
    candidate = here.parent / "assets" / "templates"
    if candidate.is_dir():
        return candidate
    raise FileNotFoundError(
        f"Could not find templates directory at {candidate}. "
        "The skill package appears to be corrupt."
    )


def materialize(
    templates_dir: Path,
    out_dir: Path,
    project_name: str,
    force: bool,
    write_assess: bool = False,
    audience_prefix: str | None = None,
    keep_flavor: str = "general",
) -> tuple[list[str], list[str]]:
    """Write the missing templates; return (written, skipped) file names.

    When ``write_assess`` is True, also materialize ``assess.md`` (the
    Phase -1 deliverable). ``assess.md`` is independent of the
    ``TEMPLATE_FILES`` list -- it only appears when the user opts in via
    ``--assess``, keeping the default behaviour unchanged.

    When ``audience_prefix`` is given, it is prepended verbatim to the four
    non-hub generated docs and to ``assess.md``; ``README.md`` (the hub) is
    never prefixed.

    ``keep_flavor`` selects which ``<!-- flavor: NAME -->`` blocks survive
    in the written files. The default ``general`` strips every flavor block
    (no flavor-specific prose is kept); any other name keeps only blocks
    tagged with that name. ``{{PROJECT_NAME}}`` substitution and the
    audience prefix are applied first, so the strip sees final text.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    skipped: list[str] = []
    for name in TEMPLATE_FILES:
        src = templates_dir / name
        dst = out_dir / name
        if dst.exists() and not force:
            skipped.append(name)
            print(f"  skipped (exists): {dst}")
            continue
        text = src.read_text(encoding="utf-8")
        # Substitute only the project-name placeholder; all other
        # {{...}} placeholders are intentionally preserved so the
        # agent can fill them with evidence from Phase 2 of the
        # skill workflow.
        text = text.replace("{{PROJECT_NAME}}", project_name)
        if audience_prefix and name != HUB_FILE:
            text = audience_prefix + text
        text = _strip_flavors(text, keep_flavor)
        dst.write_text(text, encoding="utf-8")
        written.append(name)
        print(f"  wrote {dst}")

    if write_assess:
        assess_src = templates_dir / "assess.md"
        assess_dst = out_dir / "assess.md"
        if not assess_src.is_file():
            print(f"  error: --assess requested but {assess_src} is missing",
                  file=sys.stderr)
            return written, skipped
        if assess_dst.exists() and not force:
            skipped.append("assess.md")
            print(f"  skipped (exists): {assess_dst}")
        else:
            text = assess_src.read_text(encoding="utf-8").replace(
                "{{PROJECT_NAME}}", project_name
            )
            if audience_prefix:
                text = audience_prefix + text
            text = _strip_flavors(text, keep_flavor)
            assess_dst.write_text(text, encoding="utf-8")
            written.append("assess.md")
            print(f"  wrote {assess_dst}")

    return written, skipped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold the repo-doc-miner five-file doc set."
    )
    parser.add_argument(
        "repo_root",
        type=Path,
        help="Absolute or relative path to the target repository's root.",
    )
    parser.add_argument(
        "--project-name",
        required=True,
        help="Display name of the project (used to replace {{PROJECT_NAME}}).",
    )
    parser.add_argument(
        "--out",
        default="docs/guides",
        help="Output sub-directory under repo-root (default: docs/guides).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing template files in the output directory (default: skip them).",
    )
    parser.add_argument(
        "--assess",
        action="store_true",
        help="Additionally materialize the Phase -1 assess.md template. Default: off.",
    )
    parser.add_argument(
        "--audience",
        default=None,
        metavar="NAME",
        help=("Prefix each generated doc with the audience block "
              "(_audience_block.md), substituting {{AUDIENCE}}. NAME is "
              "free-form (e.g. 'contributor', 'first-time-end-user'). "
              "Default: no audience block."),
    )
    parser.add_argument(
        "--flavor",
        default="general",
        choices=["general", "pinn", "cli", "lib", "monorepo"],
        help=("Which flavor-specific template blocks to keep. "
              "Default: 'general' (strips every flavor-tagged block). "
              "See assets/templates/_flavor_strip.md for the convention. "
              "Reserved names: pinn (PINN/DeepXDE), cli (CLI tools), "
              "lib (plain libraries), monorepo (multi-language monorepos)."),
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    if not repo_root.is_dir():
        print(f"error: repo root does not exist: {repo_root}", file=sys.stderr)
        return 1

    out_dir = (repo_root / args.out).resolve()
    try:
        templates_dir = locate_templates_dir()
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    audience_block = templates_dir / "_audience_block.md"
    if not audience_block.is_file():
        print(f"error: audience block missing at {audience_block}; "
              "the skill package appears to be corrupt.", file=sys.stderr)
        return 1

    audience_prefix: str | None = None
    if args.audience:
        try:
            block = audience_block.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read audience block: {exc}", file=sys.stderr)
            return 1
        audience_prefix = (block
                           .replace("{{PROJECT_NAME}}", args.project_name)
                           .replace("{{AUDIENCE}}", args.audience))

    print(f"Scaffolding docs for project '{args.project_name}'")
    print(f"  templates: {templates_dir}")
    print(f"  output:    {out_dir}")
    written, skipped = materialize(templates_dir, out_dir, args.project_name,
                                   args.force, write_assess=args.assess,
                                   audience_prefix=audience_prefix,
                                   keep_flavor=args.flavor)
    print(f"Done. {len(written)} written, {len(skipped)} skipped.")
    if args.assess:
        assess_status = ("written" if "assess.md" in written
                         else "skipped" if "assess.md" in skipped
                         else "missing template")
        print(f"  assess.md: {assess_status}.")
    print("Next: fill the {{...}} placeholders per SKILL.md workflow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
