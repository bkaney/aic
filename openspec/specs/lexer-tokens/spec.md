## ADDED Requirements

### Requirement: Complete keyword token set
The lexer SHALL recognize all reserved keywords defined in `docs/syntax.md` as distinct `TokKind` variants: `module`, `use`, `pub`, `as`, `let`, `const`, `mut`, `fn`, `async`, `await`, `return`, `struct`, `enum`, `type`, `trait`, `impl`, `where`, `effects`, `match`, `if`, `else`, `loop`, `for`, `in`, `break`, `continue`, `extern`, `true`, `false`, `none`, `shadow`.

#### Scenario: Reserved keyword is emitted as its kind
- **WHEN** the lexer scans a reserved keyword (e.g., `mut`, `break`, `shadow`, `type`)
- **THEN** it emits a token with the corresponding `TokKind` variant, not `TokKind.IDENT`

#### Scenario: Keyword prefix is an identifier
- **WHEN** the lexer scans a word that begins with a keyword but continues with alphanumeric chars (e.g., `mutate`, `typecheck`)
- **THEN** it emits `TokKind.IDENT` with the full lexeme

### Requirement: Distinct arrow token kinds
The lexer SHALL emit `TokKind.FAT_ARROW` for `=>` and `TokKind.THIN_ARROW` for `->`. The former `TokKind.ARROW` kind SHALL NOT exist.

#### Scenario: Fat arrow emitted for match arm separator
- **WHEN** the lexer scans `=>`
- **THEN** it emits a token with kind `TokKind.FAT_ARROW` and lexeme `"=>"`

#### Scenario: Thin arrow emitted for return type separator
- **WHEN** the lexer scans `->`
- **THEN** it emits a token with kind `TokKind.THIN_ARROW` and lexeme `"->"`

#### Scenario: Equals sign alone is not an arrow
- **WHEN** the lexer scans `=` not followed by `>`
- **THEN** it emits `TokKind.EQ` with lexeme `"="`

### Requirement: EOF token terminates every token stream
The lexer SHALL append a `TokKind.EOF` token as the final element of the token list for every input, including empty input.

#### Scenario: Empty input yields only EOF
- **WHEN** the lexer scans an empty string
- **THEN** the token list has exactly one element with kind `TokKind.EOF`
