## ADDED Requirements

### Requirement: Decimal and float integer literals
The lexer SHALL emit `TokKind.INT` for decimal integer literals and `TokKind.FLOAT` for float literals. The token's `value` field SHALL contain the parsed numeric value as a Python `int` or `float`.

#### Scenario: Decimal integer
- **WHEN** the lexer scans `42`
- **THEN** it emits `TokKind.INT` with lexeme `"42"` and value `42`

#### Scenario: Float with decimal point
- **WHEN** the lexer scans `1.5`
- **THEN** it emits `TokKind.FLOAT` with lexeme `"1.5"` and value `1.5`

#### Scenario: Float with exponent notation
- **WHEN** the lexer scans `2e5`
- **THEN** it emits `TokKind.FLOAT` with lexeme `"2e5"` and value `200000.0`

### Requirement: Hexadecimal integer literals
The lexer SHALL emit `TokKind.INT` for hexadecimal integer literals prefixed with `0x` or `0X`. The token's `value` field SHALL contain the parsed integer value. The original lexeme SHALL be preserved exactly.

#### Scenario: Lowercase hex prefix
- **WHEN** the lexer scans `0xff`
- **THEN** it emits `TokKind.INT` with lexeme `"0xff"` and value `255`

#### Scenario: Uppercase hex prefix
- **WHEN** the lexer scans `0XAB`
- **THEN** it emits `TokKind.INT` with lexeme `"0XAB"` and value `171`

#### Scenario: Hex digits include A-F and a-f
- **WHEN** the lexer scans `0x1a2B`
- **THEN** it emits `TokKind.INT` with value `6699`

### Requirement: Standard string literals with escape sequences
The lexer SHALL emit `TokKind.STRING` for double-quoted string literals. The token's `value` field SHALL contain the decoded string content (escapes processed). The lexeme SHALL include the surrounding quotes.

#### Scenario: Simple string
- **WHEN** the lexer scans `"hello"`
- **THEN** it emits `TokKind.STRING` with value `"hello"`

#### Scenario: String with escape sequences
- **WHEN** the lexer scans `"a\nb"`
- **THEN** it emits `TokKind.STRING` with value containing a newline between `a` and `b`

### Requirement: Raw string literals
The lexer SHALL emit `TokKind.STRING` for raw string literals prefixed with `r`. Raw strings SHALL NOT process escape sequences; backslashes are literal. The token's `value` field SHALL contain the raw content between the quotes.

#### Scenario: Raw string preserves backslash
- **WHEN** the lexer scans `r"\n"`
- **THEN** it emits `TokKind.STRING` with value `"\\n"` (two characters: backslash + n)

#### Scenario: Raw string `r` alone is an identifier
- **WHEN** the lexer scans `r` not followed by `"`
- **THEN** it emits `TokKind.IDENT` with lexeme `"r"`

### Requirement: Bytes literals
The lexer SHALL emit `TokKind.BYTES` for bytes literals prefixed with `b`. The token's `value` field SHALL contain the raw byte content between the quotes as a Python `bytes` object.

#### Scenario: Simple bytes literal
- **WHEN** the lexer scans `b"abc"`
- **THEN** it emits `TokKind.BYTES` with value `b"abc"`

#### Scenario: Bytes `b` alone is an identifier
- **WHEN** the lexer scans `b` not followed by `"`
- **THEN** it emits `TokKind.IDENT` with lexeme `"b"`

### Requirement: Boolean and none literals
The lexer SHALL emit `TokKind.TRUE`, `TokKind.FALSE`, and `TokKind.NONE` for the literals `true`, `false`, and `none` respectively.

#### Scenario: Boolean true
- **WHEN** the lexer scans `true`
- **THEN** it emits `TokKind.TRUE`

#### Scenario: None keyword
- **WHEN** the lexer scans `none`
- **THEN** it emits `TokKind.NONE`
