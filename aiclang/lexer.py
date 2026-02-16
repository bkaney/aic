from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

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

    def lex(self) -> List[Token]:
        while not self._eof():
            ch = self._peek()
            if ch in (' ', '\t', '\r'):
                self._advance()
                continue
            if ch == '\n':
                self._advance_line()
                continue
            if ch == '/':
                if self._match('/'):
                    if self._match('/'):
                        self._lex_doc_comment()
                    else:
                        self._skip_line_comment()
                    continue
                if self._match('*'):
                    self._skip_block_comment()
                    continue
                self._emit(TokKind.SLASH, "/")
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
                self._advance();
                if not self._eof() and self._peek() == '>':
                    self._advance(); self._emit(TokKind.ARROW, '=>')
                else:
                    self._emit(TokKind.EQ, '=')
                continue
            if ch == '?':
                self._advance(); self._emit(TokKind.QUESTION, '?'); continue
            if ch == '&':
                self._advance(); self._emit(TokKind.AMP, '&'); continue
            if ch == '*':
                self._advance(); self._emit(TokKind.STAR, '*'); continue
            if ch == '+':
                self._advance(); self._emit(TokKind.PLUS, '+'); continue
            if ch == '-':
                self._advance(); self._emit(TokKind.MINUS, '-'); continue
            if ch == '%':
                self._advance(); self._emit(TokKind.PERCENT, '%'); continue
            if ch == '!':
                self._advance(); self._emit(TokKind.BANG, '!'); continue

            # Unknown char fallback
            self._advance()  # skip unknown

        self.tokens.append(Token(TokKind.EOF, "", self._span(0)))
        return self.tokens

    # Internals
    def _eof(self) -> bool:
        return self.i >= self.len

    def _peek(self) -> str:
        return self.src[self.i]

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

    def _emit(self, kind: TokKind, lexeme: str, value: Optional[object] = None):
        self.tokens.append(Token(kind, lexeme, self._span(len(lexeme)), value))

    def _match(self, expected: str) -> bool:
        if self._eof() or self.src[self.i] != expected:
            return False
        self._advance()
        return True

    def _skip_line_comment(self):
        while not self._eof() and self._peek() != '\n':
            self._advance()

    def _skip_block_comment(self):
        depth = 1
        self._advance()  # we already consumed '/*' second char
        while not self._eof() and depth > 0:
            ch = self._advance()
            if ch == '/' and not self._eof() and self._peek() == '*':
                self._advance(); depth += 1
            elif ch == '*' and not self._eof() and self._peek() == '/':
                self._advance(); depth -= 1
            elif ch == '\n':
                self.line += 1
                self.col = 1

    def _lex_doc_comment(self):
        # starting after '///'
        start_col = self.col - 2  # we've consumed '//' and second '/', adjust roughly
        text = []
        while not self._eof() and self._peek() != '\n':
            text.append(self._advance())
        content = ''.join(text)
        # Trim a leading space
        content = content[1:] if content.startswith(' ') else content
        span = Span(self.cfg.file, self.line, start_col, self.i - len(content), len(content))
        self.tokens.append(Token(TokKind.DOC_COMMENT, content, span))

    def _lex_ident_or_keyword(self):
        start_i = self.i
        start_col = self.col
        while not self._eof() and (self._peek().isalnum() or self._peek() == '_'):
            self._advance()
        lexeme = self.src[start_i:self.i]
        kind = KEYWORDS.get(lexeme, TokKind.IDENT)
        self.tokens.append(Token(kind, lexeme, Span(self.cfg.file, self.line, start_col, start_i, self.i - start_i)))

    def _lex_number(self):
        start_i = self.i
        start_col = self.col
        seen_dot = False
        while not self._eof() and (self._peek().isdigit() or (self._peek() == '.' and not seen_dot)):
            if self._peek() == '.':
                seen_dot = True
            self._advance()
        lexeme = self.src[start_i:self.i]
        kind = TokKind.FLOAT if '.' in lexeme else TokKind.INT
        value = float(lexeme) if kind == TokKind.FLOAT else int(lexeme)
        self.tokens.append(Token(kind, lexeme, Span(self.cfg.file, self.line, start_col, start_i, self.i - start_i), value))

    def _lex_string(self):
        start_col = self.col
        self._advance()  # opening quote
        buf = []
        while not self._eof() and self._peek() != '"':
            ch = self._advance()
            if ch == '\\' and not self._eof():
                buf.append(ch)
                buf.append(self._advance())
            else:
                buf.append(ch)
        if not self._eof():
            self._advance()  # closing quote
        lexeme = '"' + ''.join(buf) + '"'
        self._emit(TokKind.STRING, lexeme, ''.join(buf))

