## ADDED Requirements

### Requirement: Parse enum declaration
`_parse_enum_decl()` SHALL parse `pub? enum Name { Variant...; ... }` and return an `EnumDecl` node with `name`, `variants`, `vis`, and `doc` populated from the source.

#### Scenario: Minimal enum parses to EnumDecl
- **WHEN** the parser encounters `enum Color {}`
- **THEN** it returns an `EnumDecl` with `name == "Color"`, `variants == []`, and `vis == False`

#### Scenario: Public enum sets vis flag
- **WHEN** the parser encounters `pub enum Color {}`
- **THEN** the resulting `EnumDecl` has `vis == True`

#### Scenario: Enum with variants populates variant list
- **WHEN** the parser encounters `enum Shape { Circle; Square; }`
- **THEN** the resulting `EnumDecl` has `variants` containing two `EnumVariant` nodes named `"Circle"` and `"Square"`

### Requirement: Parse unit enum variant
`_parse_enum_decl()` SHALL parse a bare identifier followed by `;` as a unit variant — an `EnumVariant` with `name` set and `fields == []`.

#### Scenario: Unit variant has empty fields list
- **WHEN** an enum body contains `None;`
- **THEN** the corresponding `EnumVariant` has `name == "None"` and `fields == []`

### Requirement: Parse tuple enum variant
`_parse_enum_decl()` SHALL parse `Variant(Type, ...)` followed by `;` as a tuple variant — an `EnumVariant` with `name` set and `fields` containing the parsed types.

#### Scenario: Single-payload tuple variant
- **WHEN** an enum body contains `Some(i32);`
- **THEN** the corresponding `EnumVariant` has `name == "Some"` and `fields` containing one `IdentType` with `name == "i32"`

#### Scenario: Multi-payload tuple variant
- **WHEN** an enum body contains `Pair(i32, str);`
- **THEN** the corresponding `EnumVariant` has `fields` containing two `IdentType` nodes in order

#### Scenario: Variant with path type payload
- **WHEN** an enum body contains `Wrapped(std::io::Error);`
- **THEN** the corresponding `EnumVariant` has `fields[0]` as a `PathType` with segments `["std", "io", "Error"]`

### Requirement: Enum variant terminated by semicolon
`_parse_enum_decl()` SHALL consume `;` after each variant and emit `E0002` with a fix-it if the semicolon is absent.

#### Scenario: Missing semicolon after variant emits E0002
- **WHEN** an enum variant is not followed by `;`
- **THEN** the parser emits an `E0002` diagnostic and continues parsing

### Requirement: Enum body enclosed in braces
`_parse_enum_decl()` SHALL expect `{` after the enum name and `}` closing the body, emitting `E0001` if either brace is absent.

#### Scenario: Missing opening brace emits E0001
- **WHEN** `enum Foo` is not followed by `{`
- **THEN** the parser emits an `E0001` diagnostic
