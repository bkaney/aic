## Why

The lexer is the foundation for all parser, formatter, and diagnostic work in v0.1. The current lexer handles core keywords and basic punctuation but is missing operators (`<`, `>`, `<=`, `>=`, `==`, `!=`, `&&`, `||`, `|`, `->`), keywords (`mut`, `break`, `continue`, `shadow`, `type`), and literal forms (hex integers, raw strings, bytes literals) required by `docs/syntax.md`. No downstream parser step can proceed without a complete token set, and no tests exist to verify correctness of even the current implementation.

## What Changes

- Add missing comparison operators: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Add missing logical operators: `&&`, `||`
- Add pipe operator: `|`
- Add thin arrow: `->` (currently `=>` exists as `ARROW`; rename to `FAT_ARROW` and add `THIN_ARROW` for `->`)
- Add missing keywords to `TokKind` and `KEYWORDS`: `mut`, `break`, `continue`, `shadow`, `type`
- Add hex integer literal support (`0xFF`, `0XAB`)
- Add raw string literal support (`r"..."`)
- Add bytes literal support (`b"..."`)
- Implement trivia tracking: store whitespace and comment positions in a side channel for downstream doc-comment association and formatter fidelity
- Add comprehensive lexer unit tests covering all token kinds, edge cases, unterminated strings, invalid escapes, and error tokens
- Add `.aic` example files that exercise the full token surface for golden-test use downstream

## Capabilities

### New Capabilities

- `lexer-tokens`: Complete token kind enumeration covering all MVP keywords, operators, punctuation, and literal forms defined in `docs/syntax.md`
- `lexer-literals`: Lexing of all literal forms — integers (decimal, hex), floats, strings (with escapes), raw strings, bytes literals, booleans, `none`
- `lexer-operators`: Lexing of all operator and punctuation tokens including multi-character sequences (`::`, `=>`, `->`, `<=`, `>=`, `==`, `!=`, `&&`, `||`)
- `lexer-trivia`: Side-channel tracking of whitespace, line comments, block comments, and doc comments with span data for formatter and doc-comment association
- `lexer-tests`: Unit test suite and example `.aic` files validating all token kinds, edge cases, and error handling

### Modified Capabilities

_(none — no existing specs)_

## Impact

- **`aiclang/token.py`**: New `TokKind` variants, updated `KEYWORDS` dict, rename `ARROW` → `FAT_ARROW` + add `THIN_ARROW` (**BREAKING** for current parser references to `TokKind.ARROW`)
- **`aiclang/lexer.py`**: New lexing methods for operators, hex, raw strings, bytes; trivia side channel; refactored operator dispatch
- **`aiclang/parser.py`**: Must update `ARROW` references to `FAT_ARROW` (mechanical rename)
- **`aiclang/formatter.py`**: Must update any `ARROW` references (mechanical rename)
- **New test files**: `tests/test_lexer.py` and example files under `tests/examples/`
- **No external dependencies added**
