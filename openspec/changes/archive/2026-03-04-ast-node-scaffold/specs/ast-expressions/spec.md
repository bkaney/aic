## ADDED Requirements

### Requirement: LiteralKind enum
`ast.py` SHALL define a `LiteralKind` enum with members: `INT`, `FLOAT`, `STRING`, `BYTES`, `RAW_STRING`, `BOOL`, `NONE`.

#### Scenario: LiteralKind is importable
- **WHEN** a caller does `from aiclang.ast import LiteralKind`
- **THEN** no `ImportError` is raised

### Requirement: LiteralExpr node
`ast.py` SHALL define a `LiteralExpr` dataclass extending `Node` with fields: `kind: LiteralKind`, `value: str`.

#### Scenario: LiteralExpr stores raw source text
- **WHEN** a `LiteralExpr` is constructed with `kind=LiteralKind.INT` and `value="0xFF"`
- **THEN** `node.value` is `"0xFF"` (unchanged from source)

#### Scenario: LiteralExpr for boolean
- **WHEN** a `LiteralExpr` is constructed with `kind=LiteralKind.BOOL` and `value="true"`
- **THEN** `node.kind` is `LiteralKind.BOOL`

### Requirement: IdentExpr node
`ast.py` SHALL define an `IdentExpr` dataclass extending `Node` with field `name: str`.

#### Scenario: IdentExpr stores identifier text
- **WHEN** an `IdentExpr` is constructed with `name="x"`
- **THEN** `node.name` is `"x"`

### Requirement: PathExpr node
`ast.py` SHALL define a `PathExpr` dataclass extending `Node` with field `segments: List[str]`.

#### Scenario: PathExpr stores path segments
- **WHEN** a `PathExpr` is constructed with `segments=["std", "io", "read"]`
- **THEN** `node.segments` has three elements

### Requirement: BinaryExpr node
`ast.py` SHALL define a `BinaryExpr` dataclass extending `Node` with fields: `op: str`, `left: Expr`, `right: Expr`.

#### Scenario: BinaryExpr stores operator as string
- **WHEN** a `BinaryExpr` is constructed with `op="+"` and two operand expressions
- **THEN** `node.op` is `"+"`, `node.left` and `node.right` are accessible

### Requirement: UnaryExpr node
`ast.py` SHALL define a `UnaryExpr` dataclass extending `Node` with fields: `op: str`, `operand: Expr`.

#### Scenario: UnaryExpr stores operator and operand
- **WHEN** a `UnaryExpr` is constructed with `op="!"` and an operand
- **THEN** `node.op` is `"!"` and `node.operand` is accessible

### Requirement: CallExpr node
`ast.py` SHALL define a `CallExpr` dataclass extending `Node` with fields: `callee: Expr`, `args: List[Expr]`.

#### Scenario: CallExpr carries callee and argument list
- **WHEN** a `CallExpr` is constructed with a callee and two args
- **THEN** `node.callee` is the callee expression and `len(node.args)` is 2

### Requirement: MemberExpr node
`ast.py` SHALL define a `MemberExpr` dataclass extending `Node` with fields: `object: Expr`, `member: str`.

#### Scenario: MemberExpr carries object and field name
- **WHEN** a `MemberExpr` is constructed with an object and `member="x"`
- **THEN** `node.member` is `"x"`

### Requirement: IndexExpr node
`ast.py` SHALL define an `IndexExpr` dataclass extending `Node` with fields: `object: Expr`, `index: Expr`.

#### Scenario: IndexExpr carries object and index expression
- **WHEN** an `IndexExpr` is constructed
- **THEN** `node.object` and `node.index` are accessible

### Requirement: AwaitExpr node
`ast.py` SHALL define an `AwaitExpr` dataclass extending `Node` with field `expr: Expr`.

#### Scenario: AwaitExpr wraps the awaited expression
- **WHEN** an `AwaitExpr` is constructed
- **THEN** `node.expr` is the inner expression

### Requirement: TryExpr node
`ast.py` SHALL define a `TryExpr` dataclass extending `Node` with field `expr: Expr` representing the `?` postfix operator.

#### Scenario: TryExpr wraps the tried expression
- **WHEN** a `TryExpr` is constructed
- **THEN** `node.expr` is the inner expression

### Requirement: Expr union alias covers all expression node kinds
`ast.py` SHALL define `Expr = Union[LiteralExpr, IdentExpr, PathExpr, BinaryExpr, UnaryExpr, CallExpr, MemberExpr, IndexExpr, AwaitExpr, BlockExpr, ReturnExpr, TryExpr, IfExpr]` and expose it at module level.

#### Scenario: Expr alias is importable from ast module
- **WHEN** a caller does `from aiclang.ast import Expr`
- **THEN** no `ImportError` is raised

### Requirement: ReturnExpr node
`ast.py` SHALL define a `ReturnExpr` dataclass extending `Node` with field `value: Optional[Expr] = None`.

#### Scenario: ReturnExpr with value
- **WHEN** a `ReturnExpr` is constructed with a value expression
- **THEN** `node.value` is that expression

#### Scenario: ReturnExpr without value
- **WHEN** a `ReturnExpr` is constructed with no value
- **THEN** `node.value` is `None`
