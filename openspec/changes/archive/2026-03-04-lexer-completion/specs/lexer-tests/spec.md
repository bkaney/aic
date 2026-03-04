## ADDED Requirements

### Requirement: pytest unit test suite for the lexer
A file `tests/test_lexer.py` SHALL exist and SHALL be executable with `pytest` from the project root with no additional configuration. All tests in the suite SHALL pass after the lexer-completion step is applied.

#### Scenario: pytest discovers and runs all lexer tests
- **WHEN** `pytest tests/test_lexer.py` is run from the project root
- **THEN** all tests are collected and pass with exit code 0

### Requirement: Tests cover all token kinds
The test suite SHALL contain at least one test assertion for every `TokKind` variant that the lexer can emit, verifying the correct kind, lexeme, and (where applicable) value.

#### Scenario: Each keyword has a test
- **WHEN** the test suite is inspected
- **THEN** every keyword in `KEYWORDS` has at least one test asserting it lexes to the correct `TokKind`

#### Scenario: Each operator token kind has a test
- **WHEN** the test suite is inspected  
- **THEN** every operator `TokKind` (`LT`, `GT`, `LTEQ`, `GTEQ`, `EQEQ`, `NEQ`, `ANDAND`, `OROR`, `PIPE`, `THIN_ARROW`, `FAT_ARROW`, etc.) has at least one test

### Requirement: Tests cover edge cases and error-adjacent inputs
The test suite SHALL include tests for inputs that are near-misses or edge cases for disambiguation (e.g., `-` vs `->`, `&` vs `&&`, `=` vs `==` vs `=>`).

#### Scenario: Disambiguation tests for multi-char operators
- **WHEN** each multi-character operator is tested alongside its single-character prefix alone
- **THEN** both cases emit the correct distinct token kinds

#### Scenario: Identifier vs keyword disambiguation
- **WHEN** inputs like `mutate`, `for_each`, `truthy`, `none_value` are lexed
- **THEN** they produce `TokKind.IDENT`, not keyword tokens

### Requirement: Tests cover literal value extraction
The test suite SHALL assert the parsed `value` field for all literal token types: integers (decimal and hex), floats, strings, raw strings, and bytes.

#### Scenario: Literal value assertions
- **WHEN** a literal (e.g., `0xff`, `1.5`, `"hello"`, `r"\n"`, `b"abc"`) is lexed
- **THEN** the resulting token's `value` field equals the expected Python value

### Requirement: Token surface example file
A file `tests/examples/token_surface.aic` SHALL exist containing AIC source that exercises every token kind at least once. This file SHALL be parseable by the tokenizer (no lexer errors) and is intended for use as a downstream golden test input.

#### Scenario: token_surface.aic lexes without skipping unknown characters
- **WHEN** `token_surface.aic` is lexed
- **THEN** the resulting token list contains no unknown-character skips (all characters are accounted for by a recognized token kind)

#### Scenario: token_surface.aic is self-documenting
- **WHEN** the file is read
- **THEN** it contains inline comments labeling each token group (keywords, literals, operators, etc.)

### Requirement: Span accuracy for all token types
The test suite SHALL assert that `Span.line`, `Span.column`, and `Span.length` are accurate for representative tokens across all kinds.

#### Scenario: Span reflects source position
- **WHEN** a token appears on line 3, column 5 of the source
- **THEN** its span has `line=3` and `column=5`

#### Scenario: Multi-character token span length is correct
- **WHEN** the token `<=` is emitted
- **THEN** its span has `length=2`
