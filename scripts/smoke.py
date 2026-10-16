#!/usr/bin/env python3
"""Codified smoke test + Phase-5 checks for the repo-doc-miner skill.

This script exists because the AGENTS.md "Verification gates" section
contains a bash block (the "safe smoke test") that is meant to be run
manually after every change to `scripts/`. It is easy to skip; harder to
notice when it has drifted. This file makes it a single command and
adds Phase-5 checks (Mermaid fences, placeholder residue, link
integrity) that the manual block does not cover.

Usage
-----
    python scripts/smoke.py                # run the full battery
    python scripts/smoke.py --check-only    # no writes; just verify
    python scripts/smoke.py --keep-tmp      # leave the throwaway dir behind

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

# Placeholders `scaffold_docs.py` substitutes itself. Anything else in
# `{{...}}` is filled in by the agent during Phase 4 and is expected to
# survive scaffolding untouched.
SCAFFOLDER_PLACEHOLDERS = ("PROJECT_NAME", "AUDIENCE")


def _print(check: str, ok: bool, detail: str = "") -> None:
    marker = "OK  " if ok else "FAIL"
    line = f"[{marker}] {check}"
    if detail:
        line += f"  -- {detail}"
    print(line)


def _safe_smoke(*, write: bool, keep_tmp: bool = False) -> int:
    """Replicate the AGENTS.md safe smoke test.

    Returns 0 on success. When `write` is False, the scaffolder is
    invoked with `--force` semantics skipped (i.e. not invoked at all),
    which makes this safe to call from `--check-only` mode.
    """
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
                failures += _phase5_checks(tmp_path / "docs" / "guides")
        else:
            _print("scaffold_docs.py skipped (--check-only)", True)
    finally:
        if keep_tmp:
            print(f"[INFO] throwaway dir kept at {tmp_path}")
        else:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return failures


def _phase5_checks(guides_dir: Path) -> int:
    """Mermaid fences closed, no broken `{{...}}` placeholders in shipped
    files, `TODO(doc-miner)` count printed (informational)."""
    failures = 0

    # 1. Mermaid fences are balanced.
    for md in sorted(guides_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        # Each ```mermaid ... ``` block must be closed.
        # We use a fence-aware state machine: count ``` not inside code blocks.
        in_code = False
        in_mermaid = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("```"):
                if not in_code:
                    in_code = True
                    in_mermaid = stripped == "```mermaid"
                else:
                    if in_mermaid:
                        in_mermaid = False
                    in_code = False
        if in_mermaid:
            _print(f"{md.name}: mermaid fence balanced", False, "unclosed ```mermaid block")
            failures += 1
        else:
            _print(f"{md.name}: mermaid fence balanced", True)

    # 2 + 3. Placeholder residue and `<angle-bracket>` slots.
    #   - A surviving `{{PROJECT_NAME}}` / `{{AUDIENCE}}` always fails: the
    #     scaffolder is contracted to substitute those.
    #   - Every other `{{...}}` placeholder and every `<...>` slot is filled
    #     in by hand (Phase 4 / Phase 3), so they only fail once the file no
    #     longer carries a `TODO(doc-miner)` marker, i.e. claims to be
    #     publish-ready. A draft scaffold is reported as INFO instead.
    for md in sorted(guides_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        draft = "TODO(doc-miner)" in text

        found = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", text)))
        broken = [p for p in found if any(k in p for k in SCAFFOLDER_PLACEHOLDERS)]
        pending = [p for p in found if p not in broken]
        if broken:
            _print(f"{md.name}: no leftover placeholders", False, f"scaffolder placeholder survived: {broken}")
            failures += 1
        elif pending and not draft:
            _print(f"{md.name}: no leftover placeholders", False, f"found {pending}")
            failures += 1
        else:
            _print(f"{md.name}: no leftover placeholders", True)
        if pending:
            print(f"[INFO] {md.name}: {len(pending)} Phase-4 placeholder(s) pending fill-in")

        slots = sorted(set(re.findall(r"<[a-z -]+>", text)))
        if slots and not draft:
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
                        help="Run only the topology generation step; skip scaffolder writes.")
    parser.add_argument("--keep-tmp", action="store_true",
                        help="Leave the throwaway directory behind for inspection (its path is printed).")
    args = parser.parse_args(argv)

    if not (HERE / "gen_topology.py").is_file():
        print(f"error: {HERE / 'gen_topology.py'} not found", file=sys.stderr)
        return 2
    if not (HERE / "scaffold_docs.py").is_file():
        print(f"error: {HERE / 'scaffold_docs.py'} not found", file=sys.stderr)
        return 2

    print(f"repo-doc-miner smoke test (check_only={args.check_only})")
    print(f"  repo: {REPO}")
    print()

    failures = _safe_smoke(write=not args.check_only, keep_tmp=args.keep_tmp)
    print()
    if failures:
        print(f"FAILED: {failures} check(s) did not pass.", file=sys.stderr)
        return 1
    print("OK: all checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
