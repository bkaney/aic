## Why

The current `aiclang/ast.py` defines only four nodes (`File`, `ModuleDecl`, `UseDecl`, `DocComment`), covering roughly 5% of the v0.1 language surface. The parser, formatter, and all downstream steps are blocked until a complete, stable set of AST nodes exists — this scaffold unblocks parallel work on parser steps 3–7 and formatter steps 9–11.

## What Changes

- Expand `aiclang/ast.py` with ~30 new dataclass nodes covering all v0.1 constructs.
- All nodes extend the existing `Node` base (carries `Span`); no changes to `Node` itself.
- `File` gains `items: List[Item]` to hold top-level declarations alongside existing fields.
- Nodes are data-only (no semantic fields such as resolved types or trait bindings).
- Doc comment attachment field (`doc: Optional[DocComment]`) added to all item-level nodes.

## Capabilities

### New Capabilities
- `ast-declarations`: Node definitions for `StructDecl`, `EnumDecl`, `TypeAlias`, `ConstDecl`, `LetStmt`, and supporting types (`StructField`, `EnumVariant`).
- `ast-functions`: Node definitions for `FnItem`, `GenericParam`, `Param`, `WhereClause`, `EffectsClause`, and return-type representation.
- `ast-traits-impls`: Node definitions for `TraitDecl`, `ImplBlock`, and method signature nodes.
- `ast-expressions`: Node definitions for all expression kinds: `LiteralExpr`, `IdentExpr`, `PathExpr`, `BinaryExpr`, `UnaryExpr`, `CallExpr`, `MemberExpr`, `IndexExpr`, `AwaitExpr`, `BlockExpr`, `ReturnExpr`, `TryExpr`.
- `ast-patterns`: Node definitions for `WildcardPat`, `IdentPat`, `LiteralPat`, `TuplePat`, `StructPat`, `EnumPat`.
- `ast-control-flow`: Node definitions for `IfExpr`, `LoopStmt`, `ForStmt`, `MatchExpr`, `MatchArm`.

### Modified Capabilities

*(none — no existing specs cover AST nodes)*

## Impact

- **`aiclang/ast.py`**: Primary change target; all new nodes added here.
- **`aiclang/parser.py`**: Imports from `ast.py` — existing refs (`ModuleDecl`, `UseDecl`, `File`) remain unchanged; new nodes referenced in future parser steps.
- **`aiclang/formatter.py`**: Imports from `ast.py` — existing refs unchanged; new nodes used in future formatter steps.
- **`tests/`**: New `tests/test_ast.py` covering node construction, span propagation, and doc comment attachment for each node group.
- **No breaking changes** to existing public API; only additions.
