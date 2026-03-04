"""Tests for aiclang.lexer — covers all token kinds, disambiguation, literals,
trivia, spans, and edge cases."""
from __future__ import annotations

import pytest
from aiclang.lexer import Lexer, LexerConfig
from aiclang.token import KEYWORDS, TokKind, Token


# ── Helpers ──────────────────────────────────────────────────────────────────

def lex(src: str) -> list[Token]:
    """Return the token list (trivia-free) for the given source string."""
    return Lexer(src, LexerConfig(file="<test>")).lex()


def lex_with_trivia(src: str) -> tuple[list[Token], list[Token]]:
    """Return (tokens, trivia) for the given source string."""
    return Lexer(src, LexerConfig(file="<test>")).lex_with_trivia()


def kinds(src: str) -> list[TokKind]:
    """Return just the token kinds (excluding EOF) for the given source."""
    return [t.kind for t in lex(src) if t.kind != TokKind.EOF]


# ── EOF ───────────────────────────────────────────────────────────────────────

def test_empty_source_yields_only_eof():
    tokens = lex("")
    assert len(tokens) == 1
    assert tokens[0].kind == TokKind.EOF


def test_whitespace_only_yields_eof():
    tokens = lex("   \t\n  ")
    assert len(tokens) == 1
    assert tokens[0].kind == TokKind.EOF


# ── Keywords ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("kw,expected_kind", list(KEYWORDS.items()))
def test_keyword(kw, expected_kind):
    toks = lex(kw)
    assert toks[0].kind == expected_kind
    assert toks[0].lexeme == kw


@pytest.mark.parametrize("word", [
    "mutate", "for_each", "truthy", "none_value", "returns", "breaking",
    "continues", "shadow_var", "typeof", "extern_fn",
])
def test_keyword_prefix_is_ident(word):
    toks = lex(word)
    assert toks[0].kind == TokKind.IDENT
    assert toks[0].lexeme == word


# ── Single-character punctuation ─────────────────────────────────────────────

@pytest.mark.parametrize("char,expected_kind", [
    ('{', TokKind.LBRACE),
    ('}', TokKind.RBRACE),
    ('(', TokKind.LPAREN),
    (')', TokKind.RPAREN),
    ('[', TokKind.LBRACK),
    (']', TokKind.RBRACK),
    (';', TokKind.SEMI),
    (',', TokKind.COMMA),
    ('.', TokKind.DOT),
    ('?', TokKind.QUESTION),
    ('*', TokKind.STAR),
    ('+', TokKind.PLUS),
    ('/', TokKind.SLASH),
    ('%', TokKind.PERCENT),
])
def test_single_char_punctuation(char, expected_kind):
    toks = lex(char)
    assert toks[0].kind == expected_kind
    assert toks[0].lexeme == char


# ── Multi-character operator disambiguation ───────────────────────────────────

def test_lt_alone():
    assert kinds("<")[0] == TokKind.LT

def test_lteq():
    assert kinds("<=")[0] == TokKind.LTEQ
    assert lex("<=")[0].lexeme == "<="

def test_gt_alone():
    assert kinds(">")[0] == TokKind.GT

def test_gteq():
    assert kinds(">=")[0] == TokKind.GTEQ
    assert lex(">=")[0].lexeme == ">="

def test_eq_alone():
    assert kinds("=")[0] == TokKind.EQ

def test_eqeq():
    assert kinds("==")[0] == TokKind.EQEQ
    assert lex("==")[0].lexeme == "=="

def test_fat_arrow():
    assert kinds("=>")[0] == TokKind.FAT_ARROW
    assert lex("=>")[0].lexeme == "=>"

def test_bang_alone():
    assert kinds("!")[0] == TokKind.BANG

def test_neq():
    assert kinds("!=")[0] == TokKind.NEQ
    assert lex("!=")[0].lexeme == "!="

def test_amp_alone():
    assert kinds("&")[0] == TokKind.AMP

def test_andand():
    assert kinds("&&")[0] == TokKind.ANDAND
    assert lex("&&")[0].lexeme == "&&"

def test_pipe_alone():
    assert kinds("|")[0] == TokKind.PIPE

def test_oror():
    assert kinds("||")[0] == TokKind.OROR
    assert lex("||")[0].lexeme == "||"

def test_minus_alone():
    assert kinds("-")[0] == TokKind.MINUS

def test_thin_arrow():
    assert kinds("->")[0] == TokKind.THIN_ARROW
    assert lex("->")[0].lexeme == "->"

def test_colon_alone():
    assert kinds(":")[0] == TokKind.COLON

def test_coloncolon():
    assert kinds("::")[0] == TokKind.COLONCOLON
    assert lex("::")[0].lexeme == "::"

def test_fat_arrow_not_thin_arrow():
    """=> and -> are distinct."""
    assert kinds("=>")[0] == TokKind.FAT_ARROW
    assert kinds("->")[0] == TokKind.THIN_ARROW


# ── Identifier ────────────────────────────────────────────────────────────────

def test_identifier():
    toks = lex("snake_case")
    assert toks[0].kind == TokKind.IDENT
    assert toks[0].lexeme == "snake_case"

def test_identifier_with_digits():
    toks = lex("x1_y2")
    assert toks[0].kind == TokKind.IDENT

def test_underscore_identifier():
    toks = lex("_")
    assert toks[0].kind == TokKind.IDENT
    assert toks[0].lexeme == "_"


# ── Integer literals ──────────────────────────────────────────────────────────

def test_decimal_int():
    tok = lex("42")[0]
    assert tok.kind == TokKind.INT
    assert tok.lexeme == "42"
    assert tok.value == 42

def test_zero():
    tok = lex("0")[0]
    assert tok.kind == TokKind.INT
    assert tok.value == 0

def test_hex_lowercase_prefix():
    tok = lex("0xff")[0]
    assert tok.kind == TokKind.INT
    assert tok.lexeme == "0xff"
    assert tok.value == 255

def test_hex_uppercase_prefix():
    tok = lex("0XAB")[0]
    assert tok.kind == TokKind.INT
    assert tok.lexeme == "0XAB"
    assert tok.value == 171

def test_hex_mixed_case_digits():
    tok = lex("0x1a2B")[0]
    assert tok.kind == TokKind.INT
    assert tok.value == 0x1a2B


# ── Float literals ────────────────────────────────────────────────────────────

def test_float_decimal():
    tok = lex("1.5")[0]
    assert tok.kind == TokKind.FLOAT
    assert tok.lexeme == "1.5"
    assert tok.value == 1.5

def test_float_exponent():
    tok = lex("2e5")[0]
    assert tok.kind == TokKind.FLOAT
    assert tok.value == pytest.approx(200000.0)


# ── String literals ───────────────────────────────────────────────────────────

def test_simple_string():
    tok = lex('"hello"')[0]
    assert tok.kind == TokKind.STRING
    assert tok.value == "hello"

def test_string_with_newline_escape():
    tok = lex(r'"a\nb"')[0]
    assert tok.kind == TokKind.STRING
    assert tok.value == "a\nb"

def test_string_with_tab_escape():
    tok = lex(r'"a\tb"')[0]
    assert tok.value == "a\tb"

def test_string_with_quote_escape():
    tok = lex(r'"say \"hi\""')[0]
    assert tok.value == 'say "hi"'

def test_raw_string_no_escape_processing():
    tok = lex(r'r"\n"')[0]
    assert tok.kind == TokKind.STRING
    assert tok.value == r"\n"   # two chars: backslash + n

def test_raw_string_r_alone_is_ident():
    toks = lex("r = 5")
    assert toks[0].kind == TokKind.IDENT
    assert toks[0].lexeme == "r"

def test_bytes_literal():
    tok = lex('b"abc"')[0]
    assert tok.kind == TokKind.BYTES
    assert tok.value == b"abc"

def test_bytes_b_alone_is_ident():
    toks = lex("b = 1")
    assert toks[0].kind == TokKind.IDENT
    assert toks[0].lexeme == "b"


# ── Boolean and none ──────────────────────────────────────────────────────────

def test_true():
    assert kinds("true")[0] == TokKind.TRUE

def test_false():
    assert kinds("false")[0] == TokKind.FALSE

def test_none():
    assert kinds("none")[0] == TokKind.NONE


# ── Span accuracy ─────────────────────────────────────────────────────────────

def test_span_line_and_col():
    # "let" starts at line 1, col 1
    tok = lex("let")[0]
    assert tok.span.line == 1
    assert tok.span.column == 1
    assert tok.span.length == 3

def test_span_after_newline():
    # Second line, first token
    toks = lex("let\nfn")
    fn_tok = toks[1]  # 'fn' is after 'let' and newline
    assert fn_tok.kind == TokKind.FN
    assert fn_tok.span.line == 2
    assert fn_tok.span.column == 1

def test_span_multichar_operator():
    tok = lex("<=")[0]
    assert tok.span.length == 2
    assert tok.span.column == 1

def test_span_column_offset():
    # "fn" at column 5 (after 4 spaces)
    tok = lex("    fn")[0]
    assert tok.kind == TokKind.FN
    assert tok.span.column == 5


# ── Trivia side channel ───────────────────────────────────────────────────────

def test_trivia_line_comment_not_in_main_tokens():
    tokens, trivia = lex_with_trivia("let x = 1; // a comment")
    main_kinds = [t.kind for t in tokens]
    assert TokKind.LINE_COMMENT not in main_kinds
    assert any(t.kind == TokKind.LINE_COMMENT for t in trivia)

def test_trivia_line_comment_value():
    _, trivia = lex_with_trivia("// hello world")
    assert trivia[0].kind == TokKind.LINE_COMMENT
    assert trivia[0].value == " hello world"

def test_trivia_block_comment():
    _, trivia = lex_with_trivia("/* block */")
    assert trivia[0].kind == TokKind.BLOCK_COMMENT

def test_trivia_nested_block_comment():
    _, trivia = lex_with_trivia("/* outer /* inner */ still */")
    assert len(trivia) == 1
    assert trivia[0].kind == TokKind.BLOCK_COMMENT

def test_trivia_doc_comment_not_in_main():
    tokens, trivia = lex_with_trivia("/// doc\nfn foo() {}")
    main_kinds = [t.kind for t in tokens]
    assert TokKind.DOC_COMMENT not in main_kinds
    assert any(t.kind == TokKind.DOC_COMMENT for t in trivia)

def test_trivia_doc_comment_value():
    _, trivia = lex_with_trivia("/// A doc comment")
    assert trivia[0].kind == TokKind.DOC_COMMENT
    assert trivia[0].value == "A doc comment"

def test_trivia_whitespace_produces_no_trivia_tokens():
    _, trivia = lex_with_trivia("   \n\t  \n")
    assert trivia == []

def test_lex_returns_same_as_lex_with_trivia_first_element():
    src = "let x = 1; // note"
    tokens = lex(src)
    tokens2, _ = lex_with_trivia(src)
    assert [t.kind for t in tokens] == [t.kind for t in tokens2]


# ── Misc edge cases ───────────────────────────────────────────────────────────

def test_multiple_tokens_in_sequence():
    toks = lex("let x: i32 = 42;")
    k = [t.kind for t in toks if t.kind != TokKind.EOF]
    assert k == [
        TokKind.LET, TokKind.IDENT, TokKind.COLON, TokKind.IDENT,
        TokKind.EQ, TokKind.INT, TokKind.SEMI,
    ]

def test_match_arm_tokens():
    toks = lex("Ok(v) => v,")
    k = [t.kind for t in toks if t.kind != TokKind.EOF]
    assert TokKind.FAT_ARROW in k

def test_fn_return_type_arrow():
    toks = lex("fn foo() -> i32 {}")
    k = [t.kind for t in toks if t.kind != TokKind.EOF]
    assert TokKind.THIN_ARROW in k
    assert TokKind.FAT_ARROW not in k

def test_pipe_in_pattern():
    toks = lex("A | B")
    k = [t.kind for t in toks if t.kind != TokKind.EOF]
    assert k == [TokKind.IDENT, TokKind.PIPE, TokKind.IDENT]

def test_logical_and_vs_amp():
    assert kinds("&&")[0] == TokKind.ANDAND
    assert kinds("& &")[0] == TokKind.AMP
    assert kinds("& &")[1] == TokKind.AMP

def test_logical_or_vs_pipe():
    assert kinds("||")[0] == TokKind.OROR
    assert kinds("| |")[0] == TokKind.PIPE
