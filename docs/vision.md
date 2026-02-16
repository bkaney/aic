# AIC: An AI‑First Programming Language — Vision

This document captures the goals, constraints, and guiding principles for AIC, a programming language designed to maximize first‑try correctness when authored by AI language models, while remaining pleasant and predictable for human developers.

## Purpose
- Optimize for “first compile succeeds” from LLM‑generated code.
- Remove ambiguity through regular syntax, deterministic semantics, and a canonical formatter enforced by the compiler.
- Provide actionable diagnostics and typed holes so partial code still checks and guides completion.

## Design Goals
- Determinism: Fully specified evaluation order; no hidden mutations or implicit conversions.
- Regularity: One obvious way to express each construct; no dialects.
- Local reasoning: Types are explicit or inferred locally; avoid whole‑program inference.
- Fast feedback: `aic check` is sub‑second on small projects; diagnostics are stable and machine‑readable.
- Partial programs: Typed holes (`_`) and `todo()`/`unimplemented()` allow iterative construction without cascading errors.
- Predictable libraries: Minimal, opinionated stdlib with one canonical API per domain.
- Reproducible builds: Deterministic outputs with stable hashing.

## Non‑Goals
- Novel or surprising syntax features.
- Complex type features (HKTs, dependent types) in the MVP.
- Operator overloading, user‑defined operators, or implicit conversions.
- Magic globals or wildcard imports.

## Positioning
- Mid‑level, compiled, safe language. Sits above C/Rust in ergonomics while keeping predictable performance via monomorphized generics and a minimal runtime (async executor, channels, ARC).
- Not intended for kernels, hard real‑time, or bare‑metal drivers in MVP. Interop and profiles may broaden scope later.

## Guiding Principles
- Explicit over implicit: imports, visibility, effects, and error propagation are spelled out.
- Small orthogonal core: structs, enums, traits, generics (monomorphized), async, pattern matching.
- Format to compile: canonical formatter is enforced by the compiler; misformatted code fails `check`.
- Clear boundaries: strong module system; one module per file; `pub` exports are enumerated.
- Stability: language and diagnostics change behind version flags with a deprecation policy.
- Token economy: keep the surface terse. Prefer short, widely‑known keywords (`fn`, `let`, `pub`, `use`, `impl`, `trait`, `enum`, `match`, `async`, `await`). Avoid boilerplate and excessive ceremony. Standard library module names are short (`io`, `net`, `fs`, `json`, `fmt`).

## LLM‑Optimization Summary (MVP vs Post‑MVP)
- Syntax regularity & tokens (MVP): short, familiar keywords; explicit `return;`; required semicolons; one statement per line; canonical formatter. Post‑MVP: evaluate safe semicolon elision behind an edition.
- Imports & names (MVP): one import form with alias; no wildcards; FQN always valid (`std::json::decode`), with fix‑its to add `use`.
- Types & generics (MVP): local inference only; no implicit conversions. MVP‑candidate: `_` in type positions for local inference; `cast<T>(x)` instead of `as`. Post‑MVP: `derive(...)` for a small, fixed set of std traits (no macros).
- Control flow (MVP): exhaustive `match`; no fallthrough; commas after arms. MVP‑candidate: `if let` sugar. Post‑MVP: minimal `defer` for cleanup.
- Errors (MVP): `Result<T,E>` + `?`, unified adapters (`map_err`, `with_context`, `ensure`). Panics/abort gated by explicit effects.
- Effects (MVP): explicit `effects(io, net, fs, proc)`. MVP‑candidate: lexical `with(net) { ... }` sugar for localized requirements. Post‑MVP: library‑defined custom effects.
- Concurrency (MVP): structured tasks, channels, timers; single canonical runtime. MVP‑candidate: `select { ... }` with regular blocks.
- Strings/format (MVP): single `fmt::format` with numbered placeholders; raw strings `r"..."`; bytes `b"..."`.
- Collections/iter (MVP): one `vec[T]` with `vec![..]` literal; minimal iterator traits (`IntoIter`, `Map`, `Filter`).
- Incomplete code (MVP): typed holes `_` in expr and pattern; `todo()/unimplemented()` are warnings; code actions to fill missing `match` arms; safe stub generation.
- Diagnostics (MVP): one error → one fix‑it; stable, machine‑readable diagnostics.

## Language Pillars
- Types: primitives, structs, enums (tagged unions), tuples, arrays/slices, maps, generics (monomorphized via specialization).
- Traits: ad‑hoc polymorphism with `trait` and `impl`; no inheritance; no overloading.
- Error handling: `Result<T, E>` with `?` sugar; no exceptions.
- Pattern matching: exhaustive on enums; irrefutable bindings otherwise.
- Concurrency: `async/await`, tasks, channels; no data races without explicit synchronization.
- Effects: tiny capability system (e.g., `io`, `net`, `fs`, `proc`) declared on functions and checked at compile time.
- Memory: ARC with a small cycle breaker; no user‑visible lifetimes or manual frees.
- Interop: C ABI FFI and WASM export in MVP; bindings for JS/Python can layer on top.

## Modules and Build
- One module per file; file name equals module tail (`module path.name;`).
- Explicit imports via `use path::to::item`.
- `project.toml` declares project metadata, targets, dependencies, and compiler options.
- Standard layout: `src/`, `tests/`, `project.toml`, `README.md`.

## Diagnostics and Typed Holes
- `_` stands for a typed hole at expression or pattern positions; the compiler reports the expected type and suggestions.
- `todo("reason")` and `unimplemented()` compile with warnings, not errors.
- Diagnostics are stable, actionable, and machine‑readable (JSON) with fix‑its and suggested code snippets.
- Single root cause policy: avoid cascaded noise after the first error in a span.

## Standard Library (MVP)
- Core: `option`, `result`, `collections`, `time`, `fmt`.
- IO/Net: `fs`, `http`, `sockets`, `process`, `env`.
- Concurrency: `task`, `channel`, `timer`, `select`.
- Serde: JSON/TOML with derive‑based encode/decode.
- Test: unit tests and doc tests via `///` blocks.

## Memory Model
- Safe by default: ARC ensures values remain valid while referenced.
- Cycle handling: Background cycle detector frees unreachable cycles; deterministic finalizers are not guaranteed.
- Mutability: explicit via `mut` fields or interior mutability types (`Mutex`, `Atomic`).

## Effects (Capabilities)
- Functions declare required capabilities via a trailing `effects(...)` clause.
- Calling an effectful function requires the caller to declare compatible effects or to call through a sandbox API.
- Example: `fn read_config(path: string) -> Result<string, IoErr> effects(io) { ... }`

## Concurrency
- Structured concurrency: tasks are scoped; `join` and `cancel` primitives.
- Async runtime in stdlib; `await` yields only at well‑defined points.
- Channels for message passing; no shared mutable state without synchronization wrappers.

## Interop
- C ABI FFI: `extern "C"` blocks with explicit types and calling conventions.
- WASM: compile to WASM with predictable imports/exports; `aic build --target wasm32`.

## Benchmarks and Success Criteria
- Compilation success rate on canonical tasks (CLI, HTTP client/server, JSON transform, concurrent worker).
- Edit distance to green: number of compile‑error/fix cycles to pass provided tests.
- Token budget: mean tokens per working solution across model sizes.
- Cold build time: check + build under 1s for small apps.
- Diagnostic quality: fraction of errors with exact fix‑its.

## Out of Scope for MVP
- Macros, code generation within the language, or metaprogramming features.
- User‑defined operators and complex precedence rules.
- Global type inference or whole‑program specialization.

## Avoiding Common LLM Pitfalls (Recommendations)
- No operator overloading or user‑defined operators; keep a small, fixed precedence table.
- No macros or attribute‑driven codegen; prefer explicit `derive(...)` post‑MVP only for a fixed std trait set.
- No default imports or preludes; forbid wildcard imports. Require explicit `use` and visibility.
- No implicit numeric widening; require explicit casts via `cast<T>(x)`.
- Shadowing is off by default; use `shadow let` to opt in when intentional.
- Deterministic evaluation order; avoid context‑sensitive grammar and hidden side effects.
- Single canonical stdlib API per domain (e.g., one HTTP client) to reduce decision surface.
- Format‑or‑fail to prevent style drift and ambiguous diffs.

## Example Snapshot
```aic
module http.client;
use std::net::http;
use std::json as json;
use std::fmt as fmt;

pub struct User {
    id: u64;
    name: string;
}

pub enum HttpErr { Status(u16); Decode(string); Net(string); }

pub async fn fetch_user(id: u64) -> Result<User, HttpErr> effects(net) {
    let url = fmt::format("/users/{}", id);
    let resp = await http.get(url);
    if resp.status != 200 { return Err(HttpErr::Status(resp.status)); }
    let u: User = json.decode(resp.body).map_err(HttpErr::Decode)?;
    return Ok(u);
}
```

## Versioning and Stability
- Semantic versioning for the compiler and stdlib.
- Language editions gate breaking changes (`edition = "2025"`), with auto‑migrations in the formatter.

---
Questions to align on next:
- Target priority (native vs WASM first)?
- Effects scope in MVP (`io`, `net`, `fs`, `proc` sufficient?).
- Interop priorities (C only vs C + Python/JS shims early).
