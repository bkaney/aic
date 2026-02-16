from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .token import Span


@dataclass
class FixIt:
    replacement: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int


@dataclass
class Diagnostic:
    code: str
    level: str  # "error" | "warning"
    message: str
    span: Span
    notes: List[str]
    fixits: List[FixIt]

    def to_json(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "level": self.level,
            "message": self.message,
            "span": {
                "file": self.span.file,
                "line": self.span.line,
                "column": self.span.column,
            },
            "notes": list(self.notes),
            "fixits": [
                {
                    "range": {
                        "start": {"line": f.start_line, "column": f.start_col},
                        "end": {"line": f.end_line, "column": f.end_col},
                    },
                    "replacement": f.replacement,
                }
                for f in self.fixits
            ],
        }

