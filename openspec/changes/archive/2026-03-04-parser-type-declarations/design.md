## Context

`aiclang/parser.py` currently exposes a `Parser` class with two public nonterminals (`_parse_module_decl`, `_parse_use_decl`) and a `parse_file()` driver that handles only `module` + `use` sequences. The helper infrastructure (`_peek`, `_advance`, `_maybe`, `_expect`, `_error`, `_error_with_fix`, `_span_here`) is healthy and reusable. All new work extends `parser.py` in-place; no new files are created.

The AST node layer (`aiclang/ast.py`) is now complete with `StructDecl`, `EnumDecl`, `TypeAlias`, `ConstDecl`, and all type-position nodes. The lexer produces the full keyword set (`struct`, `enum`, `type`, `const`, `pub`) and operator set needed here.

## Goals / Non-Goals

**Goals:**
- Replace the `use`-only top-level loop with a general item dispatch loop.
- Parse `struct`, `enum`, `type`, and `const` declarations into the correct AST nodes.
- Parse all type-position forms: `IdentType`, `PathType`, `TupleType`, `ArrayType`.
- Attach leading `DocComment` tokens to the `doc` field of the following item.
- Emit `E0001`/`E0002` diagnostics on missing tokens within declarations.
- Synchronize on `;` and `}` after a declaration-level error.

**Non-Goals:**
- Parsing function bodies, expressions (beyond literal/ident initializers for `const`), traits, or impls — those are Steps 4–7.
- Type bound resolution, generics on type declarations — deferred to later steps.
- `E0003`–`E0013` error codes beyond what's naturally encountered here.
- Formatter integration — that is Step 9.

## Decisions

### 1. General dispatch loop with a pending-doc-comment slot

**Decision**: `parse_file()` is restructured as a `while not EOF` loop. Each iteration:
1. Consume a `DOC_COMMENT` token into a `pending_doc` slot if present.
2. Dispatch on the next token kind (`PUB`, `STRUCT`, `ENUM`, `TYPE`, `CONST`, `USE`, `MODULE`) to the appropriate parser.
3. Pass `pending_doc` into the item parser so it can attach it to the node's `doc` field.
4. Clear `pending_doc` after each item.

**Rationale**: A flat dispatch loop is simpler than a recursive-descent item list. The pending-doc slot is stateless per iteration and avoids a separate attachment pass.

**Alternative considered**: A separate post-parse doc-attachment pass scanning `file.items`. Rejected — requires two iterations over items and complicates span tracking.

---

### 2. `_parse_type()` as a shared helper

**Decision**: Add `_parse_type() -> Type_` that handles the following forms based on lookahead:
- `(` → `TupleType` (comma-separated list, closing `)`)
- `[` → `ArrayType` (single type, closing `]`)
- `IDENT` followed by `::` → `PathType` (consume all `IDENT :: ...` segments)
- `IDENT` alone → `IdentType`

All declaration parsers (`_parse_struct_decl`, `_parse_enum_decl`, etc.) call `_parse_type()` for field/variant/alias type positions.

**Rationale**: Centralizing type parsing eliminates duplication and ensures consistent behavior across all declaration forms.

---

### 3. Field/variant terminators use `;` inside braces

**Decision**: Struct fields and enum variants are terminated by `;` (not `,`), matching the AIC language syntax. The parser consumes `;` after each field/variant and emits `E0002` with a fix-it if missing.

**Rationale**: Consistent with `docs/syntax.md` — AIC uses `;` as the statement/field terminator throughout, not `,` as in Rust.

---

### 4. `const` initializer: literal or identifier only

**Decision**: `_parse_const_decl()` accepts only a single `LiteralExpr` (int, float, string, bool, none) or `IdentExpr` as the initializer, producing the appropriate `Expr` node. Anything else emits `E0001` and uses a sentinel `LiteralExpr(kind=INT, value="0")`.

**Rationale**: Full expression parsing (Pratt parser) is Step 5. Restricting `const` initializers to atoms lets Step 3 be self-contained without forward-depending on Step 5's infrastructure.

---

### 5. Panic-mode recovery: skip to next `}` or `;` at top level

**Decision**: When dispatch encounters an unexpected token in the item loop (not `pub`, `struct`, `enum`, `type`, `const`, `use`, `module`, doc comment, or EOF), emit `E0001` and advance until the next `;` or `}` or EOF, then resume the loop.

Within a declaration (e.g., inside a struct's `{}`), unrecognized tokens cause a field-level skip to the next `;` inside that block.

**Rationale**: Sync tokens `;` and `}` are the v0.1 strategy defined in the implementation plan. Keeping recovery shallow (top-level loop) avoids complex nested recovery state at this step.

---

### 6. `pub` visibility: a prefix consumed before dispatch

**Decision**: When the dispatch loop sees `PUB`, it sets a `vis = True` flag and advances, then dispatches on the *next* token. The `vis` flag (and `pending_doc`) are passed into each item parser. Item parsers that don't support `pub` (e.g., `use`) emit a warning but still parse the item.

**Alternative considered**: Each item parser independently checks for a leading `PUB`. Rejected — duplicates the lookahead logic and makes the dispatch loop harder to follow.

## Risks / Trade-offs

- **`const` initializer restriction** → Callers that try to parse complex const exprs will get a sentinel node. Acceptable for v0.1; Step 5 will replace `_parse_const_decl`'s initializer logic with the Pratt parser.
- **No generic parameters on declarations** → `struct Foo<T> {}` will fail to parse. The dispatch loop will emit `E0001` on `<`. Acceptable: generics on declarations are a Step 4 concern.
- **`_parse_type()` does not handle nested generics** → `Vec<i32>` cannot be parsed yet. Type positions only accept plain idents, paths, tuples, and arrays. Acceptable for this step.
- **Growing `parser.py`** → The file will be ~350 lines after this step. Still manageable; splitting into sub-modules is a future refactor if needed.
