## Context

The lexer in `aiclang/lexer.py` and `aiclang/token.py` currently handles ~60% of the required token surface. The existing architecture — a single-pass character scanner with a `_peek`/`_advance` model — is sound and should be extended rather than replaced. The parser (`aiclang/parser.py`) has one reference to `TokKind.ARROW` (used where `=>` was intended as a fat arrow). No tests exist. All downstream steps (AST scaffold, parser, formatter) are blocked until the token set is complete and verified.

## Goals / Non-Goals

**Goals:**
- Complete the `TokKind` enum and `KEYWORDS` dict to cover the full `docs/syntax.md` surface
- Extend the lexer's single-pass scanner with operators, hex literals, raw strings, bytes literals
- Correctly disambiguate multi-character sequences (`->` vs `-`, `<=` vs `<`, `==` vs `=`, `&&`, `||`, `::`)
- Add a trivia side channel (separate list) for whitespace, line comments, block comments, and doc comments with spans
- Rename `ARROW` → `FAT_ARROW` for `=>` and introduce `THIN_ARROW` for `->`
- Add a pytest-based unit test suite covering all token kinds, edge cases, and error paths
- Add example `.aic` source files that exercise the full token surface

**Non-Goals:**
- No semantic analysis of tokens (keyword context, reserved word conflicts)
- No full `ERROR` token recovery scheme — unknown chars are skipped with a future TODO; panic-mode recovery belongs in Step 8
- No Unicode identifier support beyond ASCII (deferring to post-MVP)
- No column-accurate span repair for multi-line strings (deferred)

## Decisions

### 1. Rename `ARROW` → `FAT_ARROW`; add `THIN_ARROW`

**Decision**: Rename the existing `ARROW` kind (currently emitted for `=>`) to `FAT_ARROW`. Add `THIN_ARROW` for `->`.

**Rationale**: The two arrows have completely different syntactic roles — `=>` is a match arm separator, `->` is a return type separator. Conflating them in a single `ARROW` kind would force the parser to inspect the lexeme string rather than the kind, weakening the token abstraction. Renaming now, while the parser is minimal (one reference), is trivially cheap.

**Alternatives considered**: Keep `ARROW` for `->` and rename `=>` to `FAT_ARROW`. Rejected — `->` is the "primary" arrow in most languages and would conventionally hold the shorter name, but AIC's parser is fresh so either mapping works; `FAT_ARROW`/`THIN_ARROW` is self-documenting.

---

### 2. Multi-character operator dispatch via double-peek

**Decision**: Extend the existing `_peek`/`_advance` character loop with a `_peek_next()` helper that looks at `src[i+1]` without consuming. For each leading character that starts a multi-char sequence (`<`, `>`, `=`, `!`, `&`, `|`, `-`), consume the first char then conditionally consume the second.

**Rationale**: The current codebase already uses this pattern for `::`/`:` and `=>`/`=`. Extending it uniformly keeps the scanner simple, avoids a state machine or regex engine, and stays O(1) per token. The full multi-char set is small and bounded.

**Alternatives considered**: Regex-based tokenizer (e.g., `re.Scanner`). Rejected — harder to attach precise spans, harder to extend with custom literal forms.

---

### 3. Trivia side channel as a parallel list

**Decision**: The `Lexer` maintains a second list `self.trivia: List[Token]` populated with whitespace, line-comment, block-comment, and doc-comment tokens. The main `self.tokens` list remains trivia-free (matches current behavior). Callers that need trivia (future formatter, doc-comment attacher) receive both lists from a new `lex_with_trivia() -> Tuple[List[Token], List[Token]]` method. The existing `lex()` method remains unchanged for compatibility.

**Rationale**: The parser never needs trivia; feeding it a clean token stream simplifies look-ahead logic. The formatter critically needs trivia for comment preservation. Separating the lists at lex time is cheaper than filtering at parse/format time.

**Alternatives considered**: Interleave trivia tokens in the main list with a `is_trivia` flag (Roslyn/rust-analyzer style). Rejected for v0.1 — lossless CST is the right long-term model but adds parser complexity before the parser even exists. Defer to v0.2.

---

### 4. `r"..."` and `b"..."` literal disambiguation

**Decision**: In the top-level `_scan` loop, when the current character is `r` or `b`, peek at the next character. If it is `"`, consume the prefix character and dispatch immediately to `_lex_raw_string()` or `_lex_bytes_string()`. Otherwise, fall through to `_lex_ident_or_keyword()` as normal.

**Rationale**: `r` and `b` are legal identifiers in AIC. The literal prefix is context-determined by the immediately following `"`. Peeking ahead in the main scan loop before entering identifier scanning avoids any backtracking and handles all cases with a single lookahead.

**Edge cases**: `r = 5;` → `IDENT("r")`. `r"..."` → `STRING` with raw flag. `b"..."` → `BYTES`.

---

### 5. Hex integer literals

**Decision**: In `_lex_number`, after consuming `0`, check for `x` or `X`. If found, consume hex digits `[0-9a-fA-F]` until a non-hex char. Emit `INT` with integer `value` (Python `int(lexeme, 16)`). Preserve the original lexeme (e.g., `"0xFF"`) for formatter fidelity.

**Rationale**: Minimal extension to existing `_lex_number`. Python's `int(s, 16)` handles the conversion trivially.

**Error case**: `0x` with no following hex digits → emit `INT` with value `0` and a diagnostic (E0004). Deferred to Step 8 full error recovery; for now emit a best-effort token.

---

### 6. Test structure with pytest

**Decision**: Create `tests/test_lexer.py` using `pytest`. Each test function covers a logical group: keywords, operators, literals, trivia, edge cases. Parameterized tests (`@pytest.mark.parametrize`) used for operator and keyword tables. Create `tests/examples/token_surface.aic` as a single file exercising every token kind for downstream golden-test use.

**Rationale**: pytest is the standard Python test framework, requires no configuration for simple cases, and supports parametrize cleanly. Keeping examples as `.aic` files makes them reusable as golden inputs for the formatter and parser steps.

---

### 7. Unknown character handling

**Decision**: Retain the current behavior of silently skipping unknown characters. Add a `# TODO(lexer): emit E0001 unknown char` comment at the skip site as a marker for Step 8.

**Rationale**: The priority of this step is completing the valid token set. Error token design (E0001) is formally scoped to Step 8 (Parser: Error Recovery and Diagnostics).

## Risks / Trade-offs

- **`FAT_ARROW` rename breaks parser** → The parser currently references `TokKind.ARROW` in one place. The rename must be applied atomically in the same commit; failing to update it will cause an `AttributeError` at parse time. Mitigated by updating `parser.py` and `formatter.py` in the same task.
- **Trivia span accuracy** → Doc comment spans in the current code are approximate (column calculation is off-by-one in some cases). The trivia side channel will surface this. Mitigated by adding span-specific test assertions; correctness can be tightened incrementally.
- **`b"..."` / `r"..."` interaction with future `b""` type annotations** → If AIC ever introduces a `b` type alias, the disambiguation rule would conflict. Accepted as low risk; post-MVP grammar can resolve with a keyword if needed.
- **No fuzzing in this step** → Fuzzing is scoped to Step 13 (Golden Tests and Acceptance). The unit tests cover known edge cases; unknown inputs may surface panics. Mitigated by the unknown-char skip fallback and EOF guards in all inner loops.

## Open Questions

- Should `shadow` be a full keyword (reserved everywhere) or a contextual keyword (only valid before `let`)? For v0.1 lexing, treating it as a full keyword is simplest; the parser can loosen this later.
- Should the trivia list include whitespace tokens, or only comments? Whitespace trivia bloats the list significantly. For v0.1, include only comments and doc comments; whitespace is reconstructed by the formatter from indentation rules.
