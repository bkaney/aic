## ADDED Requirements

### Requirement: Parse type alias declaration
`_parse_type_alias()` SHALL parse `pub? type Name = Type;` and return a `TypeAlias` node with `name`, `type_`, `vis`, and `doc` populated from the source.

#### Scenario: Simple type alias parses to TypeAlias
- **WHEN** the parser encounters `type MyInt = i32;`
- **THEN** it returns a `TypeAlias` with `name == "MyInt"` and `type_` as an `IdentType` with `name == "i32"`

#### Scenario: Public type alias sets vis flag
- **WHEN** the parser encounters `pub type MyInt = i32;`
- **THEN** the resulting `TypeAlias` has `vis == True`

#### Scenario: Type alias with path type
- **WHEN** the parser encounters `type Writer = std::io::Write;`
- **THEN** the resulting `TypeAlias` has `type_` as a `PathType` with segments `["std", "io", "Write"]`

#### Scenario: Type alias with tuple type
- **WHEN** the parser encounters `type Pair = (i32, str);`
- **THEN** the resulting `TypeAlias` has `type_` as a `TupleType` with two elements

#### Scenario: Missing equals sign emits E0001
- **WHEN** `type Foo` is not followed by `=`
- **THEN** the parser emits an `E0001` diagnostic

#### Scenario: Missing semicolon after type alias emits E0002
- **WHEN** a type alias declaration is not followed by `;`
- **THEN** the parser emits an `E0002` diagnostic

### Requirement: Parse const declaration
`_parse_const_decl()` SHALL parse `pub? const NAME: Type = Expr;` and return a `ConstDecl` node with `name`, `type_`, `value`, `vis`, and `doc` populated from the source.

#### Scenario: Integer literal const parses to ConstDecl
- **WHEN** the parser encounters `const MAX: i32 = 100;`
- **THEN** it returns a `ConstDecl` with `name == "MAX"`, `type_` as `IdentType("i32")`, and `value` as a `LiteralExpr` with kind `INT`

#### Scenario: String literal const parses correctly
- **WHEN** the parser encounters `const GREETING: str = "hello";`
- **THEN** the resulting `ConstDecl` has `value` as a `LiteralExpr` with kind `STRING`

#### Scenario: Boolean literal const parses correctly
- **WHEN** the parser encounters `const FLAG: bool = true;`
- **THEN** the resulting `ConstDecl` has `value` as a `LiteralExpr` with kind `BOOL`

#### Scenario: Identifier initializer parses to IdentExpr
- **WHEN** the parser encounters `const VALUE: i32 = OTHER_CONST;`
- **THEN** the resulting `ConstDecl` has `value` as an `IdentExpr`

#### Scenario: Public const sets vis flag
- **WHEN** the parser encounters `pub const MAX: i32 = 255;`
- **THEN** the resulting `ConstDecl` has `vis == True`

#### Scenario: Non-literal non-ident initializer emits E0001 and uses sentinel
- **WHEN** the parser encounters a complex expression as the const initializer
- **THEN** it emits an `E0001` diagnostic and sets `value` to a sentinel `LiteralExpr(kind=INT, value="0")`

#### Scenario: Missing colon after const name emits E0001
- **WHEN** `const NAME` is not followed by `:`
- **THEN** the parser emits an `E0001` diagnostic

#### Scenario: Missing equals sign after const type emits E0001
- **WHEN** `const NAME: Type` is not followed by `=`
- **THEN** the parser emits an `E0001` diagnostic

#### Scenario: Missing semicolon after const declaration emits E0002
- **WHEN** a const declaration is not followed by `;`
- **THEN** the parser emits an `E0002` diagnostic
