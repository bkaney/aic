## ADDED Requirements

### Requirement: Trivia side channel via lex_with_trivia
The lexer SHALL provide a `lex_with_trivia()` method that returns a tuple `(tokens, trivia)` where `tokens` is the standard token list (trivia-free, identical to what `lex()` returns) and `trivia` is a list of `Token` objects for comments and doc comments with accurate spans.

#### Scenario: lex_with_trivia returns both lists
- **WHEN** `lex_with_trivia()` is called on source containing both code and comments
- **THEN** it returns a 2-tuple where the first element is the code token list and the second is the trivia token list

#### Scenario: Standard lex() is unaffected
- **WHEN** `lex()` is called on the same source
- **THEN** it returns exactly the same token list as the first element of `lex_with_trivia()`

### Requirement: Line comments captured in trivia
The lexer SHALL capture `//` line comments (excluding `///` doc comments) in the trivia list with kind `TokKind.LINE_COMMENT`. The token's `value` SHALL contain the comment text excluding the `//` prefix. The span SHALL cover the full comment including the `//` prefix.

#### Scenario: Line comment is trivia, not a main token
- **WHEN** the source contains `let x = 1; // foo`
- **THEN** the main token list does NOT contain any comment token
- **THEN** the trivia list contains one `TokKind.LINE_COMMENT` token with value `" foo"`

### Requirement: Block comments captured in trivia
The lexer SHALL capture `/* ... */` block comments in the trivia list with kind `TokKind.BLOCK_COMMENT`. Nested block comments SHALL be handled correctly (each `/*` increments depth, each `*/` decrements).

#### Scenario: Block comment in trivia list
- **WHEN** the source contains `/* a block */`
- **THEN** the trivia list contains one `TokKind.BLOCK_COMMENT` token
- **THEN** the main token list does not contain it

#### Scenario: Nested block comments do not terminate early
- **WHEN** the source contains `/* outer /* inner */ still outer */`
- **THEN** the trivia list contains one `TokKind.BLOCK_COMMENT` covering the full span

### Requirement: Doc comments captured in trivia with DOC_COMMENT kind
The lexer SHALL capture `///` doc comments in the trivia list with kind `TokKind.DOC_COMMENT`. The `value` field SHALL contain the trimmed comment text (leading space stripped). Doc comments SHALL NOT appear in the main token list.

#### Scenario: Doc comment in trivia, not main tokens
- **WHEN** the source contains `/// A doc comment\nfn foo() {}`
- **THEN** the main token list does NOT contain `TokKind.DOC_COMMENT`
- **THEN** the trivia list contains one `TokKind.DOC_COMMENT` with value `"A doc comment"`

#### Scenario: Doc comment span covers triple-slash prefix
- **WHEN** the source contains `/// text`
- **THEN** the trivia `DOC_COMMENT` token's span starts at the `///` column

### Requirement: Whitespace is NOT stored in trivia
The lexer SHALL NOT add whitespace tokens to the trivia list. Whitespace is silently consumed. Only comment and doc-comment tokens appear in trivia.

#### Scenario: Spaces and newlines produce no trivia tokens
- **WHEN** the source contains only spaces, tabs, and newlines
- **THEN** `lex_with_trivia()` returns an empty trivia list and a token list containing only `TokKind.EOF`
