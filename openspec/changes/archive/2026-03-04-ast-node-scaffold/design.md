## Context

`aiclang/ast.py` currently defines four nodes: `Node` (base), `DocComment`, `ModuleDecl`, `UseDecl`, and `File`. All use Python `dataclasses` and share the `Span`-bearing `Node` base. The parser and formatter import directly from this module; the public interface is small and stable.

This design covers the structural decisions for expanding `ast.py` to the full v0.1 node set (~35 classes) without breaking existing callers.

## Goals / Non-Goals

**Goals:**
- Define every AST node needed for v0.1 parse surface (declarations, functions, traits, impls, expressions, patterns, control flow).
- Maintain consistency with the existing `dataclass`-on-`Node` pattern.
- Keep nodes data-only — no methods, no semantic resolution, no type information.
- Provide stable, importable names so parser steps 3–7 and formatter steps 9–11 can proceed in parallel.

**Non-Goals:**
- Visitor pattern, tree traversal helpers, or pretty-printing on nodes (formatter owns output).
- Semantic fields (resolved types, trait bounds, scope info) — deferred to v0.2+.
- Macros, operator overloading, semicolon elision.
- Changes to `Node`, `Span`, or `Token` — those are lexer-layer concerns.

## Decisions

### 1. Keep the `@dataclass` / `Node` pattern — no union types or tagged enums

**Decision**: Every node is a `@dataclass` subclass of `Node`. Expression and statement variants are distinct classes, not a single ADT.

**Rationale**: Consistent with existing code; Python's structural typing lets callers use `isinstance` checks. A `Union[LiteralExpr, BinaryExpr, ...]` type alias provides type-checker precision without runtime cost.

**Alternative considered**: A single `Expr` tagged-union enum. Rejected — would require rewriting the existing four nodes and adds indirection without benefit at this stage.

---

### 2. Use `Union` type aliases for abstract categories

**Decision**: Define module-level aliases:
```python
Expr = Union[LiteralExpr, IdentExpr, PathExpr, BinaryExpr, ...]
Pattern = Union[WildcardPat, IdentPat, LiteralPat, ...]
Stmt = Union[LetStmt, ExprStmt, ReturnStmt]
Item = Union[StructDecl, EnumDecl, TypeAlias, ConstDecl, FnItem, TraitDecl, ImplBlock, UseDecl, ModuleDecl]
Type_ = Union[IdentType, PathType, TupleType, ArrayType]
```

**Rationale**: Gives mypy/pyright precise narrowing while keeping the node classes flat. Avoids a separate abstract base per category.

---

### 3. `doc: Optional[DocComment] = None` on all item-level nodes

**Decision**: Add an optional `doc` field to every node that can carry a doc comment: `StructDecl`, `EnumDecl`, `TypeAlias`, `ConstDecl`, `FnItem`, `TraitDecl`, `ImplBlock`, `StructField`, `EnumVariant`.

**Rationale**: Doc comment attachment is part of the lossless AST requirement. The parser attaches the preceding `DocComment` node when it constructs an item. Expressions and patterns do not carry docs.

---

### 4. `File.items` replaces the scattered `uses` / `docs` fields

**Decision**: Replace `File.uses: List[UseDecl]` and `File.docs: List[DocComment]` with a single `File.items: List[Item]` that preserves source order. Keep `File.module: Optional[ModuleDecl]`.

**Rationale**: The formatter needs source order across all top-level declarations. A flat item list is simpler to traverse than parallel lists. Existing parser code produces `File` directly — updating it is a one-site change.

**Migration**: The existing parser sets `file.uses` and `file.docs`; those fields are removed. The parser is in the same repo and the only caller — no external API break.

---

### 5. Literal values stored as raw strings, not parsed Python values

**Decision**: `LiteralExpr.value: str` holds the raw source text (e.g., `"0xFF"`, `"3.14"`, `r"raw\nstring"`). A `kind: LiteralKind` enum (`INT`, `FLOAT`, `STRING`, `BYTES`, `RAW_STRING`, `BOOL`, `NONE`) distinguishes types.

**Rationale**: The formatter must reproduce source faithfully without re-serializing values. Semantic evaluation is not a v0.1 concern. Avoids loss of precision (e.g., integer bases, escape sequences).

---

### 6. `BlockExpr` used for both expression-blocks and statement-blocks

**Decision**: A single `BlockExpr(stmts: List[Stmt], expr: Optional[Expr])` node covers function bodies, `if` branches, `loop` bodies, and standalone block expressions. The trailing `expr` (no semicolon) represents a block's final value expression.

**Rationale**: Avoids duplicate `Block` vs `BlockExpr` types. The formatter treats both identically; the parser context determines whether a trailing expression is legal.

---

### 7. Operator represented as a string token text, not a separate enum

**Decision**: `BinaryExpr.op: str` and `UnaryExpr.op: str` store the operator source text (`"+"`, `"&&"`, `"!="`, etc.) rather than a dedicated `Op` enum.

**Rationale**: No semantic analysis at this stage; the formatter only needs to print the op back out. An `Op` enum adds churn when adding operators — deferred to when the type checker needs it.

## Risks / Trade-offs

- **`File` field removal is a breaking change to existing parser code** → Mitigated: only one call site (`parser.py`), updated in the same PR as `ast.py`.
- **`Union` aliases grow large** → Acceptable at this scale (~12 expression types); if the list grows unwieldy, a sealed base class can be introduced in v0.2.
- **`op: str` loses static exhaustiveness checking** → Accepted trade-off for simplicity; the parser validates ops at construction time.
- **No visitor/traversal helpers** → Formatter and future passes must use `isinstance` chains; add helpers if pattern proves painful in practice.
