## 1. Preparation

- [x] 1.1 Add imports in `parser.py` for all new AST node types: `StructDecl`, `StructField`, `EnumDecl`, `EnumVariant`, `TypeAlias`, `ConstDecl`, `IdentType`, `PathType`, `TupleType`, `ArrayType`, `LiteralExpr`, `IdentExpr`, `LiteralKind`
- [x] 1.2 Create `tests/test_parser.py` with test module scaffold and necessary imports

## 2. Type Expression Parser

- [x] 2.1 Implement `_parse_type() -> Type_` method with lookahead dispatch on `(`, `[`, and `IDENT`
- [x] 2.2 Implement `IdentType` branch: consume `IDENT` and return `IdentType(name=...)`
- [x] 2.3 Implement `PathType` branch: consume `IDENT` + one or more `:: IDENT` sequences and return `PathType(segments=[...])`
- [x] 2.4 Implement `TupleType` branch: consume `(`, comma-separated type list, `)` and return `TupleType(elements=[...])`
- [x] 2.5 Implement `ArrayType` branch: consume `[`, single type, `]` and return `ArrayType(element=...)`
- [x] 2.6 Add tests for all four type-expression forms (IdentType, PathType, TupleType, ArrayType)

## 3. Dispatch Loop

- [x] 3.1 Rewrite `parse_file()` with a `while not EOF` dispatch loop replacing the `use`-only loop
- [x] 3.2 Add `pending_doc: Optional[DocComment]` slot initialized to `None` each iteration
- [x] 3.3 Handle `DOC_COMMENT` token: consume into `pending_doc` and continue to next iteration
- [x] 3.4 Handle `PUB` prefix: set `vis = True`, advance, then dispatch on the next token
- [x] 3.5 Dispatch `STRUCT` → `_parse_struct_decl(vis, pending_doc)`; append result to `file.items`
- [x] 3.6 Dispatch `ENUM` → `_parse_enum_decl(vis, pending_doc)`; append result to `file.items`
- [x] 3.7 Dispatch `TYPE` → `_parse_type_alias(vis, pending_doc)`; append result to `file.items`
- [x] 3.8 Dispatch `CONST` → `_parse_const_decl(vis, pending_doc)`; append result to `file.items`
- [x] 3.9 Retain `USE` → `_parse_use_decl(pending_doc)` and `MODULE` → `_parse_module_decl()` dispatch arms
- [x] 3.10 Add tests for multi-declaration files parsed in source order

## 4. Struct Declaration Parser

- [x] 4.1 Implement `_parse_struct_decl(vis, doc) -> StructDecl` method
- [x] 4.2 Consume `STRUCT`, expect `IDENT` for name (emit `E0001` if missing)
- [x] 4.3 Expect `{` opening brace (emit `E0001` if missing)
- [x] 4.4 Parse field loop: consume `IDENT`, `:`, call `_parse_type()`, expect `;` (emit `E0002` if `;` missing)
- [x] 4.5 Expect `}` closing brace (emit `E0001` if missing)
- [x] 4.6 Return `StructDecl(name=..., fields=[...], vis=vis, doc=doc, span=...)`
- [x] 4.7 Add tests for: empty struct, struct with fields, pub struct, struct with path/tuple/array field types, missing semicolons

## 5. Enum Declaration Parser

- [x] 5.1 Implement `_parse_enum_decl(vis, doc) -> EnumDecl` method
- [x] 5.2 Consume `ENUM`, expect `IDENT` for name (emit `E0001` if missing)
- [x] 5.3 Expect `{` opening brace (emit `E0001` if missing)
- [x] 5.4 Parse variant loop: consume `IDENT` for variant name
- [x] 5.5 If `(` follows variant name, parse comma-separated payload types until `)` (tuple variant)
- [x] 5.6 Expect `;` after each variant (emit `E0002` if missing)
- [x] 5.7 Expect `}` closing brace (emit `E0001` if missing)
- [x] 5.8 Return `EnumDecl(name=..., variants=[...], vis=vis, doc=doc, span=...)`
- [x] 5.9 Add tests for: empty enum, unit variants, tuple variants, pub enum, multi-payload variants

## 6. Type Alias and Const Parsers

- [x] 6.1 Implement `_parse_type_alias(vis, doc) -> TypeAlias` method
- [x] 6.2 Consume `TYPE`, expect `IDENT` for name, expect `=` (emit `E0001` if missing), call `_parse_type()`, expect `;` (emit `E0002` if missing)
- [x] 6.3 Return `TypeAlias(name=..., type_=..., vis=vis, doc=doc, span=...)`
- [x] 6.4 Implement `_parse_const_decl(vis, doc) -> ConstDecl` method
- [x] 6.5 Consume `CONST`, expect `IDENT` for name, expect `:` (emit `E0001` if missing), call `_parse_type()`, expect `=` (emit `E0001` if missing)
- [x] 6.6 Parse initializer: accept `LiteralExpr` (int/float/string/bool/none) or `IdentExpr`; emit `E0001` and use sentinel `LiteralExpr(kind=INT, value="0")` for anything else
- [x] 6.7 Expect `;` after const initializer (emit `E0002` if missing)
- [x] 6.8 Return `ConstDecl(name=..., type_=..., value=..., vis=vis, doc=doc, span=...)`
- [x] 6.9 Add tests for: type alias with ident/path/tuple types, const with int/string/bool/ident initializers, pub type alias, pub const, sentinel on complex initializer

## 7. Doc Comment Attachment

- [x] 7.1 Pass `pending_doc` parameter into `_parse_struct_decl`, `_parse_enum_decl`, `_parse_type_alias`, `_parse_const_decl`, and `_parse_use_decl`
- [x] 7.2 Assign `pending_doc` to the `doc` field of each returned node
- [x] 7.3 Clear `pending_doc` (set to `None`) after each item is appended in the dispatch loop
- [x] 7.4 Add tests for: doc comment attached to struct, enum, type alias, const, and use; declaration without doc comment has `doc == None`; only last of consecutive doc comments attached

## 8. Error Recovery

- [x] 8.1 Add top-level recovery arm in dispatch loop: on unknown token, emit `E0001`, advance to next `;`, `}`, or EOF, then resume loop
- [x] 8.2 Add field-level recovery in `_parse_struct_decl`: on unexpected field token, emit `E0001`, skip to next `;` within the block
- [x] 8.3 Add variant-level recovery in `_parse_enum_decl`: on unexpected variant token, emit `E0001`, skip to next `;` within the block
- [x] 8.4 Verify all recovery diagnostics use code `"E0001"` and carry the span of the first unexpected token
- [x] 8.5 Add tests for: top-level unknown token recovery resumes parsing, struct field recovery, enum variant recovery, single diagnostic per recovery event

## 9. Final Verification

- [x] 9.1 Run `task check` (lint + full test suite) and fix any failures
- [x] 9.2 Confirm all new test cases in `tests/test_parser.py` pass
