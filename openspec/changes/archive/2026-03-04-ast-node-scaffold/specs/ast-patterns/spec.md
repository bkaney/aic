## ADDED Requirements

### Requirement: WildcardPat node
`ast.py` SHALL define a `WildcardPat` dataclass extending `Node` with no additional fields, representing the `_` pattern.

#### Scenario: WildcardPat is constructible with only a span
- **WHEN** a `WildcardPat` is constructed with a `Span`
- **THEN** the node is created without error

### Requirement: IdentPat node
`ast.py` SHALL define an `IdentPat` dataclass extending `Node` with fields: `name: str`, `mut: bool = False`.

#### Scenario: IdentPat stores binding name
- **WHEN** an `IdentPat` is constructed with `name="x"`
- **THEN** `node.name` is `"x"`

#### Scenario: IdentPat default is immutable binding
- **WHEN** an `IdentPat` is constructed without specifying `mut`
- **THEN** `node.mut` is `False`

### Requirement: LiteralPat node
`ast.py` SHALL define a `LiteralPat` dataclass extending `Node` with field `lit: LiteralExpr`.

#### Scenario: LiteralPat carries the literal expression
- **WHEN** a `LiteralPat` is constructed with a `LiteralExpr`
- **THEN** `node.lit` is that expression

### Requirement: TuplePat node
`ast.py` SHALL define a `TuplePat` dataclass extending `Node` with field `elements: List[Pattern]`.

#### Scenario: TuplePat stores element patterns
- **WHEN** a `TuplePat` is constructed with two element patterns
- **THEN** `node.elements` has length 2

### Requirement: StructPat node
`ast.py` SHALL define a `StructPat` dataclass extending `Node` with fields: `name: str`, `fields: List[StructPatField]`.

#### Scenario: StructPat carries struct name and field patterns
- **WHEN** a `StructPat` is constructed with `name="Point"` and a list of field patterns
- **THEN** `node.name` is `"Point"` and `node.fields` is accessible

### Requirement: StructPatField node
`ast.py` SHALL define a `StructPatField` dataclass extending `Node` with fields: `name: str`, `pattern: Pattern`.

#### Scenario: StructPatField pairs field name with sub-pattern
- **WHEN** a `StructPatField` is constructed with `name="x"` and an `IdentPat`
- **THEN** `node.name` is `"x"` and `node.pattern` is that `IdentPat`

### Requirement: EnumPat node
`ast.py` SHALL define an `EnumPat` dataclass extending `Node` with fields: `name: str`, `elements: List[Pattern]`.

#### Scenario: EnumPat carries variant name and payload patterns
- **WHEN** an `EnumPat` is constructed with `name="Some"` and one element pattern
- **THEN** `node.name` is `"Some"` and `len(node.elements)` is 1

#### Scenario: Unit enum pattern has empty elements
- **WHEN** an `EnumPat` is constructed with no elements
- **THEN** `node.elements` is an empty list

### Requirement: Pattern union alias covers all pattern node kinds
`ast.py` SHALL define `Pattern = Union[WildcardPat, IdentPat, LiteralPat, TuplePat, StructPat, EnumPat]` and expose it at module level.

#### Scenario: Pattern alias is importable from ast module
- **WHEN** a caller does `from aiclang.ast import Pattern`
- **THEN** no `ImportError` is raised
