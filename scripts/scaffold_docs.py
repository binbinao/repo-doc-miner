#!/usr/bin/env python3
"""Scaffold the five-file doc set for the repo-doc-miner skill.

Creates <repo-root>/<out>/ and materializes the five Markdown templates
(topology, README, developer_guide, user_guide, tutorial) from the
skill's assets/templates/ directory, with a single {{PROJECT_NAME}}
placeholder substituted. All other {{...}} placeholders are intentionally
left in place so the CodeBuddy agent can fill them during Phase 4 of the
workflow described in SKILL.md.

Existing template files in the output directory are left untouched unless
--force is supplied, so a Phase-1 topology.md is never clobbered.

Usage
-----
    python scripts/scaffold_docs.py <repo-root> \
        --project-name "MyProject" \
        [--out docs/guides] \
        [--force]

Exit codes
----------
    0  success (files written and/or skipped)
    1  repo root does not exist, or the templates directory is missing
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TEMPLATE_FILES = (
    "topology.md",
    "README.md",
    "developer_guide.md",
    "user_guide.md",
    "tutorial.md",
)


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
) -> tuple[list[str], list[str]]:
    """Write the missing templates; return (written, skipped) file names."""
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
        dst.write_text(text, encoding="utf-8")
        written.append(name)
        print(f"  wrote {dst}")
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

    print(f"Scaffolding docs for project '{args.project_name}'")
    print(f"  templates: {templates_dir}")
    print(f"  output:    {out_dir}")
    written, skipped = materialize(templates_dir, out_dir, args.project_name, args.force)
    print(f"Done. {len(written)} written, {len(skipped)} skipped.")
    print("Next: fill the {{...}} placeholders per SKILL.md workflow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
