# AIC Roadmap (Draft)

This roadmap sequences MVP milestones, acceptance criteria, and LLM‑focused benchmarks.

## Milestones

1. Parser + AST + Formatter (v0.1)
- Deliver an unambiguous grammar; parse modules, types, functions, traits, impls, match, loops.
- Canonical formatter enforced by `aic check`.
- Acceptance: can parse/format the examples in `docs/syntax.md`.
- Token economy pass: verify compact formatting and short keyword set; record baseline token metrics on samples.
 - Detailed plan: see `docs/roadmap/v0.1-plan.md`.

2. Type Checker + Effects (v0.2)
- Name resolution, local type inference, trait method resolution, `where` constraints.
- Effects declaration and checking; simple propagation.
- Acceptance: `aic check` validates typed holes and emits actionable diagnostics.

3. Codegen: WASM (v0.3)
- Lower monomorphized IR to `wasm32-wasi`; runtime shims for async executor and ARC.
- Acceptance: run CLI sample and HTTP client sample under WASI.

4. Minimal Stdlib (v0.4)
- `option`, `result`, `collections`, `fmt`, `time`, `io`, `json`.
- Acceptance: all examples in `docs/vision.md` compile and run.

5. Concurrency + Async Runtime (v0.5)
- Tasks, channels, timers, `select`; structured concurrency.
- Acceptance: concurrent worker benchmark passes; graceful shutdown demo.

6. FFI: C ABI + Host Bindings (v0.6)
- `extern "C"` blocks; call into C; expose simple C ABI from AIC.
- Acceptance: FFI sample compiles and runs both directions.

7. Language Server + Fix‑its (v0.7)
- Completion, hover, go‑to, rename, code actions; typed hole hints.
- Acceptance: fix‑it application resolves at least 60% of common errors in sample tasks.

8. Package Management (v0.8)
- `project.lock`, local path + git dependencies; basic registry optional.
- Acceptance: reproducible builds across machines.

9. Stabilization + Docs (v0.9)
- Freeze syntax; refine diagnostics; author book‑style docs.
- Acceptance: green on all benchmarks; no breaking changes remaining for 1.0.
 - Tokenization audit: confirm improvements reduce tokens without harming readability or success rate.

10. 1.0 Release
- Semver stability; LTS branch; edition file in `project.toml`.

## Benchmarks (LLM‑Focused)
- First‑try success: percent of generated solutions compiling on first attempt across canonical tasks (CLI, HTTP service, JSON transform, concurrency worker).
- Edit distance to green: mean number of compile/fix cycles to pass tests.
- Diagnostic utility: fraction of errors yielding a single, correct fix‑it.
- Token budget: mean tokens per valid solution for mid‑tier models.
- Build latency: time for `aic check` and `aic run` on small apps (<1s target).

## Risks and Mitigations
- Grammar drift → enforce formatter+check; add golden syntax tests.
- Type system complexity → keep features minimal; prefer library patterns.
- Runtime bloat → thin async runtime; ARC tuned; optional features behind flags.
- Interop needs → start with C + WASM; stage higher‑level bindings later.

## Open Questions
- Which targets first: `native`, `wasm32`, or both?
- Scope of effects in MVP (is `proc` needed early?).
- How soon to introduce a registry vs. rely on git/path deps?

## Next Steps
- Confirm target priority and effects scope.
- Start parser/formatter prototype aligned with `docs/syntax.md`.
- Draft `project.toml` schema validation.
