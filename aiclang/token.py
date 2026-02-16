from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class TokKind(Enum):
    EOF = auto()
    IDENT = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BYTES = auto()

    MODULE = auto()
    USE = auto()
    PUB = auto()
    AS = auto()
    TRAIT = auto()
    IMPL = auto()
    STRUCT = auto()
    ENUM = auto()
    FN = auto()
    ASYNC = auto()
    AWAIT = auto()
    WHERE = auto()
    EFFECTS = auto()
    RETURN = auto()
    MATCH = auto()
    IF = auto()
    ELSE = auto()
    LOOP = auto()
    FOR = auto()
    IN = auto()
    LET = auto()
    CONST = auto()
    TRUE = auto()
    FALSE = auto()
    NONE = auto()
    EXTERN = auto()

    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACK = auto()  # [
    RBRACK = auto()  # ]
    SEMI = auto()    # ;
    COLON = auto()   # :
    COLONCOLON = auto()  # ::
    COMMA = auto()   # ,
    DOT = auto()     # .
    EQ = auto()      # =
    ARROW = auto()   # ->
    QUESTION = auto()# ?
    AMP = auto()     # &
    STAR = auto()    # *
    PLUS = auto()    # +
    MINUS = auto()   # -
    SLASH = auto()   # /
    PERCENT = auto() # %
    BANG = auto()    # !

    DOC_COMMENT = auto()  # leading /// ... (line)


KEYWORDS = {
    "module": TokKind.MODULE,
    "use": TokKind.USE,
    "pub": TokKind.PUB,
    "as": TokKind.AS,
    "trait": TokKind.TRAIT,
    "impl": TokKind.IMPL,
    "struct": TokKind.STRUCT,
    "enum": TokKind.ENUM,
    "fn": TokKind.FN,
    "async": TokKind.ASYNC,
    "await": TokKind.AWAIT,
    "where": TokKind.WHERE,
    "effects": TokKind.EFFECTS,
    "return": TokKind.RETURN,
    "match": TokKind.MATCH,
    "if": TokKind.IF,
    "else": TokKind.ELSE,
    "loop": TokKind.LOOP,
    "for": TokKind.FOR,
    "in": TokKind.IN,
    "let": TokKind.LET,
    "const": TokKind.CONST,
    "true": TokKind.TRUE,
    "false": TokKind.FALSE,
    "none": TokKind.NONE,
    "extern": TokKind.EXTERN,
}


@dataclass
class Span:
    file: str
    line: int
    column: int
    index: int
    length: int


@dataclass
class Token:
    kind: TokKind
    lexeme: str
    span: Span
    value: Optional[object] = None

