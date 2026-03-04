## ADDED Requirements

### Requirement: FnItem node
`ast.py` SHALL define a `FnItem` dataclass extending `Node` with fields: `name: str`, `generics: List[GenericParam]`, `params: List[Param]`, `ret: Optional[Type_]`, `where_: Optional[WhereClause]`, `effects: Optional[EffectsClause]`, `body: BlockExpr`, `doc: Optional[DocComment] = None`, `vis: bool = False`, `async_: bool = False`.

#### Scenario: FnItem default is sync and private
- **WHEN** a `FnItem` is constructed without specifying `async_` or `vis`
- **THEN** `node.async_` is `False` and `node.vis` is `False`

#### Scenario: FnItem with return type
- **WHEN** a `FnItem` is constructed with a `ret` type node
- **THEN** `node.ret` is that type node

#### Scenario: FnItem without return type
- **WHEN** a `FnItem` is constructed with `ret=None`
- **THEN** `node.ret` is `None`

### Requirement: GenericParam node
`ast.py` SHALL define a `GenericParam` dataclass extending `Node` with field `name: str`.

#### Scenario: GenericParam carries the type parameter name
- **WHEN** a `GenericParam` is constructed with `name="T"`
- **THEN** `node.name` is `"T"`

### Requirement: Param node
`ast.py` SHALL define a `Param` dataclass extending `Node` with fields: `name: str`, `type_: Type_`, `self_: bool = False`.

#### Scenario: Regular parameter carries name and type
- **WHEN** a `Param` is constructed with a name and type
- **THEN** `node.name` and `node.type_` are accessible

#### Scenario: Self parameter is flagged
- **WHEN** a `Param` is constructed with `self_=True`
- **THEN** `node.self_` is `True`

### Requirement: WhereClause node
`ast.py` SHALL define a `WhereClause` dataclass extending `Node` with field `constraints: List[WhereConstraint]`.

#### Scenario: WhereClause stores constraints
- **WHEN** a `WhereClause` is constructed with one or more `WhereConstraint` nodes
- **THEN** `node.constraints` returns those nodes

### Requirement: WhereConstraint node
`ast.py` SHALL define a `WhereConstraint` dataclass extending `Node` with fields: `param: str`, `bound: Type_`.

#### Scenario: WhereConstraint carries parameter name and bound
- **WHEN** a `WhereConstraint` is constructed with `param="T"` and a bound type
- **THEN** `node.param` is `"T"` and `node.bound` is accessible

### Requirement: EffectsClause node
`ast.py` SHALL define an `EffectsClause` dataclass extending `Node` with field `effects: List[str]`.

#### Scenario: EffectsClause stores effect names as strings
- **WHEN** an `EffectsClause` is constructed with `effects=["io", "net"]`
- **THEN** `node.effects` is `["io", "net"]`

### Requirement: BlockExpr node
`ast.py` SHALL define a `BlockExpr` dataclass extending `Node` with fields: `stmts: List[Stmt]`, `expr: Optional[Expr] = None`.

#### Scenario: BlockExpr with statements only
- **WHEN** a `BlockExpr` is constructed with statements and no trailing expr
- **THEN** `node.expr` is `None`

#### Scenario: BlockExpr with trailing expression
- **WHEN** a `BlockExpr` is constructed with a trailing `expr`
- **THEN** `node.expr` is that expression node

### Requirement: Stmt union alias covers all statement node kinds
`ast.py` SHALL define `Stmt = Union[LetStmt, ExprStmt, ReturnStmt]` and expose it at module level.

#### Scenario: Stmt alias is importable from ast module
- **WHEN** a caller does `from aiclang.ast import Stmt`
- **THEN** no `ImportError` is raised

### Requirement: ExprStmt node
`ast.py` SHALL define an `ExprStmt` dataclass extending `Node` with field `expr: Expr`.

#### Scenario: ExprStmt wraps an expression
- **WHEN** an `ExprStmt` is constructed with an expression node
- **THEN** `node.expr` is that expression

### Requirement: ReturnStmt node
`ast.py` SHALL define a `ReturnStmt` dataclass extending `Node` with field `value: Optional[Expr] = None`.

#### Scenario: ReturnStmt with value
- **WHEN** a `ReturnStmt` is constructed with a value expression
- **THEN** `node.value` is that expression

#### Scenario: Bare return has no value
- **WHEN** a `ReturnStmt` is constructed without a value
- **THEN** `node.value` is `None`
