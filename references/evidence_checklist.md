# Evidence Checklist

> **Tool vs. expectation (read first).** `scripts/gen_topology.py` is a static, stdlib-only miner. It reads up to 200 KB per file (`MAX_FILE_READ`) and never follows real imports, never executes code, and never reaches across the network. It detects:
>
> - top-level directories as `module` entities (build/vendor dirs excluded), plus typed files detected inside them (`SKILL.md`, `agents/*.md`, `commands/*.md`, `.mcp.json`, `agent.yaml`)
> - language packages (manifests under sub-directories: `pyproject.toml`, `setup.py`, `setup.cfg`, `package.json`, `Cargo.toml`, `go.mod`)
> - scripts (`*.py` / `*.sh` at the root or under `scripts/`)
> - `source → copy` and `uses` edges via keyword/path matching
>
> It does **not** detect: cross-module call graphs, dynamic dispatch, runtime plugin loading, generated artifacts, dependency lock files, Maven (`pom.xml`), or anything requiring code execution. Rows in this checklist that depend on those signals are aspirational; the agent must verify them by reading the source. Use the auto-detected `topology.md` as a starting point, not as the final answer.

> **v2 edge-ordering note:** In the topology-first workflow, gather this
> evidence *during Phase 2, walking modules along the dependency edges* drawn
> in `topology.md` — not by random file reading. Read the single source of
> truth before its synced copies. Sort the rows below by the complexity/value
> of each entity as ranked in the topology's entity inventory.

Minimum files / symbols that MUST be read during Phase 2 before writing any prose. Pick the repo-flavor row that best matches the target project; multiple rows may apply.

## Universal (always)

| Target | Why |
| --- | --- |
| `README.md` | Author-curated capability list, install commands, citation. |
| `LICENSE` | Licence identifier for metadata snapshot. |
| `CITATION.cff` (if present) | Canonical citation. |
| Top-level build/metadata file (`pyproject.toml` / `setup.py` / `package.json` / `Cargo.toml` / `go.mod` / `pom.xml`) | Package name, supported language versions, dependency list, entry points. |
| `requirements*.txt` / `environment.yml` (if present) | Runtime extras not covered by build file. |
| `.github/workflows/` (top-level only) | CI install commands, supported platforms, and the test/coverage/lint gates that run per PR. |
| `Dockerfile` / `docker/` | GPU / reproducible install hints. |
| `Makefile` | Common developer commands. |
| `tests/` / `test/` top-level layout | Test map: unit/integration split, run-all + run-one commands. |
| `CHANGELOG.md` / `CHANGES.rst` / GitHub Releases | Release cadence, breaking-change history, versioning scheme. |
| `git log` / `git tag` vitality | Last commit date, tag cadence — trust signals for developer guide §2/§17. |
| `rg -c "TODO\|FIXME"` per module | Quality/debt hotspots for developer guide §19. |
| `SUPPORT.md` / `.github/ISSUE_TEMPLATE/` / `SECURITY.md` | Getting-help channels + security policy for user guide §20. |
| Entry-point files (`__main__.py` / `cli.py` / `app.py` / `cmd/`) | Entry-point map surfaces for developer guide §4.1. |
| Existing `docs/` tree listing | Avoid style / vocabulary drift. |

## Python ML / scientific-computing library

| Target | Read strategy |
| --- | --- |
| `<pkg>/__init__.py` | Full file; record `__all__` and alias re-exports. |
| `<pkg>/model.py` (or `trainer.py`) | Full `Model.__init__`, `.compile`, `.train`, `.predict`, `.save`, `.restore`. |
| `<pkg>/config.py` | All public setters. |
| `<pkg>/backend/` or `<pkg>/engine/` | `__init__.py`, `backend.py` (interface spec), loader logic. |
| `<pkg>/data/__init__.py` | Full `__all__` list; sample one concrete data class. |
| `<pkg>/constraints/` or `<pkg>/bc/` | Base class + all subclasses' signatures (the constraint/Boundary-condition layer; renamed in newer libs). |
| `<pkg>/gradients/` or AD module | `jacobian` / `hessian` / `clear` contract. |
| `<pkg>/optimizers/__init__.py` + `config.py` | Supported optimizer names, per-backend LR schedules. |
| `<pkg>/losses.py` / `metrics.py` | Full dict of supported identifiers. |
| `<pkg>/callbacks.py` or `<pkg>/hooks.py` | Every callback class and its lifecycle method (may live under `hooks/` or `trainers/` in newer libs). |
| `examples/<forward>/*.py` | Pick 2–3 short forward examples. |
| `examples/<inverse>/*.py` or `examples/<parameter-id>/*.py` | Pick 1 parameter-identification example. |

## Python CLI / web-service

| Target | Read strategy |
| --- | --- |
| `<pkg>/__main__.py` / `cli.py` | Entry point, subcommand map. |
| `<pkg>/server.py` / `app.py` / `main.py` | Framework (FastAPI/Flask/…), routing table. |
| `<pkg>/config.py` / `settings.py` | Env vars, default ports. |
| `<pkg>/handlers/` or `routers/` | Enumerate routes; sample 1 handler. |
| `openapi.json` / `swagger/` | If present, extract endpoint list. |
| `<pkg>/auth/` or `<pkg>/middleware/` | Auth flow, middleware stack; if absent, record why. |
| `<pkg>/db/` or `<pkg>/models.py` | Data access patterns, ORM usage, schema migrations. |
| `<pkg>/api/` or `<pkg>/schemas/` | Request/response schemas (pydantic / dataclass / interface definitions). |
| `<pkg>/tasks/` or `<pkg>/jobs/` | Background worker definitions, queue integrations. |
| `<pkg>/logging.py` or `<pkg>/observability/` | Structured logging, metrics, tracing setup. |

## Node / TypeScript library

| Target | Read strategy |
| --- | --- |
| `package.json` | `main`, `types`, `exports`, `scripts`. |
| `src/index.ts` | Public re-exports. |
| `tsconfig.json` | Language target, module system. |
| `src/<core>/` | Main class(es) + public types. |
| `examples/` or `demo/` | One runnable example. |
| `package.json` `peerDependencies` | Compatibility matrix (often missed by docs). |
| `tsconfig.json` `compilerOptions` | Target / module / strictness settings. |
| `src/<core>/index.ts` | Public type re-exports (where types live). |
| `src/<core>/types.ts` or `*.d.ts` | Public type definitions. |
| `src/<core>/errors.ts` | Error classes and their contracts. |

## Rust crate

| Target | Read strategy |
| --- | --- |
| `Cargo.toml` | crate name, edition, dependency set. |
| `src/main.rs` | Binary entry point, argument parsing, and top-level wiring. |
| `src/<module>/` (non-`mod.rs`) | Internal data structures, trait impls, and helpers the public API delegates to. |
| `examples/` | One small example. |
| `Cargo.toml` `[features]` | Optional-feature matrix and their dependencies. |
| `src/lib.rs` | `pub use` re-exports + the main public API. |
| `src/<module>/mod.rs` | Per-module public types and traits. |
| `src/error.rs` or `src/errors/` | Public `Error` / `Result` types and their `From` impls. |
| `tests/` or `#[cfg(test)]` modules | Per-module test coverage; sample one test per module. |

## Go module

| Target | Read strategy |
| --- | --- |
| `go.mod` | Module path, Go version. |
| Top-level `*.go` files with `package <name>` | Exported types (Capitalized). |
| `cmd/` subfolders | Discover every binary and the flag/config conventions they share. |
| `pkg/` (if present) | Public surface intended for external import. |
| `examples/` or `_examples/` | One runnable. |
| Top-level `doc.go` | Package-level doc comment (godoc). |
| `go.sum` | Pinned transitive deps (use for license/compatibility check, not behavior). |
| `cmd/<binary>/main.go` | Binary entry points and their flag parsing. |
| `internal/<pkg>/` | Private surface (still important if it does heavy lifting). |
| `<pkg>.go` files in each subdir | Exported types and their method signatures. |

## Output of Phase 2

Maintain a scratch note (internal, not a deliverable) with:

- `name`, `version`, `license`, `python_requires` / `engines` / `rust_edition`, dependency list.
- `__all__` per top-level sub-package.
- Main class signatures (constructor + 3–5 key methods).
- List of chosen example files with a 1-line summary each.
- Test-map facts: layout, run-all / run-one commands, coverage command, CI gates.
- Release facts: latest tag, last commit date, changelog path, versioning scheme.
- Quality signals: TODO/FIXME counts per module, `git shortlog -sn` top contributors.
- Support channels: issue tracker, discussions/community, security contact.

This note feeds directly into the template `{{PLACEHOLDER}}` substitutions in Phase 4.
