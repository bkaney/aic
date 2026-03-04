## 1. Token Kind Updates

- [x] 1.1 Rename `TokKind.ARROW` → `TokKind.FAT_ARROW` in `aiclang/token.py`
- [x] 1.2 Add `TokKind.THIN_ARROW` for `->`
- [x] 1.3 Add missing keyword token kinds: `MUT`, `BREAK`, `CONTINUE`, `SHADOW`, `TYPE`
- [x] 1.4 Add missing operator token kinds: `LT`, `GT`, `LTEQ`, `GTEQ`, `EQEQ`, `NEQ`
- [x] 1.5 Add logical operator token kinds: `ANDAND`, `OROR`
- [x] 1.6 Add `TokKind.PIPE` for `|`
- [x] 1.7 Add trivia token kinds: `TokKind.LINE_COMMENT`, `TokKind.BLOCK_COMMENT`
- [x] 1.8 Add missing keywords to the `KEYWORDS` dict: `mut`, `break`, `continue`, `shadow`, `type`

## 2. Lexer: Operator Dispatch

- [x] 2.1 Add `_peek_next()` helper to look at `src[i+1]` without consuming
- [x] 2.2 Implement `<` / `<=` disambiguation using `_peek_next()`
- [x] 2.3 Implement `>` / `>=` disambiguation
- [x] 2.4 Implement `=` / `==` / `=>` (FAT_ARROW) disambiguation
- [x] 2.5 Implement `!` / `!=` disambiguation
- [x] 2.6 Implement `&` / `&&` disambiguation
- [x] 2.7 Implement `|` / `||` disambiguation
- [x] 2.8 Implement `-` / `->` (THIN_ARROW) disambiguation

## 3. Lexer: Literal Extensions

- [x] 3.1 Extend `_lex_number()` to detect `0x`/`0X` prefix and consume hex digits `[0-9a-fA-F]`
- [x] 3.2 Store hex integer value via `int(lexeme, 16)` and preserve original lexeme
- [x] 3.3 Add `_lex_raw_string()` method: consume `r"..."` with no escape processing; value is raw content
- [x] 3.4 Add `_lex_bytes_string()` method: consume `b"..."` and emit `TokKind.BYTES` with `bytes` value
- [x] 3.5 Update `_lex_ident_or_keyword()` to detect `r` or `b` followed by `"` and dispatch to the appropriate string lexer

## 4. Lexer: Trivia Side Channel

- [x] 4.1 Add `self.trivia: List[Token]` to `Lexer.__init__`
- [x] 4.2 Update `_skip_line_comment()` to emit `TokKind.LINE_COMMENT` into `self.trivia` instead of silently discarding
- [x] 4.3 Update `_skip_block_comment()` to emit `TokKind.BLOCK_COMMENT` into `self.trivia`
- [x] 4.4 Update `_lex_doc_comment()` to emit `TokKind.DOC_COMMENT` into `self.trivia` only (remove from main token list)
- [x] 4.5 Add `lex_with_trivia() -> Tuple[List[Token], List[Token]]` method that runs `lex()` and returns `(self.tokens, self.trivia)`
- [x] 4.6 Verify `lex()` return value is unchanged (trivia list is populated but not included in main token stream)

## 5. Cross-Cutting: Rename ARROW References

- [x] 5.1 Update `aiclang/parser.py`: replace all `TokKind.ARROW` references with `TokKind.FAT_ARROW`
- [x] 5.2 Scan `aiclang/formatter.py` for any `TokKind.ARROW` references and update to `TokKind.FAT_ARROW`
- [x] 5.3 Verify no remaining `TokKind.ARROW` references exist in the codebase (`grep -r "TokKind.ARROW"`)

## 6. Test Suite

- [x] 6.1 Create `tests/` directory and empty `tests/__init__.py`
- [x] 6.2 Create `tests/test_lexer.py` with a `lex(src)` helper that returns the token list
- [x] 6.3 Add parametrized tests for all keywords in `KEYWORDS` dict (assert each lexes to correct `TokKind`)
- [x] 6.4 Add tests for all single-character punctuation tokens
- [x] 6.5 Add disambiguation tests for each multi-character operator pair (`<`/`<=`, `>`/`>=`, `=`/`==`/`=>`, `!`/`!=`, `&`/`&&`, `|`/`||`, `-`/`->`)
- [x] 6.6 Add literal tests: decimal int, hex int (`0xff`, `0XAB`), float, string with escapes, raw string (`r"\n"`), bytes (`b"abc"`), `true`, `false`, `none`
- [x] 6.7 Add literal value assertion tests: verify `token.value` equals expected Python value for each literal kind
- [x] 6.8 Add identifier-vs-keyword edge case tests: `mutate`, `for_each`, `truthy`, `none_value`, `r`, `b` (without following `"`)
- [x] 6.9 Add span accuracy tests: assert `line`, `column`, `length` for tokens at known positions
- [x] 6.10 Add trivia tests: verify `lex_with_trivia()` populates trivia list with line/block/doc comments and keeps main token list clean
- [x] 6.11 Add EOF test: empty string yields exactly one `TokKind.EOF` token

## 7. Example File

- [x] 7.1 Create `tests/examples/` directory
- [x] 7.2 Create `tests/examples/token_surface.aic` with sections for each token group (keywords, operators, literals, punctuation), using inline `//` comments as section labels
- [x] 7.3 Verify `token_surface.aic` lexes with no unknown-character skips (use the trivia/main token lists to confirm full coverage)

## 8. Verification

- [x] 8.1 Run `pytest tests/test_lexer.py` and confirm all tests pass
- [x] 8.2 Confirm `aic fmt` and `aic check` still function correctly on existing `.aic` examples after the `ARROW` rename
