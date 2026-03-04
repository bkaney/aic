## ADDED Requirements

### Requirement: Top-level item dispatch loop
`parse_file()` SHALL replace the `use`-only loop with a general `while not EOF` dispatch loop that routes to the appropriate declaration parser based on the leading token kind (`PUB`, `STRUCT`, `ENUM`, `TYPE`, `CONST`, `USE`, `MODULE`, `DOC_COMMENT`).

#### Scenario: Dispatch routes struct keyword
- **WHEN** the dispatch loop encounters a `STRUCT` token at top level
- **THEN** `_parse_struct_decl()` is called and the resulting `StructDecl` node is appended to `file.items`

#### Scenario: Dispatch routes enum keyword
- **WHEN** the dispatch loop encounters an `ENUM` token at top level
- **THEN** `_parse_enum_decl()` is called and the resulting `EnumDecl` node is appended to `file.items`

#### Scenario: Dispatch routes type keyword
- **WHEN** the dispatch loop encounters a `TYPE` token at top level
- **THEN** `_parse_type_alias()` is called and the resulting `TypeAlias` node is appended to `file.items`

#### Scenario: Dispatch routes const keyword
- **WHEN** the dispatch loop encounters a `CONST` token at top level
- **THEN** `_parse_const_decl()` is called and the resulting `ConstDecl` node is appended to `file.items`

#### Scenario: Dispatch routes use keyword
- **WHEN** the dispatch loop encounters a `USE` token at top level
- **THEN** `_parse_use_decl()` is called and the resulting `UseDecl` node is appended to `file.items`

#### Scenario: Dispatch routes module keyword
- **WHEN** the dispatch loop encounters a `MODULE` token at top level
- **THEN** `_parse_module_decl()` is called and the resulting `ModuleDecl` node is appended to `file.items`

#### Scenario: Dispatch handles pub prefix before dispatch
- **WHEN** the dispatch loop encounters a `PUB` token followed by a declaration keyword
- **THEN** the `vis=True` flag is consumed and passed to the appropriate item parser, and the item is appended to `file.items`

#### Scenario: Dispatch terminates at EOF
- **WHEN** the dispatch loop encounters `EOF`
- **THEN** the loop exits and `parse_file()` returns the completed `FileNode`

#### Scenario: Multiple declarations parsed in sequence
- **WHEN** a source file contains a `struct` followed by an `enum` followed by a `const`
- **THEN** `file.items` contains three nodes in source order: `StructDecl`, `EnumDecl`, `ConstDecl`
