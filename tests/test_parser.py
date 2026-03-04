"""Tests for aiclang.parser — covers type expressions, declaration parsing,
doc attachment, dispatch loop, and error recovery."""
from __future__ import annotations

from aiclang.ast import (
    ArrayType,
    ConstDecl,
    EnumDecl,
    EnumVariant,
    IdentExpr,
    IdentType,
    LiteralExpr,
    LiteralKind,
    ModuleDecl,
    PathType,
    StructDecl,
    StructField,
    TupleType,
    TypeAlias,
    UseDecl,
)
from aiclang.lexer import Lexer, LexerConfig
from aiclang.parser import ParseResult, Parser, merge_doc_comments


# ── Helpers ──────────────────────────────────────────────────────────────────


def _lex(src: str):
    toks, trivia = Lexer(src, LexerConfig(file="<test>")).lex_with_trivia()
    return merge_doc_comments(toks, trivia)


def parse(src: str) -> ParseResult:
    """Lex and parse a complete AIC source string."""
    return Parser(_lex(src)).parse_file()


def parse_ok(src: str):
    """Parse and assert no diagnostics; return the file node."""
    result = parse(src)
    assert result.file is not None, f"parse returned None; diags={result.diagnostics}"
    assert result.diagnostics == [], f"unexpected diagnostics: {result.diagnostics}"
    return result.file


def items(src: str) -> list:
    """Return file.items for a source snippet (module header prepended)."""
    return parse_ok(f"module test;\n{src}").items


def item(src: str):
    """Return the single top-level item from a snippet."""
    got = items(src)
    assert len(got) == 1, f"expected 1 item, got {len(got)}: {got}"
    return got[0]


# ── Module declaration ────────────────────────────────────────────────────────


def test_module_decl_parsed():
    file = parse_ok("module foo;")
    assert isinstance(file.module, ModuleDecl)
    assert file.module.path == ["foo"]


def test_module_missing_raises_diagnostic():
    result = parse("struct Foo {}")
    assert result.file is None
    assert any(d.code == "E0002" for d in result.diagnostics)


# ── Type expressions ─────────────────────────────────────────────────────────


def test_ident_type_in_struct_field():
    s = item("struct S { x: i32; }")
    assert isinstance(s, StructDecl)
    assert isinstance(s.fields[0].type_, IdentType)
    assert s.fields[0].type_.name == "i32"


def test_path_type_two_segments():
    s = item("struct S { h: std::io; }")
    assert isinstance(s.fields[0].type_, PathType)
    assert s.fields[0].type_.segments == ["std", "io"]


def test_path_type_three_segments():
    s = item("struct S { w: std::io::Writer; }")
    assert isinstance(s.fields[0].type_, PathType)
    assert s.fields[0].type_.segments == ["std", "io", "Writer"]


def test_tuple_type_empty():
    s = item("struct S { t: (); }")
    assert isinstance(s.fields[0].type_, TupleType)
    assert s.fields[0].type_.elements == []


def test_tuple_type_single():
    s = item("struct S { t: (i32); }")
    t = s.fields[0].type_
    assert isinstance(t, TupleType)
    assert len(t.elements) == 1
    assert isinstance(t.elements[0], IdentType)


def test_tuple_type_multi():
    s = item("struct S { t: (i32, str, bool); }")
    t = s.fields[0].type_
    assert isinstance(t, TupleType)
    assert len(t.elements) == 3
    for el in t.elements:
        assert isinstance(el, IdentType)


def test_array_type():
    s = item("struct S { data: [u8]; }")
    at = s.fields[0].type_
    assert isinstance(at, ArrayType)
    assert isinstance(at.element, IdentType)
    assert at.element.name == "u8"


# ── Struct declaration ────────────────────────────────────────────────────────


def test_empty_struct():
    s = item("struct Point {}")
    assert isinstance(s, StructDecl)
    assert s.name == "Point"
    assert s.fields == []
    assert s.vis is False


def test_pub_struct():
    s = item("pub struct Point {}")
    assert s.vis is True


def test_struct_with_fields():
    s = item("struct Point { x: i32; y: i32; }")
    assert len(s.fields) == 2
    assert s.fields[0].name == "x"
    assert s.fields[1].name == "y"


def test_struct_field_name_and_type():
    s = item("struct S { count: u32; }")
    f = s.fields[0]
    assert isinstance(f, StructField)
    assert f.name == "count"
    assert isinstance(f.type_, IdentType)
    assert f.type_.name == "u32"


def test_struct_field_path_type():
    s = item("struct S { h: std::io::Writer; }")
    assert isinstance(s.fields[0].type_, PathType)
    assert s.fields[0].type_.segments == ["std", "io", "Writer"]


def test_struct_field_tuple_type():
    s = item("struct S { coords: (f64, f64); }")
    assert isinstance(s.fields[0].type_, TupleType)
    assert len(s.fields[0].type_.elements) == 2


def test_struct_missing_field_semi_emits_e0002():
    result = parse("module test;\nstruct S { x: i32 }")
    assert any(d.code == "E0002" for d in result.diagnostics)


# ── Enum declaration ──────────────────────────────────────────────────────────


def test_empty_enum():
    e = item("enum Color {}")
    assert isinstance(e, EnumDecl)
    assert e.name == "Color"
    assert e.variants == []
    assert e.vis is False


def test_pub_enum():
    e = item("pub enum Color {}")
    assert e.vis is True


def test_enum_unit_variants():
    e = item("enum Shape { Circle; Square; }")
    assert len(e.variants) == 2
    assert e.variants[0].name == "Circle"
    assert e.variants[0].fields == []
    assert e.variants[1].name == "Square"


def test_enum_single_payload_variant():
    e = item("enum Opt { Some(i32); }")
    v = e.variants[0]
    assert isinstance(v, EnumVariant)
    assert v.name == "Some"
    assert len(v.fields) == 1
    assert isinstance(v.fields[0], IdentType)
    assert v.fields[0].name == "i32"


def test_enum_multi_payload_variant():
    e = item("enum E { Pair(i32, str); }")
    v = e.variants[0]
    assert len(v.fields) == 2
    assert isinstance(v.fields[0], IdentType)
    assert isinstance(v.fields[1], IdentType)


def test_enum_path_type_payload():
    e = item("enum E { Wrapped(std::io::Error); }")
    assert isinstance(e.variants[0].fields[0], PathType)
    assert e.variants[0].fields[0].segments == ["std", "io", "Error"]


def test_enum_missing_variant_semi_emits_e0002():
    result = parse("module test;\nenum E { A }")
    assert any(d.code == "E0002" for d in result.diagnostics)


# ── Type alias ────────────────────────────────────────────────────────────────


def test_type_alias_ident():
    t = item("type MyInt = i32;")
    assert isinstance(t, TypeAlias)
    assert t.name == "MyInt"
    assert isinstance(t.type_, IdentType)
    assert t.type_.name == "i32"
    assert t.vis is False


def test_pub_type_alias():
    t = item("pub type MyInt = i32;")
    assert t.vis is True


def test_type_alias_path_type():
    t = item("type Writer = std::io::Write;")
    assert isinstance(t.type_, PathType)
    assert t.type_.segments == ["std", "io", "Write"]


def test_type_alias_tuple_type():
    t = item("type Pair = (i32, str);")
    assert isinstance(t.type_, TupleType)
    assert len(t.type_.elements) == 2


def test_type_alias_missing_eq_emits_e0001():
    result = parse("module test;\ntype Foo i32;")
    assert any(d.code == "E0001" for d in result.diagnostics)


def test_type_alias_missing_semi_emits_e0002():
    result = parse("module test;\ntype Foo = i32")
    assert any(d.code == "E0002" for d in result.diagnostics)


# ── Const declaration ─────────────────────────────────────────────────────────


def test_const_int():
    c = item("const MAX: i32 = 100;")
    assert isinstance(c, ConstDecl)
    assert c.name == "MAX"
    assert isinstance(c.type_, IdentType)
    assert c.type_.name == "i32"
    assert isinstance(c.value, LiteralExpr)
    assert c.value.kind == LiteralKind.INT
    assert c.vis is False


def test_const_string():
    c = item('const GREETING: str = "hello";')
    assert isinstance(c.value, LiteralExpr)
    assert c.value.kind == LiteralKind.STRING


def test_const_bool():
    c = item("const FLAG: bool = true;")
    assert isinstance(c.value, LiteralExpr)
    assert c.value.kind == LiteralKind.BOOL


def test_const_ident_initializer():
    c = item("const VALUE: i32 = OTHER;")
    assert isinstance(c.value, IdentExpr)
    assert c.value.name == "OTHER"


def test_pub_const():
    c = item("pub const MAX: i32 = 0;")
    assert c.vis is True


def test_const_missing_colon_emits_e0001():
    result = parse("module test;\nconst NAME i32 = 0;")
    assert any(d.code == "E0001" for d in result.diagnostics)


def test_const_missing_eq_emits_e0001():
    result = parse("module test;\nconst NAME: i32 0;")
    assert any(d.code == "E0001" for d in result.diagnostics)


def test_const_missing_semi_emits_e0002():
    result = parse("module test;\nconst MAX: i32 = 0")
    assert any(d.code == "E0002" for d in result.diagnostics)


# ── Doc attachment ────────────────────────────────────────────────────────────


def test_doc_attached_to_struct():
    s = item("/// A point.\nstruct Point {}")
    assert s.doc is not None
    assert "A point" in s.doc.text


def test_doc_attached_to_enum():
    e = item("/// A color.\nenum Color {}")
    assert e.doc is not None


def test_doc_attached_to_type_alias():
    t = item("/// An alias.\ntype MyInt = i32;")
    assert t.doc is not None


def test_doc_attached_to_const():
    c = item("/// A const.\nconst X: i32 = 1;")
    assert c.doc is not None


def test_doc_attached_to_use():
    u = item("/// A use.\nuse foo::bar;")
    assert isinstance(u, UseDecl)
    assert u.doc is not None


def test_no_doc_gives_none():
    s = item("struct Point {}")
    assert s.doc is None


def test_consecutive_doc_comments_last_wins():
    s = item("/// First.\n/// Second.\nstruct Point {}")
    assert s.doc is not None
    assert "Second" in s.doc.text


# ── Dispatch loop / multi-declaration ────────────────────────────────────────


def test_multiple_declarations_in_order():
    got = items("struct S {}\nenum E {}\nconst C: i32 = 0;")
    assert isinstance(got[0], StructDecl)
    assert isinstance(got[1], EnumDecl)
    assert isinstance(got[2], ConstDecl)


def test_use_still_works():
    u = item("use std::io;")
    assert isinstance(u, UseDecl)
    assert u.path == ["std", "io"]


def test_pub_before_enum():
    e = item("pub enum E {}")
    assert e.vis is True


# ── Error recovery ────────────────────────────────────────────────────────────


def test_top_level_unknown_token_recovery():
    """Garbage token at top level should recover and parse the next valid decl."""
    result = parse("module test;\n42;\nstruct S {}")
    assert result.file is not None
    assert any(d.code == "E0001" for d in result.diagnostics)
    # Recovery should still produce the struct
    structs = [i for i in result.file.items if isinstance(i, StructDecl)]
    assert len(structs) == 1
    assert structs[0].name == "S"


def test_top_level_recovery_emits_single_diagnostic():
    """One recovery event = one E0001 diagnostic (not one per skipped token)."""
    result = parse("module test;\n42 + foo;\nstruct S {}")
    e0001_count = sum(1 for d in result.diagnostics if d.code == "E0001")
    assert e0001_count == 1


def test_struct_field_recovery():
    """Bad token in struct field position recovers and parses subsequent field."""
    result = parse("module test;\nstruct S { 42; y: i32; }")
    assert result.file is not None
    assert any(d.code == "E0001" for d in result.diagnostics)
    structs = [i for i in result.file.items if isinstance(i, StructDecl)]
    assert len(structs) == 1
    # The valid field y should be parsed after recovery
    field_names = [f.name for f in structs[0].fields]
    assert "y" in field_names


def test_enum_variant_recovery():
    """Bad token in enum variant position recovers and parses subsequent variant."""
    result = parse("module test;\nenum E { 42; Good; }")
    assert result.file is not None
    assert any(d.code == "E0001" for d in result.diagnostics)
    enums = [i for i in result.file.items if isinstance(i, EnumDecl)]
    assert len(enums) == 1
    variant_names = [v.name for v in enums[0].variants]
    assert "Good" in variant_names


def test_recovery_diagnostic_has_e0001():
    """All recovery-emitted diagnostics use code E0001."""
    result = parse("module test;\n@bad;")
    codes = [d.code for d in result.diagnostics]
    assert "E0001" in codes
