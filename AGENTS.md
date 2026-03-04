# AGENTS.md — Instructions for AI Agents

This file describes how to work in the `aic` repository. Read it before making changes.

## Project Overview

AIC is an AI-first programming language implemented in Python (v0.1 reference interpreter).
The Python package is `aiclang/`. The CLI entry point is `bin/aic`.

## Environment Setup

The project uses a Python venv at `.venv/`. **Always activate it before running any commands:**

```bash
source .venv/bin/activate
```

Python version: 3.14+ (managed via asdf, pinned in `.tool-versions` if present).

## Task Runner

Tasks are defined in `pyproject.toml` under `[tool.taskipy.tasks]` and run via `task`.

| Command      | What it does                        |
|-------------|-------------------------------------|
| `task test`  | Run the test suite (`pytest tests/`) |
| `task lint`  | Syntax check + ruff lint             |
| `task fix`   | Lint and auto-fix safe issues        |
| `task check` | Full check: lint then test           |

**Always run `task check` before considering any change complete.**

## Project Layout

```
aiclang/        Python package (lexer, parser, AST, formatter, diagnostics, CLI)
tests/          pytest test suite
  examples/     .aic example files used as test inputs
scripts/        Developer scripts (lint.py, etc.)
bin/            CLI entry points (aic)
docs/           Specs, roadmap, comparisons
openspec/       Structured change artifacts (proposal → design → specs → tasks)
```

## Code Conventions

- Python style is enforced by `ruff` (config in `pyproject.toml`).
- `E702` (semicolons on one line) is suppressed — the lexer dispatch table uses this style intentionally.
- Type hints are required for all public functions.
- Tests live in `tests/` and are discovered automatically by pytest.

## OpenSpec Workflow

Features are developed using the OpenSpec artifact workflow:

1. `proposal.md` — problem + motivation
2. `design.md` — approach and key decisions
3. `specs/` — one spec file per logical area
4. `tasks.md` — checklist of implementation tasks

Active changes live in `openspec/changes/<name>/`. Completed changes are archived to `openspec/changes/archive/`.

## Key References

- [docs/syntax.md](docs/syntax.md) — language syntax
- [docs/vision.md](docs/vision.md) — design principles
- [docs/roadmap/v0.1-plan.md](docs/roadmap/v0.1-plan.md) — current implementation plan
