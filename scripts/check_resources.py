#!/usr/bin/env python3
"""Cross-check the SKILL.md `## Resources` section against the actual
files under `assets/templates/`, `references/`, and `scripts/`.

Run via `python3 scripts/check_resources.py`. Always exits 0; the check
is informational. Use this to spot drift after adding a new template or
reference: if the script reports "1 disk file missing from SKILL.md",
add the new file to the `## Resources` section.

Exit codes
----------
    0  always
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# Files to exclude from the disk-side scan (not user-facing assets).
EXCLUDE = {
    "__pycache__",
    "smoke.py",  # not in SKILL.md Resources; the smoke battery is a dev tool
}


def _disk_files() -> dict[str, list[str]]:
    """Return {category: [path-glob, ...]} for the 3 resource categories."""
    out: dict[str, list[str]] = {"templates": [], "references": [], "scripts": []}
    for md in sorted((ROOT / "assets" / "templates").glob("*.md")):
        out["templates"].append(f"assets/templates/{md.name}")
    for md in sorted((ROOT / "references").glob("*.md")):
        out["references"].append(f"references/{md.name}")
    for sh in sorted((ROOT / "scripts").glob("*.py")):
        if sh.name in EXCLUDE:
            continue
        out["scripts"].append(f"scripts/{sh.name}")
    for sh in sorted((ROOT / "scripts").glob("*.sh")):
        out["scripts"].append(f"scripts/{sh.name}")
    return out


def _skill_entries() -> dict[str, list[str]]:
    """Return {category: [path-glob, ...]} parsed from SKILL.md `## Resources`."""
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    # `## Resources` is a top-level H2 in SKILL.md; its `###` subsections
    # are `### scripts/`, `### assets/templates/`, `### references/`.
    out: dict[str, list[str]] = {"templates": [], "references": [], "scripts": []}
    in_resources = False
    current_cat: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            in_resources = line.startswith("## Resources")
            current_cat = None
            continue
        if not in_resources:
            continue
        if line.startswith("### "):
            sub = line[len("### "):].strip().rstrip("/")
            if sub in ("scripts", "assets/templates", "references"):
                current_cat = {
                    "scripts": "scripts",
                    "assets/templates": "templates",
                    "references": "references",
                }[sub]
            else:
                current_cat = None
            continue
        if current_cat is None or not line.startswith("- "):
            continue
        # Each bullet is `- \`path/to/file\` — desc`. Capture the first
        # backtick-quoted token (the file path).
        match = re.search(r"`([^`]+)`", line)
        if match:
            path = match.group(1)
            # SKILL.md writes paths as `assets/templates/...` (no
            # leading `./`); normalise.
            out[current_cat].append(path)
    return out


def main() -> int:
    disk = _disk_files()
    skill = _skill_entries()
    print("check_resources.py — SKILL.md Resources vs disk")
    print()
    for cat in ("templates", "references", "scripts"):
        d = set(disk[cat])
        s = set(skill[cat])
        only_disk = d - s
        only_skill = s - d
        print(f"### {cat}")
        print(f"  disk: {len(d):3d}   SKILL.md: {len(s):3d}   in both: {len(d & s):3d}")
        if only_disk:
            for p in sorted(only_disk):
                print(f"  INFO disk-only: {p}")
        if only_skill:
            for p in sorted(only_skill):
                print(f"  INFO skill-only (may be a mention in prose, not a link): {p}")
        print()
    print("OK: check complete (informational; does not fail the build).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
