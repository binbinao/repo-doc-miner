# repo-doc-miner — top-level Makefile.
#
# Use `make help` to list targets. The default target is `help` (no work).
#
# `make test` is the canonical "does the skill work" check: it runs
# scripts/smoke.py and exits non-zero on any failure. `make smoke-strict`
# adds the Phase 4 --guides-dir --strict audit (informational, exits 0
# on a draft-state scaffold).
#
# `make clean` removes build caches and the throwaway guides directory
# the smoke battery creates; it does not touch any user files.

.PHONY: help test smoke smoke-strict clean validate

PYTHON ?= python3
SCRIPT_DIR := scripts
SMOKE := $(PYTHON) $(SCRIPT_DIR)/smoke.py
GEN_TOP := $(PYTHON) $(SCRIPT_DIR)/gen_topology.py
SCAFF := $(PYTHON) $(SCRIPT_DIR)/scaffold_docs.py

help:
	@echo "repo-doc-miner Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  test           run the full battery (scripts/smoke.py); exits non-zero on failure"
	@echo "  smoke          alias for test"
	@echo "  smoke-strict   scaffold a throwaway + audit with --strict --guides-dir"
	@echo "  validate       run smoke + smoke-strict (full validation suite)"
	@echo "  clean          remove __pycache__ and the throwaway guides/ subdirectory"
	@echo "  help           this message (default)"
	@echo ""
	@echo "Variables (override on the command line):"
	@echo "  PYTHON=python3.11  which Python interpreter to use"

test: smoke

smoke:
	@$(SMOKE)

smoke-strict:
	@tmp=$$(mktemp -d) && \
	  git -C $$tmp init -q && \
	  $(SCAFF) $$tmp --project-name Demo --force --assess --audience contributor > /dev/null && \
	  $(SMOKE) --guides-dir $$tmp/docs/guides --strict ; \
	  status=$$? ; \
	  rm -rf $$tmp ; \
	  exit $$status

validate: smoke smoke-strict
	@echo "validate: full battery + throwaway --strict audit passed."

clean:
	@find . -name __pycache__ -type d -prune -exec rm -rf {} +
	@rm -rf docs/guides
	@echo "cleaned"
