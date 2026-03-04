## ADDED Requirements

### Requirement: Top-level panic-mode recovery on unexpected tokens
When the dispatch loop encounters a token that is not a valid item start (`pub`, `struct`, `enum`, `type`, `const`, `use`, `module`, `DOC_COMMENT`, EOF), it SHALL emit an `E0001` diagnostic, then advance past tokens until it reaches `;`, `}`, or EOF, and then resume the dispatch loop.

#### Scenario: Unexpected top-level token triggers recovery
- **WHEN** the dispatch loop encounters an unexpected token (e.g., a bare integer literal) at top level
- **THEN** it emits exactly one `E0001` diagnostic and skips forward to the next `;`, `}`, or EOF

#### Scenario: Recovery resumes parsing after skip
- **WHEN** panic-mode recovery skips over an unexpected token sequence ending at `;`
- **THEN** the dispatch loop resumes and successfully parses subsequent valid declarations

#### Scenario: Recovery on EOF stops the loop
- **WHEN** panic-mode recovery reaches EOF while scanning for a sync token
- **THEN** the dispatch loop exits normally

#### Scenario: Only one diagnostic emitted per recovery event
- **WHEN** multiple unexpected tokens appear in a row before a sync point
- **THEN** the parser emits exactly one `E0001` diagnostic (not one per skipped token)

### Requirement: Declaration-level field recovery in struct body
Within a struct body, when an unexpected token appears in a field position, `_parse_struct_decl()` SHALL emit a single `E0001` diagnostic, skip to the next `;` inside the block, and continue parsing remaining fields.

#### Scenario: Invalid field token skips to next semicolon
- **WHEN** a struct body contains an unexpected token where a field name is expected
- **THEN** the parser emits one `E0001`, skips to the next `;`, and continues parsing subsequent fields

#### Scenario: Valid field after recovery is parsed correctly
- **WHEN** an invalid field is followed by a valid `name: Type;` field
- **THEN** the valid field appears in `StructDecl.fields` after recovery

### Requirement: Declaration-level variant recovery in enum body
Within an enum body, when an unexpected token appears in a variant position, `_parse_enum_decl()` SHALL emit a single `E0001` diagnostic, skip to the next `;`, and continue parsing remaining variants.

#### Scenario: Invalid variant token skips to next semicolon
- **WHEN** an enum body contains an unexpected token where a variant name is expected
- **THEN** the parser emits one `E0001`, skips to the next `;`, and continues parsing subsequent variants

### Requirement: Recovery diagnostic uses E0001 code
All recovery-emitted diagnostics SHALL use error code `E0001` (unexpected token) and SHALL include the span of the first unexpected token encountered.

#### Scenario: Recovery diagnostic carries E0001 code
- **WHEN** panic-mode recovery fires at any level
- **THEN** the emitted diagnostic has code `"E0001"`
