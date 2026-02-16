# AIC Tooling and Compiler (Draft)

This document covers the command‑line interface, diagnostics, language server, project layout, and build pipeline for AIC.

## CLI: `aic`
- `aic init` — scaffold a new project in the current directory.
- `aic fmt` — format the workspace; fails if non‑canonical.
- `aic check` — fast parse + typecheck + effects check; no codegen.
- `aic build` — produce binaries/libraries; `--target {native|wasm32}`.
- `aic run` — build then run the default target.
- `aic test` — run unit and doc tests.
- `aic doc` — generate API docs from `///` comments.
- `aic scaffold <template>` — generate canonical skeletons (e.g., `cli`, `http-client`, `service`).

## Project Layout
```
myproj/
  project.toml
  src/
    main.aic
  tests/
    main_test.aic
  README.md
```

## `project.toml` (MVP schema)
```toml
[project]
name = "myproj"
version = "0.1.0"
edition = "2025"

[target]
# one of: "native", "wasm32"
kind = "native"

[deps]
# name = "version"
http = "0.1"
json = "0.1"
```

## Build Pipeline
- Phases: parse → lower → typecheck → effects check → monomorphize → codegen → link.
- Incremental: per‑file modules with stable hashing; cache all phases.
- Reproducible: pinned toolchain, deterministic codegen orders, hermetic dependencies.
- Parallel: modules build in parallel when dependencies are satisfied.

## Diagnostics
- All commands can emit machine‑readable diagnostics via `--json`.
- Diagnostic structure:
```json
{
  "code": "E0301",
  "level": "error",
  "message": "type mismatch: expected string, found i32",
  "span": {"file": "src/main.aic", "line": 12, "column": 17},
  "notes": ["hint: add to_string()"],
  "fixits": [{
    "range": {"start": {"line":12, "column":17}, "end": {"line":12, "column":19}},
    "replacement": "to_string()"
  }]
}
```
- Stability: codes and message schemas are versioned and documented.

## Language Server (LSP)
- Features: completion, hover types, go‑to definition, find references, rename, code actions (fix‑its), formatting, inlay hints.
- Typed holes: on `_`, show expected type and example snippets.
- Index: per‑module symbol index with cross‑references.

## Formatter
- The formatter is canonical, compact, and opinionated; `aic check` fails on unformatted code.
- Compactness rules: minimal spaces, no vertical alignment, stable line‑breaking.
- Fine‑grained ignores via `// aic:ignore-next-line` in exceptional cases.
- `aic fmt --stats` (planned) outputs token and character counts to track budget.

## Testing
- Unit tests: `test` blocks inside files or separate files under `tests/`.
- Doc tests: code in `///` fenced blocks compiled and run with `aic test`.
- Snapshots: opt‑in snapshot testing utility in stdlib for stable textual outputs.

## Packaging and Dependencies
- Version ranges: caret `^` semantics by default; lockfile `project.lock` records exact versions.
- Registry: out of scope for MVP; local path and git deps supported first (network policy permitting).

## Codegen Targets
- Native: via LLVM backend (MVP can start with a simpler C or Cranelift path).
- WASM: `wasm32-wasi` with a small runtime shim; deterministic by default.

## Scaffolds (Examples)
- `aic scaffold cli` — main with argument parsing and a `run()` stub.
- `aic scaffold http-client` — async runtime, HTTP client example, JSON serde.
- `aic scaffold service` — structured concurrency, graceful shutdown, logging.

## Telemetry (Opt‑in)
- Anonymous stats on compile times and diagnostic fix‑it application rates to improve LLM guidance.
- Fully disabled by default; explicit opt‑in via `project.toml` or env var.

## Exit Codes
- 0: success
- 1: build failure (errors)
- 2: formatter disagreements
- 3: test failures
- 4: misuse (invalid flags, etc.)

## Security
- Effects system supports static allow‑listing (e.g., deny `net` in tests).
- Sandboxed execution for `aic run --target wasm32` during tests.

## Example Workflow
```
aic init
# edit src/main.aic

aic fmt
aic check --json > diag.json
# fix using suggested fix‑its

aic run
```
