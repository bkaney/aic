from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List

from .diagnostics import Diagnostic
from .formatter import format_file
from .lexer import Lexer, LexerConfig
from .parser import Parser


EXIT_SUCCESS = 0
EXIT_BUILD_ERROR = 1
EXIT_FORMAT_DISAGREEMENT = 2


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def diag_to_json_list(diags: List[Diagnostic]):
    return [d.to_json() for d in diags]


def collect_aic_files(paths: List[str]) -> List[str]:
    files: List[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, fs in os.walk(p):
                for name in fs:
                    if name.endswith(".aic"):
                        files.append(os.path.join(root, name))
        else:
            if p.endswith(".aic"):
                files.append(p)
    return sorted(files)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="aic")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fmt = sub.add_parser("fmt", help="format source files")
    p_fmt.add_argument("paths", nargs="*", default=["."], help="files or directories")
    p_fmt.add_argument("--check", action="store_true", help="check only, do not write")
    p_fmt.add_argument("--json", action="store_true", help="emit JSON diagnostics")

    p_check = sub.add_parser("check", help="parse + format check (no codegen)")
    p_check.add_argument("paths", nargs="*", default=["."], help="files or directories")
    p_check.add_argument("--json", action="store_true", help="emit JSON diagnostics")

    return parser.parse_args(argv)


def run_fmt(paths: List[str], check: bool, emit_json: bool) -> int:
    files = collect_aic_files(paths)
    disagreements = 0
    diagnostics: List[Diagnostic] = []
    for path in files:
        src = read_file(path)
        lex = Lexer(src, LexerConfig(file=path))
        toks = lex.lex()
        parser = Parser(toks)
        res = parser.parse_file()
        if res.file is None:
            diagnostics.extend(res.diagnostics)
            continue
        formatted = format_file(res.file)
        if formatted != src:
            disagreements += 1
            if emit_json:
                # Report a formatter disagreement diagnostic
                diagnostics.append(
                    Diagnostic(
                        code="E0014",
                        level="error",
                        message=f"formatter disagreement: {os.path.relpath(path)}",
                        span=toks[0].span,
                        notes=[],
                        fixits=[],
                    )
                )
            if not check:
                write_file(path, formatted)
    if emit_json and diagnostics:
        print(json.dumps(diag_to_json_list(diagnostics), indent=2))
    if disagreements > 0 and check:
        return EXIT_FORMAT_DISAGREEMENT
    return EXIT_SUCCESS


def run_check(paths: List[str], emit_json: bool) -> int:
    files = collect_aic_files(paths)
    any_errors = False
    diagnostics: List[Diagnostic] = []
    for path in files:
        src = read_file(path)
        lex = Lexer(src, LexerConfig(file=path))
        toks = lex.lex()
        parser = Parser(toks)
        res = parser.parse_file()
        if res.file is None or res.diagnostics:
            any_errors = True
            diagnostics.extend(res.diagnostics)
            continue
        # Compare formatted output without writing
        formatted = format_file(res.file)
        if formatted != src:
            any_errors = True
            diagnostics.append(
                Diagnostic(
                    code="E0014",
                    level="error",
                    message=f"formatter disagreement: {os.path.relpath(path)}",
                    span=toks[0].span,
                    notes=[],
                    fixits=[],
                )
            )

    if emit_json and diagnostics:
        print(json.dumps(diag_to_json_list(diagnostics), indent=2))
    return EXIT_BUILD_ERROR if any_errors else EXIT_SUCCESS


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(argv or sys.argv[1:])
    if ns.cmd == "fmt":
        return run_fmt(ns.paths, ns.check, ns.json)
    if ns.cmd == "check":
        return run_check(ns.paths, ns.json)
    return EXIT_BUILD_ERROR


if __name__ == "__main__":
    raise SystemExit(main())

