from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import List, Optional, Union

from .token import Span


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


@dataclass
class Node:
    span: Span


# ---------------------------------------------------------------------------
# Comments and visibility (shared by many nodes)
# ---------------------------------------------------------------------------


@dataclass
class DocComment(Node):
    text: str


# ---------------------------------------------------------------------------
# Module-level declarations (kept from original)
# ---------------------------------------------------------------------------


@dataclass
class ModuleDecl(Node):
    path: List[str]


@dataclass
class UseDecl(Node):
    path: List[str]
    alias: Optional[str]
    doc: Optional[DocComment] = None


# ---------------------------------------------------------------------------
# Type nodes
# ---------------------------------------------------------------------------


class LiteralKind(enum.Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BYTES = "BYTES"
    RAW_STRING = "RAW_STRING"
    BOOL = "BOOL"
    NONE = "NONE"


@dataclass
class IdentType(Node):
    name: str


@dataclass
class PathType(Node):
    segments: List[str]


@dataclass
class TupleType(Node):
    elements: List[Type_]  # noqa: F821


@dataclass
class ArrayType(Node):
    element: Type_  # noqa: F821


# ---------------------------------------------------------------------------
# Pattern nodes
# ---------------------------------------------------------------------------


@dataclass
class WildcardPat(Node):
    pass


@dataclass
class IdentPat(Node):
    name: str
    mut: bool = False


@dataclass
class LiteralPat(Node):
    lit: LiteralExpr  # noqa: F821


@dataclass
class TuplePat(Node):
    elements: List[Pattern]  # noqa: F821


@dataclass
class StructPatField(Node):
    name: str
    pattern: Pattern  # noqa: F821


@dataclass
class StructPat(Node):
    name: str
    fields: List[StructPatField]


@dataclass
class EnumPat(Node):
    name: str
    elements: List[Pattern]  # noqa: F821


# ---------------------------------------------------------------------------
# Expression nodes
# ---------------------------------------------------------------------------


@dataclass
class LiteralExpr(Node):
    kind: LiteralKind
    value: str


@dataclass
class IdentExpr(Node):
    name: str


@dataclass
class PathExpr(Node):
    segments: List[str]


@dataclass
class BinaryExpr(Node):
    op: str
    left: Expr  # noqa: F821
    right: Expr  # noqa: F821


@dataclass
class UnaryExpr(Node):
    op: str
    operand: Expr  # noqa: F821


@dataclass
class CallExpr(Node):
    callee: Expr  # noqa: F821
    args: List[Expr]  # noqa: F821


@dataclass
class MemberExpr(Node):
    object: Expr  # noqa: F821
    member: str


@dataclass
class IndexExpr(Node):
    object: Expr  # noqa: F821
    index: Expr  # noqa: F821


@dataclass
class AwaitExpr(Node):
    expr: Expr  # noqa: F821


@dataclass
class TryExpr(Node):
    expr: Expr  # noqa: F821


@dataclass
class ReturnExpr(Node):
    value: Optional[Expr] = None  # noqa: F821


# ---------------------------------------------------------------------------
# Control flow and blocks
# (BlockExpr, IfExpr, LoopStmt, ForStmt, MatchArm, MatchExpr)
# These rely on Expr and Stmt forward refs — fine with from __future__ import annotations
# ---------------------------------------------------------------------------


@dataclass
class BlockExpr(Node):
    stmts: List[Stmt] = field(default_factory=list)  # noqa: F821
    expr: Optional[Expr] = None  # noqa: F821


@dataclass
class IfExpr(Node):
    condition: Expr  # noqa: F821
    then_: BlockExpr
    else_: Optional[Expr] = None  # noqa: F821


@dataclass
class LoopStmt(Node):
    body: BlockExpr


@dataclass
class ForStmt(Node):
    name: str
    iter: Expr  # noqa: F821
    body: BlockExpr


@dataclass
class MatchArm(Node):
    patterns: List[Pattern]  # noqa: F821
    body: Expr  # noqa: F821


@dataclass
class MatchExpr(Node):
    subject: Expr  # noqa: F821
    arms: List[MatchArm]


# ---------------------------------------------------------------------------
# Statement nodes
# ---------------------------------------------------------------------------


@dataclass
class ExprStmt(Node):
    expr: Expr  # noqa: F821


@dataclass
class ReturnStmt(Node):
    value: Optional[Expr] = None  # noqa: F821


@dataclass
class LetStmt(Node):
    name: str
    mut: bool = False
    type_: Optional[Type_] = None  # noqa: F821
    value: Optional[Expr] = None  # noqa: F821


# ---------------------------------------------------------------------------
# Union aliases — defined after all constituent classes
# ---------------------------------------------------------------------------

Type_ = Union[IdentType, PathType, TupleType, ArrayType]

Pattern = Union[WildcardPat, IdentPat, LiteralPat, TuplePat, StructPat, EnumPat]

Expr = Union[
    LiteralExpr,
    IdentExpr,
    PathExpr,
    BinaryExpr,
    UnaryExpr,
    CallExpr,
    MemberExpr,
    IndexExpr,
    AwaitExpr,
    BlockExpr,
    ReturnExpr,
    TryExpr,
    IfExpr,
]

Stmt = Union[LetStmt, ExprStmt, ReturnStmt, LoopStmt, ForStmt]

# ---------------------------------------------------------------------------
# Declaration nodes
# ---------------------------------------------------------------------------


@dataclass
class StructField(Node):
    name: str
    type_: Type_
    doc: Optional[DocComment] = None


@dataclass
class StructDecl(Node):
    name: str
    fields: List[StructField] = field(default_factory=list)
    doc: Optional[DocComment] = None
    vis: bool = False


@dataclass
class EnumVariant(Node):
    name: str
    fields: List[Type_] = field(default_factory=list)
    doc: Optional[DocComment] = None


@dataclass
class EnumDecl(Node):
    name: str
    variants: List[EnumVariant] = field(default_factory=list)
    doc: Optional[DocComment] = None
    vis: bool = False


@dataclass
class TypeAlias(Node):
    name: str
    type_: Type_
    doc: Optional[DocComment] = None
    vis: bool = False


@dataclass
class ConstDecl(Node):
    name: str
    type_: Type_
    value: Expr
    doc: Optional[DocComment] = None
    vis: bool = False


# ---------------------------------------------------------------------------
# Function nodes
# ---------------------------------------------------------------------------


@dataclass
class GenericParam(Node):
    name: str


@dataclass
class Param(Node):
    name: str
    type_: Type_
    self_: bool = False


@dataclass
class WhereConstraint(Node):
    param: str
    bound: Type_


@dataclass
class WhereClause(Node):
    constraints: List[WhereConstraint] = field(default_factory=list)


@dataclass
class EffectsClause(Node):
    effects: List[str] = field(default_factory=list)


@dataclass
class FnItem(Node):
    name: str
    params: List[Param] = field(default_factory=list)
    generics: List[GenericParam] = field(default_factory=list)
    ret: Optional[Type_] = None
    where_: Optional[WhereClause] = None
    effects: Optional[EffectsClause] = None
    body: Optional[BlockExpr] = None
    doc: Optional[DocComment] = None
    vis: bool = False
    async_: bool = False


# ---------------------------------------------------------------------------
# Trait and impl nodes
# ---------------------------------------------------------------------------


@dataclass
class TraitDecl(Node):
    name: str
    methods: List[FnItem] = field(default_factory=list)
    doc: Optional[DocComment] = None
    vis: bool = False


@dataclass
class ImplBlock(Node):
    type_: Type_
    trait_: Optional[str] = None
    methods: List[FnItem] = field(default_factory=list)
    doc: Optional[DocComment] = None


# ---------------------------------------------------------------------------
# Item union alias and File
# ---------------------------------------------------------------------------

Item = Union[
    StructDecl,
    EnumDecl,
    TypeAlias,
    ConstDecl,
    FnItem,
    TraitDecl,
    ImplBlock,
    UseDecl,
    ModuleDecl,
]


@dataclass
class File(Node):
    module: Optional[ModuleDecl] = None
    items: List[Item] = field(default_factory=list)

