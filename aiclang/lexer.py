from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .token import KEYWORDS, Span, TokKind, Token


@dataclass
class LexerConfig:
    file: str


class Lexer:
    def __init__(self, src: str, cfg: LexerConfig):
        self.src = src
        self.cfg = cfg
        self.i = 0
        self.line = 1
        self.col = 1
        self.len = len(src)
        self.tokens: List[Token] = []
        self.trivia: List[Token] = []

    def lex(self) -> List[Token]:
        self._scan()
        return self.tokens

    def lex_with_trivia(self) -> Tuple[List[Token], List[Token]]:
        self._scan()
        return self.tokens, self.trivia

    def _scan(self):
        if self.tokens:
            return  # already scanned
        while not self._eof():
            ch = self._peek()
            if ch in (' ', '\t', '\r'):
                self._advance()
                continue
            if ch == '\n':
                self._advance_line()
                continue
            if ch == '/':
                self._advance()  # consume the '/'
                if not self._eof() and self._peek() == '/':
                    self._advance()  # consume second '/'
                    if not self._eof() and self._peek() == '/':
                        self._advance()  # consume third '/'
                        self._lex_doc_comment()
                    else:
                        self._lex_line_comment()
                    continue
                if not self._eof() and self._peek() == '*':
                    self._advance()  # consume '*'
                    self._lex_block_comment()
                    continue
                self._emit(TokKind.SLASH, "/")
                continue
            if ch == 'r' or ch == 'b':
                # May be raw/bytes string prefix — check ahead
                if ch == 'r' and self.i + 1 < self.len and self.src[self.i + 1] == '"':
                    self._advance()  # consume 'r'
                    self._lex_raw_string()
                    continue
                if ch == 'b' and self.i + 1 < self.len and self.src[self.i + 1] == '"':
                    self._advance()  # consume 'b'
                    self._lex_bytes_string()
                    continue
                self._lex_ident_or_keyword()
                continue
            if ch.isalpha() or ch == '_':
                self._lex_ident_or_keyword()
                continue
            if ch.isdigit():
                self._lex_number()
                continue
            if ch == '"':
                self._lex_string()
                continue

            # punctuation and operators
            if ch == '{':
                self._advance(); self._emit(TokKind.LBRACE, '{'); continue
            if ch == '}':
                self._advance(); self._emit(TokKind.RBRACE, '}'); continue
            if ch == '(':
                self._advance(); self._emit(TokKind.LPAREN, '('); continue
            if ch == ')':
                self._advance(); self._emit(TokKind.RPAREN, ')'); continue
            if ch == '[':
                self._advance(); self._emit(TokKind.LBRACK, '['); continue
            if ch == ']':
                self._advance(); self._emit(TokKind.RBRACK, ']'); continue
            if ch == ';':
                self._advance(); self._emit(TokKind.SEMI, ';'); continue
            if ch == ',':
                self._advance(); self._emit(TokKind.COMMA, ','); continue
            if ch == '.':
                self._advance(); self._emit(TokKind.DOT, '.'); continue
            if ch == ':':
                self._advance()
                if not self._eof() and self._peek() == ':':
                    self._advance(); self._emit(TokKind.COLONCOLON, '::')
                else:
                    self._emit(TokKind.COLON, ':')
                continue
            if ch == '=':
                self._advance()
                if not self._eof() and self._peek() == '>':
                    self._advance(); self._emit(TokKind.FAT_ARROW, '=>')
                elif not self._eof() and self._peek() == '=':
                    self._advance(); self._emit(TokKind.EQEQ, '==')
                else:
                    self._emit(TokKind.EQ, '=')
                continue
            if ch == '!':
                self._advance()
                if not self._eof() and self._peek() == '=':
                    self._advance(); self._emit(TokKind.NEQ, '!=')
                else:
                    self._emit(TokKind.BANG, '!')
                continue
            if ch == '<':
                self._advance()
                if not self._eof() and self._peek() == '=':
                    self._advance(); self._emit(TokKind.LTEQ, '<=')
                else:
                    self._emit(TokKind.LT, '<')
                continue
            if ch == '>':
                self._advance()
                if not self._eof() and self._peek() == '=':
                    self._advance(); self._emit(TokKind.GTEQ, '>=')
                else:
                    self._emit(TokKind.GT, '>')
                continue
            if ch == '&':
                self._advance()
                if not self._eof() and self._peek() == '&':
                    self._advance(); self._emit(TokKind.ANDAND, '&&')
                else:
                    self._emit(TokKind.AMP, '&')
                continue
            if ch == '|':
                self._advance()
                if not self._eof() and self._peek() == '|':
                    self._advance(); self._emit(TokKind.OROR, '||')
                else:
                    self._emit(TokKind.PIPE, '|')
                continue
            if ch == '-':
                self._advance()
                if not self._eof() and self._peek() == '>':
                    self._advance(); self._emit(TokKind.THIN_ARROW, '->')
                else:
                    self._emit(TokKind.MINUS, '-')
                continue
            if ch == '?':
                self._advance(); self._emit(TokKind.QUESTION, '?'); continue
            if ch == '*':
                self._advance(); self._emit(TokKind.STAR, '*'); continue
            if ch == '+':
                self._advance(); self._emit(TokKind.PLUS, '+'); continue
            if ch == '%':
                self._advance(); self._emit(TokKind.PERCENT, '%'); continue

            # TODO(lexer): emit E0001 for unknown character
            self._advance()  # skip unknown

        self.tokens.append(Token(TokKind.EOF, "", self._span(0)))

    # ── Internals ────────────────────────────────────────────────────────────

    def _eof(self) -> bool:
        return self.i >= self.len

    def _peek(self) -> str:
        return self.src[self.i]

    def _peek_next(self) -> Optional[str]:
        return self.src[self.i + 1] if self.i + 1 < self.len else None

    def _advance(self) -> str:
        ch = self.src[self.i]
        self.i += 1
        self.col += 1
        return ch

    def _advance_line(self):
        self.i += 1
        self.line += 1
        self.col = 1

    def _span(self, length: int) -> Span:
        return Span(self.cfg.file, self.line, self.col - length, self.i - length, length)

    def _span_from(self, start_i: int, start_col: int) -> Span:
        length = self.i - start_i
        return Span(self.cfg.file, self.line, start_col, start_i, length)

    def _emit(self, kind: TokKind, lexeme: str, value: Optional[object] = None):
        self.tokens.append(Token(kind, lexeme, self._span(len(lexeme)), value))

    def _emit_trivia(self, kind: TokKind, lexeme: str, span: Span, value: Optional[object] = None):
        self.trivia.append(Token(kind, lexeme, span, value))

    def _match(self, expected: str) -> bool:
        if self._eof() or self.src[self.i] != expected:
            return False
        self._advance()
        return True

    # ── Comments ─────────────────────────────────────────────────────────────

    def _lex_line_comment(self):
        """Emit a LINE_COMMENT trivia token for `// ...` (already consumed `//`)."""
        start_i = self.i - 2
        start_col = self.col - 2
        text = []
        while not self._eof() and self._peek() != '\n':
            text.append(self._advance())
        lexeme = '//' + ''.join(text)
        span = Span(self.cfg.file, self.line, start_col, start_i, len(lexeme))
        self._emit_trivia(TokKind.LINE_COMMENT, lexeme, span, ''.join(text))

    def _lex_doc_comment(self):
        """Emit a DOC_COMMENT trivia token for `/// ...` (already consumed `///`)."""
        start_i = self.i - 3
        start_col = self.col - 3
        text = []
        while not self._eof() and self._peek() != '\n':
            text.append(self._advance())
        content = ''.join(text)
        content = content[1:] if content.startswith(' ') else content
        lexeme = '///' + ''.join(text)
        span = Span(self.cfg.file, self.line, start_col, start_i, len(lexeme))
        self._emit_trivia(TokKind.DOC_COMMENT, lexeme, span, content)

    def _lex_block_comment(self):
        """Emit a BLOCK_COMMENT trivia token for `/* ... */` (already consumed `/*`)."""
        start_i = self.i - 2
        start_col = self.col - 2
        start_line = self.line
        depth = 1
        while not self._eof() and depth > 0:
            ch = self._advance()
            if ch == '/' and not self._eof() and self._peek() == '*':
                self._advance(); depth += 1
            elif ch == '*' and not self._eof() and self._peek() == '/':
                self._advance(); depth -= 1
            elif ch == '\n':
                self.line += 1
                self.col = 1
        lexeme = self.src[start_i:self.i]
        span = Span(self.cfg.file, start_line, start_col, start_i, self.i - start_i)
        self._emit_trivia(TokKind.BLOCK_COMMENT, lexeme, span)

    # ── Identifiers and Keywords ─────────────────────────────────────────────

    def _lex_ident_or_keyword(self):
        start_i = self.i
        start_col = self.col
        while not self._eof() and (self._peek().isalnum() or self._peek() == '_'):
            self._advance()
        lexeme = self.src[start_i:self.i]
        kind = KEYWORDS.get(lexeme, TokKind.IDENT)
        self.tokens.append(Token(kind, lexeme, Span(self.cfg.file, self.line, start_col, start_i, self.i - start_i)))

    # ── Numbers ──────────────────────────────────────────────────────────────

    def _lex_number(self):
        start_i = self.i
        start_col = self.col
        # Check for hex prefix
        if self._peek() == '0' and self.i + 1 < self.len and self.src[self.i + 1] in ('x', 'X'):
            self._advance()  # '0'
            self._advance()  # 'x'/'X'
            while not self._eof() and self.src[self.i] in '0123456789abcdefABCDEF':
                self._advance()
            lexeme = self.src[start_i:self.i]
            value = int(lexeme, 16)
            self.tokens.append(Token(TokKind.INT, lexeme, Span(self.cfg.file, self.line, start_col, start_i, self.i - start_i), value))
            return
        seen_dot = False
        seen_exp = False
        while not self._eof():
            ch = self._peek()
            if ch.isdigit():
                self._advance()
            elif ch == '.' and not seen_dot and not seen_exp:
                # Only treat as float if next char is a digit
                if self.i + 1 < self.len and self.src[self.i + 1].isdigit():
                    seen_dot = True
                    self._advance()
                else:
                    break
            elif ch in ('e', 'E') and not seen_exp:
                seen_exp = True
                self._advance()
                if not self._eof() and self._peek() in ('+', '-'):
                    self._advance()
            else:
                break
        lexeme = self.src[start_i:self.i]
        if seen_dot or seen_exp:
            kind = TokKind.FLOAT
            value: object = float(lexeme)
        else:
            kind = TokKind.INT
            value = int(lexeme)
        self.tokens.append(Token(kind, lexeme, Span(self.cfg.file, self.line, start_col, start_i, self.i - start_i), value))

    # ── Strings ──────────────────────────────────────────────────────────────

    def _lex_string(self):
        start_i = self.i
        start_col = self.col
        self._advance()  # opening quote
        buf = []
        while not self._eof() and self._peek() != '"':
            ch = self._advance()
            if ch == '\\' and not self._eof():
                esc = self._advance()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', '0': '\0'}
                buf.append(escape_map.get(esc, esc))
            else:
                buf.append(ch)
        if not self._eof():
            self._advance()  # closing quote
        lexeme = self.src[start_i:self.i]
        value = ''.join(buf)
        self.tokens.append(Token(TokKind.STRING, lexeme, Span(self.cfg.file, self.line, start_col, start_i, self.i - start_i), value))

    def _lex_raw_string(self):
        """Called after consuming the `r` prefix. Lexes `"..."` with no escape processing."""
        start_i = self.i - 1  # include the 'r'
        start_col = self.col - 1
        self._advance()  # opening quote
        buf = []
        while not self._eof() and self._peek() != '"':
            ch = self._advance()
            if ch == '\n':
                self.line += 1
                self.col = 1
            buf.append(ch)
        if not self._eof():
            self._advance()  # closing quote
        lexeme = self.src[start_i:self.i]
        value = ''.join(buf)
        self.tokens.append(Token(TokKind.STRING, lexeme, Span(self.cfg.file, self.line, start_col, start_i, self.i - start_i), value))

    def _lex_bytes_string(self):
        """Called after consuming the `b` prefix. Lexes `"..."` and emits BYTES."""
        start_i = self.i - 1  # include the 'b'
        start_col = self.col - 1
        self._advance()  # opening quote
        buf = []
        while not self._eof() and self._peek() != '"':
            ch = self._advance()
            if ch == '\\' and not self._eof():
                esc = self._advance()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', '0': '\0'}
                buf.append(escape_map.get(esc, esc))
            else:
                buf.append(ch)
        if not self._eof():
            self._advance()  # closing quote
        lexeme = self.src[start_i:self.i]
        value = ''.join(buf).encode('utf-8')
        self.tokens.append(Token(TokKind.BYTES, lexeme, Span(self.cfg.file, self.line, start_col, start_i, self.i - start_i), value))
