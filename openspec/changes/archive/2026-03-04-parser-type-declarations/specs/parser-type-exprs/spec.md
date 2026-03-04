## ADDED Requirements

### Requirement: IdentType parsing
`_parse_type()` SHALL parse a bare `IDENT` token (not followed by `::`) into an `IdentType` node with `name` set to the identifier text.

#### Scenario: Single identifier becomes IdentType
- **WHEN** `_parse_type()` is called with input `Foo`
- **THEN** it returns an `IdentType` with `name == "Foo"`

### Requirement: PathType parsing
`_parse_type()` SHALL parse an `IDENT` followed by one or more `::` + `IDENT` sequences into a `PathType` node whose `segments` list contains each identifier in order.

#### Scenario: Two-segment path becomes PathType
- **WHEN** `_parse_type()` is called with input `std::io`
- **THEN** it returns a `PathType` with `segments == ["std", "io"]`

#### Scenario: Three-segment path becomes PathType
- **WHEN** `_parse_type()` is called with input `a::b::c`
- **THEN** it returns a `PathType` with `segments == ["a", "b", "c"]`

### Requirement: TupleType parsing
`_parse_type()` SHALL parse a `(` token followed by a comma-separated list of types and a closing `)` into a `TupleType` node whose `elements` list contains the parsed types in order.

#### Scenario: Empty tuple type
- **WHEN** `_parse_type()` is called with input `()`
- **THEN** it returns a `TupleType` with `elements == []`

#### Scenario: Single-element tuple type
- **WHEN** `_parse_type()` is called with input `(i32)`
- **THEN** it returns a `TupleType` with `elements` containing one `IdentType`

#### Scenario: Multi-element tuple type
- **WHEN** `_parse_type()` is called with input `(i32, str, bool)`
- **THEN** it returns a `TupleType` with `elements` containing three `IdentType` nodes in order

### Requirement: ArrayType parsing
`_parse_type()` SHALL parse a `[` token followed by a single type and a closing `]` into an `ArrayType` node whose `element` is the parsed type.

#### Scenario: Array type wraps element type
- **WHEN** `_parse_type()` is called with input `[u8]`
- **THEN** it returns an `ArrayType` whose `element` is an `IdentType` with `name == "u8"`

### Requirement: _parse_type used by all declaration parsers
All declaration parsers (`_parse_struct_decl`, `_parse_enum_decl`, `_parse_type_alias`, `_parse_const_decl`) SHALL call `_parse_type()` for every type-position token, ensuring consistent parsing behavior.

#### Scenario: Struct field uses _parse_type
- **WHEN** a struct field has a path type annotation (`std::io`)
- **THEN** the field's `type_` is a `PathType` with segments `["std", "io"]`

#### Scenario: Enum variant uses _parse_type
- **WHEN** an enum variant payload is `[u8]`
- **THEN** the variant's first field type is an `ArrayType`
