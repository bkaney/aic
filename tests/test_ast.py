"""Construction tests for all AST node types."""
from __future__ import annotations

from aiclang.ast import (
    # Union aliases
    Expr,
    Item,
    Pattern,
    Stmt,
    Type_,
    # Type nodes
    ArrayType,
    IdentType,
    LiteralKind,
    PathType,
    TupleType,
    # Pattern nodes
    EnumPat,
    IdentPat,
    LiteralPat,
    StructPat,
    StructPatField,
    TuplePat,
    WildcardPat,
    # Expression nodes
    AwaitExpr,
    BinaryExpr,
    BlockExpr,
    CallExpr,
    IdentExpr,
    IndexExpr,
    LiteralExpr,
    MemberExpr,
    PathExpr,
    ReturnExpr,
    TryExpr,
    UnaryExpr,
    # Control flow
    ForStmt,
    IfExpr,
    LoopStmt,
    MatchArm,
    MatchExpr,
    # Statement nodes
    ExprStmt,
    LetStmt,
    ReturnStmt,
    # Declaration nodes
    ConstDecl,
    EnumDecl,
    EnumVariant,
    StructDecl,
    StructField,
    TypeAlias,
    # Function nodes
    EffectsClause,
    FnItem,
    GenericParam,
    Param,
    WhereClause,
    WhereConstraint,
    # Trait/impl nodes
    ImplBlock,
    TraitDecl,
    # Top-level
    File,
    ModuleDecl,
    UseDecl,
)
from aiclang.token import Span

SPAN = Span(file="test", line=1, column=1, index=0, length=0)


# ---------------------------------------------------------------------------
# Type nodes
# ---------------------------------------------------------------------------


def test_literal_kind_members() -> None:
    assert LiteralKind.INT.value == "INT"
    assert LiteralKind.RAW_STRING.value == "RAW_STRING"
    assert LiteralKind.NONE.value == "NONE"


def test_ident_type() -> None:
    t = IdentType(span=SPAN, name="i32")
    assert t.name == "i32"


def test_path_type() -> None:
    t = PathType(span=SPAN, segments=["std", "io", "Result"])
    assert len(t.segments) == 3


def test_tuple_type() -> None:
    t = TupleType(span=SPAN, elements=[IdentType(SPAN, "i32"), IdentType(SPAN, "str")])
    assert len(t.elements) == 2


def test_array_type() -> None:
    t = ArrayType(span=SPAN, element=IdentType(SPAN, "u8"))
    assert t.element.name == "u8"  # type: ignore[union-attr]


def test_type_alias_importable() -> None:
    # Type_ is defined at module level
    assert Type_ is not None


# ---------------------------------------------------------------------------
# Declaration nodes
# ---------------------------------------------------------------------------


def test_struct_field() -> None:
    f = StructField(span=SPAN, name="x", type_=IdentType(SPAN, "i32"))
    assert f.name == "x"
    assert f.doc is None


def test_struct_decl_defaults() -> None:
    s = StructDecl(span=SPAN, name="Point")
    assert s.vis is False
    assert s.doc is None
    assert s.fields == []


def test_struct_decl_with_fields() -> None:
    field_ = StructField(SPAN, "x", IdentType(SPAN, "i32"))
    s = StructDecl(span=SPAN, name="Point", fields=[field_])
    assert s.fields[0].name == "x"


def test_enum_variant_unit() -> None:
    v = EnumVariant(span=SPAN, name="None")
    assert v.fields == []


def test_enum_variant_tuple() -> None:
    v = EnumVariant(span=SPAN, name="Some", fields=[IdentType(SPAN, "i32")])
    assert len(v.fields) == 1


def test_enum_decl_defaults() -> None:
    e = EnumDecl(span=SPAN, name="Option")
    assert e.vis is False
    assert e.variants == []


def test_enum_decl_with_variants() -> None:
    v = EnumVariant(SPAN, "None")
    e = EnumDecl(span=SPAN, name="Option", variants=[v])
    assert len(e.variants) == 1


def test_type_alias() -> None:
    ta = TypeAlias(span=SPAN, name="MyInt", type_=IdentType(SPAN, "i32"))
    assert ta.name == "MyInt"
    assert ta.vis is False


def test_const_decl() -> None:
    lit = LiteralExpr(SPAN, LiteralKind.INT, "42")
    c = ConstDecl(span=SPAN, name="MAX", type_=IdentType(SPAN, "i32"), value=lit)
    assert c.name == "MAX"
    assert c.vis is False


def test_let_stmt_defaults() -> None:
    let = LetStmt(span=SPAN, name="x")
    assert let.mut is False
    assert let.type_ is None
    assert let.value is None


def test_let_stmt_with_type_and_value() -> None:
    v = LiteralExpr(SPAN, LiteralKind.INT, "1")
    let = LetStmt(span=SPAN, name="x", type_=IdentType(SPAN, "i32"), value=v)
    assert let.type_ is not None
    assert let.value is not None


# ---------------------------------------------------------------------------
# Function nodes
# ---------------------------------------------------------------------------


def test_generic_param() -> None:
    g = GenericParam(span=SPAN, name="T")
    assert g.name == "T"


def test_param_defaults() -> None:
    p = Param(span=SPAN, name="x", type_=IdentType(SPAN, "i32"))
    assert p.self_ is False


def test_param_self() -> None:
    p = Param(span=SPAN, name="self", type_=IdentType(SPAN, "Self"), self_=True)
    assert p.self_ is True


def test_where_constraint() -> None:
    wc = WhereConstraint(span=SPAN, param="T", bound=IdentType(SPAN, "Display"))
    assert wc.param == "T"


def test_where_clause() -> None:
    wc = WhereConstraint(SPAN, "T", IdentType(SPAN, "Display"))
    clause = WhereClause(span=SPAN, constraints=[wc])
    assert len(clause.constraints) == 1


def test_effects_clause() -> None:
    e = EffectsClause(span=SPAN, effects=["io", "net"])
    assert e.effects == ["io", "net"]


def test_expr_stmt() -> None:
    expr = IdentExpr(SPAN, "foo")
    s = ExprStmt(span=SPAN, expr=expr)
    assert s.expr.name == "foo"  # type: ignore[union-attr]


def test_return_stmt_with_value() -> None:
    v = LiteralExpr(SPAN, LiteralKind.INT, "0")
    r = ReturnStmt(span=SPAN, value=v)
    assert r.value is not None


def test_return_stmt_bare() -> None:
    r = ReturnStmt(span=SPAN)
    assert r.value is None


def test_block_expr_empty() -> None:
    b = BlockExpr(span=SPAN)
    assert b.stmts == []
    assert b.expr is None


def test_block_expr_with_trailing_expr() -> None:
    e = LiteralExpr(SPAN, LiteralKind.INT, "1")
    b = BlockExpr(span=SPAN, stmts=[], expr=e)
    assert b.expr is not None


def test_fn_item_defaults() -> None:
    body = BlockExpr(SPAN)
    fn = FnItem(span=SPAN, name="foo", body=body)
    assert fn.async_ is False
    assert fn.vis is False
    assert fn.generics == []
    assert fn.params == []
    assert fn.ret is None
    assert fn.where_ is None
    assert fn.effects is None


def test_fn_item_with_ret_type() -> None:
    body = BlockExpr(SPAN)
    fn = FnItem(span=SPAN, name="bar", body=body, ret=IdentType(SPAN, "i32"))
    assert fn.ret is not None


def test_stmt_alias_importable() -> None:
    assert Stmt is not None


# ---------------------------------------------------------------------------
# Expression nodes
# ---------------------------------------------------------------------------


def test_literal_expr_raw_value() -> None:
    e = LiteralExpr(SPAN, LiteralKind.INT, "0xFF")
    assert e.value == "0xFF"
    assert e.kind == LiteralKind.INT


def test_literal_expr_bool() -> None:
    e = LiteralExpr(SPAN, LiteralKind.BOOL, "true")
    assert e.kind == LiteralKind.BOOL


def test_ident_expr() -> None:
    e = IdentExpr(SPAN, "x")
    assert e.name == "x"


def test_path_expr() -> None:
    e = PathExpr(SPAN, ["std", "io", "read"])
    assert len(e.segments) == 3


def test_binary_expr() -> None:
    left = LiteralExpr(SPAN, LiteralKind.INT, "1")
    right = LiteralExpr(SPAN, LiteralKind.INT, "2")
    e = BinaryExpr(SPAN, op="+", left=left, right=right)
    assert e.op == "+"


def test_unary_expr() -> None:
    operand = LiteralExpr(SPAN, LiteralKind.BOOL, "true")
    e = UnaryExpr(SPAN, op="!", operand=operand)
    assert e.op == "!"


def test_call_expr() -> None:
    callee = IdentExpr(SPAN, "foo")
    arg1 = LiteralExpr(SPAN, LiteralKind.INT, "1")
    arg2 = LiteralExpr(SPAN, LiteralKind.INT, "2")
    e = CallExpr(SPAN, callee=callee, args=[arg1, arg2])
    assert len(e.args) == 2


def test_member_expr() -> None:
    obj = IdentExpr(SPAN, "point")
    e = MemberExpr(SPAN, object=obj, member="x")
    assert e.member == "x"


def test_index_expr() -> None:
    obj = IdentExpr(SPAN, "arr")
    idx = LiteralExpr(SPAN, LiteralKind.INT, "0")
    e = IndexExpr(SPAN, object=obj, index=idx)
    assert e.index is not None


def test_await_expr() -> None:
    inner = IdentExpr(SPAN, "fut")
    e = AwaitExpr(SPAN, expr=inner)
    assert e.expr.name == "fut"  # type: ignore[union-attr]


def test_try_expr() -> None:
    inner = CallExpr(SPAN, callee=IdentExpr(SPAN, "f"), args=[])
    e = TryExpr(SPAN, expr=inner)
    assert e.expr is not None


def test_return_expr_with_value() -> None:
    v = LiteralExpr(SPAN, LiteralKind.INT, "0")
    e = ReturnExpr(SPAN, value=v)
    assert e.value is not None


def test_return_expr_bare() -> None:
    e = ReturnExpr(SPAN)
    assert e.value is None


def test_expr_alias_importable() -> None:
    assert Expr is not None


# ---------------------------------------------------------------------------
# Pattern nodes
# ---------------------------------------------------------------------------


def test_wildcard_pat() -> None:
    p = WildcardPat(span=SPAN)
    assert p.span == SPAN


def test_ident_pat_defaults() -> None:
    p = IdentPat(span=SPAN, name="x")
    assert p.mut is False


def test_ident_pat_mutable() -> None:
    p = IdentPat(span=SPAN, name="x", mut=True)
    assert p.mut is True


def test_literal_pat() -> None:
    lit = LiteralExpr(SPAN, LiteralKind.INT, "42")
    p = LiteralPat(span=SPAN, lit=lit)
    assert p.lit.value == "42"  # type: ignore[union-attr]


def test_tuple_pat() -> None:
    p = TuplePat(span=SPAN, elements=[WildcardPat(SPAN), IdentPat(SPAN, "x")])
    assert len(p.elements) == 2


def test_struct_pat_field() -> None:
    f = StructPatField(span=SPAN, name="x", pattern=IdentPat(SPAN, "a"))
    assert f.name == "x"


def test_struct_pat() -> None:
    f = StructPatField(SPAN, "x", IdentPat(SPAN, "a"))
    p = StructPat(span=SPAN, name="Point", fields=[f])
    assert p.name == "Point"
    assert len(p.fields) == 1


def test_enum_pat_unit() -> None:
    p = EnumPat(span=SPAN, name="None", elements=[])
    assert p.elements == []


def test_enum_pat_with_payload() -> None:
    p = EnumPat(span=SPAN, name="Some", elements=[IdentPat(SPAN, "x")])
    assert len(p.elements) == 1


def test_pattern_alias_importable() -> None:
    assert Pattern is not None


# ---------------------------------------------------------------------------
# Control flow nodes
# ---------------------------------------------------------------------------


def test_if_expr_no_else() -> None:
    cond = LiteralExpr(SPAN, LiteralKind.BOOL, "true")
    e = IfExpr(span=SPAN, condition=cond, then_=BlockExpr(SPAN))
    assert e.else_ is None


def test_if_expr_with_block_else() -> None:
    cond = LiteralExpr(SPAN, LiteralKind.BOOL, "true")
    else_block = BlockExpr(SPAN)
    e = IfExpr(span=SPAN, condition=cond, then_=BlockExpr(SPAN), else_=else_block)
    assert isinstance(e.else_, BlockExpr)


def test_if_expr_with_else_if() -> None:
    inner_cond = LiteralExpr(SPAN, LiteralKind.BOOL, "false")
    inner_if = IfExpr(span=SPAN, condition=inner_cond, then_=BlockExpr(SPAN))
    outer_cond = LiteralExpr(SPAN, LiteralKind.BOOL, "true")
    e = IfExpr(span=SPAN, condition=outer_cond, then_=BlockExpr(SPAN), else_=inner_if)
    assert isinstance(e.else_, IfExpr)


def test_loop_stmt() -> None:
    body = BlockExpr(SPAN)
    s = LoopStmt(span=SPAN, body=body)
    assert s.body is body


def test_for_stmt() -> None:
    iter_expr = IdentExpr(SPAN, "items")
    body = BlockExpr(SPAN)
    s = ForStmt(span=SPAN, name="x", iter=iter_expr, body=body)
    assert s.name == "x"
    assert s.body is body


def test_match_arm_single_pattern() -> None:
    pat = WildcardPat(SPAN)
    body = LiteralExpr(SPAN, LiteralKind.INT, "1")
    arm = MatchArm(span=SPAN, patterns=[pat], body=body)
    assert len(arm.patterns) == 1


def test_match_arm_or_pattern() -> None:
    p1 = LiteralPat(SPAN, LiteralExpr(SPAN, LiteralKind.INT, "1"))
    p2 = LiteralPat(SPAN, LiteralExpr(SPAN, LiteralKind.INT, "2"))
    body = LiteralExpr(SPAN, LiteralKind.BOOL, "true")
    arm = MatchArm(span=SPAN, patterns=[p1, p2], body=body)
    assert len(arm.patterns) == 2


def test_match_expr() -> None:
    subject = IdentExpr(SPAN, "x")
    arm = MatchArm(SPAN, [WildcardPat(SPAN)], LiteralExpr(SPAN, LiteralKind.INT, "0"))
    m = MatchExpr(span=SPAN, subject=subject, arms=[arm])
    assert len(m.arms) == 1


# ---------------------------------------------------------------------------
# Trait and impl nodes
# ---------------------------------------------------------------------------


def test_trait_decl_defaults() -> None:
    t = TraitDecl(span=SPAN, name="Display")
    assert t.vis is False
    assert t.methods == []
    assert t.doc is None


def test_trait_decl_with_methods() -> None:
    fn = FnItem(SPAN, "fmt")
    t = TraitDecl(span=SPAN, name="Display", methods=[fn])
    assert len(t.methods) == 1


def test_impl_block_inherent() -> None:
    impl = ImplBlock(span=SPAN, type_=IdentType(SPAN, "Point"))
    assert impl.trait_ is None
    assert impl.methods == []


def test_impl_block_trait() -> None:
    impl = ImplBlock(span=SPAN, type_=IdentType(SPAN, "Point"), trait_="Display")
    assert impl.trait_ == "Display"


def test_item_alias_importable() -> None:
    assert Item is not None


# ---------------------------------------------------------------------------
# File node
# ---------------------------------------------------------------------------


def test_file_items_source_order() -> None:
    mod = ModuleDecl(SPAN, ["myapp"])
    use1 = UseDecl(SPAN, ["std", "io"], None)
    use2 = UseDecl(SPAN, ["std", "fmt"], None)
    fn = FnItem(SPAN, "main")
    f = File(span=SPAN, module=mod, items=[use1, use2, fn])
    assert len(f.items) == 3
    assert isinstance(f.items[0], UseDecl)
    assert isinstance(f.items[2], FnItem)


def test_file_module_separate_from_items() -> None:
    mod = ModuleDecl(SPAN, ["myapp"])
    use = UseDecl(SPAN, ["std", "io"], None)
    f = File(span=SPAN, module=mod, items=[use])
    assert f.module is mod
    assert isinstance(f.items[0], UseDecl)


def test_file_defaults() -> None:
    f = File(span=SPAN)
    assert f.module is None
    assert f.items == []


# ---------------------------------------------------------------------------
# Union alias import smoke tests
# ---------------------------------------------------------------------------


def test_all_union_aliases_importable() -> None:
    for alias in (Expr, Stmt, Pattern, Item, Type_):
        assert alias is not None
