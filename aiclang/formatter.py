from __future__ import annotations

from typing import List

from .ast import File


def format_file(f: File) -> str:
    lines: List[str] = []
    if f.module is not None:
        lines.append(f"module {'.'.join(f.module.path)};")
    if f.uses:
        # sort by path lexicographically
        sorted_uses = sorted(f.uses, key=lambda u: '::'.join(u.path))
        for u in sorted_uses:
            path = '::'.join(u.path)
            if u.alias:
                lines.append(f"use {path} as {u.alias};")
            else:
                lines.append(f"use {path};")
    # ensure trailing newline and single newline join
    return "\n".join(lines) + ("\n" if lines else "")

