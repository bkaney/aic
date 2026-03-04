## ADDED Requirements

### Requirement: Comparison operators
The lexer SHALL emit distinct token kinds for all comparison operators: `TokKind.LT` (`<`), `TokKind.GT` (`>`), `TokKind.LTEQ` (`<=`), `TokKind.GTEQ` (`>=`), `TokKind.EQEQ` (`==`), `TokKind.NEQ` (`!=`).

#### Scenario: Less-than alone
- **WHEN** the lexer scans `<` not followed by `=`
- **THEN** it emits `TokKind.LT` with lexeme `"<"`

#### Scenario: Less-than-or-equal
- **WHEN** the lexer scans `<=`
- **THEN** it emits `TokKind.LTEQ` with lexeme `"<="`

#### Scenario: Greater-than alone
- **WHEN** the lexer scans `>` not followed by `=`
- **THEN** it emits `TokKind.GT` with lexeme `">"`

#### Scenario: Greater-than-or-equal
- **WHEN** the lexer scans `>=`
- **THEN** it emits `TokKind.GTEQ` with lexeme `">="`

#### Scenario: Double equals
- **WHEN** the lexer scans `==`
- **THEN** it emits `TokKind.EQEQ` with lexeme `"=="`

#### Scenario: Not-equal
- **WHEN** the lexer scans `!=`
- **THEN** it emits `TokKind.NEQ` with lexeme `"!="`

#### Scenario: Bang alone is not NEQ
- **WHEN** the lexer scans `!` not followed by `=`
- **THEN** it emits `TokKind.BANG` with lexeme `"!"`

### Requirement: Logical operators
The lexer SHALL emit `TokKind.ANDAND` for `&&` and `TokKind.OROR` for `||`.

#### Scenario: Double ampersand
- **WHEN** the lexer scans `&&`
- **THEN** it emits `TokKind.ANDAND` with lexeme `"&&"`

#### Scenario: Single ampersand is not logical and
- **WHEN** the lexer scans `&` not followed by `&`
- **THEN** it emits `TokKind.AMP` with lexeme `"&"`

#### Scenario: Double pipe
- **WHEN** the lexer scans `||`
- **THEN** it emits `TokKind.OROR` with lexeme `"||"`

#### Scenario: Single pipe is not logical or
- **WHEN** the lexer scans `|` not followed by `|`
- **THEN** it emits `TokKind.PIPE` with lexeme `"|"`

### Requirement: Pipe operator
The lexer SHALL emit `TokKind.PIPE` for a single `|` character not part of a `||` sequence.

#### Scenario: Pipe in match arm
- **WHEN** the lexer scans `A | B`
- **THEN** it emits `TokKind.IDENT("A")`, `TokKind.PIPE`, `TokKind.IDENT("B")`

### Requirement: All single-character punctuation tokens
The lexer SHALL emit correct token kinds for all single-character punctuation: `{` `}` `(` `)` `[` `]` `;` `:` `,` `.` `=` `?` `&` `*` `+` `-` `/` `%` `!`.

#### Scenario: Each punctuation character emits the correct kind
- **WHEN** the lexer scans each punctuation character individually (not part of a multi-char sequence)
- **THEN** it emits the corresponding `TokKind` with the single-character lexeme

### Requirement: Multi-character operator disambiguation is greedy
The lexer SHALL use maximal-munch: it SHALL always consume the longest matching operator sequence.

#### Scenario: `::` is emitted as COLONCOLON not two COLONs
- **WHEN** the lexer scans `::`
- **THEN** it emits one `TokKind.COLONCOLON` token, not two `TokKind.COLON` tokens

#### Scenario: `->` is emitted as THIN_ARROW not MINUS then GT
- **WHEN** the lexer scans `->`
- **THEN** it emits one `TokKind.THIN_ARROW` token
