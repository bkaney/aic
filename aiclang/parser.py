from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .ast import DocComment, File, ModuleDecl, UseDecl
from .diagnostics import Diagnostic, FixIt
from .token import TokKind, Token


@dataclass
class ParseResult:
    file: Optional[File]
    diagnostics: List[Diagnostic]


class Parser:
    def __init__(self, tokens: List[Token]):
        self.toks = tokens
        self.i = 0
        self.diags: List[Diagnostic] = []

    def parse_file(self) -> ParseResult:
        file_node = File(span=self._span_here())
        # Optional leading doc comments
        docs = []
        while self._peek_k(TokKind.DOC_COMMENT):
            tok = self._advance()
            docs.append(DocComment(text=tok.lexeme, span=tok.span))
        file_node.docs = docs

        # module decl (required for now)
        if self._peek_k(TokKind.MODULE):
            mod = self._parse_module_decl()
            file_node.module = mod
        else:
            self._error("E0002", "expected 'module' declaration", self._peek())
            return ParseResult(None, self.diags)

        # zero or more use decls
        while self._peek_k(TokKind.USE) or self._peek_k(TokKind.DOC_COMMENT):
            if self._peek_k(TokKind.DOC_COMMENT):
                # skip/attach as file doc for now
                tok = self._advance()
                file_node.docs.append(DocComment(text=tok.lexeme, span=tok.span))
                continue
            use = self._parse_use_decl()
            file_node.uses.append(use)

        # We stop here for v0.1 minimal subset
        return ParseResult(file_node, self.diags)

    # --- nonterminals ---
    def _parse_module_decl(self) -> ModuleDecl:
        kw = self._expect(TokKind.MODULE, "E0001", "expected 'module'")
        segs, last_span = self._parse_module_path()
        semi = self._maybe(TokKind.SEMI)
        if not semi:
            # Suggest adding semicolon at end of line
            self._error_with_fix(
                code="E0002",
                msg="expected ';' after module declaration",
                tok=last_span_tok(self._peek(-1)),
                fix=FixIt(replacement=";", start_line=kw.span.line, start_col=kw.span.column, end_line=kw.span.line, end_col=kw.span.column),
            )
        return ModuleDecl(path=segs, span=kw.span)

    def _parse_use_decl(self) -> UseDecl:
        kw = self._expect(TokKind.USE, "E0001", "expected 'use'")
        path, _ = self._parse_use_path()
        alias = None
        if self._maybe(TokKind.AS):
            alias_tok = self._expect(TokKind.IDENT, "E0001", "expected identifier after 'as'")
            alias = alias_tok.lexeme
        semi = self._maybe(TokKind.SEMI)
        if not semi:
            self._error_with_fix(
                code="E0002",
                msg="expected ';' after use declaration",
                tok=self._peek(-1),
                fix=FixIt(replacement=";", start_line=kw.span.line, start_col=kw.span.column, end_line=kw.span.line, end_col=kw.span.column),
            )
        return UseDecl(path=path, alias=alias, span=kw.span)

    def _parse_module_path(self) -> Tuple[List[str], Token]:
        segs: List[str] = []
        first = self._expect(TokKind.IDENT, "E0001", "expected identifier in module path")
        segs.append(first.lexeme)
        last_tok = first
        while self._maybe(TokKind.DOT):
            nxt = self._expect(TokKind.IDENT, "E0001", "expected identifier after '.' in module path")
            segs.append(nxt.lexeme)
            last_tok = nxt
        return segs, last_tok

    def _parse_use_path(self) -> Tuple[List[str], Token]:
        segs: List[str] = []
        first = self._expect(TokKind.IDENT, "E0001", "expected identifier in use path")
        segs.append(first.lexeme)
        last_tok = first
        while self._maybe(TokKind.COLONCOLON):
            nxt = self._expect(TokKind.IDENT, "E0001", "expected identifier after '::' in use path")
            segs.append(nxt.lexeme)
            last_tok = nxt
        return segs, last_tok

    # --- helpers ---
    def _peek(self, lookahead: int = 0) -> Token:
        idx = self.i + lookahead
        if idx < 0:
            idx = 0
        if idx >= len(self.toks):
            return self.toks[-1]
        return self.toks[idx]

    def _peek_k(self, kind: TokKind) -> bool:
        return self._peek().kind == kind

    def _advance(self) -> Token:
        tok = self._peek()
        self.i = min(self.i + 1, len(self.toks) - 1)
        return tok

    def _maybe(self, kind: TokKind) -> Optional[Token]:
        if self._peek_k(kind):
            return self._advance()
        return None

    def _expect(self, kind: TokKind, code: str, msg: str) -> Token:
        if self._peek_k(kind):
            return self._advance()
        self._error(code, msg, self._peek())
        # Attempt recovery: fabricate a token with current span
        return self._advance()

    def _error(self, code: str, msg: str, tok: Token):
        self.diags.append(
            Diagnostic(code=code, level="error", message=msg, span=tok.span, notes=[], fixits=[])
        )

    def _error_with_fix(self, code: str, msg: str, tok: Token, fix: FixIt):
        self.diags.append(
            Diagnostic(code=code, level="error", message=msg, span=tok.span, notes=[], fixits=[fix])
        )

    def _span_here(self):
        tok = self._peek()
        return tok.span


def last_span_tok(tok: Token) -> Token:
    return tok

