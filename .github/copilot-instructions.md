# GitHub Copilot Instructions

## Project

AIC is an AI-first programming language. The v0.1 reference implementation is in Python (`aiclang/` package).

## Environment

- Python venv at `.venv/` — activate with `source .venv/bin/activate`
- Task runner: `taskipy` — run `task check` (lint + tests) before finishing any change

## Available Tasks

```bash
task test   # pytest tests/ -q
task lint   # syntax check + ruff
task fix    # lint --fix
task check  # lint then test
```

## Conventions

- Ruff enforces style; config in `pyproject.toml`
- `E702` (semicolons) is suppressed — intentional in `lexer.py` dispatch table
- All public functions require type hints
- Tests in `tests/`, one file per module (`test_lexer.py`, etc.)
- OpenSpec workflow: change artifacts in `openspec/changes/<name>/`

## Key Files

- `aiclang/token.py` — `TokKind` enum, `KEYWORDS`, `Span`, `Token`
- `aiclang/lexer.py` — single-pass scanner, `lex()` / `lex_with_trivia()`
- `aiclang/parser.py` — parser (minimal, expanding)
- `aiclang/ast.py` — AST node definitions
- `aiclang/formatter.py` — canonical formatter
- `aiclang/diagnostics.py` — structured diagnostic output
- `docs/syntax.md` — authoritative language syntax reference
