# AIC — An AI-First Programming Language

AIC is a programming language designed to maximize first-try correctness when authored by AI language models, while remaining pleasant and predictable for human developers. It features deterministic semantics, regular syntax, a canonical formatter enforced by the compiler, and actionable diagnostics.

## Status

🚧 **Early Development** — Currently implementing v0.1 (Parser + AST + Formatter)

The language specification and tooling are actively being developed. See the [roadmap](docs/roadmap.md) for planned milestones.

## Quick Start

```bash
# Format AIC source files
./bin/aic fmt [files or directories]

# Check syntax and formatting (no codegen)
./bin/aic check [files or directories]

# Check formatting without writing
./bin/aic fmt --check [files or directories]
```

## Documentation

### Core Documentation

- **[Vision](docs/vision.md)** — Goals, design principles, and LLM-optimization strategy
- **[Syntax](docs/syntax.md)** — Language syntax, semantics, and formatting rules
- **[Roadmap](docs/roadmap.md)** — Milestones and acceptance criteria
- **[Tooling](docs/tooling.md)** — Compiler, formatter, LSP, and development tools

### Detailed Planning

- **[v0.1 Plan](docs/roadmap/v0.1-plan.md)** — Parser, AST, and formatter implementation details

### Language Comparisons

AIC draws inspiration from several modern languages while optimizing for AI code generation. See how AIC compares to other languages:

- [AIC vs C](docs/compare/aic-vs-c.md)
- [AIC vs C#](docs/compare/aic-vs-csharp.md)
- [AIC vs Go](docs/compare/aic-vs-go.md)
- [AIC vs Java](docs/compare/aic-vs-java.md)
- [AIC vs Python](docs/compare/aic-vs-python.md)
- [AIC vs Rust](docs/compare/aic-vs-rust.md)
- [AIC vs TypeScript](docs/compare/aic-vs-typescript.md)

## Key Features

- **Deterministic Semantics** — Fully specified evaluation order, no hidden mutations or implicit conversions
- **Regular Syntax** — One obvious way to express each construct; no dialects
- **Canonical Formatting** — Enforced by the compiler; misformatted code fails `check`
- **Actionable Diagnostics** — One error → one fix-it; stable, machine-readable output
- **Typed Holes** — Use `_` in expressions and patterns for iterative development
- **Explicit Effects** — Track I/O, networking, and other effects in the type system
- **Token Economy** — Short, familiar keywords to reduce token count and improve AI generation

## Design Principles

1. **Explicit over implicit** — Imports, visibility, effects, and error propagation are spelled out
2. **Local reasoning** — Types are explicit or inferred locally; avoid whole-program inference
3. **Small orthogonal core** — Structs, enums, traits, generics, async, pattern matching
4. **Fast feedback** — Sub-second checking on small projects
5. **Partial programs** — Typed holes and `todo()`/`unimplemented()` allow iterative construction

## Project Structure

```
aiclang/         Python implementation of the AIC compiler
  cli.py         Command-line interface
  lexer.py       Lexical analyzer
  parser.py      Parser
  ast.py         Abstract syntax tree
  formatter.py   Canonical formatter
  diagnostics.py Error reporting
  token.py       Token definitions
bin/
  aic            CLI entry point
docs/            Language documentation
```

## Requirements

- Python 3.7+

## Development

The current implementation is a Python-based prototype focusing on the parser, AST, and formatter. Future milestones will add:

- Type checker with effects system (v0.2)
- WebAssembly codegen (v0.3)
- Standard library (v0.4)
- Async runtime (v0.5)
- LSP and development tools (v0.7)

See the [roadmap](docs/roadmap.md) for the complete development plan.

## License

*To be determined*

## Contributing

As this is an early-stage project, contribution guidelines will be established as the language stabilizes. Feel free to explore the documentation and provide feedback on the design.
