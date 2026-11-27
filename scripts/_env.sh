#!/usr/bin/env bash
# scripts/_env.sh — source this file to set REPO_DOC_MINER_HOME.
#
# Usage:
#   source scripts/_env.sh
#   python "$REPO_DOC_MINER_HOME/scripts/gen_topology.py" <repo-root>
#
# Or in one line:
#   REPO_DOC_MINER_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" \
#       python scripts/gen_topology.py <repo-root>
#
# Setting the variable lets agents reference the skill's scripts and
# templates from outside the skill directory without hard-coding paths.

# Resolve the skill root: the parent of the directory that holds this file.
_REPO_DOC_MINER_HOME="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
export REPO_DOC_MINER_HOME="$_REPO_DOC_MINER_HOME"
