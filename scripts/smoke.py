#!/usr/bin/env python3
"""Codified smoke test + Phase-5 checks for the repo-doc-miner skill.

This script exists because the AGENTS.md "Verification gates" section
contains a bash block (the "safe smoke test") that is meant to be run
manually after every change to `scripts/`. It is easy to skip; harder to
notice when it has drifted. This file makes it a single command and
adds Phase-5 checks (Mermaid fences, placeholder residue) that the manual
block does not cover. Relative-link checking is part of the manual Phase-5
sweep (`SKILL.md`), not of this script.

Usage
-----
    python scripts/smoke.py                # run the full battery
    python scripts/smoke.py --check-only    # skip the Phase-4 scaffolder step
    python scripts/smoke.py --strict        # full Phase-5 publish gate
    python scripts/smoke.py --keep-tmp      # leave the throwaway dir behind

Policy
------
The placeholder checks have two tiers. The scaffolder contract always
applies: the placeholders `scaffold_docs.py` substitutes itself
(`{{PROJECT_NAME}}`, `{{AUDIENCE}}`) must not survive. Every other
`{{...}}` placeholder and every `<...>` slot is filled in by hand during
Phase 4 / Phase 3, so it is reported as `[INFO]` and only fails under
`--strict`, and only for a file that no longer carries a
`TODO(doc-miner)` marker (i.e. claims to be publish-ready).

`--check-only` runs only the `gen_topology.py` step — that step still
writes `topology.md` into the throwaway directory; only the Phase-4
scaffolder is skipped.

Exit codes
----------
    0  every check passed
    1  one or more checks failed (printed to stderr)
    2  invocation error (bad args, scripts not on PATH, etc.)
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parent

# Sanity: the Phase 3 + Phase 4 auxiliary files must exist.
for _aux_path in (
    REPO / "scripts" / "_env.sh",
    REPO / "assets" / "templates" / "_flavor_strip.md",
):
    if not _aux_path.is_file():
        print(f"error: required file missing: {_aux_path}", file=sys.stderr)
        raise SystemExit(2)

# The placeholders `scaffold_docs.py` substitutes itself, in the exact
# braced shape the residue scan finds. Anything else in `{{...}}` is filled
# in by the agent during Phase 4 and is expected to survive scaffolding
# untouched. Membership is exact so that e.g. `{{PRIMARY_AUDIENCE}}` (from
# `assets/templates/assess.md`) is not mistaken for `{{AUDIENCE}}`.
SCAFFOLDER_PLACEHOLDERS = frozenset({"{{PROJECT_NAME}}", "{{AUDIENCE}}"})


def _print(check: str, ok: bool, detail: str = "") -> None:
    marker = "OK  " if ok else "FAIL"
    line = f"[{marker}] {check}"
    if detail:
        line += f"  -- {detail}"
    print(line)


def _fence_problems(text: str) -> list[str]:
    """Describe every unbalanced fenced code block in ``text``.

    Tracks the open fence (backtick-run length + info string) instead of
    toggling a boolean, so a fence that opens while another block is still
    open — an unclosed ```mermaid followed by ```bash, say — is reported
    instead of silently closing the first block.
    """
    problems: list[str] = []
    open_run = 0
    open_info = ""
    open_line = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if not stripped.startswith("```"):
            continue
        run = len(stripped) - len(stripped.lstrip("`"))
        info = stripped[run:].strip()
        if open_run and info:
            problems.append(
                f"line {lineno}: ```{info} opened while the block from line "
                f"{open_line} is still open"
            )
            open_run, open_info, open_line = run, info, lineno
        elif open_run and run >= open_run:
            open_run, open_info, open_line = 0, "", 0
        elif not open_run:
            open_run, open_info, open_line = run, info, lineno
        # A shorter bare fence inside an open block is block content.
    if open_run:
        problems.append(f"line {open_line}: unclosed ```{open_info} block")
    return problems


def _safe_smoke(*, write: bool, keep_tmp: bool = False, strict: bool = False,
                guides_dir: Path | None = None) -> int:
    """Replicate the AGENTS.md safe smoke test.

    Returns 0 on success. When `write` is False, the scaffolder is
    invoked with `--force` semantics skipped (i.e. not invoked at all),
    which makes this safe to call from `--check-only` mode.

    When `guides_dir` is set, audit that directory in place instead of
    generating a throwaway scaffold. The `strict` flag enables the
    publish-ready check in `_phase5_checks` (only meaningful with a real
    `docs/guides/` set).
    """
    if guides_dir is not None:
        if not guides_dir.is_dir():
            _print(f"guides-dir {guides_dir} is not a directory", False)
            return 1
        return _phase5_checks(guides_dir, strict=strict)

    failures = 0
    tmp_dir = tempfile.mkdtemp(prefix="rsm-smoke-")
    tmp_path = Path(tmp_dir)
    try:
        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)

        gen = subprocess.run(
            [sys.executable, str(HERE / "gen_topology.py"), str(tmp_path), "--project-name", "Demo"],
            capture_output=True, text=True,
        )
        if gen.returncode != 0:
            _print("gen_topology.py on throwaway", False, gen.stderr.strip().splitlines()[-1] if gen.stderr else "exit non-zero")
            failures += 1
        else:
            _print("gen_topology.py on throwaway", True, gen.stdout.strip().splitlines()[-1] if gen.stdout else "")

        if write:
            scaff = subprocess.run(
                [sys.executable, str(HERE / "scaffold_docs.py"), str(tmp_path),
                 "--project-name", "Demo", "--force"],
                capture_output=True, text=True,
            )
            if scaff.returncode != 0:
                _print("scaffold_docs.py on throwaway", False, scaff.stderr.strip().splitlines()[-1] if scaff.stderr else "exit non-zero")
                failures += 1
            else:
                _print("scaffold_docs.py on throwaway", True, scaff.stdout.strip().splitlines()[-1] if scaff.stdout else "")
                # Phase-5 checks on the materialized output
                failures += _phase5_checks(tmp_path / "docs" / "guides", strict=strict)
        else:
            _print("scaffold_docs.py skipped (--check-only)", True)
    finally:
        if keep_tmp:
            print(f"[INFO] throwaway dir kept at {tmp_path}")
        else:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return failures


def _phase5_checks(guides_dir: Path, *, strict: bool = False) -> int:
    """Mermaid fences closed, no broken `{{...}}` placeholders in shipped
    files, `TODO(doc-miner)` count printed (informational)."""
    failures = 0

    # 1. Fenced code blocks are balanced and each block is closed.
    for md in sorted(guides_dir.glob("*.md")):
        problems = _fence_problems(md.read_text(encoding="utf-8"))
        if problems:
            _print(f"{md.name}: mermaid fence balanced", False, "; ".join(problems))
            failures += 1
        else:
            _print(f"{md.name}: mermaid fence balanced", True)

    # 2 + 3. Placeholder residue and `<angle-bracket>` slots.
    #   - A surviving `{{PROJECT_NAME}}` / `{{AUDIENCE}}` always fails: the
    #     scaffolder is contracted to substitute those.
    #   - Every other `{{...}}` placeholder and every `<...>` slot is filled
    #     in by hand (Phase 4 / Phase 3), so it is reported as `[INFO]` by
    #     default and only fails under `--strict`, and only for a file that
    #     no longer carries a `TODO(doc-miner)` marker, i.e. claims to be
    #     publish-ready.
    for md in sorted(guides_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        publish_ready = "TODO(doc-miner)" not in text

        found = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", text)))
        broken = [p for p in found if p in SCAFFOLDER_PLACEHOLDERS]
        pending = [p for p in found if p not in SCAFFOLDER_PLACEHOLDERS]
        if broken:
            _print(f"{md.name}: no leftover placeholders", False, f"scaffolder placeholder survived: {broken}")
            failures += 1
        elif strict and pending and publish_ready:
            _print(f"{md.name}: no leftover placeholders", False, f"found {pending}")
            failures += 1
        else:
            _print(f"{md.name}: no leftover placeholders", True)
        if pending:
            print(f"[INFO] {md.name}: {len(pending)} Phase-4 placeholder(s) pending fill-in")

        slots = sorted(set(re.findall(r"<[a-z -]+>", text)))
        if strict and slots and publish_ready:
            _print(f"{md.name}: no <angle-bracket> slots", False, f"found {slots}")
            failures += 1
        else:
            _print(f"{md.name}: no <angle-bracket> slots", True)
        if slots:
            print(f"[INFO] {md.name}: {len(slots)} <angle-bracket> slot(s) pending manual fill-in")

    # 4. Informational: TODO(doc-miner) count per file.
    for md in sorted(guides_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        todo = text.count("TODO(doc-miner)")
        if todo:
            print(f"[INFO] {md.name}: {todo} TODO(doc-miner) marker(s) (expected before Phase 4 fill-in)")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check-only", action="store_true",
                        help="Run only the topology generation step (it still writes into the "
                             "throwaway dir); skip the Phase-4 scaffolder step.")
    parser.add_argument("--strict", action="store_true",
                        help="Full Phase-5 publish gate: also fail on Phase-4 placeholders and "
                             "<angle-bracket> slots left in a file with no TODO(doc-miner) marker.")
    parser.add_argument("--keep-tmp", action="store_true",
                        help="Leave the throwaway directory behind for inspection (its path is printed).")
    parser.add_argument("--guides-dir", type=Path, default=None,
                        help="Audit an existing docs/guides/ directory in place "
                             "(no throwaway generation). Combined with --strict, "
                             "fail on Phase-4 placeholders and <...> slots in "
                             "publish-ready files (no TODO(doc-miner) marker).")
    args = parser.parse_args(argv)

    if not (HERE / "gen_topology.py").is_file():
        print(f"error: {HERE / 'gen_topology.py'} not found", file=sys.stderr)
        return 2
    if not (HERE / "scaffold_docs.py").is_file():
        print(f"error: {HERE / 'scaffold_docs.py'} not found", file=sys.stderr)
        return 2

    print(f"repo-doc-miner smoke test (check_only={args.check_only}, strict={args.strict})")
    print(f"  repo: {REPO}")
    print()

    failures = _safe_smoke(write=not args.check_only, keep_tmp=args.keep_tmp,
                           strict=args.strict, guides_dir=args.guides_dir)
    print()
    if failures:
        print(f"FAILED: {failures} check(s) did not pass.", file=sys.stderr)
        return 1
    print("OK: all checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
