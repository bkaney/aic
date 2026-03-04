## Why

The parser currently handles only `module` and `use` declarations, covering about 5% of the v0.1 language surface. Extending it to parse `struct`, `enum`, `type`, and `const` declarations — with visibility, doc comment attachment, and basic error recovery — unblocks the formatter (Step 9) and is the foundational parse-loop expansion required by all subsequent parser steps.

## What Changes

- Extend `parse_file()` with a general top-level item dispatch loop replacing the `use`-only loop.
- Add a reusable type-expression parser (`_parse_type()`) used by all declaration parsers.
- Add `_parse_struct_decl()`, `_parse_enum_decl()`, `_parse_type_alias()`, `_parse_const_decl()` nonterminals.
- Add `pub` visibility prefix handling shared by all declaration parsers.
- Attach leading doc comments to the item immediately following them.
- Add panic-mode error recovery on `;` and `}` for declaration-level parse errors.
- Emit `E0001`/`E0002` diagnostics for missing tokens in declaration context.
- Add parser unit tests covering all new declaration forms.

## Capabilities

### New Capabilities
- `parser-decl-dispatch`: Top-level item dispatch loop in `parse_file()` that routes tokens to the appropriate declaration parser based on lookahead (`pub`, `struct`, `enum`, `type`, `const`, `use`, `module`, doc comment).
- `parser-type-exprs`: Reusable `_parse_type()` method covering single-segment `IdentType`, qualified `PathType` (`::`-separated), `TupleType` (parenthesized comma list), and `ArrayType` (`[T]`).
- `parser-struct-decl`: Parses `pub? struct Name { field: Type; ... }` into `StructDecl` AST nodes, including field lists with semicolons and optional trailing doc comments on fields.
- `parser-enum-decl`: Parses `pub? enum Name { Variant(Type, ...); ... }` into `EnumDecl` with `EnumVariant` nodes, supporting unit and tuple variants separated by semicolons.
- `parser-type-alias`: Parses `pub? type Name = Type;` into `TypeAlias` and `pub? const NAME: Type = expr;` into `ConstDecl` with simple literal/identifier initializers.
- `parser-doc-attachment`: Tracks pending `DocComment` tokens and attaches them to the `doc` field of the immediately following item node (struct, enum, type alias, const, use).
- `parser-recovery-decl`: Panic-mode synchronization at declaration level: on unexpected tokens, skip forward to the next `;` or `}` sync point and emit a single `E0001` diagnostic before resuming.

### Modified Capabilities

*(none — no existing specs cover parser declarations)*

## Impact

- **`aiclang/parser.py`**: Primary change target. Imports expand to include all new AST node types from `ast.py`. The `parse_file()` method and helper infrastructure are extended; no existing helper methods are removed.
- **`aiclang/ast.py`**: Read-only dependency. `StructDecl`, `EnumDecl`, `TypeAlias`, `ConstDecl`, `StructField`, `EnumVariant`, `IdentType`, `PathType`, `TupleType`, `ArrayType`, `LiteralExpr`, `IdentExpr`, `LiteralKind` imported and constructed.
- **`tests/test_lexer.py`**: Unaffected (lexer unchanged).
- **`tests/test_ast.py`**: Unaffected (AST node construction unchanged).
- **`tests/test_parser.py`**: New test file covering all new declaration forms, doc attachment, and error recovery cases.
- **No breaking changes** to existing `ParseResult`, `Parser.__init__`, or `parse_file()` public return type.
