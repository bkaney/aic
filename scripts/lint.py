#!/usr/bin/env python3
"""Syntax check and lint runner for the aiclang project.

Usage:
    python scripts/lint.py          # check aiclang/ and tests/
    python scripts/lint.py --fix    # auto-fix safe issues
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TARGETS = ["aiclang", "tests", "scripts"]


def syntax_check(paths: list[Path]) -> int:
    """Parse each .py file with ast.parse; report syntax errors."""
    errors = 0
    for path in paths:
        src = path.read_text(encoding="utf-8")
        try:
            ast.parse(src, filename=str(path))
        except SyntaxError as exc:
            rel = path.relative_to(ROOT)
            print(f"SYNTAX {rel}:{exc.lineno}: {exc.msg}")
            errors += 1
    return errors


def ruff_check(fix: bool) -> int:
    """Run ruff; return its exit code."""
    import subprocess

    ruff = ROOT / ".venv" / "bin" / "ruff"
    if not ruff.exists():
        ruff = "ruff"  # fall back to PATH

    cmd = [str(ruff), "check"] + TARGETS
    if fix:
        cmd.append("--fix")
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Syntax + lint checker")
    parser.add_argument("--fix", action="store_true", help="Auto-fix safe issues via ruff")
    parser.add_argument("--syntax-only", action="store_true", help="Skip ruff, only syntax check")
    args = parser.parse_args()

    py_files = [
        p for target in TARGETS
        for p in (ROOT / target).rglob("*.py")
    ]

    print(f"Checking {len(py_files)} files...\n")

    syntax_errors = syntax_check(py_files)
    if syntax_errors:
        print(f"\n{syntax_errors} syntax error(s) found.")
    else:
        print("Syntax OK")

    if args.syntax_only:
        sys.exit(1 if syntax_errors else 0)

    print()
    lint_rc = ruff_check(fix=args.fix)

    if syntax_errors or lint_rc != 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
