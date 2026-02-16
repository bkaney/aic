from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .token import Span


@dataclass
class Node:
    span: Span


@dataclass
class DocComment(Node):
    text: str


@dataclass
class ModuleDecl(Node):
    path: List[str]


@dataclass
class UseDecl(Node):
    path: List[str]
    alias: Optional[str]


@dataclass
class File(Node):
    module: Optional[ModuleDecl] = None
    uses: List[UseDecl] = field(default_factory=list)
    docs: List[DocComment] = field(default_factory=list)

