## 1. Foundation and Type Aliases

- [x] 1.1 Add `LiteralKind` enum to `ast.py` with members `INT`, `FLOAT`, `STRING`, `BYTES`, `RAW_STRING`, `BOOL`, `NONE`
- [x] 1.2 Add `IdentType` and `PathType` dataclasses extending `Node`
- [x] 1.3 Add `TupleType` and `ArrayType` dataclasses extending `Node`
- [x] 1.4 Define `Type_ = Union[IdentType, PathType, TupleType, ArrayType]` at module level

## 2. Declaration Nodes

- [x] 2.1 Add `StructField` dataclass (`name: str`, `type_: Type_`, `doc: Optional[DocComment] = None`)
- [x] 2.2 Add `StructDecl` dataclass (`name`, `fields`, `doc`, `vis`)
- [x] 2.3 Add `EnumVariant` dataclass (`name`, `fields: List[Type_]`, `doc`)
- [x] 2.4 Add `EnumDecl` dataclass (`name`, `variants`, `doc`, `vis`)
- [x] 2.5 Add `TypeAlias` dataclass (`name`, `type_`, `doc`, `vis`)
- [x] 2.6 Add `ConstDecl` dataclass (`name`, `type_`, `value: Expr`, `doc`, `vis`)
- [x] 2.7 Add `LetStmt` dataclass (`name`, `mut: bool`, `type_: Optional[Type_]`, `value: Optional[Expr]`)

## 3. Function Nodes

- [x] 3.1 Add `GenericParam` dataclass (`name: str`)
- [x] 3.2 Add `Param` dataclass (`name`, `type_`, `self_: bool = False`)
- [x] 3.3 Add `WhereConstraint` dataclass (`param: str`, `bound: Type_`)
- [x] 3.4 Add `WhereClause` dataclass (`constraints: List[WhereConstraint]`)
- [x] 3.5 Add `EffectsClause` dataclass (`effects: List[str]`)
- [x] 3.6 Add `ExprStmt` dataclass (`expr: Expr`)
- [x] 3.7 Add `ReturnStmt` dataclass (`value: Optional[Expr] = None`)
- [x] 3.8 Add `BlockExpr` dataclass (`stmts: List[Stmt]`, `expr: Optional[Expr] = None`)
- [x] 3.9 Add `FnItem` dataclass with all fields (`name`, `generics`, `params`, `ret`, `where_`, `effects`, `body`, `doc`, `vis`, `async_`)
- [x] 3.10 Define `Stmt = Union[LetStmt, ExprStmt, ReturnStmt, LoopStmt, ForStmt]` at module level

## 4. Expression Nodes

- [x] 4.1 Add `LiteralExpr` dataclass (`kind: LiteralKind`, `value: str`)
- [x] 4.2 Add `IdentExpr` dataclass (`name: str`)
- [x] 4.3 Add `PathExpr` dataclass (`segments: List[str]`)
- [x] 4.4 Add `BinaryExpr` dataclass (`op: str`, `left: Expr`, `right: Expr`)
- [x] 4.5 Add `UnaryExpr` dataclass (`op: str`, `operand: Expr`)
- [x] 4.6 Add `CallExpr` dataclass (`callee: Expr`, `args: List[Expr]`)
- [x] 4.7 Add `MemberExpr` dataclass (`object: Expr`, `member: str`)
- [x] 4.8 Add `IndexExpr` dataclass (`object: Expr`, `index: Expr`)
- [x] 4.9 Add `AwaitExpr` dataclass (`expr: Expr`)
- [x] 4.10 Add `TryExpr` dataclass (`expr: Expr`)
- [x] 4.11 Add `ReturnExpr` dataclass (`value: Optional[Expr] = None`)
- [x] 4.12 Define `Expr = Union[LiteralExpr, IdentExpr, PathExpr, BinaryExpr, UnaryExpr, CallExpr, MemberExpr, IndexExpr, AwaitExpr, BlockExpr, ReturnExpr, TryExpr, IfExpr]` at module level (after `IfExpr` is defined)

## 5. Pattern Nodes

- [x] 5.1 Add `WildcardPat` dataclass (no additional fields)
- [x] 5.2 Add `IdentPat` dataclass (`name: str`, `mut: bool = False`)
- [x] 5.3 Add `LiteralPat` dataclass (`lit: LiteralExpr`)
- [x] 5.4 Add `TuplePat` dataclass (`elements: List[Pattern]`)
- [x] 5.5 Add `StructPatField` dataclass (`name: str`, `pattern: Pattern`)
- [x] 5.6 Add `StructPat` dataclass (`name: str`, `fields: List[StructPatField]`)
- [x] 5.7 Add `EnumPat` dataclass (`name: str`, `elements: List[Pattern]`)
- [x] 5.8 Define `Pattern = Union[WildcardPat, IdentPat, LiteralPat, TuplePat, StructPat, EnumPat]` at module level

## 6. Control Flow Nodes

- [x] 6.1 Add `IfExpr` dataclass (`condition: Expr`, `then_: BlockExpr`, `else_: Optional[Expr] = None`)
- [x] 6.2 Add `LoopStmt` dataclass (`body: BlockExpr`)
- [x] 6.3 Add `ForStmt` dataclass (`name: str`, `iter: Expr`, `body: BlockExpr`)
- [x] 6.4 Add `MatchArm` dataclass (`patterns: List[Pattern]`, `body: Expr`)
- [x] 6.5 Add `MatchExpr` dataclass (`subject: Expr`, `arms: List[MatchArm]`)

## 7. Trait and Impl Nodes

- [x] 7.1 Add `TraitDecl` dataclass (`name`, `methods: List[FnItem]`, `doc`, `vis`)
- [x] 7.2 Add `ImplBlock` dataclass (`trait_: Optional[str]`, `type_: Type_`, `methods: List[FnItem]`, `doc`)
- [x] 7.3 Define `Item = Union[StructDecl, EnumDecl, TypeAlias, ConstDecl, FnItem, TraitDecl, ImplBlock, UseDecl, ModuleDecl]` at module level

## 8. Update File Node

- [x] 8.1 Replace `File.uses: List[UseDecl]` and `File.docs: List[DocComment]` with `File.items: List[Item]`
- [x] 8.2 Update `parser.py` to populate `File.items` instead of the removed fields
- [x] 8.3 Update `formatter.py` to iterate `file.items` instead of `file.uses` / `file.docs`

## 9. Tests

- [x] 9.1 Create `tests/test_ast.py`
- [x] 9.2 Add construction tests for all declaration nodes (StructDecl, EnumDecl, TypeAlias, ConstDecl, LetStmt)
- [x] 9.3 Add construction tests for all function nodes (FnItem defaults, GenericParam, Param, WhereClause, EffectsClause, BlockExpr)
- [x] 9.4 Add construction tests for all expression nodes (LiteralExpr raw value, BinaryExpr, CallExpr, etc.)
- [x] 9.5 Add construction tests for all pattern nodes
- [x] 9.6 Add construction tests for all control flow nodes (IfExpr branches, MatchArm OR pattern)
- [x] 9.7 Add construction tests for TraitDecl, ImplBlock, and updated File.items
- [x] 9.8 Verify all union aliases (`Expr`, `Stmt`, `Pattern`, `Item`, `Type_`) are importable without error

## 10. Quality Gate

- [x] 10.1 Run `task check` (lint + tests) and fix any errors
