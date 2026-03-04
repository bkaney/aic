## ADDED Requirements

### Requirement: IfExpr node
`ast.py` SHALL define an `IfExpr` dataclass extending `Node` with fields: `condition: Expr`, `then_: BlockExpr`, `else_: Optional[Expr] = None`.

#### Scenario: IfExpr without else branch
- **WHEN** an `IfExpr` is constructed with a condition and then-block only
- **THEN** `node.else_` is `None`

#### Scenario: IfExpr with else block
- **WHEN** an `IfExpr` is constructed with a `BlockExpr` as `else_`
- **THEN** `node.else_` is that `BlockExpr`

#### Scenario: IfExpr with else-if chain
- **WHEN** an `IfExpr` is constructed with another `IfExpr` as `else_`
- **THEN** `node.else_` is that nested `IfExpr`

### Requirement: LoopStmt node
`ast.py` SHALL define a `LoopStmt` dataclass extending `Node` with field `body: BlockExpr`.

#### Scenario: LoopStmt carries the loop body
- **WHEN** a `LoopStmt` is constructed with a `BlockExpr`
- **THEN** `node.body` is that block

### Requirement: ForStmt node
`ast.py` SHALL define a `ForStmt` dataclass extending `Node` with fields: `name: str`, `iter: Expr`, `body: BlockExpr`.

#### Scenario: ForStmt carries binding name, iterator, and body
- **WHEN** a `ForStmt` is constructed with `name="x"`, an iterator expression, and a body block
- **THEN** `node.name` is `"x"`, `node.iter` and `node.body` are accessible

### Requirement: MatchExpr node
`ast.py` SHALL define a `MatchExpr` dataclass extending `Node` with fields: `subject: Expr`, `arms: List[MatchArm]`.

#### Scenario: MatchExpr carries subject and arms
- **WHEN** a `MatchExpr` is constructed with a subject expression and two arms
- **THEN** `node.subject` is accessible and `len(node.arms)` is 2

### Requirement: MatchArm node
`ast.py` SHALL define a `MatchArm` dataclass extending `Node` with fields: `patterns: List[Pattern]`, `body: Expr`.

#### Scenario: MatchArm carries one or more patterns and a body
- **WHEN** a `MatchArm` is constructed with a single `WildcardPat` and a `LiteralExpr` body
- **THEN** `len(node.patterns)` is 1 and `node.body` is the `LiteralExpr`

#### Scenario: MatchArm with multiple patterns (OR arm)
- **WHEN** a `MatchArm` is constructed with two patterns
- **THEN** `len(node.patterns)` is 2

### Requirement: IfExpr is included in the Expr union alias
`ast.py` SHALL include `IfExpr` in the `Expr` union alias so that if-expressions may appear anywhere an expression is expected.

#### Scenario: IfExpr is a valid Expr
- **WHEN** an `IfExpr` instance is used where an `Expr` is expected
- **THEN** static type checkers accept it without error

### Requirement: LoopStmt and ForStmt are included in the Stmt union alias
`ast.py` SHALL include `LoopStmt` and `ForStmt` in the `Stmt` union alias.

#### Scenario: LoopStmt is a valid Stmt
- **WHEN** a `LoopStmt` instance is assigned to a variable typed as `Stmt`
- **THEN** static type checkers accept it without error

#### Scenario: ForStmt is a valid Stmt
- **WHEN** a `ForStmt` instance is assigned to a variable typed as `Stmt`
- **THEN** static type checkers accept it without error
