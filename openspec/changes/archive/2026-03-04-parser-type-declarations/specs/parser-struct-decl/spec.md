## ADDED Requirements

### Requirement: Parse struct declaration
`_parse_struct_decl()` SHALL parse `pub? struct Name { field: Type; ... }` and return a `StructDecl` node with `name`, `fields`, `vis`, and `doc` populated from the source.

#### Scenario: Minimal struct parses to StructDecl
- **WHEN** the parser encounters `struct Point {}`
- **THEN** it returns a `StructDecl` with `name == "Point"`, `fields == []`, and `vis == False`

#### Scenario: Public struct sets vis flag
- **WHEN** the parser encounters `pub struct Point {}`
- **THEN** the resulting `StructDecl` has `vis == True`

#### Scenario: Struct with fields populates field list
- **WHEN** the parser encounters `struct Point { x: i32; y: i32; }`
- **THEN** the resulting `StructDecl` has `fields` containing two `StructField` nodes with names `"x"` and `"y"`

### Requirement: Parse struct fields
`_parse_struct_decl()` SHALL parse each field as `name: Type;`, constructing a `StructField` node with `name` and `type_` set, and consuming the terminating `;`.

#### Scenario: Field name and type are captured
- **WHEN** a struct body contains `count: u32;`
- **THEN** the corresponding `StructField` has `name == "count"` and `type_` is an `IdentType` with `name == "u32"`

#### Scenario: Field with path type
- **WHEN** a struct body contains `handler: std::io::Writer;`
- **THEN** the corresponding `StructField` has `type_` as a `PathType` with segments `["std", "io", "Writer"]`

#### Scenario: Field with tuple type
- **WHEN** a struct body contains `coords: (f64, f64);`
- **THEN** the corresponding `StructField` has `type_` as a `TupleType` with two `IdentType` elements

#### Scenario: Missing semicolons after field emits E0002
- **WHEN** a struct field is missing the terminating `;`
- **THEN** the parser emits an `E0002` diagnostic and continues parsing the next field

### Requirement: Struct body enclosed in braces
`_parse_struct_decl()` SHALL expect `{` after the struct name and `}` closing the body, emitting `E0001` if either brace is absent.

#### Scenario: Missing opening brace emits E0001
- **WHEN** `struct Foo` is not followed by `{`
- **THEN** the parser emits an `E0001` diagnostic

#### Scenario: Missing closing brace emits E0001
- **WHEN** a struct body is not closed with `}`
- **THEN** the parser emits an `E0001` diagnostic
