from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .ast import (
    ArrayType,
    ConstDecl,
    DocComment,
    EnumDecl,
    EnumVariant,
    File,
    IdentExpr,
    IdentType,
    LiteralExpr,
    LiteralKind,
    ModuleDecl,
    PathType,
    StructDecl,
    StructField,
    TupleType,
    Type_,
    TypeAlias,
    UseDecl,
)
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

        # Consume any leading doc comments (module has no doc field)
        while self._peek_k(TokKind.DOC_COMMENT):
            self._advance()

        # module decl (required as first real item)
        if self._peek_k(TokKind.MODULE):
            mod = self._parse_module_decl()
            file_node.module = mod
        else:
            self._error("E0002", "expected 'module' declaration", self._peek())
            return ParseResult(None, self.diags)

        # General top-level item dispatch loop
        pending_doc: Optional[DocComment] = None
        while not self._peek_k(TokKind.EOF):
            vis = False

            # Collect a doc comment into the pending slot
            if self._peek_k(TokKind.DOC_COMMENT):
                tok = self._advance()
                pending_doc = DocComment(text=tok.lexeme, span=tok.span)
                continue

            # Consume optional pub prefix
            if self._peek_k(TokKind.PUB):
                self._advance()
                vis = True

            kind = self._peek().kind

            if kind == TokKind.STRUCT:
                node = self._parse_struct_decl(vis, pending_doc)
                file_node.items.append(node)
            elif kind == TokKind.ENUM:
                node = self._parse_enum_decl(vis, pending_doc)
                file_node.items.append(node)
            elif kind == TokKind.TYPE:
                node = self._parse_type_alias(vis, pending_doc)
                file_node.items.append(node)
            elif kind == TokKind.CONST:
                node = self._parse_const_decl(vis, pending_doc)
                file_node.items.append(node)
            elif kind == TokKind.USE:
                node = self._parse_use_decl(pending_doc)
                file_node.items.append(node)
            elif kind == TokKind.MODULE:
                node = self._parse_module_decl()
                file_node.items.append(node)
            else:
                # Panic-mode top-level recovery
                bad_tok = self._peek()
                self._error("E0001", f"unexpected token '{bad_tok.lexeme}'", bad_tok)
                while (
                    not self._peek_k(TokKind.EOF)
                    and not self._peek_k(TokKind.SEMI)
                    and not self._peek_k(TokKind.RBRACE)
                ):
                    self._advance()
                if self._peek_k(TokKind.SEMI) or self._peek_k(TokKind.RBRACE):
                    self._advance()

            pending_doc = None

        return ParseResult(file_node, self.diags)

    # -------------------------------------------------------------------------
    # Type expression parser
    # -------------------------------------------------------------------------

    def _parse_type(self) -> Type_:
        tok = self._peek()
        if tok.kind == TokKind.LPAREN:
            return self._parse_tuple_type()
        elif tok.kind == TokKind.LBRACK:
            return self._parse_array_type()
        elif tok.kind == TokKind.IDENT:
            return self._parse_ident_or_path_type()
        else:
            self._error("E0001", f"expected type, got '{tok.lexeme}'", tok)
            self._advance()
            return IdentType(name="<error>", span=tok.span)

    def _parse_ident_or_path_type(self) -> Type_:
        first = self._expect(TokKind.IDENT, "E0001", "expected identifier in type")
        segments = [first.lexeme]
        while self._peek_k(TokKind.COLONCOLON):
            self._advance()
            seg = self._expect(TokKind.IDENT, "E0001", "expected identifier after '::'")
            segments.append(seg.lexeme)
        if len(segments) == 1:
            return IdentType(name=segments[0], span=first.span)
        return PathType(segments=segments, span=first.span)

    def _parse_tuple_type(self) -> TupleType:
        lparen = self._expect(TokKind.LPAREN, "E0001", "expected '('")
        elements: List[Type_] = []
        while not self._peek_k(TokKind.RPAREN) and not self._peek_k(TokKind.EOF):
            elements.append(self._parse_type())
            if not self._maybe(TokKind.COMMA):
                break
        self._expect(TokKind.RPAREN, "E0001", "expected ')'")
        return TupleType(elements=elements, span=lparen.span)

    def _parse_array_type(self) -> ArrayType:
        lbrack = self._expect(TokKind.LBRACK, "E0001", "expected '['")
        element = self._parse_type()
        self._expect(TokKind.RBRACK, "E0001", "expected ']'")
        return ArrayType(element=element, span=lbrack.span)

    # -------------------------------------------------------------------------
    # Declaration parsers
    # -------------------------------------------------------------------------

    def _parse_struct_decl(
        self, vis: bool = False, doc: Optional[DocComment] = None
    ) -> StructDecl:
        kw = self._expect(TokKind.STRUCT, "E0001", "expected 'struct'")
        name_tok = self._expect(TokKind.IDENT, "E0001", "expected struct name")
        self._expect(TokKind.LBRACE, "E0001", "expected '{' after struct name")
        fields: List[StructField] = []
        while not self._peek_k(TokKind.RBRACE) and not self._peek_k(TokKind.EOF):
            # Field-level recovery on unexpected token
            if not self._peek_k(TokKind.IDENT):
                bad = self._peek()
                self._error("E0001", f"expected field name, got '{bad.lexeme}'", bad)
                while (
                    not self._peek_k(TokKind.SEMI)
                    and not self._peek_k(TokKind.RBRACE)
                    and not self._peek_k(TokKind.EOF)
                ):
                    self._advance()
                self._maybe(TokKind.SEMI)
                continue
            field_name = self._advance()
            self._expect(TokKind.COLON, "E0001", "expected ':' after field name")
            field_type = self._parse_type()
            if not self._maybe(TokKind.SEMI):
                self._error_with_fix(
                    code="E0002",
                    msg="expected ';' after struct field",
                    tok=self._peek(-1),
                    fix=FixIt(
                        replacement=";",
                        start_line=kw.span.line,
                        start_col=kw.span.column,
                        end_line=kw.span.line,
                        end_col=kw.span.column,
                    ),
                )
            fields.append(
                StructField(name=field_name.lexeme, type_=field_type, span=field_name.span)
            )
        self._expect(TokKind.RBRACE, "E0001", "expected '}' to close struct body")
        return StructDecl(name=name_tok.lexeme, fields=fields, doc=doc, vis=vis, span=kw.span)

    def _parse_enum_decl(
        self, vis: bool = False, doc: Optional[DocComment] = None
    ) -> EnumDecl:
        kw = self._expect(TokKind.ENUM, "E0001", "expected 'enum'")
        name_tok = self._expect(TokKind.IDENT, "E0001", "expected enum name")
        self._expect(TokKind.LBRACE, "E0001", "expected '{' after enum name")
        variants: List[EnumVariant] = []
        while not self._peek_k(TokKind.RBRACE) and not self._peek_k(TokKind.EOF):
            # Variant-level recovery on unexpected token
            if not self._peek_k(TokKind.IDENT):
                bad = self._peek()
                self._error("E0001", f"expected variant name, got '{bad.lexeme}'", bad)
                while (
                    not self._peek_k(TokKind.SEMI)
                    and not self._peek_k(TokKind.RBRACE)
                    and not self._peek_k(TokKind.EOF)
                ):
                    self._advance()
                self._maybe(TokKind.SEMI)
                continue
            var_name = self._advance()
            payload: List[Type_] = []
            if self._maybe(TokKind.LPAREN):
                while not self._peek_k(TokKind.RPAREN) and not self._peek_k(TokKind.EOF):
                    payload.append(self._parse_type())
                    if not self._maybe(TokKind.COMMA):
                        break
                self._expect(TokKind.RPAREN, "E0001", "expected ')' after variant payload")
            if not self._maybe(TokKind.SEMI):
                self._error_with_fix(
                    code="E0002",
                    msg="expected ';' after enum variant",
                    tok=self._peek(-1),
                    fix=FixIt(
                        replacement=";",
                        start_line=kw.span.line,
                        start_col=kw.span.column,
                        end_line=kw.span.line,
                        end_col=kw.span.column,
                    ),
                )
            variants.append(
                EnumVariant(name=var_name.lexeme, fields=payload, span=var_name.span)
            )
        self._expect(TokKind.RBRACE, "E0001", "expected '}' to close enum body")
        return EnumDecl(name=name_tok.lexeme, variants=variants, doc=doc, vis=vis, span=kw.span)

    def _parse_type_alias(
        self, vis: bool = False, doc: Optional[DocComment] = None
    ) -> TypeAlias:
        kw = self._expect(TokKind.TYPE, "E0001", "expected 'type'")
        name_tok = self._expect(TokKind.IDENT, "E0001", "expected type alias name")
        self._expect(TokKind.EQ, "E0001", "expected '=' after type alias name")
        aliased = self._parse_type()
        if not self._maybe(TokKind.SEMI):
            self._error_with_fix(
                code="E0002",
                msg="expected ';' after type alias",
                tok=self._peek(-1),
                fix=FixIt(
                    replacement=";",
                    start_line=kw.span.line,
                    start_col=kw.span.column,
                    end_line=kw.span.line,
                    end_col=kw.span.column,
                ),
            )
        return TypeAlias(name=name_tok.lexeme, type_=aliased, doc=doc, vis=vis, span=kw.span)

    def _parse_const_decl(
        self, vis: bool = False, doc: Optional[DocComment] = None
    ) -> ConstDecl:
        kw = self._expect(TokKind.CONST, "E0001", "expected 'const'")
        name_tok = self._expect(TokKind.IDENT, "E0001", "expected const name")
        self._expect(TokKind.COLON, "E0001", "expected ':' after const name")
        const_type = self._parse_type()
        self._expect(TokKind.EQ, "E0001", "expected '=' after const type")
        value = self._parse_const_initializer()
        if not self._maybe(TokKind.SEMI):
            self._error_with_fix(
                code="E0002",
                msg="expected ';' after const declaration",
                tok=self._peek(-1),
                fix=FixIt(
                    replacement=";",
                    start_line=kw.span.line,
                    start_col=kw.span.column,
                    end_line=kw.span.line,
                    end_col=kw.span.column,
                ),
            )
        return ConstDecl(
            name=name_tok.lexeme, type_=const_type, value=value, doc=doc, vis=vis, span=kw.span
        )

    def _parse_const_initializer(self) -> LiteralExpr | IdentExpr:
        tok = self._peek()
        if tok.kind == TokKind.INT:
            self._advance()
            return LiteralExpr(kind=LiteralKind.INT, value=tok.lexeme, span=tok.span)
        elif tok.kind == TokKind.FLOAT:
            self._advance()
            return LiteralExpr(kind=LiteralKind.FLOAT, value=tok.lexeme, span=tok.span)
        elif tok.kind == TokKind.STRING:
            self._advance()
            return LiteralExpr(kind=LiteralKind.STRING, value=tok.lexeme, span=tok.span)
        elif tok.kind == TokKind.TRUE:
            self._advance()
            return LiteralExpr(kind=LiteralKind.BOOL, value=tok.lexeme, span=tok.span)
        elif tok.kind == TokKind.FALSE:
            self._advance()
            return LiteralExpr(kind=LiteralKind.BOOL, value=tok.lexeme, span=tok.span)
        elif tok.kind == TokKind.NONE:
            self._advance()
            return LiteralExpr(kind=LiteralKind.NONE, value=tok.lexeme, span=tok.span)
        elif tok.kind == TokKind.IDENT:
            self._advance()
            return IdentExpr(name=tok.lexeme, span=tok.span)
        else:
            self._error(
                "E0001",
                f"expected literal or identifier as const initializer, got '{tok.lexeme}'",
                tok,
            )
            return LiteralExpr(kind=LiteralKind.INT, value="0", span=tok.span)

    # -------------------------------------------------------------------------
    # Pre-existing nonterminals
    # -------------------------------------------------------------------------

    def _parse_module_decl(self) -> ModuleDecl:
        kw = self._expect(TokKind.MODULE, "E0001", "expected 'module'")
        segs, _last_tok = self._parse_module_path()
        semi = self._maybe(TokKind.SEMI)
        if not semi:
            self._error_with_fix(
                code="E0002",
                msg="expected ';' after module declaration",
                tok=last_span_tok(self._peek(-1)),
                fix=FixIt(
                    replacement=";",
                    start_line=kw.span.line,
                    start_col=kw.span.column,
                    end_line=kw.span.line,
                    end_col=kw.span.column,
                ),
            )
        return ModuleDecl(path=segs, span=kw.span)

    def _parse_use_decl(self, doc: Optional[DocComment] = None) -> UseDecl:
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
                fix=FixIt(
                    replacement=";",
                    start_line=kw.span.line,
                    start_col=kw.span.column,
                    end_line=kw.span.line,
                    end_col=kw.span.column,
                ),
            )
        return UseDecl(path=path, alias=alias, doc=doc, span=kw.span)

    def _parse_module_path(self) -> Tuple[List[str], Token]:
        segs: List[str] = []
        first = self._expect(TokKind.IDENT, "E0001", "expected identifier in module path")
        segs.append(first.lexeme)
        last_tok = first
        while self._maybe(TokKind.DOT):
            nxt = self._expect(
                TokKind.IDENT, "E0001", "expected identifier after '.' in module path"
            )
            segs.append(nxt.lexeme)
            last_tok = nxt
        return segs, last_tok

    def _parse_use_path(self) -> Tuple[List[str], Token]:
        segs: List[str] = []
        first = self._expect(TokKind.IDENT, "E0001", "expected identifier in use path")
        segs.append(first.lexeme)
        last_tok = first
        while self._maybe(TokKind.COLONCOLON):
            nxt = self._expect(
                TokKind.IDENT, "E0001", "expected identifier after '::' in use path"
            )
            segs.append(nxt.lexeme)
            last_tok = nxt
        return segs, last_tok

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

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
        # Attempt recovery: advance past the unexpected token
        return self._advance()

    def _error(self, code: str, msg: str, tok: Token) -> None:
        self.diags.append(
            Diagnostic(code=code, level="error", message=msg, span=tok.span, notes=[], fixits=[])
        )

    def _error_with_fix(self, code: str, msg: str, tok: Token, fix: FixIt) -> None:
        self.diags.append(
            Diagnostic(
                code=code, level="error", message=msg, span=tok.span, notes=[], fixits=[fix]
            )
        )

    def _span_here(self) -> object:
        tok = self._peek()
        return tok.span


def last_span_tok(tok: Token) -> Token:
    return tok


def merge_doc_comments(tokens: List[Token], trivia: List[Token]) -> List[Token]:
    """Merge DOC_COMMENT trivia tokens into the main token stream in source order.

    The lexer emits DOC_COMMENT as trivia (not regular tokens). This function
    interleaves them back into the token list so the parser can see them.
    EOF must remain last.
    """
    doc_toks = [t for t in trivia if t.kind == TokKind.DOC_COMMENT]
    if not doc_toks:
        return tokens
    # tokens[-1] is always EOF — keep it last
    eof = tokens[-1]
    body = tokens[:-1]
    merged = sorted(body + doc_toks, key=lambda t: t.span.index)
    return merged + [eof]

